#!/usr/bin/env python3
import json
import platform
import re
import shlex
from argparse import (
    ArgumentParser,
    Namespace,
)
from urllib.parse import urlparse

from script import Script


class KotlinLspInstaller(Script):
    def _get_artifact(self, body: str, os_name: str, arch: str):
        platform_label = {
            "linux": "Linux",
            "macos": "macOS",
            "windows": "Windows",
        }[os_name]
        arch_label = {"x64": "x64", "arm64": "arm64"}[arch]
        target = f"Download for {platform_label}-{arch_label}".casefold()
        links = re.findall(
            r"\[(?P<label>[^\]]+)\]\((?P<url>https?://[^\s)]+)\)",
            body,
        )
        candidates = []

        for (label, url), (checksum_label, checksum_url) in zip(links, links[1:]):
            if " ".join(label.split()).casefold() != target:
                continue
            checksum_label = re.sub(r"[^a-z0-9]", "", checksum_label.casefold())
            if "sha256" not in checksum_label or "checksum" not in checksum_label:
                continue

            path = urlparse(url).path.casefold()
            if path.endswith(".tar.gz"):
                candidates.append((0, url, checksum_url, "tar.gz"))
            elif path.endswith((".zip", ".sit")):
                candidates.append((0, url, checksum_url, "zip"))
            elif path.endswith(".vsix"):
                candidates.append((1, url, checksum_url, "zip"))

        if not candidates:
            raise RuntimeError(
                f"Could not find a Kotlin LSP download URL for "
                f"{platform_label}-{arch_label}"
            )
        _, url, checksum_url, archive_type = min(candidates)
        return url, checksum_url, archive_type

    def _install_artifact(self, artifact, version: str):
        archive_url, checksum_url, archive_type = artifact
        self.shell.env.update(
            {
                "KOTLIN_LSP_ARCHIVE_URL": archive_url,
                "KOTLIN_LSP_CHECKSUM_URL": checksum_url,
                "KOTLIN_LSP_ARCHIVE_TYPE": archive_type,
                "KOTLIN_LSP_VERSION": version,
                "KOTLIN_LSP_INSTALL_DIR": str(self.HOME / ".local" / "kotlin-lsp"),
                "KOTLIN_LSP_BIN_DIR": str(self.HOME / ".local" / "bin"),
            }
        )
        ok, out, err = self.shell.exec(
            f"Installing kotlin lsp (v{version})",
            r"""
            set -euo pipefail

            install_dir=$KOTLIN_LSP_INSTALL_DIR
            bin_dir=$KOTLIN_LSP_BIN_DIR
            version=$KOTLIN_LSP_VERSION
            target="$install_dir/kotlin-server-$version"
            current="$bin_dir/kotlin-lsp.sh"
            mkdir -p -- "$install_dir" "$bin_dir"

            stage=$(mktemp -d "$install_dir/.staging-$version-XXXXXX")
            backup="$stage/previous-server"
            temporary_link="$bin_dir/.kotlin-lsp.sh.$$"
            published=
            backed_up=
            committed=
            cleanup() {
                status=$?
                trap - EXIT INT TERM
                rm -f -- "$temporary_link"
                if [ -z "$committed" ]; then
                    [ -z "$published" ] || rm -rf -- "$target"
                    [ -z "$backed_up" ] || mv -- "$backup" "$target"
                fi
                rm -rf -- "$stage"
                exit "$status"
            }
            trap cleanup EXIT INT TERM

            archive="$stage/archive"
            checksum="$stage/archive.sha256"
            extracted="$stage/extracted"
            curl -fLsS --retry 3 -o "$archive" "$KOTLIN_LSP_ARCHIVE_URL"
            curl -fLsS --retry 3 -o "$checksum" "$KOTLIN_LSP_CHECKSUM_URL"

            expected=$(awk 'NR == 1 { print tolower($1) }' "$checksum")
            printf '%s\n' "$expected" | grep -Eq '^[0-9a-f]{64}$' || {
                echo "Kotlin LSP checksum file is invalid" >&2
                exit 1
            }
            if command -v sha256sum >/dev/null 2>&1; then
                actual=$(sha256sum "$archive" | awk '{ print $1 }')
            elif command -v shasum >/dev/null 2>&1; then
                actual=$(shasum -a 256 "$archive" | awk '{ print $1 }')
            else
                echo "sha256sum or shasum is required" >&2
                exit 1
            fi
            [ "$actual" = "$expected" ] || {
                echo "Kotlin LSP archive checksum mismatch" >&2
                exit 1
            }

            mkdir -- "$extracted"
            case "$KOTLIN_LSP_ARCHIVE_TYPE" in
                tar.gz) tar -xzf "$archive" -C "$extracted" ;;
                zip) unzip -q "$archive" -d "$extracted" ;;
                *) echo "Unsupported Kotlin LSP archive type" >&2; exit 1 ;;
            esac

            find "$extracted" -type f -path '*/bin/intellij-server' \
                -print > "$stage/launchers"
            [ "$(wc -l < "$stage/launchers" | tr -d '[:space:]')" = 1 ] || {
                echo "Kotlin LSP archive must contain exactly one launcher" >&2
                exit 1
            }
            launcher=$(sed -n '1p' "$stage/launchers")
            chmod +x "$launcher"
            "$launcher" --version | grep -Fq "LS-$version" || {
                echo "Kotlin LSP launcher version verification failed" >&2
                exit 1
            }

            previous=
            if [ -L "$current" ]; then
                previous=$(readlink "$current")
                previous=${previous%/bin/intellij-server}
            fi
            if [ -e "$target" ] || [ -L "$target" ]; then
                mv -- "$target" "$backup"
                backed_up=1
            fi
            mv -- "$(dirname "$(dirname "$launcher")")" "$target"
            published=1
            ln -s "$target/bin/intellij-server" "$temporary_link"
            mv -f -- "$temporary_link" "$current"
            committed=1

            case "$previous" in
                "$install_dir"/kotlin-server-*) ;;
                *) previous= ;;
            esac
            for directory in "$install_dir"/kotlin-server-*; do
                [ -d "$directory" ] || continue
                [ "$directory" = "$target" ] && continue
                [ "$directory" = "$previous" ] && continue
                rm -rf -- "$directory"
            done
            """,
        )
        if not ok:
            raise RuntimeError(
                f"Failed to install Kotlin LSP: {err or out or 'unknown error'}"
            )

    def run(self):
        system = platform.system().lower()
        machine = platform.machine().lower()
        os_name = {
            "darwin": "macos",
            "linux": "linux",
            "windows": "windows",
        }.get(system)
        arch = {
            "x86_64": "x64",
            "amd64": "x64",
            "arm64": "arm64",
            "aarch64": "arm64",
        }.get(machine)
        if os_name is None:
            raise RuntimeError(f"Unsupported operating system: {system}")
        if arch is None:
            raise RuntimeError(f"Unsupported architecture: {machine}")

        ok, out, err = self.shell.run(
            "curl -fsSL "
            "https://api.github.com/repos/Kotlin/kotlin-lsp/releases/latest"
        )
        if not ok:
            raise RuntimeError(f"Failed to fetch latest Kotlin LSP release: {err}")

        release = json.loads(out)
        version = release["tag_name"].rsplit("/", 1)[-1].removeprefix("v")
        current = self.HOME / ".local" / "bin" / "kotlin-lsp.sh"
        if current.is_file():
            current_ok, current_version, _ = self.shell.run(
                f"{shlex.quote(str(current))} --version"
            )
            if current_ok and f"LS-{version}" in current_version:
                print(f"Kotlin LSP v{version} is already installed")
                return

        artifact = self._get_artifact(release.get("body", ""), os_name, arch)
        self._install_artifact(artifact, version)


if __name__ == "__main__":
    KotlinLspInstaller(ArgumentParser().parse_args()).run()

#!/usr/bin/env python3
import json
import platform
import re
import shlex
import uuid
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
        install_dir = self.HOME / ".local" / "kotlin-lsp"
        self.shell.env.update(
            {
                "KOTLIN_LSP_ARCHIVE_URL": archive_url,
                "KOTLIN_LSP_CHECKSUM_URL": checksum_url,
                "KOTLIN_LSP_ARCHIVE_TYPE": archive_type,
                "KOTLIN_LSP_VERSION": version,
                "KOTLIN_LSP_INSTALL_DIR": str(install_dir),
                "KOTLIN_LSP_BIN_DIR": str(self.HOME / ".local" / "bin"),
                "KOTLIN_LSP_STAGE_DIR": str(
                    install_dir / f".staging-{version}-{uuid.uuid4().hex}"
                ),
            }
        )
        installed = self.shell.exec_list(
            f"Installing kotlin lsp v{version} "
            "[download/checksum/prepare/activate/cleanup]",
            r"""
            set -euo pipefail
            stage=$KOTLIN_LSP_STAGE_DIR
            archive="$stage/archive"
            checksum="$stage/archive.sha256"
            mkdir -p -- "$stage" "$KOTLIN_LSP_BIN_DIR"
            curl -fLsS --retry 3 -o "$archive" "$KOTLIN_LSP_ARCHIVE_URL"
            curl -fLsS --retry 3 -o "$checksum" "$KOTLIN_LSP_CHECKSUM_URL"
            touch "$stage/downloaded"
            """,
            r"""
            set -euo pipefail
            stage=$KOTLIN_LSP_STAGE_DIR
            [ -f "$stage/downloaded" ]
            archive="$stage/archive"
            checksum="$stage/archive.sha256"
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
            touch "$stage/checksum-verified"
            """,
            r"""
            set -euo pipefail
            stage=$KOTLIN_LSP_STAGE_DIR
            [ -f "$stage/checksum-verified" ]
            archive="$stage/archive"
            extracted="$stage/extracted"
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
            "$launcher" --version | grep -Fq "LS-$KOTLIN_LSP_VERSION" || {
                echo "Kotlin LSP launcher version verification failed" >&2
                exit 1
            }
            mv -- "$(dirname "$(dirname "$launcher")")" "$stage/server"
            touch "$stage/prepared"
            """,
            r"""
            set -euo pipefail
            stage=$KOTLIN_LSP_STAGE_DIR
            [ -f "$stage/prepared" ]
            install_dir=$KOTLIN_LSP_INSTALL_DIR
            bin_dir=$KOTLIN_LSP_BIN_DIR
            target="$install_dir/kotlin-server-$KOTLIN_LSP_VERSION"
            current="$bin_dir/kotlin-lsp.sh"
            backup="$stage/previous-server"
            temporary_link="$bin_dir/.kotlin-lsp.sh.$$"
            published=
            backed_up=
            committed=
            rollback() {
                status=$?
                trap - EXIT INT TERM
                rm -f -- "$temporary_link"
                if [ -z "$committed" ]; then
                    [ -z "$published" ] || rm -rf -- "$target"
                    [ -z "$backed_up" ] || mv -- "$backup" "$target"
                fi
                exit "$status"
            }
            trap rollback EXIT INT TERM
            previous=
            if [ -L "$current" ]; then
                previous=$(readlink "$current")
                previous=${previous%/bin/intellij-server}
            fi
            printf '%s\n' "$previous" > "$stage/previous-server-path"
            if [ -e "$target" ] || [ -L "$target" ]; then
                mv -- "$target" "$backup"
                backed_up=1
            fi
            mv -- "$stage/server" "$target"
            published=1
            ln -s "$target/bin/intellij-server" "$temporary_link"
            mv -f -- "$temporary_link" "$current"
            committed=1
            touch "$stage/committed"
            """,
            r"""
            set -euo pipefail
            stage=$KOTLIN_LSP_STAGE_DIR
            if [ -f "$stage/committed" ]; then
                install_dir=$KOTLIN_LSP_INSTALL_DIR
                target="$install_dir/kotlin-server-$KOTLIN_LSP_VERSION"
                previous=$(sed -n '1p' "$stage/previous-server-path")
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
            fi
            rm -rf -- "$stage"
            """,
        )
        if not installed:
            raise RuntimeError("Failed to install Kotlin LSP")

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

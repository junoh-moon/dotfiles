#!/usr/bin/env python3
import hashlib
import json
import os
import platform
import re
import shlex
import shutil
import tempfile
import uuid
from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from script import Script
from shell import Shell


@dataclass(frozen=True)
class ReleaseArtifact:
    url: str
    checksum_url: str
    archive_type: str


class KotlinLspInstaller(Script):
    def __init__(self, args: Namespace):
        super().__init__(args)
        self.HOME = Path.home()
        self.shell = Shell()

    def _get_platform_info(self):
        """Detect current platform and architecture for release matching."""
        system = platform.system().lower()
        machine = platform.machine().lower()

        # Map system names
        if system == "darwin":
            os_name = "macos"
        elif system == "linux":
            os_name = "linux"
        elif system == "windows":
            os_name = "windows"
        else:
            raise RuntimeError(f"Unsupported operating system: {system}")

        # Map architecture names
        if machine in ("x86_64", "amd64"):
            arch = "x64"
        elif machine in ("arm64", "aarch64"):
            arch = "arm64"
        else:
            raise RuntimeError(f"Unsupported architecture: {machine}")

        return os_name, arch

    def _get_latest_release(self):
        cmd = (
            "curl -fsSL https://api.github.com/repos/Kotlin/kotlin-lsp/releases/latest"
        )
        ok, out, err = self.shell.run(cmd)
        if not ok:
            raise RuntimeError(f"Failed to fetch latest kotlin-lsp release: {err}")

        return json.loads(out)

    def _get_version_from_tag(self, tag_name: str):
        return tag_name.rsplit("/", 1)[-1].removeprefix("v")

    def _get_artifact_from_release_body(
        self,
        body: str,
        os_name: str,
        arch: str,
    ) -> ReleaseArtifact:
        platform_label = {
            "linux": "Linux",
            "macos": "macOS",
            "windows": "Windows",
        }[os_name]
        arch_label = {
            "x64": "x64",
            "arm64": "arm64",
        }[arch]
        target_label = f"Download for {platform_label}-{arch_label}".casefold()
        links = re.findall(
            r"\[(?P<label>[^\]]+)\]\((?P<url>https?://[^\s)]+)\)",
            body,
        )
        candidates = []
        for index, (label, url) in enumerate(links):
            if " ".join(label.split()).casefold() != target_label:
                continue

            if index + 1 >= len(links):
                continue
            checksum_label, checksum_url = links[index + 1]
            normalized_checksum_label = re.sub(
                r"[^a-z0-9]",
                "",
                checksum_label.casefold(),
            )
            if (
                "sha256" not in normalized_checksum_label
                or "checksum" not in normalized_checksum_label
            ):
                continue

            path = urlparse(url).path.casefold()
            if path.endswith(".tar.gz"):
                candidates.append((0, ReleaseArtifact(url, checksum_url, "tar.gz")))
            elif path.endswith((".zip", ".sit")):
                candidates.append((0, ReleaseArtifact(url, checksum_url, "zip")))
            elif path.endswith(".vsix"):
                candidates.append((1, ReleaseArtifact(url, checksum_url, "zip")))

        if candidates:
            return min(candidates, key=lambda candidate: candidate[0])[1]

        raise RuntimeError(
            f"Could not find a Kotlin LSP download URL for "
            f"{platform_label}-{arch_label}"
        )

    def _install_artifact(self, artifact: ReleaseArtifact, version: str):
        install_dir = self.HOME / ".local" / "kotlin-lsp"
        install_dir.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(
            prefix=f".staging-{version}-",
            dir=install_dir,
        ) as temporary_dir:
            staging_dir = Path(temporary_dir)
            archive_path = staging_dir / "kotlin-lsp-archive"
            checksum_path = staging_dir / "kotlin-lsp-archive.sha256"
            for url, destination in (
                (artifact.url, archive_path),
                (artifact.checksum_url, checksum_path),
            ):
                command = (
                    "curl --fail --location --silent --show-error "
                    f"--retry 3 --output {shlex.quote(str(destination))} "
                    f"{shlex.quote(url)}"
                )
                ok, _, err = self.shell.run(command)
                if not ok:
                    raise RuntimeError(f"Failed to download {url}: {err}")

            checksum_match = re.match(
                r"(?P<checksum>[0-9a-fA-F]{64})\b",
                checksum_path.read_text().strip(),
            )
            if checksum_match is None:
                raise RuntimeError("Kotlin LSP checksum file is invalid")

            digest = hashlib.sha256()
            with archive_path.open("rb") as archive:
                for chunk in iter(lambda: archive.read(1024 * 1024), b""):
                    digest.update(chunk)
            if digest.hexdigest() != checksum_match.group("checksum").casefold():
                raise RuntimeError("Kotlin LSP archive checksum mismatch")

            extracted_dir = staging_dir / "extracted"
            extracted_dir.mkdir()
            if artifact.archive_type == "tar.gz":
                extract_command = (
                    f"tar -xzf {shlex.quote(str(archive_path))} "
                    f"-C {shlex.quote(str(extracted_dir))}"
                )
            elif artifact.archive_type == "zip":
                extract_command = (
                    f"unzip -q {shlex.quote(str(archive_path))} "
                    f"-d {shlex.quote(str(extracted_dir))}"
                )
            else:
                raise RuntimeError(
                    f"Unsupported Kotlin LSP archive type: {artifact.archive_type}"
                )

            ok, _, err = self.shell.run(extract_command)
            if not ok:
                raise RuntimeError(f"Failed to extract Kotlin LSP archive: {err}")

            launcher_candidates = list(extracted_dir.glob("**/bin/intellij-server"))
            if len(launcher_candidates) != 1:
                raise RuntimeError(
                    "Kotlin LSP archive must contain exactly one "
                    "bin/intellij-server launcher"
                )

            staged_launcher = launcher_candidates[0]
            staged_launcher.chmod(staged_launcher.stat().st_mode | 0o111)
            ok, output, err = self._launcher_version(staged_launcher)
            if not ok or f"LS-{version}" not in output:
                details = err or output or "no version output"
                raise RuntimeError(
                    f"Kotlin LSP launcher verification failed: {details}"
                )

            staged_server = staged_launcher.parent.parent
            launcher_relative_path = staged_launcher.relative_to(staged_server)
            server_dir = install_dir / f"kotlin-server-{version}"
            bin_dir = self.HOME / ".local" / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            current_link = bin_dir / "kotlin-lsp.sh"
            previous_server = self._get_installed_server(current_link, install_dir)
            backup_dir = install_dir / (f".backup-{version}-{uuid.uuid4().hex}")
            temporary_link = bin_dir / (f".kotlin-lsp.sh.{uuid.uuid4().hex}")
            had_existing_target = server_dir.exists()

            try:
                if had_existing_target:
                    server_dir.replace(backup_dir)
                staged_server.replace(server_dir)
                installed_launcher = server_dir / launcher_relative_path
                temporary_link.symlink_to(installed_launcher)
                os.replace(temporary_link, current_link)
            except Exception:
                temporary_link.unlink(missing_ok=True)
                if server_dir.exists():
                    shutil.rmtree(server_dir)
                if backup_dir.exists():
                    backup_dir.replace(server_dir)
                raise
            else:
                if backup_dir.exists():
                    shutil.rmtree(backup_dir)

            self._remove_obsolete_servers(
                install_dir,
                keep={server_dir, previous_server, staging_dir},
            )
            return installed_launcher

    def _get_installed_server(self, launcher: Path, install_dir: Path):
        if not launcher.exists():
            return None

        resolved_launcher = launcher.resolve()
        for parent in resolved_launcher.parents:
            if parent.parent == install_dir and parent.name.startswith(
                "kotlin-server-"
            ):
                return parent
        return None

    def _remove_obsolete_servers(self, install_dir: Path, keep):
        kept_servers = {path for path in keep if path is not None}
        for pattern in ("kotlin-server-*", ".staging-*", ".backup-*"):
            for directory in install_dir.glob(pattern):
                if directory not in kept_servers and directory.is_dir():
                    shutil.rmtree(directory)

    def _launcher_version(self, launcher: Path):
        if not launcher.is_file():
            return False, "", "launcher does not exist"
        return self.shell.run(f"{shlex.quote(str(launcher))} --version")

    def run(self):
        release = self._get_latest_release()
        version = self._get_version_from_tag(release["tag_name"])
        current_launcher = self.HOME / ".local" / "bin" / "kotlin-lsp.sh"
        current_ok, current_version, _ = self._launcher_version(current_launcher)
        if current_ok and f"LS-{version}" in current_version:
            print(f"Kotlin LSP v{version} is already installed")
            return

        os_name, arch = self._get_platform_info()
        artifact = self._get_artifact_from_release_body(
            release.get("body", ""),
            os_name,
            arch,
        )
        self._install_artifact(artifact, version)


if __name__ == "__main__":
    from argparse import ArgumentParser

    KotlinLspInstaller(ArgumentParser().parse_args()).run()

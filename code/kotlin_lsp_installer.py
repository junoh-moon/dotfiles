#!/usr/bin/env python3
import json
import platform
import re
from argparse import Namespace
from pathlib import Path

from script import Script
from shell import Shell


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
        cmd = "curl -fsSL https://api.github.com/repos/Kotlin/kotlin-lsp/releases/latest"
        ok, out, err = self.shell.run(cmd)
        if not ok:
            raise RuntimeError(f"Failed to fetch latest kotlin-lsp release: {err}")

        return json.loads(out)

    def _get_version_from_tag(self, tag_name: str):
        return tag_name.rsplit("/", 1)[-1].removeprefix("v")

    def _get_vsix_url_from_release_body(self, body: str, os_name: str, arch: str):
        platform_label = {
            "linux": "Linux",
            "macos": "macOS",
            "windows": "Windows",
        }[os_name]
        arch_label = {
            "x64": "x64",
            "arm64": "arm64",
        }[arch]

        pattern = (
            rf"Download for {re.escape(platform_label)}-{re.escape(arch_label)}"
            r"\]\((https://download-cdn\.jetbrains\.com/kotlin-lsp/[^\s)]+)\)"
        )
        for url in re.findall(pattern, body):
            if url.endswith(".vsix"):
                return url

        raise RuntimeError(
            f"Could not find a VSIX download URL for {platform_label}-{arch_label}"
        )

    def run(self):
        release = self._get_latest_release()
        version = self._get_version_from_tag(release["tag_name"])
        os_name, arch = self._get_platform_info()
        kotlin_lsp_link = self._get_vsix_url_from_release_body(
            release.get("body", ""),
            os_name,
            arch,
        )
        kotlin_lsp_dir = self.HOME / ".local" / "kotlin-lsp"
        server_dir = kotlin_lsp_dir / f"kotlin-server-{version}"
        launcher = server_dir / "bin" / "intellij-server"
        archive_path = Path("/tmp") / Path(kotlin_lsp_link).name
        staging_dir = Path("/tmp") / f"kotlin-lsp-vsix-{version}"
        installed = self.shell.exec_list(
            f"Installing kotlin lsp (v{version})",
            f"rm -rf '{kotlin_lsp_dir}' '{staging_dir}'",
            f"mkdir -p '{kotlin_lsp_dir}' '{staging_dir}'",
            f"mkdir -p '{self.HOME}/.local/bin'",
            f"curl -Lfo '{archive_path}' '{kotlin_lsp_link}'",
            f"unzip -q '{archive_path}' 'extension/server/*' -d '{staging_dir}'",
            f"mv '{staging_dir}/extension/server' '{server_dir}'",
            f"rm -rf '{staging_dir}' '{archive_path}'",
            f"chmod +x '{launcher}'",
            f"ln -sf '{launcher}' '{self.HOME}/.local/bin/kotlin-lsp.sh'",
        )
        if not installed:
            raise RuntimeError("Failed to install kotlin-lsp from VSIX")

if __name__ == "__main__":
    from argparse import ArgumentParser
    KotlinLspInstaller(ArgumentParser().parse_args()).run()

#!/usr/bin/env python3
import platform
from argparse import Namespace
from pathlib import Path
from sys import stderr

from script import Script
from shell import Shell
from util import GithubDownloadable


class KotlinLspInstaller(Script, GithubDownloadable):
    def __init__(self, args: Namespace):
        super().__init__(args)
        self.HOME = Path.home()
        self.shell = Shell()

    def _get_platform_info(self):
        """Detect current platform and architecture for download URL"""
        system = platform.system().lower()
        machine = platform.machine().lower()

        # Map system names
        if system == "darwin":
            os_name = "mac"
        elif system == "linux":
            os_name = "linux"
        elif system == "windows":
            os_name = "win"
        else:
            raise RuntimeError(f"Unsupported operating system: {system}")

        # Map architecture names
        if machine in ("x86_64", "amd64"):
            arch = "x64"
        elif machine in ("arm64", "aarch64"):
            arch = "aarch64"
        else:
            raise RuntimeError(f"Unsupported architecture: {machine}")

        return os_name, arch

    def _get_latest_version(self):
        """Fetch the latest version from GitHub releases"""
        cmd = """curl -s https://api.github.com/repos/Kotlin/kotlin-lsp/releases/latest |
            python3 -c "import sys, json; print(json.load(sys.stdin)['tag_name'])"
            """
        ok, out, err = self.shell.run(cmd)
        if not ok:
            print(f"Failed to fetch latest kotlin-lsp version: {err}", file=stderr)
            # Fallback to a known working version
            return "261.13587.0"

        # Extract version from tag (e.g., kotlin-lsp/v261.13587.0 -> 261.13587.0)
        version = out.strip()
        if '/' in version:
            version = version.split('/')[-1]
        if version.startswith('v'):
            version = version[1:]

        return version

    def run(self):
        version = self._get_latest_version()
        os_name, arch = self._get_platform_info()
        kotlin_lsp_link = f"https://download-cdn.jetbrains.com/kotlin-lsp/{version}/kotlin-lsp-{version}-{os_name}-{arch}.zip"
        kotlin_lsp_dir = f"{self.HOME}/.local/kotlin-lsp"
        self.shell.exec_list(
            f"Installing kotlin lsp (v{version})",
            f"rm -rf {kotlin_lsp_dir}",
            f"mkdir -p {kotlin_lsp_dir}",
            f"curl -Lfo /tmp/kotlin-lsp.zip '{kotlin_lsp_link}'",
            f"unzip -o /tmp/kotlin-lsp.zip -d {kotlin_lsp_dir}/",
            f"chmod +x {kotlin_lsp_dir}/kotlin-lsp.sh",
            f"ln -sf {kotlin_lsp_dir}/kotlin-lsp.sh {self.HOME}/.local/bin/kotlin-lsp.sh",
            "rm -f /tmp/kotlin-lsp.zip",
        )

if __name__ == "__main__":
    from argparse import ArgumentParser
    KotlinLspInstaller(ArgumentParser().parse_args()).run()

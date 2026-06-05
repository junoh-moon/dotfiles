#!/usr/bin/env python3
import platform
from argparse import (
    ArgumentParser,
    Namespace,
)

from script import Script
from util import GithubDownloadable


class NodeInstaller(Script, GithubDownloadable):
    def __init__(self, args: Namespace):
        super().__init__(args)

    def run(self):
        self._install_fnm()
        self._sourced_exec(
            "Installing nodejs lts via fnm",
            "fnm install --lts && fnm default lts-latest",
        )
        self._sourced_exec(
            "Installing yarn",
            "npm install --global yarn",
        )

        if self.args.typescript:
            self._sourced_exec(
                "Installing typescript related things",
                "npm install -g typescript ts-node pkg tslib",
            )
        return

    def _install_fnm(self):
        "Download the fnm binary (distributed as a zip) into ~/.local/bin."
        system = platform.system().lower()
        machine = platform.machine().lower()
        if system == "darwin":
            asset = "fnm-macos.zip"
        elif machine in ("arm64", "aarch64"):
            asset = "fnm-arm64.zip"
        elif machine.startswith("arm"):
            asset = "fnm-arm32.zip"
        else:
            asset = "fnm-linux.zip"

        link = self.get_download_link("Schniz/fnm", asset)
        if not link:
            raise RuntimeError("Could not resolve fnm download link")

        # The zip holds the `fnm` binary either at its root or under a
        # platform-named subdir, mirroring fnm's own install script.
        self.shell.exec(
            "Installing fnm",
            f"""
            set -e
            dl=$(mktemp -d)
            curl -fsSL -o "$dl/fnm.zip" "{link}"
            unzip -q "$dl/fnm.zip" -d "$dl"
            if [ -f "$dl/fnm" ]; then src="$dl/fnm"; else src="$dl"/*/fnm; fi
            install -m 755 $src "{self.HOME}/.local/bin/fnm"
            rm -rf "$dl"
            """,
        )

    def _sourced_exec(self, message: str, cmd: str):
        "Run cmd with the fnm-managed node on PATH (fnm lives in ~/.local/bin)."
        return self.shell.exec(message, f'eval "$(fnm env)" && {cmd}')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--typescript",
        "-t",
        action="store_true",
        help="install typescript",
        default=False,
    )

    NodeInstaller(parser.parse_args()).run()

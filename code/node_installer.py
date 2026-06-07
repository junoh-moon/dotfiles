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
        self._install_mise()
        mise = f"{self.HOME}/.local/bin/mise"
        config = f"{self.HOME}/.config/mise/config.toml"
        # On first install (no config yet) pin the current LTS into the config so
        # the choice is recorded; on every later run the existing pin is left
        # untouched, so Node is never silently upgraded. The config is per-machine
        # runtime state (gitignored), not part of the dotfiles.
        self.shell.exec(
            "Pinning current Node LTS (first install only; existing pin is kept)",
            f"""
            set -e
            if [ ! -f "{config}" ]; then
                mkdir -p "$(dirname "{config}")"
                lts=$("{mise}" latest node@lts)
                printf '[tools]\\nnode = "%s"\\n' "$lts" > "{config}"
            fi
            """,
        )
        self.shell.exec(
            "Installing the pinned Node version via mise",
            f'"{mise}" install',
        )

        if self.args.typescript:
            self._mise_exec(
                "Installing typescript related things",
                "npm install -g typescript ts-node pkg tslib",
            )
        return

    def _install_mise(self):
        "Download the mise binary (a tar.gz holding bin/mise) into ~/.local/bin."
        system = platform.system().lower()
        machine = platform.machine().lower()
        os_name = "macos" if system == "darwin" else "linux"
        arch = "arm64" if machine in ("arm64", "aarch64") else "x64"
        asset = f"-{os_name}-{arch}.tar.gz"  # leading dash avoids the -musl variant

        link = self.get_download_link("jdx/mise", asset)
        if not link:
            raise RuntimeError("Could not resolve mise download link")

        self.shell.exec(
            "Installing mise",
            f"""
            set -e
            dl=$(mktemp -d)
            curl -fsSL "{link}" | tar xz -C "$dl"
            install -m 755 "$dl/mise/bin/mise" "{self.HOME}/.local/bin/mise"
            rm -rf "$dl"
            """,
        )

    def _mise_exec(self, message: str, cmd: str):
        "Run cmd with mise's tools (the pinned Node) on PATH."
        return self.shell.exec(
            message, f'"{self.HOME}/.local/bin/mise" exec -- {cmd}'
        )


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

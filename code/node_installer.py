#!/usr/bin/env python3
from argparse import (
    ArgumentParser,
    Namespace,
)
from pathlib import Path

from script import Script


class NodeInstaller(Script):
    def __init__(self, args: Namespace):
        super().__init__(args)
        self.HOME = Path.home()

    def run(self):
        self.shell.exec(
            "Installing nvm",
            """
            _NVM_VER=$(curl -s "https://api.github.com/repos/nvm-sh/nvm/releases/latest" | grep '"tag_name":' | cut -d '"' -f 4);
            echo $_NVM_VER
            curl -s -o- https://raw.githubusercontent.com/nvm-sh/nvm/$_NVM_VER/install.sh | PROFILE=/dev/null bash
            """,
            # Set PROFILE to /dev/null to not update .zshrc or .bashrc
        )
        self._sourced_exec(
            "Installing nodejs lts via nvm",
            f"nvm install --lts --reinstall-packages-from=current",
        )
        self._sourced_exec(
            "Installing yarn",
            f"npm install --global yarn",
        )

        if self.args.typescript:
            self._sourced_exec(
                "Installing typescript related things",
                "npm install -g typescript ts-node pkg tslib",
            )
        return

    def _sourced_exec(self, message: str, cmd: str):
        return self.shell.exec(message, f"source {self.HOME}/.nvm/nvm.sh && {cmd}")


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


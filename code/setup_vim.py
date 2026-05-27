#!/usr/bin/env python3

import os
import platform
from argparse import (
    ArgumentParser,
    Namespace,
)

from script import Script
from util import GithubDownloadable


class Vim(Script, GithubDownloadable):
    def __init__(self, args: Namespace):
        super().__init__(args)
        self.nvm_path = f"{self.HOME}/.nvm/nvm.sh"
        self.optional_cargo_path = f"{self.HOME}/.cargo/env"  # This variable is not used on MacOS since Rust in installed via homebrew.

    def run(self) -> None:
        for cmd in ["npm", "python3 -m pip", "vim", "cargo"]:
            if not self._exists(cmd):
                raise RuntimeError(f"{cmd} is required")

        self._install_neovim()

        HOME = self.HOME
        proj_root = self.proj_root

        self.shell.exec(
            "Symbolic linking .vimrc", f'ln -fs "{proj_root}"/.vimrc {HOME}/.vimrc'
        )

        if not os.path.islink(f"{HOME}/.config"):
            self.shell.exec(
                f"Aliasing {HOME}/.config",
                f"""
                if [ -L {HOME}/.config ]; then
                    unlink {HOME}/.config
                else
                    rm -rf {HOME}/.config
                fi
                    
                ln -s "{proj_root}"/config {HOME}/.config
                """,
            )

        if self._exists("nvim"):
            self._setup_for_nvim()
        else:
            self._exec(
                "Installing vim plugins", "vim --not-a-term -c PlugInstall -c quitall"
            )

        self.shell.exec("Adding executable permission to HOME", f"chmod 755 {HOME}")

        self.shell.exec_list(
            "Symbolic linking other files",
            f"mkdir -p {HOME}/.vim",
            f'ln -sf "{proj_root}"/config/nvim/coc-settings.json {HOME}/.vim/',
            f'ln -sf "{proj_root}"/.coc.vimrc {HOME}/',
            f'ln -fs "{proj_root}"/.latexmkrc {HOME}/.latexmkrc',
        )

        self.shell.exec(
            "Installing yapf, black, rope, and coverage",
            "python3 -m pip install black yapf rope coverage",
        )

        if self.args.elixir:
            self.shell.exec_list(
                "Installing elixir-ls",
                "git clone https://github.com/elixir-lsp/elixir-ls.git ~/.elixir-ls",
                "cd ~/.elixir-ls && "
                ". $HOME/.asdf/asdf.sh && "
                "mix local.hex --force && "
                "mix local.rebar --force && "
                "mix deps.get && "
                "mix compile && "
                "mix elixir_ls.release -o release",
            )

        return

    def _install_neovim(self):
        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == "darwin":
            suffix = f"macos-{'arm64' if machine == 'arm64' else 'x86_64'}.tar.gz"
        else:
            suffix = f"linux-{'arm64' if machine in ('arm64', 'aarch64') else 'x86_64'}.tar.gz"

        self._mkdir(f"{self.HOME}/.local")
        self.shell.exec(
            "Installing the latest stable neovim",
            self.github_dl_cmd(
                "neovim/neovim",
                suffix=suffix,
                strip=1,
                binpath=f"{self.HOME}/.local",
            ),
        )

    def _setup_for_nvim(self):
        HOME = self.HOME
        proj_root = self.proj_root

        self.shell.exec(
            "Installing tree-sitter cli",
            self._sourced_cmd("cargo install tree-sitter-cli"),
        )

        self.shell.exec_list(
            "Installing plugins for neovim",
            "python3 -m pip install --upgrade 'pynvim @ git+https://github.com/neovim/pynvim'",  # At the time of writing, pynvim on pypi does not support python >= 3.12.
            "nvim --headless -c PlugInstall -c quitall",
            "nvim --headless -c CocUpdateSync -c quitall",
            "nvim --headless -c TSUpdateSync -c quitall",
        )
        return

    def _exists(self, cmd: str) -> bool:
        return super()._exists(self._sourced_cmd(cmd))

    def _sourced_cmd(self, cmd: str):
        return f"source {self.optional_cargo_path}; source {self.nvm_path} && {cmd}"

    def _exec(self, message: str, cmd: str):
        if self._exists(self.nvm_path):
            return self.shell.exec(message, self._sourced_cmd(cmd))
        else:
            return self.shell.exec(message, cmd)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--elixir", action="store_true")
    Vim(parser.parse_args()).run()

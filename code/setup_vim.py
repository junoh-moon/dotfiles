#!/usr/bin/env python3

import os
import platform
from argparse import (
    ArgumentParser,
    Namespace,
)
from pathlib import Path

from script import Script
from util import GithubDownloadable


class Vim(Script, GithubDownloadable):
    def __init__(self, args: Namespace):
        super().__init__(args)
        self.optional_cargo_path = f"{self.HOME}/.cargo/env"  # This variable is not used on MacOS since Rust in installed via homebrew.

    def run(self) -> None:
        for cmd in ["npm", "python3 -m pip"]:
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

    def _install_tree_sitter_cli(self):
        system = platform.system().lower()
        machine = platform.machine().lower()

        os_name = "macos" if system == "darwin" else "linux"
        arch = "arm64" if machine in ("arm64", "aarch64") else "x64"
        suffix = f"cli-{os_name}-{arch}.zip"

        link = self.get_download_link("tree-sitter/tree-sitter", suffix)
        if not link:
            return
        self.shell.exec_list(
            "Installing tree-sitter cli",
            f"curl -L {link} -o /tmp/tree-sitter-cli.zip",
            f"unzip -o /tmp/tree-sitter-cli.zip -d {self.HOME}/.local/bin",
            f"chmod +x {self.HOME}/.local/bin/tree-sitter",
            "rm /tmp/tree-sitter-cli.zip",
        )

    def _setup_for_nvim(self):
        self._install_tree_sitter_cli()

        python_host_dir = self._nvim_python_host_dir()
        python_host_prog = python_host_dir / "bin" / "python"

        self.shell.exec_list(
            "Installing plugins for neovim",
            f'python3 -m venv "{python_host_dir}"',
            f'"{python_host_prog}" -m pip install --upgrade pip',
            f'"{python_host_prog}" -m pip install --upgrade \'pynvim @ git+https://github.com/neovim/pynvim\'',  # At the time of writing, pynvim on pypi does not support python >= 3.12.
            "nvim --headless -c PlugInstall -c quitall",
            "nvim --headless -c CocUpdateSync -c quitall",
            "nvim --headless -c TSUpdateSync -c quitall",
        )
        return

    def _nvim_python_host_dir(self):
        return self.HOME / ".local" / "share" / "nvim" / "python3-host"

    def _exists(self, cmd: str) -> bool:
        return super()._exists(self._sourced_cmd(cmd))

    def _sourced_cmd(self, cmd: str):
        # Put mise's shims (the pinned Node/npm) and cargo on PATH for the command.
        return (
            f"source {self.optional_cargo_path}; "
            f'export PATH="{self.HOME}/.local/share/mise/shims:$PATH"; {cmd}'
        )

    def _exec(self, message: str, cmd: str):
        if self.shell.run(f"{self.HOME}/.local/bin/mise --version")[0]:
            return self.shell.exec(message, self._sourced_cmd(cmd))
        else:
            return self.shell.exec(message, cmd)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--elixir", action="store_true")
    Vim(parser.parse_args()).run()

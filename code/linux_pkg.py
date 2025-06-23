#!/usr/bin/env python3

from argparse import (
    ArgumentParser,
    Namespace,
)
from pathlib import Path

from elixir_installer import ElixirInstaller
from java_installer import JavaInstaller
from kotlin_lsp_installer import KotlinLspInstaller
from node_installer import NodeInstaller
from script import Script
from util import GithubDownloadable


class LinuxAMD64(Script, GithubDownloadable):
    def __init__(self, args: Namespace):
        super().__init__(args)
        self.HOME = Path.home()

        self.zsh_completion_path = f"{self.HOME}/.local/share/zsh/vendor-completions"
        self.bash_completion_path = (
            f"{self.HOME}/.local/share/bash-completion/completions"
        )
        self.man_path = f"{self.HOME}/.local/share/man/man1"

    def run(self):
        self._mkdir(f"{self.HOME}/.local/bin")

        self.shell.exec(
            "Installing rust",
            "curl https://sh.rustup.rs -sSf | sh -s -- -y --no-modify-path",
        )

        self.shell.exec(
            "Installing visidata",
            "pip3 install --upgrade visidata",
        )

        self.shell.sudo_exec(
            "Installing tldr",
            "snap install tldr",
        )

        self.shell.exec(
            "Installing MinySubtitleConverter",
            self.github_dl_cmd(
                "snowphone/MinySubtitleConverter",
                "linux-amd64.tar.gz",
            ),
        )

        self.shell.exec(
            "Installing bazel-lsp",
            self.github_dl_single_cmd(
                "cameron-martin/bazel-lsp",
                "linux-amd64",
                f"{self.HOME}/.local/bin/bazel-lsp",
            ),
        )

        self.shell.exec(
            "Installing k9s",
            self.github_dl_cmd(
                "derailed/k9s",
                "Linux_amd64.tar.gz",
            ),
        )

        self.shell.exec_list(
            "Installing subtitle matcher",
            "rm -rf /tmp/subtitle_matcher",
            "git clone https://github.com/snowphone/Subtitle-Matcher.git /tmp/subtitle_matcher",
            "cd /tmp/subtitle_matcher && make install",
            "python3 -m pip install --upgrade tabulate",
            "rm -rf /tmp/subtitle_matcher",
        )

        self.shell.exec(
            "Installing commitgpt",
            f"source $HOME/.cargo/env && cargo install --force --git https://github.com/snowphone/CommitGPT",
        )

        self.shell.exec(
            "Installing macchina",
            f"source $HOME/.cargo/env && cargo install --force macchina",
        )

        self.shell.exec(
            "Installing pudb, a python debugger", "pip3 install --upgrade pudb"
        )
        self.shell.exec_list(
            "Installing yq, an yaml parser",
            "wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O ~/.local/bin/yq",
            "chmod +x ~/.local/bin/yq",
        )
        self.shell.exec_list(
            "Installing yt-dlp",
            "pip3 install --user --force-reinstall https://github.com/yt-dlp/yt-dlp/archive/master.tar.gz",
            f"ln -sf {self.HOME}/.local/bin/yt-dlp {self.HOME}/.local/bin/youtube-dl",
        )

        self.shell.exec(
            "Installing tools for python",
            "pip3 install --upgrade black isort poetry",
        )

        self.shell.exec(
            "Installing caterpillar, an hls downloader",
            "pip3 install --upgrade caterpillar-hls",
        )
        if self.args.latex:
            self.shell.sudo_exec("Refreshing fonts", "fc-cache -f -v")

        self._mkdir(self.zsh_completion_path)
        self._mkdir(self.bash_completion_path)
        self._mkdir(self.man_path)

        self._install_fd()

        self._install_tty_clock()

        self.shell.exec(
            "Installing ripgrep-all",
            self.github_dl_cmd(
                "phiresky/ripgrep-all", "x86_64-unknown-linux-musl.tar.gz", 1
            ),
        )

        self.shell.exec(
            "Installing viddy",
            self.github_dl_cmd("sachaos/viddy", "linux-x86_64.tar.gz"),
        )

        self.shell.exec(
            "Installing gotop", self.github_dl_cmd("xxxserxxx/gotop", "linux_amd64.tgz")
        )

        self.shell.exec_list(
            "Installing btop++",
            self.github_dl_cmd(
                "aristocratos/btop",
                "x86_64-linux-musl.tbz",
                binpath="/tmp",
                tar_extract_flags="xj",
            ),
            "cd /tmp/btop && make install PREFIX=$HOME/.local",
            "rm -rf /tmp/btop",
        )

        self._install_bat()

        self.shell.exec_list(
            "Installing glow",
            self.github_dl_cmd("charmbracelet/glow", "linux_x86_64.tar.gz", strip=1),
            f"mv {self.HOME}/.local/bin/completions/glow.zsh {self.zsh_completion_path}/_glow",
            f"mv {self.HOME}/.local/bin/completions/glow.bash {self.bash_completion_path}/glow",
            f"mv {self.HOME}/.local/bin/manpages/glow.1.gz {self.man_path}/glow.1.gz",
            f"rm -rf {self.HOME}/.local/bin/completions",
            f"rm -rf {self.HOME}/.local/bin/manpages",
        )

        self.shell.exec(
            "Installing the latest stable neovim from Github repo",
            self.github_dl_cmd(
                "neovim/neovim",
                suffix="linux-x86_64.tar.gz",
                strip=1,
                binpath=f"{self.HOME}/.local",
            ),
        )

        KotlinLspInstaller(self.args).run()

        if self.args.java:
            JavaInstaller(self.args).run()

        self.shell.exec(
            "Removing auxiliary files",
            f"rm -rf {self.HOME}/.local/bin/autocomplete {self.HOME}/.local/bin/completion {self.HOME}/.local/bin/LICENSE* {self.HOME}/.local/bin/*.md {self.HOME}/.local/bin/doc",
        )

        if self.args.elixir:
            ElixirInstaller(self.args).run()

        NodeInstaller(self.args).run()

        self.shell.exec_list(
            "Installing 7zip",
            self.dl_cmd(
                "https://7-zip.org/a/7z2408-linux-x64.tar.xz",
                tar_extract_flags="xJ",
            ),
            f"rm -rf {self.HOME}/.local/bin/MANUAL {self.HOME}/.local/bin/readme.txt  {self.HOME}/.local/bin/History.txt {self.HOME}/.local/bin/License.txt {self.HOME}/.local/bin/7zzs",
            f"mv -f {self.HOME}/.local/bin/7zz {self.HOME}/.local/bin/7z",
        )

        return

    def _install_tty_clock(self):
        self.shell.exec_list(
            "Installing tty_clock",
            f"git clone https://github.com/xorg62/tty-clock.git /tmp/tty_clock",
            f"cd /tmp/tty_clock && make install PREFIX={self.HOME}/.local MANPATH={self.HOME}/.local/share/man/man1",
            f"cd",
            f"rm -rf /tmp/tty_clock",
        )
        return

    def _install_fd(self):
        self.shell.exec_list(
            "Installing fd",
            self.github_dl_cmd("sharkdp/fd", "x86_64-unknown-linux-musl.tar.gz", 1),
            f"mv {self.HOME}/.local/bin/autocomplete/_fd {self.zsh_completion_path}/_fd",
            f"mv {self.HOME}/.local/bin/autocomplete/fd.bash {self.bash_completion_path}/fd",
            f"mv {self.HOME}/.local/bin/fd.1 {self.man_path}/fd.1",
        )

    def _install_bat(self):
        self.shell.exec_list(
            "Installing bat",
            self.github_dl_cmd("sharkdp/bat", "x86_64-unknown-linux-musl.tar.gz", 1),
            f"mv {self.HOME}/.local/bin/autocomplete/bat.zsh {self.zsh_completion_path}/_bat",
            f"mv {self.HOME}/.local/bin/autocomplete/bat.bash {self.bash_completion_path}/bat",
            f"mv {self.HOME}/.local/bin/bat.1 {self.man_path}/bat.1",
        )


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--latex", action="store_true")
    argparser.add_argument("--java", action="store_true")
    argparser.add_argument("--elixir", action="store_true")
    argparser.add_argument(
        "--typescript",
        "-t",
        action="store_true",
        help="install typescript",
        default=False,
    )

    LinuxAMD64(argparser.parse_args()).run()

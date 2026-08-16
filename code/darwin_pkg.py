import json
import os
from argparse import Namespace
from functools import cached_property
from pathlib import Path

from java_installer import JavaInstaller
from kotlin_lsp_installer import KotlinLspInstaller
from node_installer import NodeInstaller
from package_manager import PackageManager
from script import Script
from util import (
    GithubDownloadable,
    is_m1,
)

os.environ["PATH"] = f'/usr/local/bin:/opt/homebrew/bin:{os.environ["PATH"]}'
os.environ["NONINTERACTIVE"] = "1"

# Packages from third-party taps, as (brew trust option, fully qualified name).
# Homebrew refuses to load them until the tap or the package itself is trusted,
# so DarwinPreparation taps and trusts these before any installation happens.
TAP_PACKAGES = (
    ("formula", "kiki-ki/tap/qo"),
    ("cask", "postmelee/tap/alhangeul"),
)


def tap_of(full_name: str) -> str:
    "Extracts the `user/repo` part of a fully qualified package name"
    return "/".join(full_name.split("/", 2)[:2])


def tap_packages(kind: str) -> list[str]:
    "Lists fully qualified names of the tap packages of the given kind"
    return [name for tap_kind, name in TAP_PACKAGES if tap_kind == kind]


class DarwinPreparation(Script):
    def __init__(self, args: Namespace):
        super().__init__(args)

    def run(self):
        "Installs homebrew if not exists, then prepares third-party taps"

        if not self._exists("brew"):
            self.shell.exec_list(
                "Installing homebrew",
                "sudo echo hello",  # To acquire sudo permission
                '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" < /dev/null',
            )
        self._add_taps()
        self._trust_taps()
        return

    def _add_taps(self):
        for tap in sorted({tap_of(name) for _, name in TAP_PACKAGES}):
            if tap in self._tapped:
                print(f"Skipping tap {tap} - already tapped")
                continue
            self.shell.exec(f"Tapping {tap}", f"brew tap {tap}")
        return

    def _trust_taps(self):
        """
        Homebrew ignores packages from untrusted taps, which makes both the
        installation and the `brew list` based idempotency check fail.
        """
        for kind, name in TAP_PACKAGES:
            if name in self._trusted or tap_of(name) in self._trusted:
                print(f"Skipping trust {name} - already trusted")
                continue
            self.shell.exec(f"Trusting {name}", f"brew trust --{kind} {name}")
        return

    @cached_property
    def _tapped(self) -> set[str]:
        ok, out, _ = self.shell.run("brew tap")
        if not ok:
            print("Failed to list homebrew taps")
            return set()
        return set(out.split())

    @cached_property
    def _trusted(self) -> set[str]:
        # Trusting a whole tap covers every package in it, so the tap names
        # matter as much as the individual entries.
        ok, out, _ = self.shell.run("brew trust --json v1")
        if not ok:
            print("Failed to list trusted homebrew packages")
            return set()
        return {name for names in json.loads(out).values() for name in names}


class DarwinPackageManager(PackageManager):
    @property
    def cmd(self) -> str:
        return "brew install "

    @cached_property
    def pkgs(self):
        pkgs = [
            "bash",
            "bat",
            "bear",
            "bfs",
            "btop",
            "cmake",
            "convmv",
            "coreutils",
            "dict",
            "fd",
            "ffmpeg",
            "figlet",
            "font-d2coding",
            "font-d2coding-nerd-font",
            "font-delugia-complete",
            "git",
            "git-extras",
            "glow",
            "gotop",
            "grep",
            "gzip",
            "gawk",
            "gnu-getopt",
            "gnu-sed",
            "gnu-tar",
            "htop",
            "jq",
            "k9s",
            "lbzip2",
            "llvm",
            "macchina",
            "make",
            "mmv",
            "multitail",
            "neofetch",
            "num-utils",
            "parallel",
            "pigz",
            "pixz",
            "poppler",
            "p7zip",
            "qpdf",
            "rename",
            "ripgrep",
            "ripgrep-all",
            "rsync",
            "rust",
            "shfmt",
            "shellcheck",
            "sponge",
            "starship",
            "task-spooler",
            "the_silver_searcher",
            "tmux",
            "translate-shell",
            "tree",
            "tty-clock",
            "tldr",
            "unzip",
            "viddy",
            "vim",
            "w3m",
            "watch",
            "wget",
            "yq",
            "yt-dlp",
            "zip",
        ]

        if self.args.latex:
            pkgs.append("texlive")
        if self.args.boost:
            pkgs.append("boost")
        if self.shell.env.get("DISPLAY", False):
            print("X11 is not supported")
        if self.args.golang:
            pkgs.append("go")
        if self.args.elixir:
            pkgs += ["erlang", "elixir"]
        return pkgs + tap_packages("formula")

    def do_misc(self):
        """
        TODO: Installs gdb
        """
        paths = set()
        for pkg in frozenset(self.pkgs) & {
            "gnu-sed",
            "gnu-getopt",
            "grep",
            "gnu-tar",
            "coreutils",
        }:
            ok, path, _ = self.shell.run(f"brew --prefix {pkg}")
            if not ok:
                print(f"Problem occurred while brew --prefix {pkg}")
                continue
            paths.add(f"{path}/bin")

        path = ":".join(paths)
        HOME = Path.home()
        self.shell.exec("Updating PATH", f"printf '%s' '{path}' > {HOME}/.paths")

        self.shell.exec(
            "Aliasing python to python3",
            "ln -sf $(which python3) $(which python3 | sed 's/python3/python/')",
        )


class Mac(Script, GithubDownloadable):
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

        self.shell.exec_list(
            "Installing 7zip",
            self.github_dl_cmd(
                "ip7z/7zip",
                "mac.tar.xz",
                tar_extract_flags="xJ",
            ),
            f"rm -rf {self.HOME}/.local/bin/MANUAL {self.HOME}/.local/bin/readme.txt  {self.HOME}/.local/bin/History.txt {self.HOME}/.local/bin/License.txt {self.HOME}/.local/bin/7zzs",
            f"mv -f {self.HOME}/.local/bin/7zz {self.HOME}/.local/bin/7z",
        )

        self.shell.exec(
            "Installing fzf",
            self.github_dl_cmd(
                "junegunn/fzf",
                "darwin_arm64.tar.gz" if is_m1() else "darwin_amd64.tar.gz",
            ),
        )

        KotlinLspInstaller(self.args).run()

        self.shell.exec(
            "Installing pudb, a python debugger", "pip3 install --user pudb"
        )

        self.shell.exec(
            "Installing caterpillar, an hls downloader",
            "pip3 install --user caterpillar-hls",
        )

        self.shell.exec(
            "Installing visidata",
            "pip3 install --user visidata",
        )

        if self.args.java:
            JavaInstaller(self.args).run()

        self.shell.exec(
            "Installing bazel-lsp",
            self.github_dl_single_cmd(
                "cameron-martin/bazel-lsp",
                "osx-arm64" if is_m1() else "osx-amd64",
                f"{self.HOME}/.local/bin/bazel-lsp",
            ),
        )

        self._install_casks()
        NodeInstaller(self.args).run()

        self._mkdir(self.zsh_completion_path)
        self._mkdir(self.bash_completion_path)
        self._mkdir(self.man_path)

        self.shell.exec(
            "Removing auxiliary files",
            f"rm -rf {self.HOME}/.local/bin/autocomplete {self.HOME}/.local/bin/completion {self.HOME}/.local/bin/LICENSE* {self.HOME}/.local/bin/*.md {self.HOME}/.local/bin/doc",
        )

        self._setup_configs()
        return

    def _setup_configs(self):
        self.shell.exec(
            "Importing itsycal configuration",
            f"defaults import com.mowglii.ItsycalApp {self.HOME}/.config/itsycal/config.plist",
        )

    def _install_casks(self):
        casks = [
            "adguard",
            "android-platform-tools",
            "appcleaner",
            "balenaetcher",  # iso to usb
            "calibre",
            "cursor",
            "cyberduck",  # sftp/nextcloud client
            "easyfind",  # everything alternative
            "firefox",
            "font-d2coding",
            "font-d2coding-nerd-font",
            "font-delugia-complete",
            "gureumkim",
            "iina",
            "ghostty",
            "itsycal",
            "jetbrains-toolbox",
            "karabiner-elements",
            "keepingyouawake",
            "keka",
            "krita",  # mspaint alternative
            "microsoft-edge",
            "--no-quarantine middleclick",
            "musicbrainz-picard",  # music metadata editor
            "notion",
            "orbstack",  # docker desktop alternative
            "qview",
            "raycast",
            "rectangle",
            "visual-studio-code",
            "xquartz",
        ]

        if self.args.misc:
            casks += ["libreoffice", "wine-stable"]
        casks += tap_packages("cask")

        for cask in casks:
            # 특수 옵션이 있는 cask 처리
            cask_name = cask.split()[-1] if "--no-quarantine" in cask else cask

            if cask_name in self._installed_casks:
                print(f"Skipping {cask_name} - already installed")
                continue

            self.shell.exec(
                f"Installing {cask}",
                f"brew install --cask {cask}",
            )
        return

    @cached_property
    def _installed_casks(self) -> set[str]:
        # 이미 설치된 cask 목록 가져오기
        # Casks from taps are listed as `user/repo/cask`, matching TAP_PACKAGES
        ok, installed_casks_output, _ = self.shell.run(
            "brew list --cask -1 --full-name"
        )
        if not ok:
            print("Failed to list homebrew casks")
            return set()
        return (
            set(installed_casks_output.strip().split("\n"))
            if installed_casks_output.strip()
            else set()
        )

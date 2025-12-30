from argparse import Namespace

from package_manager import PackageManager
from script import Script


class RedhatPreparation(Script):
    def __init__(self, args: Namespace):
        super().__init__(args)


class RedhatPackageManager(PackageManager):
    @property
    def cmd(self) -> str:
        return f"{self.shell.sudo} yum install -y "

    @property
    def pkgs(self):
        pkgs = """
		tar vim git gcc curl wget tmux make gzip zip unzip
		clang clang-tools-extra ctags cmake jq
		python3 python3*-devel python3-pip
		tree htop
		gzip gem prename
		""".split()

        if self.args.latex:
            pkgs.append("texlive-*")
        if self.args.boost:
            pkgs.append("boost-*")
        if self.args.java:
            pkgs += ["java-11-openjdk", "java-11-openjdk-devel"]
        if self.args.elixir:
            print("Warning: Elixir is not supported on RedHat (EPEL version outdated, Erlang Solutions unstable)")

        return pkgs

    def do_misc(self):
        self.shell.sudo_exec(
            "Installing development tools", "yum groupinstall -y 'Development Tools'"
        )

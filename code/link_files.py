#!/usr/bin/env python3
import json
import os
import re
from argparse import ArgumentParser

from script import Script


class FileLinker(Script):
    def run(self) -> None:
        HOME = self.HOME
        proj_root = self.proj_root

        self._mkdir(f"{HOME}/.local/bin/")
        self.shell.exec(
            "Symbolic linking scripts",
            f'ln -fs "{proj_root}"/scripts/* {HOME}/.local/bin/',
        )

        self.shell.exec_list(
            "Enabling tar to parallelize archiving files",
            f"ln -sf /usr/bin/lbzip2 {HOME}/.local/bin/bzip2",
            f"ln -sf /usr/bin/lbzip2 {HOME}/.local/bin/bunzip2",
            f"ln -sf /usr/bin/lbzip2 {HOME}/.local/bin/bzcat",
            f"ln -sf /usr/bin/pigz {HOME}/.local/bin/gzip",
            f"ln -sf /usr/bin/pigz {HOME}/.local/bin/gunzip",
            f"ln -sf /usr/bin/pigz {HOME}/.local/bin/gzcat",
            f"ln -sf /usr/bin/pigz {HOME}/.local/bin/zcat",
            f"ln -sf /usr/bin/pixz {HOME}/.local/bin/xz",
        )

        trueline_path = f"{HOME}/.trueline.sh"
        if not os.path.exists(trueline_path):
            self.shell.exec(
                "Downloading trueline.sh",
                f"curl -s https://raw.githubusercontent.com/petobens/trueline/master/trueline.sh -o {trueline_path}",
            )

        self.shell.exec_list(
            "Symbolic linking essential files",
            f'ln -fs "{proj_root}"/.bashrc {HOME}/.bashrc',  # Deprecated: bashrc
            f'ln -fs "{proj_root}"/.gitconfig  {HOME}/.gitconfig',  # Global git configuration
            f'ln -fs "{proj_root}"/.common.shrc {HOME}/.common.shrc',
            f'ln -fs "{proj_root}"/.sensitive.shrc {HOME}/.sensitive.shrc',
            f'ln -fs "{proj_root}"/.shinit {HOME}/.shinit',
            f'ln -fs "{proj_root}"/.zshrc {HOME}/.zshrc',
            f'ln -fs "{proj_root}"/.p10k.zsh {HOME}/.p10k.zsh',
            f'ln -fs "{proj_root}"/.mailcap {HOME}/.mailcap',  # Open text files with vim when using xdg-open
            f'ln -fs "{proj_root}"/.mailcap.order {HOME}/.mailcap.order',  # Set higher priority to vim
            f'ln -fs "{proj_root}"/.ideavimrc {HOME}/.ideavimrc',  # Set higher priority to vim
            f'ln -fs "{proj_root}"/.xprofile {HOME}/.xprofile',  # Set higher priority to vim
            f"mkdir -p {HOME}/.vim",
            f'ln -fs "{proj_root}"/tasks.ini {HOME}/.vim/tasks.ini',
        )

        self._setup_claude_code()

        if not os.path.islink(f"{HOME}/.config"):
            self.shell.exec(
                f"Aliasing {HOME}/.config",
                f'ln -fs "{proj_root}"/config {HOME}/.config',
            )

        self.shell.exec(
            "pip links to pip3",
            f"ln -nfs $(which pip3) {HOME}/.local/bin/pip",
        )

        if not os.path.islink(f"{HOME}/.clipboard"):
            self.shell.exec(
                "Linking .clipboard",
                f"""
                if [ -L {HOME}/.clipboard ];then
                    unlink {HOME}/.clipboard;
                else
                    rm -rf {HOME}/.clipboard;
                fi && \
                ln -s {self.proj_root}/clipboard {HOME}/.clipboard
                """,
            )

        WIN_CONV_PATH = f"{HOME}/.win_env_conv.shrc"
        if self._is_wsl() and not os.path.exists(WIN_CONV_PATH):
            self.shell.exec_list(
                "Fetch Windows environment variables",
                f'ln -fs "{proj_root}"/win_env_conv.shrc {WIN_CONV_PATH}',
            )

        if self._is_wsl() and os.path.exists("/mnt/c/Users"):
            link_cmds = [
                f"ln -nfs $USERPROFILE/Downloads $HOME/",
                f"ln -nfs $USERPROFILE/Videos $HOME/",
            ]
            if os.path.exists("/mnt/c/Users/mjo97"):
                link_cmds += [
                    f"ln -nfs $USERPROFILE/Dropbox/Documents $HOME/",
                ]
            else:
                link_cmds += [
                    f"ln -nfs $USERPROFILE/Documents $HOME/",
                ]

            if not os.path.islink(f"{HOME}/winHome"):
                link_cmds.append(f"ln -fs -T $USERPROFILE {HOME}/winHome")

            link_cmds = [f"source {WIN_CONV_PATH}; " + it for it in link_cmds]
            self.shell.exec_list("Symbolic linking windows folders", *link_cmds)

        self.shell.exec_list(
            "Aliasing configuration for Cursor IDE",
            f"mkdir -p $HOME/.cursor/extensions",
            rf"mkdir -p $HOME/Library/Application\ Support/Cursor/User",
            f"ln -sf {self.proj_root}/config/Cursor/extensions.json $HOME/.cursor/extensions/extensions.json",
            f"ln -sf {self.proj_root}/config/Cursor/mcp.json $HOME/.cursor/mcp.json",
            rf"ln -sf {self.proj_root}/config/Cursor/User/keybindings.json $HOME/Library/Application\ Support/Cursor/User/keybindings.json",
            rf"ln -sf {self.proj_root}/config/Cursor/User/settings.json $HOME/Library/Application\ Support/Cursor/User/settings.json",
        )

        if os.path.exists(f"{HOME}/Library/Application Support/Claude"):
            self.shell.exec(
                "Linking MCP configuration for Claude Desktop",
                rf"ln -sf {self.proj_root}/config/Cursor/mcp.json $HOME/Library/Application\ Support/Claude/claude_desktop_config.json",
            )

        return

    def _setup_claude_code(self):
        HOME = self.HOME
        proj_root = self.proj_root

        if not self.shell.run("which -a claude")[0]:
            return

        self.shell.exec_list(
            "Linking claude code configs",
            f"mkdir -p {HOME}/.claude",
            f'ln -fs "{proj_root}"/config/AGENTS.md {HOME}/.claude/CLAUDE.md',
            f'ln -fs "{proj_root}"/config/claude-code/settings.json {HOME}/.claude/settings.json',
        )
        with open(f"{proj_root}/config/claude-code/mcp.json") as f:
            mcp_list = json.load(f)
        remove_commands = [
            f"claude mcp remove --scope user -- {name} || echo '{name} is already removed'"
            for name in mcp_list.keys()
        ]
        add_commands = [
            f"claude mcp add-json --scope user -- {name} '{json.dumps(json_str)}' "
            for name, json_str in mcp_list.items()
        ]
        self.shell.exec_list(
            "Installing mcp servers for claude code",
            *remove_commands,
            *add_commands,
        )
        return

    def _is_wsl(self):
        try:
            with open("/proc/version") as f:
                text = f.read()
            return bool(re.search(r"microsoft|wsl", text, re.IGNORECASE))
        except:
            return False


if __name__ == "__main__":
    parser = ArgumentParser()
    args = parser.parse_args()

    FileLinker(args).run()

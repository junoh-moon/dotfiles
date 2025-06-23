#!/usr/bin/env python3
import json
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

    def _get_latest_version(self):
        """Fetch the latest version from GitHub releases"""
        cmd = """curl -s https://api.github.com/repos/Kotlin/kotlin-lsp/releases/latest | 
            python3 -c "import sys, json; print(json.load(sys.stdin)['tag_name'])"
            """
        ok, out, err = self.shell.run(cmd)
        if not ok:
            print(f"Failed to fetch latest kotlin-lsp version: {err}", file=stderr)
            # Fallback to a known working version
            return "0.252.17811"
        
        # Extract version from tag (e.g., kotlin-lsp/v0.252.17811 -> 0.252.17811)
        version = out.strip()
        if '/' in version:
            version = version.split('/')[-1]
        if version.startswith('v'):
            version = version[1:]
        
        return version

    def run(self):
        version = self._get_latest_version()
        kotlin_lsp_link = f"https://download-cdn.jetbrains.com/kotlin-lsp/{version}/kotlin-{version}.zip"
        self.shell.exec_list(
            f"Installing kotlin lsp (v{version})",
            f"curl -Lfo /tmp/kotlin-lsp.zip '{kotlin_lsp_link}'",
            f"unzip -o /tmp/kotlin-lsp.zip -d {self.HOME}/.local/bin/",
            f"chmod +x {self.HOME}/.local/bin/kotlin-lsp.sh",
            "rm -f /tmp/kotlin-lsp.zip",
        )

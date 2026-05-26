from sys import stderr

from shell import Shell


def is_m1():
    "Check whether the machine is Apple Silicon Mac"
    return Shell().run("uname -m")[1] == "arm64"


class GithubDownloadable:
    def dl_cmd(
        self,
        link: str,
        strip: int = 0,
        binpath: str = "$HOME/.local/bin",
        tar_extract_flags: str = "xz",
    ):
        cmd = f"""curl -L {link} |
		tar {tar_extract_flags} -C {binpath}"""
        if strip:
            cmd += f" --strip {strip}"

        return cmd

    def github_dl_cmd(
        self,
        user_repo: str,
        suffix: str,
        strip: int = 0,
        binpath: str = "$HOME/.local/bin",
        tar_extract_flags: str = "xz",
    ):
        link = self.get_download_link(user_repo, suffix)
        if not link:
            return "false"  # Returns `false` command to fail fast
        return self.dl_cmd(link, strip, binpath, tar_extract_flags)

    def github_dl_single_cmd(self, user_repo: str, suffix: str, fullpath: str):
        link = self.get_download_link(user_repo, suffix)
        if not link:
            return "false"
        return f"curl -L {link} -o {fullpath} && chmod +x {fullpath}"

    def get_download_link(self, user_repo: str, suffix: str):
        cmd = f"""curl -s https://api.github.com/repos/{user_repo}/releases/latest |
            grep browser_download_url | 
            grep -ioe 'https://.*{suffix}'  |
            
            head -n 1 
            """
        shell = Shell()
        ok, out, err = shell.run(cmd)
        if not ok:
            print(f"Failed to get download link: {err}", file=stderr)
            return None

        return out

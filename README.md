# dotfiles

## Installation

```bash
git clone 'https://junoh-moon@github.com/junoh-moon/dotfiles' ~/.dotfiles && \
cd ~/.dotfiles && ./install.sh -d [debian | redhat | darwin] [--java|--latex|--boost|--misc|--typescript]
```

Note that you may need to enter the password to decrypt the ssh key.

## Encryption and Decryption

Files with personal information are encrypted with [transcrypt](https://github.com/elasticdog/transcrypt).
The `install.sh` script will set up transcrypt, decrypt all files, and verify the
result using `.transcrypt-check` before continuing with the full installation.

The following examples will be helpful:
- `transcrypt --list` to list encrypted files
- `transcrypt --display > /dev/null` to check whether this repository is configured
- `transcrypt --add path/to/file && git add path/to/file .gitattributes` to add a file to encrypt

Do not run `transcrypt --display` without redirecting its output because it prints
the configured password. To verify decryption manually, run:

```sh
grep -Fxq 'transcrypt decryption verified' .transcrypt-check && echo 'transcrypt OK'
```

### Recovering from an Incorrect Password

An incorrect password may remain in the repository-local Git configuration even
after transcrypt reports that decryption failed. Remove the cached credentials and
return encrypted files to their original encrypted form before trying again:

```sh
git status --short
transcrypt --flush-credentials
./install.sh -d [debian | redhat | darwin]
```

Transcrypt normally requires a clean working tree. If the failed decryption itself
made encrypted files appear modified, first make sure there are no intentional
changes to those files. Only then bypass the clean-tree check:

```sh
transcrypt --flush-credentials --force
./install.sh -d [debian | redhat | darwin]
```

The `--force` option discards uncommitted changes to encrypted files. Do not use it
until those changes have been reviewed or backed up.

**CentOS7 Support:**

If you're looking for installing packages on CentOS7 without root privileges, please check out [here](https://gist.github.com/junoh-moon/f9c612a60aa25dc4940993529532eb97).
It will replace `install_packages.py`.

## MacOS Support

- XCode installation: [XcodesApp](https://github.com/XcodesOrg/XcodesApp)

## Switching from Https into Ssh

```sh
sed -Ei 's|https://(junoh-moon@)?github.com/junoh-moon/dotfiles|git@github.com:junoh-moon/dotfiles|' .git/config
```

## Windows Terminal settings.json and Delugia Font

[settings.json](https://nas.sixtyfive.me/s/botmPZwHwFCtENb)
[Delugia](https://github.com/adam7/delugia-code/releases)

## TODO

- [ ] Debugger integration
- [ ] Cloudflare

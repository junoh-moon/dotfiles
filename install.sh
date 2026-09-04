#!/usr/bin/env bash


export PATH=$HOME/.local/bin:$PATH

proj_root="$(git rev-parse --show-toplevel)"

# transcrypt script를 ~/.local/bin에 설치. manpage 포함
"$proj_root/install_transcrypt.sh"

# if transcrypt is not installed
if ! transcrypt --display > /dev/null; then
	printf "Enter password: "
	read -r PASSWORD
	# transcrypt가 레포지토리 안에 설정된다.
	# 레포지토리 안에 이미 암호화된 파일이 있는 경우, 복호화도 진행한다.
	transcrypt --cipher aes-256-cbc --password "$PASSWORD"
fi

transcrypt_check_file="$proj_root/.transcrypt-check"
transcrypt_check_value='transcrypt decryption verified'

if [[ ! -f "$transcrypt_check_file" ]] ||
	[[ "$(<"$transcrypt_check_file")" != "$transcrypt_check_value" ]]; then
	printf 'transcrypt decryption verification failed; see README.md for recovery instructions.\n' >&2
	exit 1
fi

"$proj_root"/code/full_install.py "$@"

cat <<EOF
Try the below to substitute a github protocol:

sed -Ei 's|https://(junoh-moon@)?github.com/junoh-moon/dotfiles|git@github.com:junoh-moon/dotfiles|' ${proj_root}/.git/config
EOF

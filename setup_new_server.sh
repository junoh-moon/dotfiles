#!/bin/sh

set -e

# Install docker
sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
sudo systemctl status docker
sudo usermod -aG docker $USER
newgrp docker
docker run hello-world

# esm 및 기타 이상한 motd 메시지 정리하기:
sudo apt remove needrestart ubuntu-advantage-tools
sudo chmod -x /etc/update-motd.d/50-motd-news
sudo chmod -x /etc/update-motd.d/10-help-text
sudo chmod -x /etc/update-motd.d/91-contract-ua-esm-status
sudo chmod -x /etc/update-motd.d/98-reboot-required

sudo sed -Ezi.orig \
	-e 's/(def _output_esm_service_status.outstream, have_esm_service, service_type.:\n)/\1    return\n/' \
	-e 's/(def _output_esm_package_alert.*?\n.*?\n.:\n)/\1    return\n/' \
	/usr/lib/update-notifier/apt_check.py

sudo /usr/lib/update-notifier/update-motd-updates-available --force
sudo run-parts /etc/update-motd.d

# Graphics card accelerateion (/dev/dri)
sudo apt install --install-recommends linux-generic-hwe-22.04

# Other
: <<'COMMENT'
| Item            | Description                                         |
|-----------------|-----------------------------------------------------|
| molly-guard     | Prevent accidental shutdown/reboot                  |
| network-manager | Wlan support                                        |
| xorg            | Full ububtu-server image already includes X11 server|
COMMENT
sudo apt-get install -y \
	molly-guard \
	network-manager
# xorg

cargo install macchina
git clone https://github.com/junoh-moon/cloudflare-cli && cd cloudflare-cli && make install

# 부팅시 네트워크 잡느라 너무 느려지는 상황 방지
systemctl mask systemd-networkd-wait-online.service

timedatectl set-timezone 'Asia/Seoul'

# Fail2ban and sshd
sudo apt-get install -y fail2ban
cd /etc/fail2ban/filter.d && sudo ln -sf sshd.conf sshd-61022.conf
cat <<'EOF' | sudo tee /etc/fail2ban/jail.d/defaults-debian.conf
[DEFAULT]
bantime = 1h
bantime.increment = true

[sshd]
enabled = true
findtime = 1440m
bantime = 525600m
port = ssh
mode = aggressive

[sshd-61022]
enabled = true
findtime = 1440m
bantime = 525600m
port = 61022
EOF

sudo sed 's/(#\*)Port \d+/Port 61022\nPort 22/'

if ! grep 'Port 61022' /etc/ssh/sshd_config &>/dev/null; then
	sudo sed -i -r 's/(# *)?Port [0-9]+/Port 61022\nPort 22/' /etc/ssh/sshd_config
fi

# If LC_ALL is not set, linux `sort` command works not correctly.
sudo update-locale LC_ALL=C.UTF-8

# Manual things
cat <<'EOF'
- Restore crontab and backups created by crontab.
- Go to Code/typescript/add_music and link binary: (try cat makefile)
- Crontab
EOF

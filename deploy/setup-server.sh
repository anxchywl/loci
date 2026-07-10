#!/usr/bin/env bash
set -euo pipefail

# one-time server provisioning for loci — run as root on a fresh debian/ubuntu host

APP_DIR=/opt/loci

apt-get update
apt-get install -y ca-certificates curl git ufw

if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi

ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

mkdir -p "$APP_DIR" "$APP_DIR/backups"

if [ ! -d "$APP_DIR/repo/.git" ]; then
  echo "clone the repo into $APP_DIR/repo, copy .env.example to .env, fill it, then run deploy/deploy.sh"
fi

echo "server setup complete"

#!/usr/bin/env bash
# ============================================================================
#  One-command deploy (Ubuntu/Debian VPS)
#  Usage:  sudo bash deploy.sh
#  Eta: Docker install korbe (na thakle) -> .env check korbe -> build + up.
# ============================================================================
set -euo pipefail

cd "$(dirname "$0")"

echo "==> Docker ase kina check..."
if ! command -v docker >/dev/null 2>&1; then
    echo "==> Docker install hocche..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker
fi

# docker compose plugin ase kina
if ! docker compose version >/dev/null 2>&1; then
    echo "==> docker compose plugin install hocche..."
    apt-get update -y
    apt-get install -y docker-compose-plugin
fi

if [ ! -f .env ]; then
    echo ""
    echo "!! .env file nei. Banao:  cp .env.example .env  tarpor edit koro."
    echo "   DOMAIN, EMAIL, DL_KEY oboshyoi boshabe."
    echo ""
    echo "   Ekta strong DL_KEY: $(openssl rand -hex 24 2>/dev/null || echo 'openssl-nei-nije-banaye-nao')"
    exit 1
fi

echo "==> Firewall e 80/443 khola hocche (ufw thakle)..."
if command -v ufw >/dev/null 2>&1; then
    ufw allow 80/tcp  || true
    ufw allow 443/tcp || true
fi

echo "==> Build + start..."
docker compose pull caddy || true
docker compose up -d --build

echo ""
echo "==> Status:"
docker compose ps
echo ""
DOMAIN_VAL="$(grep -E '^DOMAIN=' .env | cut -d= -f2- || true)"
echo "✅ Hoye gelo! Kichukkhon por SSL toiri hobe."
echo "   Test koro:  https://${DOMAIN_VAL}/health"
echo "   Log dekhte: docker compose logs -f"

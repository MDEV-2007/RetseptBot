#!/usr/bin/env bash
# MediScript — AWS EC2 (Ubuntu 22.04) one-time server setup
# Usage: bash deploy/setup.sh
# Run as: ubuntu user (default AWS EC2 user)
set -euo pipefail

APP_DIR="/home/ubuntu/mediscript"
DOMAIN=""  # filled in interactively below

# ── 0. Prompt for domain ─────────────────────────────────────────────────────
read -rp "Enter your domain (e.g. mediscript.uz): " DOMAIN
echo "Using domain: $DOMAIN"

# ── 1. System packages ────────────────────────────────────────────────────────
echo "==> Updating system packages..."
sudo apt-get update -y
sudo apt-get install -y \
    python3.11 python3.11-venv python3-pip \
    nginx certbot python3-certbot-nginx \
    git curl

# ── 2. App directory ─────────────────────────────────────────────────────────
echo "==> Cloning / pulling repo..."
if [ -d "$APP_DIR/.git" ]; then
    git -C "$APP_DIR" pull --ff-only
else
    # Replace with your actual repo URL
    git clone https://github.com/YOUR_USERNAME/mediscript.git "$APP_DIR"
fi

# ── 3. Python virtualenv + dependencies ──────────────────────────────────────
echo "==> Setting up virtualenv..."
python3.11 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

# ── 4. .env file ─────────────────────────────────────────────────────────────
if [ ! -f "$APP_DIR/.env" ]; then
    echo "==> Creating .env from .env.example ..."
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    echo ""
    echo "  !! Edit $APP_DIR/.env and fill in SECRET_KEY, TELEGRAM_BOT_TOKEN, etc."
    echo "  !! Then re-run: bash $APP_DIR/deploy/setup.sh"
    exit 0
fi

# ── 5. Django setup ───────────────────────────────────────────────────────────
echo "==> Running migrations + collectstatic..."
cd "$APP_DIR"
"$APP_DIR/venv/bin/python" manage.py migrate --no-input
"$APP_DIR/venv/bin/python" manage.py collectstatic --no-input

# ── 6. Systemd service ────────────────────────────────────────────────────────
echo "==> Installing systemd service..."
sudo cp "$APP_DIR/deploy/mediscript.service" /etc/systemd/system/mediscript.service
sudo systemctl daemon-reload
sudo systemctl enable mediscript
sudo systemctl restart mediscript

# ── 7. Nginx config ───────────────────────────────────────────────────────────
echo "==> Configuring Nginx..."
sudo cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/mediscript
# Replace placeholder domain in the Nginx config
sudo sed -i "s/yourdomain.com/$DOMAIN/g" /etc/nginx/sites-available/mediscript
sudo ln -sf /etc/nginx/sites-available/mediscript /etc/nginx/sites-enabled/mediscript
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

# ── 8. HTTPS (Let's Encrypt) ──────────────────────────────────────────────────
echo "==> Obtaining SSL certificate for $DOMAIN ..."
sudo certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" \
    --non-interactive --agree-tos --email "admin@$DOMAIN" \
    --redirect

sudo systemctl reload nginx

# ── 9. Done ───────────────────────────────────────────────────────────────────
echo ""
echo "✓ MediScript is live at https://$DOMAIN"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status mediscript   # check app status"
echo "  sudo journalctl -u mediscript -f   # live logs"
echo "  sudo systemctl reload nginx        # reload nginx"
echo "  certbot renew --dry-run            # test cert auto-renewal"

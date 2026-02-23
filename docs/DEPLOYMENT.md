# Deployment Guide

## Prerequisites

- **Python 3.10+** on the server
- **Git** (to clone from your GitHub repo)

---

## Option 1: Self-Host Behind Tailscale (Recommended)

This is the simplest setup — your app is only accessible on your Tailscale network.

### First-time Setup

```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/performance-tracker.git
cd performance-tracker

# Set up Python
cd backend
python3 -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows
pip install -r requirements.txt
cd ..

# Set up environment
cp .env.example .env
nano .env                         # Add your LEETIFY_API_KEY, STEAM_ID, APP_PIN, SECRET_KEY

# Test it
python run.py
# Visit http://localhost:1337
```

### Run as a Service (Linux)

Create `/etc/systemd/service/perftracker.service`:

```ini
[Unit]
Description=Performance Tracker
After=network.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/home/YOUR_USER/performance-tracker
ExecStart=/home/YOUR_USER/performance-tracker/backend/venv/bin/python run.py
Restart=always
RestartSec=5
Environment=FLASK_ENV=production

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable perftracker
sudo systemctl start perftracker
```

Check status: `sudo systemctl status perftracker`
View logs: `sudo journalctl -u perftracker -f`

### Access via Tailscale

Once Tailscale is installed on the server and your devices:

```
http://YOUR-SERVER-TAILSCALE-IP:1337
```

You can find the Tailscale IP with `tailscale ip -4` on the server.

No need for HTTPS, domain names, or reverse proxies — Tailscale encrypts traffic end-to-end.

---

## Option 2: Using gunicorn (Production WSGI)

For a more robust production setup, use gunicorn instead of Flask's dev server.

```bash
cd performance-tracker
source backend/venv/bin/activate
gunicorn --bind 0.0.0.0:1337 --workers 2 --chdir . "run:app"
```

Note: `gunicorn` is already in `requirements.txt`.

Update the systemd service `ExecStart` line:

```ini
ExecStart=/home/YOUR_USER/performance-tracker/backend/venv/bin/gunicorn --bind 0.0.0.0:1337 --workers 2 --chdir /home/YOUR_USER/performance-tracker "run:app"
```

---

## Option 3: Behind Nginx Reverse Proxy

If you want HTTPS or a domain name, put nginx in front.

### Nginx Config

```nginx
server {
    listen 80;
    server_name perf.yourdomain.com;

    # Redirect to HTTPS (use with certbot)
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name perf.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/perf.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/perf.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:1337;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Get a certificate:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d perf.yourdomain.com
```

---

## Option 4: Docker

### Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

# Backend deps
RUN pip install --no-cache-dir -r backend/requirements.txt

EXPOSE 1337

CMD ["gunicorn", "--bind", "0.0.0.0:1337", "--workers", "2", "run:app"]
```

### docker-compose.yml

```yaml
version: "3.8"
services:
  perftracker:
    build: .
    ports:
      - "1337:1337"
    volumes:
      - ./backend/data:/app/backend/data    # Persist database
      - ./.env:/app/.env                     # Mount secrets
    restart: unless-stopped
```

Run:
```bash
docker compose up -d
```

---

## GitHub Workflow

### Repo Setup

```bash
cd performance-tracker
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/performance-tracker.git
git push -u origin main
```

The `.gitignore` already excludes `.env`, `backend/data/`, and `venv/`.

### Deploying Updates

On your server after pushing changes:

```bash
cd performance-tracker
git pull

# If backend deps changed:
source backend/venv/bin/activate
pip install -r backend/requirements.txt

# Restart the service
sudo systemctl restart perftracker
```

### Optional: Auto-Deploy Script

Create `deploy.sh` in project root:

```bash
#!/bin/bash
set -e

echo "Pulling latest changes..."
git pull

echo "Updating backend dependencies..."
source backend/venv/bin/activate
pip install -r backend/requirements.txt

echo "Restarting service..."
sudo systemctl restart perftracker

echo "Done! App is live."
```

Make executable: `chmod +x deploy.sh`

Then deploying is just: `./deploy.sh`

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Flask session encryption. Use a random string (e.g., `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `APP_PIN` | Yes | The PIN to unlock the app. Default: `1337` |
| `STEAM_ID` | For CS2 | Your Steam64 ID. Find at https://steamid.io |
| `LEETIFY_API_KEY` | For CS2 | Your Leetify API key from https://api-public-docs.cs-prod.leetify.com |

### Generating a Strong Secret Key

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output into your `.env` as `SECRET_KEY`.

---

## Quick Reference

| Action | Command |
|--------|---------|
| Start (dev) | `python run.py` |
| Start (prod) | `gunicorn --bind 0.0.0.0:1337 --workers 2 "run:app"` |
| Backup DB | `cp backend/data/performance_tracker.db backup.db` |
| Reset DB | `rm backend/data/performance_tracker.db && python run.py` |
| View service logs | `sudo journalctl -u perftracker -f` |
| Deploy update | `git pull && ./deploy.sh` |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Make sure venv is activated: `source backend/venv/bin/activate` |
| CS2 sync fails | Verify `LEETIFY_API_KEY` and `STEAM_ID` in `.env`. Get your API key from Leetify |
| Port in use | Change port in `run.py` or kill the process: `lsof -i :1337` (Linux) or `netstat -ano | findstr 1337` (Windows) |
| DB locked error | Only one process should access the SQLite DB at a time. Don't run multiple instances |
| Session lost after restart | Set a persistent `SECRET_KEY` in `.env` (Flask uses it to sign cookies) |

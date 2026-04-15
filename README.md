# testboardapp

Flask service for Raspberry Pi GPIO, PMOD keypad, and ADS1115 analog inputs.

## Managed With uv

This project uses [uv](https://docs.astral.sh/uv/) for dependency and environment management.

### 1. Sync dependencies

```bash
uv sync
```

### 2. Run the service

```bash
uv run testboard.py
```

### 3. Optional runtime configuration

The service supports these environment variables:

- `TESTBOARD_HOST` (default: `0.0.0.0`)
- `TESTBOARD_PORT` (default: `5000`)
- `TESTBOARD_DEBUG` (default: `false`)
- `LOG_LEVEL` (default: `INFO`)

Example:

```bash
TESTBOARD_PORT=8080 LOG_LEVEL=DEBUG uv run testboard.py
```

### Health check

```bash
curl http://localhost:5000/healthz
```

## GitHub Push

Initialize and commit:

```bash
git init
git add .
git commit -m "Set up uv project and improve testboard service"
```

Then connect your remote and push:

```bash
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

## Run As a Systemd Service

Use systemd to start `testboard.py` automatically on boot and restart it if it crashes.

### 1. Create the service unit

```bash
sudo tee /etc/systemd/system/testboardapp.service > /dev/null << 'EOF'
[Unit]
Description=Testboard Flask Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/testboardapp
ExecStart=/home/pi/.local/bin/uv run /home/pi/testboardapp/testboard.py
Restart=always
RestartSec=5
Environment=TESTBOARD_HOST=0.0.0.0
Environment=TESTBOARD_PORT=5000
Environment=LOG_LEVEL=INFO

[Install]
WantedBy=multi-user.target
EOF
```

### 2. Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now testboardapp
```

### 3. Verify status and logs

```bash
sudo systemctl status testboardapp --no-pager
journalctl -u testboardapp -f
```

### 4. Service management

```bash
sudo systemctl restart testboardapp
sudo systemctl stop testboardapp
sudo systemctl disable testboardapp
```

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

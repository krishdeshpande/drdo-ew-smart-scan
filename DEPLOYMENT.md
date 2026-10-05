# SENTINEL-EW Deployment Guide

This guide details how to deploy the **SENTINEL-EW Tactical C2 Dashboard & Simulator** to production or access it publicly for demos, evaluation, and presentations.

The system uses a **unified single-port architecture**: HTTP static assets (`/`), tactical HUD (`/dashboard.html`), health checks (`/health`), and high-speed telemetry WebSockets (`/ws`) all operate on a single port (`$PORT` or default `8080`), compatible with standard reverse proxies and cloud PaaS providers.

---

## Deployment Options at a Glance

| Method | Cost | Setup Time | Best For |
| :--- | :---: | :---: | :--- |
| **Option 1: Hugging Face Spaces (Docker)** | **Free** | 2 minutes | AI/ML hackathon showcases, public portfolio links, zero maintenance |
| **Option 2: Render.com** | **Free** | 2 minutes | Permanent public URL directly linked to your GitHub repo |
| **Option 3: Railway.app** | **Free Tier** | 1 minute | Instant one-click git push deployment |
| **Option 4: Local Docker / Compose** | **Free** | 30 seconds | Running locally or on an internal defense VPS |
| **Option 5: Instant Cloudflare Tunnel** | **Free** | 10 seconds | Instant live public HTTPS URL from your running laptop |

---

## Option 1: Hugging Face Spaces (Recommended - Free & Permanent)

Hugging Face Spaces provides persistent container hosting with free HTTPS and WebSocket support.

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **"Create new Space"**.
2. Space Name: `sentinel-ew` or `drdo-smart-scan`
3. License: `MIT`
4. Select **Docker** as the Space SDK (Blank template).
5. Choose **Public**.
6. Click **Create Space**.
7. In your local terminal, add the Hugging Face git remote and push:
   ```bash
   git remote add space https://huggingface.co/spaces/<YOUR_HF_USERNAME>/sentinel-ew
   git push space main
   ```
8. Hugging Face will automatically build the `Dockerfile` and launch the live Tactical C2 Dashboard at:
   `https://huggingface.co/spaces/<YOUR_HF_USERNAME>/sentinel-ew`

---

## Option 2: Render.com (1-Click GitHub Web Service)

Render automatically deploys web applications whenever you push to GitHub.

1. Go to [Render Dashboard](https://dashboard.render.com/) and sign in with GitHub.
2. Click **New +** -> **Web Service**.
3. Select your repository: `krishdeshpande/drdo-ew-smart-scan`.
4. Configure settings:
   - **Name**: `sentinel-ew`
   - **Environment**: `Python 3` (or `Docker`)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python ui/server.py`
   - **Plan**: Free
5. Click **Create Web Service**.
6. Once deployed, your dashboard will be accessible at:
   `https://sentinel-ew.onrender.com`

---

## Option 3: Railway.app (Zero-Config Deploy)

1. Go to [Railway.app](https://railway.app/) and sign in with GitHub.
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select `krishdeshpande/drdo-ew-smart-scan`.
4. Railway will automatically detect the `Dockerfile` / `Procfile`, build the container, and assign a public domain.
5. In your project settings, click **Generate Domain** to get your live HTTPS URL.

---

## Option 4: Local Docker / Docker Compose

If you have Docker installed on your machine or on an AWS/GCP/Azure VM:

### Using Docker Compose:
```bash
# Build and run in detached mode
docker compose up -d

# View live logs
docker compose logs -f

# Stop the container
docker compose down
```

### Using standard Docker CLI:
```bash
# Build the production image
docker build -t sentinel-ew-dashboard:latest .

# Run the container exposing port 8080
docker run -d -p 8080:8080 --name sentinel_ew sentinel-ew-dashboard:latest

# Open in browser
# http://localhost:8080/
```

---

## Option 5: Instant Public Live Demo (Cloudflare Tunnel / LocalTunnel)

If you have the dashboard running locally on your computer and want an **instant public HTTPS link** to share with teammates, evaluators, or test on your phone right now:

### Using Cloudflare Tunnel (No account or installation required):
```bash
# Download and run cloudflared directly:
npx cloudflared tunnel --url http://localhost:8080
```
*Cloudflare will print a secure URL like `https://random-words.trycloudflare.com` that anyone in the world can access.*

### Alternatively, using LocalTunnel:
```bash
npx localtunnel --port 8080
```

---

## System Endpoints

- **Tactical C2 HUD**: `http://<host>:<port>/` or `/dashboard.html`
- **Telemetry WebSocket**: `ws://<host>:<port>/ws` (or `wss://` over HTTPS)
- **Health Check & Node Status**: `http://<host>:<port>/health`

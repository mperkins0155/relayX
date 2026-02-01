# Cloudflare → Railway Auto-Sync Setup

## Quick Start

### 1. Install Railway CLI (one time only)
```bash
npm install -g @railway/cli
railway login
```

### 2. Start Auto-Sync
```bash
# Option 1: PowerShell (recommended)
.\sync_railway_url.ps1

# Option 2: Batch file
.\sync_railway_url.bat
```

The script will:
- ✅ Monitor your Cloudflare tunnel every 30 seconds
- ✅ Detect when URL changes
- ✅ Automatically update Railway's `VOICE_GATEWAY_URL`
- ✅ Trigger automatic redeployment

## Setup (Optional - for multi-project setups)

If you have multiple Railway projects, set these:

```powershell
$env:RAILWAY_PROJECT_ID = "your-project-id"
$env:RAILWAY_SERVICE_ID = "your-backend-service-id"
```

Get these from your Railway dashboard URL:
`https://railway.app/project/{PROJECT_ID}/service/{SERVICE_ID}`

## How It Works

1. **Local**: Cloudflare tunnel starts → generates URL
2. **Script**: Detects URL change
3. **Railway**: Environment variable updated automatically
4. **Backend**: Redeploys with new voice gateway URL
5. **Calls**: Now work! 🎉

## Start Everything Together

```bash
# Start services
docker-compose up -d

# Start auto-sync (in new terminal)
.\sync_railway_url.ps1
```

Now when you make calls, Railway will always have the correct tunnel URL!

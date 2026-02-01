# Quick Reference - RelayX Deployment

## File Structure Created

```
RelayX/
├── vercel.json              ← Vercel config (auto-detects frontend)
├── railway.toml             ← Railway config (auto-detects backend)
├── SIMPLE_DEPLOYMENT.md     ← Step-by-step guide (15 min)
├── DEPLOYMENT_CHECKLIST.md  ← Track your progress
├── verify_deployment_ready.ps1 ← Run before deploying
├── VERCEL_ENV.txt          ← Copy these to Vercel
└── RAILWAY_ENV.txt         ← Copy these to Railway
```

## Three Commands to Deploy

```powershell
# 1. Verify everything is ready
.\verify_deployment_ready.ps1

# 2. Push to GitHub
git add .
git commit -m "Deploy to production"
git push origin main

# 3. Follow the guide
# Open SIMPLE_DEPLOYMENT.md and follow Part 1 & 2
```

## What Each File Does

### `vercel.json`
Tells Vercel:
- Build command: `npm install && npm run build` in frontend/
- Output: frontend/dist
- Framework: Vite

### `railway.toml`
Tells Railway:
- Build: `pip install -r backend/requirements.txt`
- Start: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health check: `/health` endpoint

### `VERCEL_ENV.txt`
Contains 3 environment variables for Vercel:
- VITE_API_URL → Your Railway backend URL
- VITE_SUPABASE_URL → Your Supabase project URL  
- VITE_SUPABASE_ANON_KEY → Your Supabase anon key

### `RAILWAY_ENV.txt`
Contains all backend environment variables:
- DATABASE_URL → From Railway PostgreSQL service
- API keys (Twilio, Groq, Cal, etc.)
- Configuration settings

## Deployment Flow

```
1. GitHub ──┬──> Railway (Backend)
            │    - Auto-builds from railway.toml
            │    - Connects to PostgreSQL
            │    - Exposes API at: https://xxx.up.railway.app
            │
            └──> Vercel (Frontend)
                 - Auto-builds from vercel.json
                 - Connects to Railway API
                 - Exposes site at: https://xxx.vercel.app
```

## After Deployment URLs

Fill these in after deploying:

```
Frontend: https://________________________________.vercel.app
Backend:  https://________________________________.up.railway.app
Database: Supabase Dashboard
```

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot connect to backend" | Update VITE_API_URL in Vercel with Railway URL |
| "CORS error" | Already handled - vercel.app domains whitelisted |
| "Database connection failed" | Check DATABASE_URL in Railway matches PostgreSQL |
| "Build failed" | Check all env vars are set, then redeploy |
| "502 Bad Gateway" | Check Railway logs for Python errors |

## Important Notes

✓ **Railway auto-generates**: PostgreSQL DATABASE_URL, public domain
✓ **Vercel auto-builds**: From vercel.json config  
✓ **CORS pre-configured**: All *.vercel.app domains allowed
✓ **Python version**: 3.11.9 (from backend/runtime.txt)
✓ **No Docker needed**: Both platforms build natively

## Support Links

- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app
- Supabase Docs: https://supabase.com/docs

---

**Ready to deploy?** Run `.\verify_deployment_ready.ps1` and follow `SIMPLE_DEPLOYMENT.md`

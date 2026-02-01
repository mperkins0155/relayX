# 🚀 RelayX Deployment Guide

This guide will help you deploy RelayX with **Frontend on Vercel** and **Backend + Database on Railway**.

---

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ GitHub account
- ✅ Vercel account (sign up with GitHub)
- ✅ Railway account (sign up with GitHub)
- ✅ Supabase account (for PostgreSQL database)
- ✅ Twilio account (for phone calls)
- ✅ Groq API key (for AI)

---

## 🎯 Part 1: Deploy Frontend to Vercel

### Step 1: Push Code to GitHub
```bash
git add .
git commit -m "chore: deployment configuration"
git push origin main
```

### Step 2: Deploy on Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click **"New Project"**
3. Import your GitHub repository: `Gauravguddeti/relayX`
4. Configure project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

### Step 3: Add Environment Variables (Vercel)
Go to **Project Settings → Environment Variables** and add:

```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_URL=https://your-backend-url.railway.app
```

> **Note**: You'll get the Railway backend URL in Part 2

### Step 4: Deploy
Click **"Deploy"** - Vercel will build and deploy your frontend automatically!

Your frontend will be live at: `https://relayx.vercel.app`

---

## 🚂 Part 2: Deploy Backend to Railway

### Step 1: Create New Project
1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose `Gauravguddeti/relayX`

### Step 2: Configure Service
Railway will auto-detect your setup. Verify:
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Root Directory**: Leave blank (we cd into backend in start command)

### Step 3: Add PostgreSQL Database
1. In your Railway project, click **"New"**
2. Select **"Database" → "PostgreSQL"**
3. Railway will create and connect the database automatically
4. Copy the `DATABASE_URL` from the PostgreSQL service

### Step 4: Add Environment Variables (Railway)
Go to your backend service → **Variables** tab and add:

```env
DATABASE_URL=postgresql://... (from Railway PostgreSQL)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number
VOICE_GATEWAY_URL=https://your-voice-gateway.railway.app
REDIS_URL=redis://default:password@redis.railway.internal:6379
USE_CLOUD_STT=false
LANDING_PAGE_AGENT_ID=your_agent_id
CAL_API_KEY=your_calendly_key
PORT=8000
```

### Step 5: Add Redis (Optional but Recommended)
1. Click **"New" → "Database" → "Redis"**
2. Copy the Redis URL to your environment variables

### Step 6: Deploy
Click **"Deploy"** - Railway will build and start your backend!

Your backend will be live at: `https://relayx-backend-production.up.railway.app`

### Step 7: Generate Domain
1. Go to your backend service settings
2. Click **"Generate Domain"**
3. Copy the domain URL (e.g., `relayx-backend.up.railway.app`)

---

## 🔗 Part 3: Connect Frontend to Backend

### Update Vercel Environment Variables
1. Go back to Vercel project settings
2. Update `VITE_API_URL` with your Railway backend URL:
   ```
   VITE_API_URL=https://relayx-backend.up.railway.app
   ```
3. Redeploy frontend (Vercel → Deployments → Redeploy)

---

## 🗄️ Part 4: Database Setup

### Option A: Use Railway PostgreSQL (Recommended)
Railway PostgreSQL is already set up! Just run migrations:

1. Go to Railway PostgreSQL service
2. Click **"Data"** tab
3. Run your schema:
```sql
-- Copy contents from db/schema.sql and paste here
```

### Option B: Use Supabase PostgreSQL
If you prefer Supabase:
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Go to **SQL Editor**
4. Paste contents from `db/schema.sql`
5. Update `DATABASE_URL` in Railway to use Supabase connection string

---

## 🎙️ Part 5: Deploy Voice Gateway (Optional)

### If you want voice calling:
1. In Railway, click **"New Service"**
2. Select same GitHub repo
3. Configure:
   - **Start Command**: `cd voice_gateway && python voice_gateway.py`
   - Add same environment variables as backend
4. Generate domain for voice gateway
5. Update `VOICE_GATEWAY_URL` in backend Railway variables

---

## ✅ Verification Checklist

- [ ] Frontend deployed on Vercel
- [ ] Backend deployed on Railway
- [ ] Database created (Railway PostgreSQL or Supabase)
- [ ] Environment variables configured on both platforms
- [ ] Frontend can reach backend API
- [ ] Database schema applied
- [ ] Test login works
- [ ] Voice gateway connected (if using calls)

---

## 🔧 Useful Commands

### Update Frontend
```bash
git add frontend/
git commit -m "update: frontend changes"
git push origin main
# Vercel auto-deploys
```

### Update Backend
```bash
git add backend/
git commit -m "update: backend changes"
git push origin main
# Railway auto-deploys
```

### View Logs
- **Vercel**: Project → Deployments → Click deployment → View Function Logs
- **Railway**: Service → Deployments → Click deployment → View Logs

---

## 🌐 Your Live URLs

After deployment, update README with:
```markdown
🌐 **Live Demo**: https://relayx.vercel.app
🔌 **API**: https://relayx-backend.up.railway.app
📊 **Health Check**: https://relayx-backend.up.railway.app/health
```

---

## 🐛 Troubleshooting

### Frontend Build Fails
- Check Node.js version (18+)
- Verify all dependencies in package.json
- Check build logs in Vercel

### Backend Won't Start
- Verify Python version (3.11+)
- Check all env vars are set
- View Railway logs for errors

### Database Connection Issues
- Verify DATABASE_URL format
- Check PostgreSQL service is running
- Ensure database schema is applied

### API Calls Fail
- Check CORS settings in backend
- Verify VITE_API_URL in frontend env
- Test API health endpoint directly

---

## 🎉 You're Live!

Your RelayX platform is now deployed and accessible to the world! 

**Next Steps**:
1. Set up custom domain on Vercel
2. Configure production environment variables
3. Set up monitoring and alerts
4. Enable auto-deployments from main branch

---

## 💡 Pro Tips

- **Auto Deploy**: Both Vercel and Railway auto-deploy on git push
- **Rollback**: Both platforms allow instant rollback to previous versions
- **Logs**: Always check logs first when debugging
- **Environment Variables**: Use different values for production vs development
- **Database Backups**: Railway provides automatic backups for PostgreSQL

Happy deploying! 🚀

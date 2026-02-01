# 🚀 Simple Deployment Guide - RelayX

Deploy RelayX in 15 minutes: Frontend on Vercel, Backend on Railway.

---

## 📋 What You Need

Before starting:
- GitHub account
- Vercel account (free) - [vercel.com](https://vercel.com)
- Railway account (free trial) - [railway.app](https://railway.app)
- Your API keys ready (Supabase, Twilio, Groq, etc.)

---

## Part 1: Deploy Backend to Railway (10 min)

### 1. Push to GitHub
```powershell
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2. Create Railway Project
1. Go to [railway.app](https://railway.app/new)
2. Click **"Deploy from GitHub repo"**
3. Select your repository: `RelayX`
4. Railway will auto-detect and start building

### 3. Add PostgreSQL Database
1. In Railway project, click **"+ New"**
2. Select **"Database" → "PostgreSQL"**
3. Wait for it to provision (1-2 minutes)
4. Click on PostgreSQL service → **"Variables"** tab
5. Copy the `DATABASE_URL` value

### 4. Add Environment Variables
1. Click on your **backend service** (not the database)
2. Go to **"Variables"** tab
3. Click **"+ New Variable"** and add these:

```env
DATABASE_URL=postgresql://... (paste from PostgreSQL service)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
USE_CLOUD_STT=true
STT_PROVIDER=groq
USE_CLOUD_TTS=false
USE_CLOUD_LLM=true
ENVIRONMENT=production
PORT=8000
BACKEND_HOST=0.0.0.0
LANDING_PAGE_AGENT_ID=your_agent_id
CAL_API_KEY=your_cal_api_key
FISH_AUDIO_API_KEY=your_fish_audio_api_key
SARVAM_API_KEY=your_sarvam_api_key
REASONING_MODEL=qwen/qwen3-32b
```

### 5. Get Backend URL
1. In Railway, click on your backend service
2. Go to **"Settings"** tab
3. Under **"Domains"**, click **"Generate Domain"**
4. Copy the URL (e.g., `https://xxx.up.railway.app`)

✅ Backend is now live!

---

## Part 2: Deploy Frontend to Vercel (5 min)

### 1. Create Vercel Project
1. Go to [vercel.com/new](https://vercel.com/new)
2. Click **"Import Project"**
3. Select your GitHub repository: `RelayX`
4. Vercel will auto-detect the configuration from `vercel.json`
5. Click **"Deploy"**

### 2. Add Environment Variables
1. While deployment is running, go to **"Settings" → "Environment Variables"**
2. Add these three variables:

```env
VITE_API_URL=https://xxx.up.railway.app
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

**Important:** Replace `VITE_API_URL` with your Railway backend URL from Part 1, Step 5

### 3. Redeploy
1. Go to **"Deployments"** tab
2. Click the three dots on the latest deployment
3. Click **"Redeploy"**

✅ Frontend is now live!

---

## Part 3: Initialize Database (2 min)

### 1. Run Database Schema
1. Go to your Supabase dashboard: [supabase.com/dashboard](https://supabase.com/dashboard)
2. Select your project
3. Go to **SQL Editor**
4. Open the file `db/schema.sql` from your project
5. Copy the entire contents
6. Paste into Supabase SQL Editor
7. Click **"Run"**

✅ Database tables created!

---

## 🎉 That's It!

Your app is now live:
- **Frontend**: `https://your-project.vercel.app`
- **Backend**: `https://xxx.up.railway.app`

### Next Steps

1. **Test the deployment**: Visit your Vercel URL and try logging in
2. **Update CORS**: If you see CORS errors, add your Vercel domain to the backend CORS settings
3. **Add custom domain** (optional): In Vercel settings, add your own domain

---

## 🔧 Troubleshooting

### Frontend build fails
- Check that all environment variables are set
- Make sure `VITE_API_URL` points to your Railway backend

### Backend won't start
- Verify `DATABASE_URL` is correctly set from Railway PostgreSQL
- Check Railway logs: Click service → "Deployments" → View logs

### Database connection fails
- Run the schema.sql in Supabase SQL Editor
- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` are correct

### CORS errors
- Add your Vercel domain to backend CORS allowed origins in `backend/main.py`

---

## 📝 Configuration Files

This deployment uses:
- `vercel.json` - Vercel configuration
- `railway.toml` - Railway configuration  
- `backend/requirements.txt` - Python dependencies
- `frontend/package.json` - Node.js dependencies

All files are included in your repository and will work automatically.

# 🚀 Deployment Checklist

Use this checklist to track your deployment progress.

## ✅ Pre-Deployment
- [ ] Code pushed to GitHub
- [ ] All API keys ready (check RAILWAY_ENV.txt and VERCEL_ENV.txt)
- [ ] Supabase project created and schema.sql run

---

## 🚂 Railway (Backend) - 10 minutes

### Setup
- [ ] Railway project created from GitHub repo
- [ ] PostgreSQL database added to project
- [ ] DATABASE_URL copied from PostgreSQL service

### Environment Variables
Add all variables from RAILWAY_ENV.txt:
- [ ] DATABASE_URL (from Railway PostgreSQL)
- [ ] SUPABASE_URL
- [ ] SUPABASE_ANON_KEY
- [ ] TWILIO_ACCOUNT_SID
- [ ] TWILIO_AUTH_TOKEN
- [ ] TWILIO_PHONE_NUMBER
- [ ] GROQ_API_KEY
- [ ] GROQ_MODEL
- [ ] Other API keys (CAL, FISH_AUDIO, SARVAM)
- [ ] Configuration variables (PORT, ENVIRONMENT, etc.)

### Verification
- [ ] Backend service deployed successfully
- [ ] Public domain generated
- [ ] Health check passes: `https://your-backend.up.railway.app/health`
- [ ] Backend URL copied (needed for Vercel)

---

## 🔵 Vercel (Frontend) - 5 minutes

### Setup
- [ ] Vercel project created from GitHub repo
- [ ] Auto-detected configuration (vercel.json)
- [ ] Initial deployment completed

### Environment Variables
Add from VERCEL_ENV.txt:
- [ ] VITE_API_URL (your Railway backend URL)
- [ ] VITE_SUPABASE_URL
- [ ] VITE_SUPABASE_ANON_KEY

### Verification
- [ ] Frontend redeployed with environment variables
- [ ] Can access the login page
- [ ] Public URL works: `https://your-project.vercel.app`

---

## 🗄️ Database Initialization

- [ ] Open Supabase SQL Editor
- [ ] Copy contents of db/schema.sql
- [ ] Run the schema in Supabase
- [ ] Verify tables created (users, agents, calls, etc.)

---

## 🧪 Testing

- [ ] Can access frontend URL
- [ ] Can register a new account
- [ ] Can log in
- [ ] Dashboard loads correctly
- [ ] Can create an agent
- [ ] API calls work (check Network tab)

---

## 🎉 Optional Enhancements

- [ ] Add custom domain to Vercel
- [ ] Add Redis to Railway (for caching)
- [ ] Set up Railway monitoring
- [ ] Configure Railway auto-deploy on git push
- [ ] Add Sentry for error tracking

---

## 📝 Important URLs

Write down your deployment URLs:

- **Frontend**: `https://______________________.vercel.app`
- **Backend**: `https://______________________.up.railway.app`
- **Database**: Supabase dashboard
- **GitHub Repo**: `https://github.com/____________________`

---

## 🔧 Common Issues

### "Cannot connect to backend"
→ Check VITE_API_URL in Vercel env vars matches Railway backend URL

### "CORS error"
→ Already configured in backend/main.py with Vercel regex

### "Database connection failed"
→ Verify DATABASE_URL in Railway matches PostgreSQL service URL

### "Build failed on Vercel"
→ Check all VITE_* variables are set, redeploy after adding them

### "502 Bad Gateway on Railway"
→ Check Railway logs for errors, verify requirements.txt installed correctly

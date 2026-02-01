# 📊 RelayX Project Analysis & Deployment Strategy

## Project Overview

**RelayX** is an AI-powered outbound calling system with:
- **Frontend**: React + TypeScript + Vite (Dashboard/UI)
- **Backend**: FastAPI + Python (REST API)
- **Database**: Supabase (PostgreSQL) 
- **Voice**: Twilio + AI Voice Gateway (WebSocket)
- **AI**: Groq (LLM), Whisper (STT), TTS engines

---

## Current Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER/BROWSER                         │
│                                                         │
│  React App (localhost:5173 or Vercel)                  │
│  - Login/Signup                                         │
│  - Dashboard                                            │
│  - Agent Management                                     │
│  - Call History                                         │
│  - Campaigns                                            │
│  - Contacts                                             │
└────────────┬────────────────────────────────────────────┘
             │
             │ HTTP/S Requests
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                │
│                                                         │
│  Routes:                                                │
│  • /auth/*          - Authentication (JWT)              │
│  • /agents/*        - Agent CRUD                        │
│  • /calls/*         - Call management                   │
│  • /campaigns/*     - Campaign execution                │
│  • /contacts/*      - Contact management                │
│  • /knowledge/*     - Knowledge base                    │
│  • /analytics/*     - Analytics                         │
│  • /cal/*           - Calendly integration              │
│                                                         │
│  Services:                                              │
│  • Twilio Client    - Initiates calls                   │
│  • LLM Client       - Groq API                          │
│  • Database Client  - Supabase                          │
│  • Scheduler        - Campaign execution                │
└────────┬────────────────────────┬───────────────────────┘
         │                        │
         │                        │ WebSocket for
         │                        │ real-time audio
         ▼                        ▼
┌──────────────────┐   ┌──────────────────────────────┐
│    Supabase      │   │   Voice Gateway (Port 8001)  │
│   (PostgreSQL)   │   │                              │
│                  │   │  • WebSocket handler         │
│  Tables:         │   │  • STT (Whisper/Groq)        │
│  - users         │   │  • LLM processing            │
│  - agents        │   │  • TTS (Coqui/FishAudio)     │
│  - calls         │   │  • Audio streaming           │
│  - transcripts   │   └──────────┬───────────────────┘
│  - campaigns     │              │
│  - contacts      │              │
│  - knowledge     │              ▼
│  - events        │   ┌──────────────────────┐
│  - templates     │   │   Twilio Cloud       │
└──────────────────┘   │   (Phone Network)    │
                       └──────────────────────┘
```

---

## Database Schema (Supabase)

### Core Tables
1. **users** - User accounts, authentication
2. **agents** - AI agent configurations (prompts, settings)
3. **calls** - Call records (status, duration, metadata)
4. **transcripts** - Conversation history
5. **campaigns** - Bulk calling campaigns
6. **contacts** - Contact lists
7. **knowledge** - Knowledge base for agents
8. **events** - Calendly/scheduling events
9. **templates** - Agent prompt templates

### Key Relationships
- agents ← calls (agent_id)
- calls ← transcripts (call_id)
- campaigns → contacts (campaign_id)
- agents ← knowledge (agent_id)

---

## Frontend-Backend Integration

### Frontend Config ([config.ts](config.ts))
```typescript
API_BASE_URL = localhost ? '' : 'https://api.relayx.tech'
```

### How It Works
1. Frontend makes HTTP requests to `/agents`, `/calls`, etc.
2. In development: Nginx proxy forwards to localhost:8000
3. In production: Direct API calls to backend URL

### API Call Pattern
```typescript
// All frontend API calls use relative URLs
fetch('/agents')           // → proxied to backend
fetch('/auth/login')       // → proxied to backend
fetch('/calls/outbound')   // → proxied to backend
```

### Environment Variables

**Frontend (.env)**
```env
VITE_API_URL=backend_url  # Actually not used in code!
VITE_SUPABASE_URL=...     # Not currently used
VITE_SUPABASE_ANON_KEY=... # Not currently used
```

**Backend (.env)**
```env
DATABASE_URL=...          # PostgreSQL connection
SUPABASE_URL=...          # Supabase project URL
SUPABASE_ANON_KEY=...     # Supabase API key
TWILIO_ACCOUNT_SID=...    # Twilio credentials
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...
GROQ_API_KEY=...          # AI/LLM keys
FISH_AUDIO_API_KEY=...
SARVAM_API_KEY=...
CAL_API_KEY=...           # Calendly
VOICE_GATEWAY_URL=...     # Voice WebSocket endpoint
```

---

## Deployment Strategy

### Option 1: Vercel (Frontend) + Railway (Backend) ✅ RECOMMENDED

#### Frontend on Vercel
- Auto-builds from `frontend/` directory
- Serves static React app
- **Issue**: Relative API URLs won't work directly

#### Backend on Railway
- Runs FastAPI with Uvicorn
- Auto-provisions PostgreSQL
- Public domain: `https://xxx.up.railway.app`

#### The Connection Problem
Frontend uses **relative URLs** (`fetch('/agents')`) expecting:
1. Development: Nginx proxy on localhost
2. Production: ??? 

**Solutions:**
1. **Update frontend config** to use absolute API URL in production
2. **Add Vercel rewrites** to proxy API requests to Railway
3. **Change frontend code** to use environment variable properly

---

### Option 2: Single Platform (Railway) - Both Frontend + Backend

Deploy both as separate services:
- Frontend service (Node.js static server)
- Backend service (Python FastAPI)
- PostgreSQL database
- All connected on Railway's private network

---

## Recommended Deployment Plan

### Phase 1: Fix Frontend API Configuration

**Current Issue:** Frontend doesn't use `VITE_API_URL` properly

**Solution:** Update [config.ts](config.ts) to:
```typescript
export const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (window.location.hostname === 'localhost' ? '' : 'https://api.relayx.tech');
```

Then update all fetch calls to:
```typescript
fetch(`${API_BASE_URL}/agents`)
```

### Phase 2: Remove Secrets from Repo

Currently blocking GitHub push:
- RAILWAY_ENV.txt has real API keys
- SIMPLE_DEPLOYMENT.md has real API keys

**Solution:**
1. Remove files from git tracking
2. Create `.env.example` templates
3. Commit sanitized versions

### Phase 3: Deploy Backend to Railway

1. Push to GitHub
2. Create Railway project from repo
3. Add PostgreSQL database
4. Set environment variables
5. Get public URL

### Phase 4: Deploy Frontend to Vercel

1. Create Vercel project from repo
2. Set `VITE_API_URL` to Railway backend URL
3. Deploy

### Phase 5: Initialize Database

1. Go to Supabase dashboard
2. Run schema.sql in SQL Editor
3. Verify tables created

---

## What Needs to Change Before Deployment

### 1. Frontend API Client ⚠️
**Files to Update:**
- `frontend/src/config.ts` - Use env var
- All `pages/*.tsx` files - Prepend `API_BASE_URL`

**Estimated Changes:** ~25 files, ~50 lines

### 2. Environment Files 🔒
**Files to Remove from Git:**
- `VERCEL_ENV.txt` (contains secrets)
- `RAILWAY_ENV.txt` (contains secrets)

**Files to Create:**
- `.env.example` (templates)

### 3. Deployment Configs ✅
**Already Created:**
- `vercel.json` ✅
- `railway.toml` ✅

---

## Next Steps

**Choose your approach:**

### A) Quick Fix (30 minutes)
1. I'll update frontend to use API_BASE_URL properly
2. Remove secrets from git
3. Deploy both to Vercel + Railway

### B) Alternative Architecture (15 minutes)
1. Keep current setup
2. Add Vercel rewrites to proxy API calls
3. No frontend code changes needed

### C) Single Platform (20 minutes)
1. Deploy both frontend and backend to Railway
2. Use Railway's internal networking
3. One platform to manage

**Which approach would you like?**

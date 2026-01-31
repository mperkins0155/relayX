# RelayX - AI Voice Calling Platform

<div align="center">

🤖 **Production-ready AI-powered voice calling system with real-time conversations**

Built with Twilio • Supabase • Sarvam AI • Groq Llama-3.3 • React + FastAPI

[Architecture](#-architecture) • [Setup](#-quick-start) • [Features](#-key-features) • [Tech Stack](#-tech-stack)

**⚡ v1.2 STABLE** - Streaming TTS, 1s Echo Protection, Modern Hindi/Marathi

</div>

---

## 📋 Overview

RelayX is a production-ready AI voice calling platform that enables intelligent, real-time phone conversations with advanced features like streaming TTS, hybrid VAD, and multilingual support (English, Hindi, Marathi).

### ✨ Key Features

- 🎯 **Real-time Voice Gateway** - WebSocket-based streaming with <2s response time
- 🗣️ **Multilingual Support** - English, Hindi, Marathi with modern conversational style
- ⚡ **Streaming TTS** - Parallel sentence generation (600ms faster responses)
- 🎙️ **Hybrid VAD** - WebRTC + Silero VAD for accurate speech detection
- 🧠 **Smart LLM** - Groq Llama-3.3-70b for natural conversations
- 📞 **Twilio Integration** - WebSocket Media Streams (8kHz mulaw audio)
- 🔊 **High-Quality STT/TTS** - Sarvam AI (Indian accent optimized)
- 💾 **Full Tracking** - Call transcripts, analytics, and metadata in Supabase
- 🌐 **Modern Web Dashboard** - React + TypeScript with real-time updates
- 🔒 **Production Ready** - Docker deployment, Redis caching, error handling

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Twilio Media Streams                         │
│                   (WebSocket + Phone Network)                       │
└────────────────┬───────────────────────────┬────────────────────────┘
                 │                           │
                 │ WebSocket (8kHz mulaw)    │ HTTP Status Callbacks
                 │ Real-time audio stream    │
                 ▼                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│               Voice Gateway (FastAPI + WebSocket)                   │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Audio Processing Pipeline (<2s total latency)               │  │
│  │                                                              │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────────┐  │  │
│  │  │ Hybrid  │─▶│ Sarvam  │─▶│  Groq   │─▶│   Sarvam     │  │  │
│  │  │   VAD   │  │   STT   │  │  Llama  │  │     TTS      │  │  │
│  │  │ (WebRTC │  │ (16kHz) │  │  3.3-70b│  │ (Streaming)  │  │  │
│  │  │ +Silero)│  │ 349ms   │  │  358ms  │  │   400ms*     │  │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └──────────────┘  │  │
│  │  *First sentence only, rest generates in parallel          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Features:                                                          │
│  • Silero VAD (CPU-only, 5MB model) for accurate speech detection  │
│  • Streaming TTS with parallel sentence generation                 │
│  • 1000ms echo protection window                                   │
│  • Barge-in support with graceful interruption                     │
│  • Language detection: English, Hindi, Marathi                     │
│  • Modern conversational style (Hindi/Marathi + English tech terms)│
│  • Redis caching for agent configs                                 │
└───────────────────────┬─────────────────────────────────────────────┘
                        │
                        │ Store: Transcripts, Analytics, Metadata
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│              FastAPI Backend + React Frontend                       │
│  ┌────────────────────┐  ┌─────────────────────────────────────┐  │
│  │  Backend (Python)  │  │  Frontend (React + TypeScript)      │  │
│  │  • Agent Mgmt      │  │  • Agent Settings UI                │  │
│  │  • Campaign Mgmt   │  │  • Campaign Dashboard               │  │
│  │  • Call Tracking   │  │  • Call Analytics                   │  │
│  │  • Analytics API   │  │  • Contact Management               │  │
│  │  • Auth & Admin    │  │  • Real-time Updates                │  │
│  └────────────────────┘  └─────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Supabase (PostgreSQL)                             │
│  • agents (AI configs)          • calls (metadata)                  │
│  • campaigns (bulk calling)     • contacts (phone numbers)          │
│  • transcripts (conversation)   • call_analysis (AI summaries)      │
│  • users (auth)                 • knowledge_base (RAG context)      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                  Cloudflare Tunnel (Production)                     │
│  Exposes: https://xxx.trycloudflare.com → voice-gateway:8001       │
└─────────────────────────────────────────────────────────────────────┘
```

## 📞 Call Flow Diagram

```
┌──────────┐                                                    
│  User    │  1. Initiates call from Dashboard/API             
└─────┬────┘                                                    
      │                                                          
      │ 2. POST /calls/outbound                                
      ▼                                                          
┌──────────────┐                                                
│   Backend    │  3. Creates call record in DB                 
│   (FastAPI)  │  4. Calls Twilio API to initiate call        
└─────┬────────┘                                                
      │                                                          
      │ 5. Twilio connects call + opens WebSocket              
      ▼                                                          
┌──────────────────────────────────────────────────────────┐   
│  Voice Gateway (WebSocket Handler)                       │   
│                                                           │   
│  Step 1: Language Selection                              │   
│  ┌─────────────────────────────────────────────────┐    │   
│  │ AI: "Hello. Do you prefer English, Hindi, or    │    │   
│  │      Marathi?"                                   │    │   
│  │ User: "Hindi"                                    │    │   
│  │ → Detected language: Hindi                      │    │   
│  │ → Updates system prompt with language style     │    │   
│  └─────────────────────────────────────────────────┘    │   
│                                                           │   
│  Step 2: Agent Greeting (Language-specific)              │   
│  ┌─────────────────────────────────────────────────┐    │   
│  │ AI: "नमस्ते! मैं Alex हूँ RelayX से।            │    │   
│  │      क्या आपके पास 2 minute हैं?"              │    │   
│  │ (Modern Hindi style: Hindi + English tech terms) │    │   
│  └─────────────────────────────────────────────────┘    │   
│                                                           │   
│  Step 3: Conversation Loop                               │   
│  ┌─────────────────────────────────────────────────┐    │   
│  │ 1. VAD detects speech                           │    │   
│  │    • WebRTC VAD Mode 2 (180ms speech start)     │    │   
│  │    • Silero VAD validation (0.4 threshold)      │    │   
│  │    • 240-450ms silence for speech_end           │    │   
│  │                                                  │    │   
│  │ 2. Buffer audio (PCM 16kHz mono)                │    │   
│  │    • Min 400ms for processing                   │    │   
│  │    • Max 4s force timeout                       │    │   
│  │                                                  │    │   
│  │ 3. STT: Audio → Text (Sarvam AI)                │    │   
│  │    • Upsampling: 8kHz → 16kHz                   │    │   
│  │    • Language: hi-IN / mr-IN / en-IN            │    │   
│  │    • Latency: ~350ms                            │    │   
│  │                                                  │    │   
│  │ 4. LLM: Text → Response (Groq Llama-3.3-70b)   │    │   
│  │    • Context: Full conversation history         │    │   
│  │    • Temperature: 0.7 (natural variation)       │    │   
│  │    • Max tokens: 200 (concise responses)        │    │   
│  │    • Latency: ~360ms                            │    │   
│  │                                                  │    │   
│  │ 5. TTS: Text → Audio (Sarvam AI Streaming)     │    │   
│  │    • Split text into sentences                  │    │   
│  │    • Generate first sentence immediately        │    │   
│  │    • Start streaming while rest generates       │    │   
│  │    • Parallel generation for remaining          │    │   
│  │    • Latency: ~400ms to first audio             │    │   
│  │                                                  │    │   
│  │ 6. Stream audio to Twilio                       │    │   
│  │    • Convert WAV → mulaw 8kHz                   │    │   
│  │    • Base64 encode                              │    │   
│  │    • Send in 20ms chunks                        │    │   
│  │    • 1000ms echo protection after completion    │    │   
│  │                                                  │    │   
│  │ 7. Loop continues until:                        │    │   
│  │    • User hangs up                              │    │   
│  │    • AI completes conversation goal             │    │   
│  │    • Timeout/error occurs                       │    │   
│  └─────────────────────────────────────────────────┘    │   
│                                                           │   
│  Step 4: Call Completion                                 │   
│  ┌─────────────────────────────────────────────────┐    │   
│  │ • Save full transcript to database              │    │   
│  │ • Generate AI analysis (summary, outcome)       │    │   
│  │ • Update call metadata (duration, status)       │    │   
│  │ • Check for scheduling intent (Calendly)        │    │   
│  └─────────────────────────────────────────────────┘    │   
└──────────────────────────────────────────────────────────┘   
      │                                                          
      │ 6. Call metadata + transcript saved                    
      ▼                                                          
┌──────────────┐                                                
│  Supabase    │  • calls table updated                        
│  (Database)  │  • transcripts stored                         
└──────────────┘  • call_analysis generated                    
```

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended for production)
- **OR** Python 3.11+ with manual setup
- **Twilio Account** (trial or paid with $1+ credit)
- **Supabase Project** (free tier works)
- **Groq API Key** (free tier: 14,400 requests/day)
- **Sarvam AI API Key** (Indian STT/TTS provider)
- **Cloudflare Tunnel** (or ngrok for development)

### 🐳 Docker Deployment (Recommended)

**1️⃣ Clone Repository**

```bash
git clone https://github.com/yourusername/RelayX.git
cd RelayX
```

**2️⃣ Configure Environment**

Create `.env` file:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_NUMBER=+1234567890

# Supabase Database
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJxxx...
SUPABASE_SERVICE_ROLE_KEY=eyJxxx...

# AI Services
GROQ_API_KEY=gsk_xxx
GROQ_MODEL=llama-3.3-70b-versatile
SARVAM_API_KEY=xxx

# Voice Gateway
VOICE_GATEWAY_URL=https://xxx.trycloudflare.com

# Redis (Docker handles this)
REDIS_URL=redis://redis:6379

# Frontend (Optional - for development)
VITE_API_URL=http://localhost:8000
```

**3️⃣ Setup Database**

Run migrations in Supabase SQL Editor:

```bash
# Copy contents from db/schema.sql and execute
```

**4️⃣ Start Services**

```bash
# Production mode
docker-compose up -d

# Development mode (with logs)
docker-compose up

# Check status
docker-compose ps

# View logs
docker-compose logs -f voice-gateway
docker-compose logs -f backend
```

**5️⃣ Access Dashboard**

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Voice Gateway: Internal (accessed via Cloudflare tunnel)

### 💻 Manual Setup (Development)

**1️⃣ Install Dependencies**

```bash
# Backend
cd backend
pip install -r requirements.txt

# Voice Gateway
cd ../voice_gateway
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

**2️⃣ Start Services**

```powershell
# Terminal 1: Redis (Docker)
docker run -d -p 6379:6379 redis:alpine

# Terminal 2: Backend
cd backend
python main.py

# Terminal 3: Voice Gateway
cd voice_gateway
python voice_gateway.py

# Terminal 4: Frontend
cd frontend
npm run dev

# Terminal 5: Cloudflare Tunnel
cloudflared tunnel --url http://localhost:8001
```

### 🔗 Cloudflare Tunnel Setup

```bash
# Get tunnel URL (changes on each restart)
# Look for: "Your quick Tunnel has been created! Visit it at:"
# https://xxx.trycloudflare.com

# Update .env with new URL
VOICE_GATEWAY_URL=https://xxx.trycloudflare.com
```

## 📖 Usage

### 🎯 Creating AI Agents

Agents define the AI's personality, conversation style, and business context.

**Via Dashboard:**

1. Navigate to "Agent Settings" in sidebar
2. Fill in agent details:
   - **Name**: e.g., "Sales Assistant"
   - **Business Type**: Select from dropdown (pre-fills prompt template)
   - **Greeting**: Opening line for calls
   - **Business Description**: What your company does
   - **System Prompt**: Full AI instructions (auto-populated)
3. Configure voice settings (optional):
   - VAD sensitivity
   - Silence thresholds
   - Echo protection timing
4. Save agent

**Via API:**

```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Demo Agent",
    "prompt_text": "You are Alex, a sales representative for RelayX...",
    "template_source": "sales",
    "voice_settings": {
      "vad_mode": 2,
      "silence_threshold_ms": 450,
      "echo_ignore_ms": 1000
    },
    "llm_model": "llama-3.3-70b-versatile",
    "temperature": 0.7,
    "max_tokens": 200,
    "is_active": true
  }'
```

### 📞 Making Calls

**Single Call (Dashboard):**

1. Go to "Campaigns" → "Start New Campaign"
2. Select agent from dropdown
3. Enter single phone number in E.164 format: `+917278082005`
4. Click "Start Campaign"
5. Monitor call progress in real-time

**Bulk Campaign (CSV Upload):**

1. Prepare CSV file with columns: `name,phone,email` (optional)
2. Upload via "Upload Contacts" button
3. Select agent and start campaign
4. Calls are queued and executed sequentially

**Via API:**

```bash
# Single call
curl -X POST http://localhost:8000/calls/outbound \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "uuid-here",
    "to_number": "+917278082005"
  }'

# Bulk campaign
curl -X POST http://localhost:8000/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Outreach Q1",
    "agent_id": "uuid-here",
    "contact_ids": ["uuid1", "uuid2", "uuid3"],
    "schedule_type": "immediate",
    "concurrent_calls": 1
  }'
```

### 📊 Analytics & Monitoring

**Dashboard Views:**

- **Campaign Dashboard**: Overall stats, call outcomes, success rates
- **Call Analytics**: Individual call details, transcripts, duration
- **Agent Performance**: Calls per agent, avg duration, outcomes

**API Endpoints:**

```bash
# Get call details
curl http://localhost:8000/calls/{call_id}

# Get full transcript
curl http://localhost:8000/calls/{call_id}/transcripts

# Get AI analysis
curl http://localhost:8000/calls/{call_id}/analysis

# Campaign stats
curl http://localhost:8000/campaigns/{campaign_id}/stats
```

### 🔧 Configuration Options

**Voice Settings (per agent):**

```json
{
  "vad_mode": 2,                    // WebRTC VAD aggressiveness (0-3)
  "silence_threshold_ms": 450,      // Silence to trigger speech_end
  "min_audio_duration_ms": 400,     // Minimum audio to process
  "min_speech_energy": 30,          // Energy threshold for speech
  "echo_ignore_ms": 1000,           // Echo protection window
  "speech_start_ms": 180,           // Frames for speech start (6 frames * 30ms)
  "speech_end_ms": 240              // Frames for speech end (8 frames * 30ms)
}
```

**Language Support:**

System automatically detects language in first exchange:
- English: Natural conversation
- Hindi: Modern conversational (Hindi + English tech terms)
- Marathi: Modern conversational (Marathi + English tech terms)

**Example modern style:**
- ✅ "AI se aap apne calls automate kar sakte hain"
- ❌ "कृत्रिम बुद्धिमत्ता से आप अपनी कॉल स्वचालित कर सकते हैं"

## 🔌 API Reference

### Agents

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/agents` | Create new agent |
| GET | `/agents` | List all agents |
| GET | `/agents/{id}` | Get agent details |
| PATCH | `/agents/{id}` | Update agent |

### Calls

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/calls/outbound` | Initiate outbound call |
| GET | `/calls` | List calls (filter by agent_id, status) |
| GET | `/calls/{id}` | Get call details |
| GET | `/calls/{id}/transcripts` | Get full conversation |
| GET | `/stats` | Dashboard statistics |
| GET | `/api-credits` | API usage tracking |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Detailed health status |
| GET | `/dashboard` | Web dashboard UI |
| GET | `/docs` | Interactive API docs |

## 🛠️ Tech Stack

### Backend & Infrastructure
- **FastAPI** - High-performance async API framework
- **Uvicorn** - ASGI server with auto-reload
- **Supabase (PostgreSQL)** - Database with Row Level Security
- **Redis** - Agent config caching and session management
- **Docker** - Containerized deployment
- **Cloudflare Tunnel** - Secure public tunnel for voice gateway

### AI & ML
- **Groq API** - Ultra-fast LLM inference
  - Model: Llama 3.3 70B Versatile
  - Latency: ~360ms per response
  - Free tier: 14,400 requests/day
- **Sarvam AI** - Indian language STT/TTS
  - STT: Saarika v2.5 (Hindi/Marathi/English)
  - TTS: Bulbul v2 (Manisha voice)
  - Optimized for Indian accents

### Voice Processing
- **Twilio Media Streams** - WebSocket audio streaming (8kHz mulaw)
- **Hybrid VAD** - WebRTC VAD Mode 2 + Silero VAD
  - Silero: CPU-only, 5MB model, 50-100MB RAM
  - Chunk size: 512 samples (32ms at 16kHz)
  - Speech threshold: 0.4 probability
- **Streaming TTS** - Parallel sentence generation
  - First sentence: ~400ms
  - Remaining: Generated in background
  - 600ms faster response time
- **Echo Protection** - 1000ms window after TTS completion

### Frontend
- **React 18** - Modern UI with hooks
- **TypeScript** - Type-safe development
- **Vite** - Lightning-fast dev server
- **Tailwind CSS** - Utility-first styling
- **React Router** - Client-side routing
- **Lucide Icons** - Beautiful icon library

### Database Schema

```sql
-- Core Tables
agents              -- AI agent configurations
calls               -- Call metadata and status
transcripts         -- Full conversation history
campaigns           -- Bulk calling campaigns
contacts            -- Phone numbers and metadata
call_analysis       -- AI-generated summaries
knowledge_base      -- RAG context for agents
users               -- Authentication and user management

-- Key Features
- Row Level Security (RLS) enabled
- Foreign key constraints
- Indexes on frequently queried columns
- Timestamps (created_at, updated_at)
```

## 📁 Project Structure

```
RelayX/
├── backend/                           # FastAPI backend server
│   ├── main.py                        # Main API entry point
│   ├── admin_routes.py                # Admin panel routes
│   ├── agent_routes.py                # Agent CRUD operations
│   ├── auth_routes.py                 # Authentication & user management
│   ├── call_routes.py                 # Call initiation & tracking
│   ├── campaign_routes.py             # Bulk calling campaigns
│   ├── contact_routes.py              # Contact management
│   ├── analytics_routes.py            # Analytics & reporting
│   ├── knowledge_routes.py            # RAG knowledge base
│   ├── campaign_executor.py           # Campaign execution engine
│   ├── scheduler.py                   # Background task scheduler
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile                     # Backend container config
│   └── static/
│       └── admin.html                 # Admin dashboard
│
├── voice_gateway/                     # Real-time voice WebSocket handler
│   ├── voice_gateway.py               # Main WebSocket server (2611 lines)
│   │   ├── Hybrid VAD (WebRTC + Silero)
│   │   ├── Streaming TTS pipeline
│   │   ├── Language detection & switching
│   │   ├── Barge-in support
│   │   ├── Echo protection (1000ms)
│   │   └── Redis caching
│   ├── requirements.txt
│   └── Dockerfile
│
├── shared/                            # Shared modules across services
│   ├── database.py                    # Supabase client wrapper
│   ├── llm_client.py                  # Groq LLM integration
│   ├── stt_client.py                  # Sarvam AI STT client
│   ├── tts_client.py                  # Sarvam AI TTS client (132 lines)
│   │   ├── generate_speech_bytes()    # Single sentence generation
│   │   └── generate_speech_streaming()# Multi-sentence streaming
│   └── cache_client.py                # Redis caching utilities
│
├── frontend/                          # React TypeScript frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx          # Campaign dashboard
│   │   │   ├── AgentSettings.tsx      # Agent configuration
│   │   │   ├── CallAnalytics.tsx      # Call analytics
│   │   │   └── ContactManager.tsx     # Contact management
│   │   ├── components/
│   │   │   ├── Navbar.tsx             # Navigation bar
│   │   │   └── Sidebar.tsx            # Sidebar navigation
│   │   ├── config.ts                  # API configuration
│   │   └── main.tsx                   # App entry point
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── nginx.conf                     # Production server config
│
├── db/                                # Database schema & migrations
│   ├── schema.sql                     # Initial database schema
│   └── migrations/
│       ├── 001_agents.sql
│       ├── 002_calls.sql
│       ├── 003_system_prompts.sql
│       └── ...
│
├── scripts/                           # Utility scripts
│   ├── create_demo_agent.py
│   ├── update_agent.py
│   └── check_calls.py
│
├── docker-compose.yml                 # Multi-container orchestration
├── .env                               # Environment configuration
├── requirements.txt                   # Root Python dependencies
└── README.md                          # This file
```

### Key Files Deep Dive

**voice_gateway/voice_gateway.py** (2611 lines)
- Lines 1-200: Imports, configuration, global state
- Lines 201-330: Configuration constants (VAD, timeouts, thresholds)
- Lines 331-620: CallSession class (state management)
- Lines 621-850: VAD and speech detection methods
- Lines 851-1600: WebSocket connection and stream handling
- Lines 1601-2030: Language detection and greeting generation
- Lines 2031-2320: User speech processing pipeline
- Lines 2321-2611: AI response with streaming TTS

**shared/tts_client.py** (132 lines)
- Lines 1-87: Single sentence TTS generation
- Lines 88-132: Streaming TTS with sentence splitting

**backend/campaign_executor.py** (500+ lines)
- Campaign queue management
- Concurrent call execution
- Retry logic and error handling
- Progress tracking

**frontend/src/pages/AgentSettings.tsx** (1200+ lines)
- Business type templates
- Voice settings presets
- System prompt builder
- Agent CRUD operations

## 🐛 Troubleshooting

### Voice Gateway Not Starting

```bash
# Check logs
docker logs relayx-voice-gateway --tail 50

# Common issues:
# - Port 8001 already in use
# - Missing environment variables
# - Redis connection failed

# Solution: Restart services
docker-compose down
docker-compose up -d
```

### AI Not Responding / Stuck

**Symptoms**: Call connects but AI doesn't speak

**Causes & Solutions**:

1. **Missing re module import** (v1.2 fixed)
   - Check logs for: `name 're' is not defined`
   - Solution: Already fixed in v1.2

2. **TTS generation error**
   - Check logs for: `Error in send_ai_response_with_bargein`
   - Verify Sarvam API key is valid

3. **Echo detection triggering too early**
   - If AI responds immediately after speaking (echoing itself)
   - Fixed in v1.2 with 1000ms echo protection window

### Call Connects But Too Fast / Echoing

**Problem**: AI responds before user can speak, or responds to its own voice

**Solution** (already implemented in v1.2):
- Echo protection increased to 1000ms
- VAD ignores audio for 1 second after AI finishes speaking
- Check logs for: `🔇 Echo protection window started (1000ms)`

### Language Detection Failing

**Problem**: AI asks for language preference multiple times

**Causes**:
- STT mishears language selection
- Common: "Hindi" → "Idea", "Hello"

**Solution**:
- System automatically retries (2 attempts)
- User can speak clearly: "English", "Hindi", "Marathi"
- Check transcript logs for STT output

### Slow Response Time

**Expected latency**: 1.1-1.5s from user stops speaking to AI starts

**Breakdown**:
- STT: 350ms
- LLM: 360ms  
- First TTS: 400ms
- **Total: ~1.1s**

**If slower**:
1. Check Groq API status
2. Check Sarvam AI status
3. Verify internet connection
4. Check logs for timeout warnings

### Cloudflare Tunnel Issues

```bash
# Tunnel URL changes on restart
# Always update .env after container restart

# Get new URL from logs:
docker logs relayx-voice-gateway | grep "trycloudflare.com"

# Update environment:
VOICE_GATEWAY_URL=https://new-url.trycloudflare.com

# Restart backend to pick up new URL:
docker-compose restart backend
```

### Twilio Call Fails

**Common issues**:

1. **Trial account limitations**
   - Add $1+ credit to remove trial restrictions
   - Verify recipient phone number in Twilio console

2. **Invalid phone number format**
   - Must be E.164 format: `+917278082005`
   - Include country code

3. **Voice Gateway URL not reachable**
   - Verify Cloudflare tunnel is running
   - Test: `curl https://your-url.trycloudflare.com/health`

4. **TwiML errors**
   - Check logs for: `TwiML requested for call:`
   - Verify WebSocket URL is correct

### Database Connection Failed

```bash
# Check Supabase credentials in .env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Test connection:
curl $SUPABASE_URL/rest/v1/agents \
  -H "apikey: $SUPABASE_ANON_KEY"
```

### Redis Connection Error

```bash
# Check if Redis is running
docker ps | grep redis

# Restart Redis
docker-compose restart redis

# Test connection
docker exec -it relayx-redis redis-cli ping
# Should return: PONG
```

### Modern Language Style Not Working

**Problem**: AI speaks pure Hindi/Marathi instead of modern mixed style

**Expected style**:
- ✅ "AI se aap calls automate kar sakte hain"
- ❌ "कृत्रिम बुद्धिमत्ता से आप कॉल स्वचालित कर सकते हैं"

**Solution** (implemented in v1.2):
- Language instructions updated with modern conversational style
- AI mixes Hindi/Marathi with English technical terms
- Check logs for language instruction being set

## 🚧 Roadmap & Version History

### v1.2 STABLE ✅ (Current - Feb 2026)
- ✅ Streaming TTS with parallel sentence generation (600ms faster)
- ✅ Echo protection increased to 1000ms (prevents self-echo)
- ✅ Modern conversational Hindi/Marathi (mixed with English tech terms)
- ✅ Bug fix: Missing `re` module import
- ✅ First sentence plays at ~1.1s (vs 1.7s in v1.1)

### v1.1 STABLE (Jan 2026)
- ✅ Silero VAD integration (CPU-only, 5MB model)
- ✅ Hybrid VAD (WebRTC + Silero) for accurate speech detection
- ✅ Reduced silence thresholds (300-600ms based on call stage)
- ✅ Groq Llama-3.3-70b model upgrade
- ✅ Improved endpointing and VAD accuracy

### v1.0 (Initial Release - 2025)
- ✅ Core outbound calling with Twilio
- ✅ Real-time STT/LLM/TTS pipeline
- ✅ Sarvam AI STT/TTS integration
- ✅ React + TypeScript dashboard
- ✅ Campaign management
- ✅ Docker deployment
- ✅ Supabase database

### 🔮 Upcoming Features

**v1.3 (Planned)**
- [ ] WebRTC direct audio streaming (bypass Twilio for lower latency)
- [ ] Voice cloning with ElevenLabs integration
- [ ] Real-time barge-in improvement (interrupt detection)
- [ ] Call recording storage (S3/Supabase)
- [ ] Webhook notifications (Slack, Discord, Email)

**v2.0 (Future)**
- [ ] Inbound call handling
- [ ] Multi-agent handoff (transfer between agents)
- [ ] Advanced analytics dashboard (sentiment analysis, success metrics)
- [ ] Voice biometrics (speaker identification)
- [ ] Multi-language expansion (50+ languages via Sarvam/ElevenLabs)
- [ ] Custom voice training (fine-tuned TTS models)
- [ ] Integration marketplace (CRM, helpdesk, calendars)
- [ ] White-label deployment option

**Infrastructure Improvements**
- [ ] Kubernetes deployment manifests
- [ ] Horizontal scaling with load balancing
- [ ] Multi-region deployment
- [ ] CDN for audio assets
- [ ] GraphQL API option
- [ ] WebSocket-based real-time dashboard updates

## 💡 Performance Optimization

### Current Performance Metrics (v1.2)

**Response Latency Breakdown:**

```
User stops speaking
    ↓
STT Processing.................. 349ms   (Sarvam AI Saarika v2.5)
    ↓
LLM Inference................... 358ms   (Groq Llama-3.3-70b)
    ↓
First Sentence TTS.............. 400ms   (Sarvam AI Bulbul v2)
    ↓
AI starts speaking.............. ~1.1s TOTAL ✅

Remaining sentences generate in parallel (non-blocking)
```

**v1.1 vs v1.2 Comparison:**

| Metric | v1.1 | v1.2 | Improvement |
|--------|------|------|-------------|
| First audio playback | 1.7s | 1.1s | **600ms faster** |
| TTS strategy | Sequential | Parallel | 40% improvement |
| Echo protection | 300ms | 1000ms | More reliable |
| Language style | Formal | Modern mixed | More natural |

**Optimization Techniques Used:**

1. **Streaming TTS** - Generate first sentence immediately, rest in parallel
2. **Redis Caching** - Agent configs cached to avoid DB queries
3. **Hybrid VAD** - Silero + WebRTC for accurate speech detection
4. **Parallel Processing** - TTS sentences generated concurrently
5. **Echo Protection** - 1s window prevents false triggers

### System Requirements

**Minimum (Development):**
- CPU: 4 cores
- RAM: 4GB
- Storage: 2GB
- Network: 10 Mbps

**Recommended (Production):**
- CPU: 8 cores
- RAM: 8GB
- Storage: 20GB (for logs and audio cache)
- Network: 50 Mbps

**Silero VAD Resource Usage:**
- Model size: 5MB (ONNX)
- RAM: 50-100MB during inference
- CPU: Minimal overhead (~5% per active call)

### Scaling Considerations

**Current Limits:**
- **Single server**: 10-20 concurrent calls
- **Bottleneck**: TTS generation (CPU-bound)
- **Network**: 8 kbps per call (Twilio mulaw)

**Horizontal Scaling:**
1. Deploy multiple voice gateway instances
2. Load balance via Twilio webhook URL rotation
3. Shared Redis for agent configs
4. Shared Supabase database

**Cost Estimates (per 1000 calls):**

| Service | Cost | Notes |
|---------|------|-------|
| Twilio | $0.85 - $1.70 | $0.0085 per minute outbound |
| Groq API | Free | 14,400 requests/day free tier |
| Sarvam AI | Varies | Check pricing at sarvam.ai |
| Supabase | Free | Up to 500MB database |
| Server | $10-50 | DigitalOcean/AWS/GCP |

## 🔒 Security & Privacy

### Data Handling

**Call Recordings:**
- Audio is NOT stored by default
- Transcripts stored in Supabase (encrypted at rest)
- Can enable S3 recording storage (optional)

**PII Protection:**
- Phone numbers hashed in logs
- Transcripts can be auto-redacted (future feature)
- Row Level Security (RLS) in Supabase

**API Keys:**
- Stored in environment variables
- Never logged or exposed
- Rotated regularly (best practice)

### Compliance

**GDPR:**
- Right to erasure: Delete call records and transcripts
- Data portability: Export call data via API
- Consent: Inform users calls are AI-powered

**HIPAA:**
- Not currently HIPAA-compliant
- Can be configured with BAA from Twilio/Supabase
- Additional audit logging required

**TCPA (US):**
- Respect Do Not Call lists
- Obtain consent before calling
- Provide opt-out mechanism

## 🤝 Contributing

Contributions are welcome! This is an active project under continuous development.

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/RelayX.git
   cd RelayX
   ```

2. **Create feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Setup development environment**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   cd frontend && npm install
   
   # Copy example env
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Make your changes**
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed

5. **Test your changes**
   ```bash
   # Backend tests (if available)
   pytest backend/tests/
   
   # Frontend tests
   cd frontend && npm test
   
   # Manual testing
   docker-compose up -d
   # Make test calls and verify behavior
   ```

6. **Commit and push**
   ```bash
   git add .
   git commit -m 'feat: Add amazing feature'
   git push origin feature/amazing-feature
   ```

7. **Open Pull Request**
   - Describe what your PR does
   - Link any related issues
   - Add screenshots/videos if UI changes

### Code Guidelines

**Python (Backend/Voice Gateway):**
- Use type hints
- Follow PEP 8 style guide
- Add docstrings to functions
- Use async/await for I/O operations

**TypeScript (Frontend):**
- Use functional components with hooks
- TypeScript strict mode
- Tailwind CSS for styling
- Component-based architecture

**Commit Messages:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Build/tooling changes

### Areas for Contribution

**High Priority:**
- 🐛 Bug fixes and stability improvements
- 📖 Documentation improvements
- 🧪 Test coverage (unit/integration/e2e)
- ♿ Accessibility improvements
- 🌍 Internationalization

**Feature Requests:**
- 📞 Inbound call handling
- 🎤 More TTS provider integrations
- 📊 Advanced analytics dashboards
- 🔌 Integration with CRMs (Salesforce, HubSpot)
- 🤖 Multi-agent workflows

**Performance:**
- ⚡ Latency optimization
- 🔄 Load testing and benchmarking
- 📈 Horizontal scaling strategies

## 🙏 Acknowledgments

### Core Technologies
- **[Twilio](https://twilio.com)** - Telephony infrastructure & Media Streams API
- **[Supabase](https://supabase.com)** - PostgreSQL database platform with real-time features
- **[Groq](https://groq.com)** - Ultra-fast LLM inference infrastructure
- **[Sarvam AI](https://sarvam.ai)** - Indian language STT/TTS optimized for regional accents
- **[Meta](https://ai.meta.com)** - Llama 3.3 language model (Apache 2.0 license)
- **[Silero VAD](https://github.com/snakers4/silero-vad)** - High-quality Voice Activity Detection

### Open Source Libraries
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[React](https://react.dev/)** - UI library for building interfaces
- **[Redis](https://redis.io/)** - In-memory data structure store
- **[Docker](https://docker.com)** - Container platform

### Community
- Thanks to all contributors who help improve RelayX
- Special thanks to early testers providing valuable feedback
- Inspired by production voice AI systems from Bland AI, Vapi, and Synthflow

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

**Commercial Use Allowed** - You can use RelayX for commercial projects.

**Attribution Required** - Keep the attribution in the README when redistributing.

## 📞 Support & Contact

### Getting Help

1. **Documentation**: Start with this README and `/docs` folder
2. **Issues**: [GitHub Issues](https://github.com/yourusername/RelayX/issues)
3. **Discussions**: [GitHub Discussions](https://github.com/yourusername/RelayX/discussions)

### Reporting Bugs

Please include:
- Operating system and version
- Docker version (if using containers)
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs (sanitize sensitive data)

### Feature Requests

Open an issue with:
- Clear description of the feature
- Use case and motivation
- Potential implementation approach (optional)

---

<div align="center">

**Built with ❤️ for developers who need production-ready AI voice calls**

⭐ Star us on GitHub if you find this useful!

[Report Bug](https://github.com/yourusername/RelayX/issues) • [Request Feature](https://github.com/yourusername/RelayX/discussions) • [Documentation](https://github.com/yourusername/RelayX/wiki)

**v1.2 STABLE** - Streaming TTS, Modern Language Style, Echo Protection

</div>

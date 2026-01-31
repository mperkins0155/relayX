# RelayX - AI-Powered Voice Calling Platform 🚀

## 🎯 Overview

RelayX is an intelligent voice calling platform that automates business communications using AI. It enables businesses to make thousands of personalized voice calls simultaneously, leveraging advanced AI for natural conversations, appointment scheduling, and lead qualification.

**Problem it solves:**
- Manual calling is time-consuming and expensive
- Businesses lose customers due to delayed follow-ups
- Limited scalability with human agents
- Inconsistent call quality and messaging

**Solution:**
RelayX provides an AI agent that makes hyper-personalized calls at scale, understands context from your knowledge base, schedules appointments automatically, and handles conversations naturally in multiple Indian languages.

---

## 💡 The Idea

RelayX transforms business outreach by:
- **AI Voice Agents**: Natural-sounding AI that speaks like a real person
- **Bulk Campaigns**: Launch 1000s of calls with a single CSV upload
- **Smart Scheduling**: Integrated with Calendly for seamless appointment booking
- **Multi-Language Support**: Supports Hindi, English, and other Indian languages via Sarvam AI
- **Knowledge Base**: AI learns from your documents to answer customer questions
- **Real-time Analytics**: Track call performance, sentiment, and outcomes

---

## 🛠️ Technology Stack

### Frontend
- **React 18** + **TypeScript** - Modern UI framework
- **Vite** - Lightning-fast build tool
- **TailwindCSS** - Utility-first styling
- **shadcn/ui** - Beautiful component library
- **Framer Motion** - Smooth animations
- **React Router** - Client-side routing

### Backend
- **FastAPI** - High-performance Python API framework
- **PostgreSQL** (Supabase) - Scalable database
- **Twilio** - Voice calling infrastructure
- **Groq LLM** - Ultra-fast AI inference
- **Sarvam AI** - Indian language TTS/STT
- **WebRTC VAD** - Voice activity detection

### Infrastructure
- **Vercel** - Frontend hosting
- **Railway** - Backend deployment
- **Supabase** - Database & authentication

### AI & ML
- **LangChain** - RAG pipeline for knowledge base
- **ChromaDB** - Vector database for embeddings
- **Groq (Llama 3)** - Fast LLM for conversations
- **Sarvam Bulbul** - Indian language TTS
- **Sarvam Saarika** - Indian language STT

---

## 🎥 Product Demo

**🔗 Live App:** [https://relayx-wine.vercel.app](https://relayx-wine.vercel.app)

**🔗 Backend API:** [https://api.relayx.tech/health](https://api.relayx.tech/health)

**Test Credentials:**
- Email: `test@relayx.ai`
- Password: `test123`

### Key Features to Try:
1. **Dashboard**: View analytics and call stats
2. **AI Agent**: Configure your voice agent personality and knowledge base
3. **Campaigns**: Upload CSV and launch bulk calling campaigns
4. **Contacts**: Manage your contact database
5. **Test Call**: Make a test call to see AI in action

---

## 📊 Key Features

### 1. AI Voice Agent Configuration
- Customize agent name, role, and personality
- Upload knowledge base documents (PDF, TXT, DOCX)
- Set conversation goals and guardrails
- Configure voice settings and language

### 2. Bulk Campaign Management
- Upload contacts via CSV
- Schedule campaigns for optimal timing
- A/B test different scripts
- Track campaign performance in real-time

### 3. Intelligent Call Handling
- Natural conversation flow with context awareness
- Automatic appointment scheduling via Calendly
- Lead qualification and scoring
- Sentiment analysis during calls

### 4. Analytics Dashboard
- Call volume and success rates
- Average call duration
- Sentiment trends
- Conversion metrics
- Cost per successful call

### 5. Multi-Language Support
- English and Hindi natively supported
- Additional Indian languages via Sarvam AI
- Automatic language detection
- Code-mixing support (Hinglish)

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend    │────▶│  Database   │
│  (Vercel)   │     │  (Railway)   │     │ (Supabase)  │
└─────────────┘     └──────────────┘     └─────────────┘
                            │
                    ┌───────┴───────┐
                    ▼               ▼
            ┌──────────────┐ ┌─────────────┐
            │ Voice Gateway│ │   Groq LLM  │
            │   (Twilio)   │ │  (AI Brain) │
            └──────────────┘ └─────────────┘
                    │
                    ▼
            ┌──────────────┐
            │  Sarvam AI   │
            │  (TTS/STT)   │
            └──────────────┘
```

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL (or Supabase account)
- Twilio account
- Groq API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Gauravguddeti/relayX.git
cd relayX
```

2. **Setup Frontend**
```bash
cd frontend
npm install
npm run dev
```

3. **Setup Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

4. **Configure Environment Variables**
See `.env.example` files in both frontend and backend directories.

---

## 📱 Use Cases

- **Lead Generation**: Qualify leads at scale before human handoff
- **Appointment Scheduling**: Book meetings automatically with AI
- **Customer Support**: Handle routine inquiries 24/7
- **Surveys & Feedback**: Collect feedback through voice calls
- **Payment Reminders**: Automated payment follow-ups
- **Event Registrations**: Register attendees via phone

---

## 🎯 Pricing

- **Starter**: ₹499/month - 100 calls/month
- **Pay As You Go**: ₹8/call - No monthly commitment
- **Enterprise**: Custom pricing for high-volume users

---

## 📧 Contact

For inquiries: [Contact through the platform](https://relayx-wine.vercel.app)

---

**Made with ❤️ for businesses that want to scale their communication**

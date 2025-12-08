"""
Voice Gateway for RelayX AI Caller
Handles Twilio Gather with Partial Results for real-time speech recognition
Real-time pipeline: Speech → Twilio STT (partial) → LLM → TTS → Audio
"""
from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import sys
import os
from loguru import logger
from datetime import datetime
from typing import Optional

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from shared.database import get_db, SupabaseDB
from shared.llm_client import get_llm_client, LLMClient
from shared.tts_client import get_tts_client, TTSClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logger
logger.add("logs/voice_gateway.log", rotation="1 day", retention="7 days", level="INFO")

# Initialize FastAPI
app = FastAPI(
    title="RelayX Voice Gateway",
    description="Twilio Gather with Partial Results handler for AI voice calls",
    version="2.0.0"
)

# Add CORS middleware to allow dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Call sessions storage
active_sessions = {}


class CallSession:
    """Manages state for an active call using Gather with partial results"""
    
    def __init__(self, call_id: str, agent_id: str):
        self.call_id = call_id
        self.agent_id = agent_id
        self.is_speaking = False  # AI is currently speaking
        self.conversation_history = []
        self.agent_config = None  # type: ignore
        self.partial_transcript = ""  # Current partial transcript
        self.user_is_speaking = False  # User is currently speaking
        self.last_activity = datetime.now()
        self.created_at = datetime.now()
        self.current_audio_url = None  # URL of currently playing audio
        
        logger.info(f"CallSession created: {call_id}")


# ==================== TWIML ENDPOINTS ====================

@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "RelayX Voice Gateway",
        "status": "running",
        "active_calls": len(active_sessions)
    }


@app.get("/info")
async def get_info():
    """Get gateway info including ngrok URL"""
    effective_url = os.getenv("VOICE_GATEWAY_URL") or ngrok_public_url or "not configured"
    return {
        "service": "RelayX Voice Gateway",
        "status": "running",
        "active_calls": len(active_sessions),
        "ngrok_url": effective_url,
        "port": int(os.getenv("VOICE_GATEWAY_PORT", 8001))
    }


@app.post("/twiml/{call_id}")
async def twiml_handler(call_id: str, request: Request):
    """
    Generate TwiML with Gather and partial results for fast speech recognition
    This enables real-time transcription and instant interruption handling
    """
    try:
        logger.info(f"TwiML requested for call: {call_id}")
        
        # Get call details from database
        db = get_db()
        call = await db.get_call(call_id)
        
        if not call:
            logger.error(f"Call {call_id} not found in database")
            return Response(content="<Response><Say>Call not found</Say></Response>", media_type="application/xml")
        
        # Get agent details
        agent = await db.get_agent(call["agent_id"])
        if not agent:
            logger.error(f"Agent {call['agent_id']} not found")
            return Response(content="<Response><Say>Agent not found</Say></Response>", media_type="application/xml")
        
        # Create session
        session = CallSession(call_id, agent["id"])
        session.agent_config = agent
        active_sessions[call_id] = session
        
        # Update call status
        await db.update_call(call_id, status="in-progress", started_at=datetime.now())
        logger.info(f"Call {call_id} status updated to in-progress")
        
        # Get base URL for callbacks
        base_url = os.getenv("VOICE_GATEWAY_URL") or ngrok_public_url
        if not base_url or base_url.startswith("https://your-"):
            logger.error("Voice Gateway URL not configured properly")
            return Response(
                content="<Response><Say>Configuration error</Say></Response>",
                media_type="application/xml"
            )
        
        # Generate initial greeting
        llm = get_llm_client()
        
        GREETING_PROMPT = """SYSTEM OVERRIDE (HIGHEST PRIORITY):
You must follow all safety guidelines. Refuse harmful, illegal, or abusive requests.
Never share private information. Stay professional and helpful.

IMPORTANT: Output ONLY the exact words you will speak. NO meta-commentary, NO quotes, NO explanations like "Here's my opening line". Just speak naturally.

OUTBOUND CALL BEHAVIOR:
- This is an OUTBOUND call - YOU called THEM
- Introduce yourself briefly and ask if they have a moment
- Keep it SHORT (1-2 sentences max)
- Sound natural and friendly

VOICE FORMATTING RULES (CRITICAL FOR TTS):
- NEVER write times as digits like "12:00" - say "twelve PM" or "noon"
- NEVER write "24/7" - say "twenty four seven"
- Write numbers as words for better pronunciation

Examples (output like these, NO quotes):
Hi! This is Emma from TechCorp. I wanted to reach out about your recent inquiry. Do you have a quick moment?
Hello! This is Mark with ABC Services. I'm following up on your interest. Is now a good time?"""
        
        base_prompt = agent.get("resolved_system_prompt") or agent.get("system_prompt", "You are a helpful AI assistant.")
        system_prompt = f"{GREETING_PROMPT}\n\n{base_prompt}"
        
        greeting = await llm.generate_response(
            messages=[{"role": "user", "content": "Say your opening line now."}],
            system_prompt=system_prompt,
            temperature=agent.get("temperature", 0.7),
            max_tokens=60
        )
        
        # Clean meta-commentary
        import re
        if any(word in greeting.lower() for word in ['here', 'opening', 'line:', 'say:', '"']):
            match = re.search(r'[""]([^""]+)[""]', greeting)
            if match:
                greeting = match.group(1)
            else:
                greeting = re.sub(r'^.*?(?:opening line|here|say)s?:?\s*', '', greeting, flags=re.IGNORECASE).strip().strip('"\'')
        
        logger.info(f"Generated greeting: {greeting}")
        
        # Save transcript
        await db.add_transcript(call_id, "assistant", greeting)
        
        # Generate TwiML with Gather and partial results
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>{greeting}</Say>
    <Gather 
        input="speech" 
        action="{base_url}/gather/{call_id}" 
        partialResultCallback="{base_url}/partial/{call_id}"
        partialResultCallbackMethod="POST"
        method="POST"
        speechTimeout="auto"
        speechModel="phone_call"
        enhanced="true"
        language="en-US">
    </Gather>
    <Redirect>{base_url}/twiml/{call_id}</Redirect>
</Response>"""
        
        logger.info(f"TwiML with Gather generated for {call_id}")
        return Response(content=twiml, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error generating TwiML for {call_id}: {e}", exc_info=True)
        return Response(
            content="<Response><Say>Sorry, there was an error</Say></Response>",
            media_type="application/xml"
        )


@app.post("/partial/{call_id}")
async def partial_result_handler(call_id: str, request: Request):
    """
    Handle partial speech results from Twilio Gather
    This fires as the user is speaking, enabling real-time interruption
    """
    try:
        form_data = await request.form()
        unstable_speech = str(form_data.get("UnstableSpeechResult", ""))
        stability = str(form_data.get("Stability", "0.0"))
        
        logger.info(f"📝 Partial result for {call_id}: '{unstable_speech}' (stability: {stability})")
        
        # Get session
        session = active_sessions.get(call_id)
        if not session:
            logger.warning(f"No session found for {call_id} in partial handler")
            return Response(content="", media_type="text/plain")
        
        # Update partial transcript
        session.partial_transcript = unstable_speech
        session.user_is_speaking = True
        session.last_activity = datetime.now()
        
        # If AI is speaking and user starts talking, interrupt AI
        if session.is_speaking and unstable_speech and len(unstable_speech.split()) >= 2:
            logger.info(f"🛑 User interruption detected! Partial: '{unstable_speech}'")
            session.is_speaking = False  # Stop AI playback
            # Twilio will handle stopping the audio automatically
        
        return Response(content="", media_type="text/plain")
        
    except Exception as e:
        logger.error(f"Error in partial result handler for {call_id}: {e}", exc_info=True)
        return Response(content="", media_type="text/plain")


@app.post("/gather/{call_id}")
async def gather_result_handler(call_id: str, request: Request):
    """
    Handle final speech result from Twilio Gather
    This fires when user stops speaking (speech timeout reached)
    Process the complete utterance and generate AI response
    """
    try:
        form_data = await request.form()
        speech_result = str(form_data.get("SpeechResult", ""))
        confidence = str(form_data.get("Confidence", "0.0"))
        
        logger.info(f"🎤 Final speech for {call_id}: '{speech_result}' (confidence: {confidence})")
        
        # Get session
        session = active_sessions.get(call_id)
        if not session:
            logger.warning(f"No session found for {call_id}")
            return Response(
                content="<Response><Say>Session expired</Say><Hangup/></Response>",
                media_type="application/xml"
            )
        
        session.user_is_speaking = False
        session.last_activity = datetime.now()
        
        # If no speech detected
        if not speech_result or speech_result.strip() == "":
            logger.info(f"No speech detected for {call_id}, prompting user")
            
            base_url = os.getenv("VOICE_GATEWAY_URL") or ngrok_public_url
            
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>I didn't catch that. Are you still there?</Say>
    <Gather 
        input="speech" 
        action="{base_url}/gather/{call_id}" 
        partialResultCallback="{base_url}/partial/{call_id}"
        partialResultCallbackMethod="POST"
        method="POST"
        speechTimeout="auto"
        speechModel="phone_call"
        enhanced="true"
        language="en-US">
    </Gather>
    <Say>I'm having trouble hearing you. Goodbye!</Say>
    <Hangup/>
</Response>"""
            return Response(content=twiml, media_type="application/xml")
        
        # Save user transcript
        db = get_db()
        await db.add_transcript(call_id, "user", speech_result)
        
        # Add to conversation history
        session.conversation_history.append({
            "role": "user",
            "content": speech_result
        })
        
        # Generate AI response
        llm = get_llm_client()
        agent = session.agent_config
        
        system_prompt = agent.get("resolved_system_prompt") or agent.get("system_prompt", "You are a helpful AI assistant.")
        
        # Add voice formatting instructions
        VOICE_INSTRUCTIONS = """
VOICE FORMATTING RULES (CRITICAL):
- NEVER write times as digits like "12:00" - say "twelve PM" or "noon"
- NEVER write "24/7" - say "twenty four seven"  
- Write numbers as words for better pronunciation
- Keep responses SHORT (1-3 sentences max)
- Sound natural and conversational
"""
        
        full_system_prompt = f"{system_prompt}\n\n{VOICE_INSTRUCTIONS}"
        
        ai_response = await llm.generate_response(
            messages=session.conversation_history,
            system_prompt=full_system_prompt,
            temperature=agent.get("temperature", 0.7),
            max_tokens=100
        )
        
        logger.info(f"🤖 AI response for {call_id}: {ai_response}")
        
        # Save AI transcript
        await db.add_transcript(call_id, "assistant", ai_response)
        
        # Add to conversation history
        session.conversation_history.append({
            "role": "assistant",
            "content": ai_response
        })
        
        # Set speaking flag
        session.is_speaking = True
        
        # Get base URL
        base_url = os.getenv("VOICE_GATEWAY_URL") or ngrok_public_url
        
        # Generate TwiML with AI response and next Gather
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>{ai_response}</Say>
    <Gather 
        input="speech" 
        action="{base_url}/gather/{call_id}" 
        partialResultCallback="{base_url}/partial/{call_id}"
        partialResultCallbackMethod="POST"
        method="POST"
        speechTimeout="auto"
        speechModel="phone_call"
        enhanced="true"
        language="en-US">
    </Gather>
    <Say>Are you still there?</Say>
    <Redirect>{base_url}/twiml/{call_id}</Redirect>
</Response>"""
        
        session.is_speaking = False
        
        return Response(content=twiml, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error in gather handler for {call_id}: {e}", exc_info=True)
        return Response(
            content="<Response><Say>Sorry, an error occurred</Say><Hangup/></Response>",
            media_type="application/xml"
        )


async def generate_call_analysis(call_id: str, db):
    """Generate AI-powered call analysis summary"""
    try:
        # Get transcripts
        transcripts = await db.get_transcripts(call_id)
        
        if not transcripts or len(transcripts) < 2:
            logger.info(f"Not enough transcript data for analysis: {call_id}")
            return
        
        # Build conversation text
        conversation_text = "\n".join([
            f"{t['speaker'].upper()}: {t['text']}" 
            for t in transcripts
        ])
        
        # Use LLM to analyze the call
        llm = get_llm_client()
        
        analysis_prompt = f"""Analyze this phone call conversation. Read the ENTIRE conversation carefully and provide accurate analysis.

CONVERSATION:
{conversation_text}

ANALYSIS INSTRUCTIONS:

1. SUMMARY: Write 2-3 sentences describing what happened in the call

2. KEY POINTS: List 2-4 main topics or important details discussed

3. USER SENTIMENT: This is CRITICAL - analyze the user's actual emotional state throughout the conversation.
   
   Look for these indicators:
   - POSITIVE: Words like "great", "perfect", "excellent", "love it", "sounds good", "thank you", enthusiasm, eagerness
   - NEGATIVE: Words like "frustrated", "confused", "problem", "issue", "disappointed", "not happy", complaints, resistance
   - NEUTRAL: Purely factual responses, business-like tone, no emotional indicators either way
   
   Pay attention to:
   - How they started vs how they ended (did sentiment improve or worsen?)
   - Their willingness to engage (eager questions vs reluctant answers?)
   - Their word choices (positive/negative language)
   - Overall tone (friendly vs cold, cooperative vs resistant)
   
   DO NOT default to neutral - only choose neutral if there are truly no emotional indicators.
   
   Choose the sentiment that BEST matches the conversation:
   - very_positive: User is enthusiastic, excited, multiple positive words, highly engaged
   - positive: User is friendly, cooperative, satisfied, helpful
   - neutral: User is purely factual/business-like with NO emotional indicators either way
   - negative: User shows frustration, annoyance, dissatisfaction, or reluctance
   - very_negative: User is angry, hostile, very upset, or openly hostile

4. OUTCOME: Based on the conversation result:
   - interested: User wants to proceed/book/buy
   - not_interested: User declined or not interested
   - call_later: User wants to be contacted later
   - needs_more_info: User needs more information before deciding
   - wrong_number: Wrong person or misunderstanding
   - other: Doesn't fit above categories

5. NEXT ACTION: Specific recommended follow-up step

Return ONLY valid JSON (no other text):
{{
  "summary": "",
  "key_points": [],
  "user_sentiment": "",
  "outcome": "",
  "next_action": ""
}}"""
        
        messages = [{"role": "user", "content": analysis_prompt}]
        response = await llm.generate_response(
            messages=messages,
            system_prompt="You are a call analysis assistant. Analyze conversations and provide structured insights.",
            temperature=0.3,
            max_tokens=300
        )
        
        # Parse JSON response
        import json
        try:
            analysis_data = json.loads(response)
        except:
            # Fallback if LLM doesn't return valid JSON
            logger.warning(f"Failed to parse LLM analysis as JSON for {call_id}")
            analysis_data = {
                "summary": response[:200],
                "key_points": ["Analysis failed to parse"],
                "user_sentiment": "neutral",
                "outcome": "other",
                "next_action": "Review transcript manually"
            }
        
        # Save analysis
        await db.save_call_analysis(
            call_id=call_id,
            summary=analysis_data.get("summary", ""),
            key_points=analysis_data.get("key_points", []),
            user_sentiment=analysis_data.get("user_sentiment", "neutral"),
            outcome=analysis_data.get("outcome", "other"),
            next_action=analysis_data.get("next_action", "")
        )
        
        logger.info(f"✅ Call analysis saved for {call_id}: {analysis_data.get('outcome')}")
        
    except Exception as e:
        logger.error(f"Error generating call analysis for {call_id}: {e}")


@app.post("/callbacks/status/{call_id}")
async def status_callback(call_id: str, request: Request):
    """
    Handle Twilio status callbacks
    Updates call status in database
    """
    try:
        form_data = await request.form()
        status = str(form_data.get("CallStatus", ""))
        call_sid = str(form_data.get("CallSid", ""))
        duration = str(form_data.get("CallDuration", ""))
        
        logger.info(f"Status callback for {call_id}: {status} | SID: {call_sid}")
        
        db = get_db()
        update_data: dict = {"status": status}  # type: ignore
        
        # Handle terminal states (call is done)
        if status in ["completed", "busy", "no-answer", "failed", "canceled"]:
            update_data["ended_at"] = datetime.now()  # type: ignore
            if duration:
                update_data["duration"] = int(duration)  # type: ignore
            
            # Only generate analysis for completed calls with conversation
            if status == "completed":
                try:
                    await generate_call_analysis(call_id, db)
                except Exception as analysis_error:
                    logger.error(f"Failed to generate call analysis for {call_id}: {analysis_error}")
        
        await db.update_call(call_id, **update_data)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error in status callback for {call_id}: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/callbacks/recording/{call_id}")
async def recording_callback(call_id: str, request: Request):
    """
    Handle Twilio recording callbacks
    Saves recording URL to database
    """
    try:
        form_data = await request.form()
        recording_url = str(form_data.get("RecordingUrl", ""))
        recording_sid = str(form_data.get("RecordingSid", ""))
        recording_duration = str(form_data.get("RecordingDuration", ""))
        
        logger.info(f"Recording callback for {call_id}: {recording_sid} | Duration: {recording_duration}s")
        
        if recording_url:
            db = get_db()
            # Twilio recording URL needs .mp3 appended for direct download
            full_recording_url = f"{recording_url}.mp3"
            
            update_data: dict = {  # type: ignore
                "recording_url": full_recording_url,
            }
            
            if recording_duration:
                update_data["recording_duration"] = int(recording_duration)  # type: ignore
            
            await db.update_call(call_id, **update_data)
            logger.info(f"✅ Recording URL saved for {call_id}: {full_recording_url}")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error in recording callback for {call_id}: {e}")
        return {"status": "error", "message": str(e)}


# ==================== STARTUP ====================

# Global ngrok URL storage
ngrok_public_url = None

@app.on_event("startup")
async def startup_event():
    """Initialize services and start ngrok tunnel"""
    global ngrok_public_url
    
    logger.info("Starting RelayX Voice Gateway...")
    
    # Start ngrok tunnel automatically
    try:
        import subprocess
        import requests
        import time
        
        logger.info("Starting ngrok tunnel on port 8001...")
        
        # Start ngrok with configuration to avoid browser warning
        # Use --log=stdout --log-level=info for debugging if needed
        subprocess.Popen(
            ["ngrok", "http", "8001", "--log=stdout"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait for ngrok to start
        time.sleep(3)
        
        # Get public URL from ngrok API
        response = requests.get("http://localhost:4040/api/tunnels")
        tunnels = response.json()["tunnels"]
        
        if tunnels:
            ngrok_public_url = tunnels[0]["public_url"]
            logger.info(f"✅ Ngrok tunnel ready: {ngrok_public_url}")
        else:
            logger.warning("⚠️ Ngrok started but no tunnels found")
            
    except Exception as e:
        logger.warning(f"Could not start ngrok automatically: {e}")
        logger.info("You can start ngrok manually: ngrok http 8001")
    
    # Pre-load AI models (skip STT since we're using Twilio's built-in)
    try:
        logger.info("Loading TTS client...")
        tts = get_tts_client()
        logger.info("✅ TTS ready")
    except Exception as e:
        logger.error(f"Failed to load TTS: {e}")
    
    logger.info("🎉 Voice Gateway startup complete")


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("VOICE_GATEWAY_HOST", "0.0.0.0")
    port = int(os.getenv("VOICE_GATEWAY_PORT", 8001))
    
    uvicorn.run(
        "voice_gateway:app",
        host=host,
        port=port,
        reload=False,  # Disable reload to keep models in memory
        log_level="info"
    )

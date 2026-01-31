"""
Reasoning Engine - Uses Qwen/DeepSeek for heavy thinking tasks
This is the BRAIN of the system. Groq/Llama is just the MOUTH.

Handles:
- Post-call deep analysis
- RAG processing and knowledge base reasoning
- Workflow decision making
- Lead scoring and categorization
- Multi-step logic and chain-of-thought
- Generating intelligent prompts for the IVR
"""
from typing import List, Dict, Optional
from loguru import logger
from shared.llm_client import LLMClient
from shared.database import SupabaseDB
import json


class ReasoningEngine:
    """Heavy reasoning engine using Qwen/DeepSeek"""
    
    def __init__(self):
        self.reasoning_llm = LLMClient(use_reasoning_model=True)
        logger.info("🧠 Reasoning Engine initialized with smart model")
    
    async def deep_call_analysis(
        self,
        call_id: str,
        transcript: str,
        agent_config: Dict,
        db: SupabaseDB
    ) -> Dict:
        """
        Deep post-call analysis using reasoning model with structured output
        - Categorize user intent
        - Score lead quality
        - Detect contradictions
        - Recommend follow-up actions
        - Identify patterns
        """
        analysis_prompt = f"""Analyze this phone call deeply as a business analyst.

AGENT PURPOSE: {agent_config.get('name', 'Unknown')}

TRANSCRIPT:
{transcript}

Perform deep reasoning:

1. USER INTENT ANALYSIS:
    - What was the user's primary goal?
    - Were there hidden objections or concerns?
    async def deep_call_analysis(
        self,
        call_id: str,
        transcript: str,
        agent_config: Dict,
        db: SupabaseDB
    ) -> Dict:
        """
        Deep post-call analysis using reasoning model
        - Categorize user intent
        - Score lead quality
        - Detect contradictions
        - Recommend follow-up actions
        - Identify patterns
        """
        # Build prompt safely using list concatenation to avoid syntax errors from embedded quotes
        prompt_parts = [
            "Analyze this phone call and return a JSON object with the following fields:",
            f"AGENT PURPOSE: {agent_config.get('name', 'Unknown')}",
            "",
            "TRANSCRIPT:",
            transcript,
            "",
            "Return strictly valid JSON (no markdown formatting) with this schema:",
            "{",
            '    "summary": "Concise 2-3 sentence summary of the call",',
            '    "outcome": "One of: Interested, Not Interested, Follow-up, Voicemail, Completed",',
            '    "sentiment": "One of: Positive, Neutral, Negative",',
            '    "confidence_score": 0.95,  // Float 0.0-1.0 representing lead quality/interest',
            '    "key_points": ["Point 1", "Point 2", "Point 3"],',
            '    "next_action": "Recommended next step (e.g. \'Send SMS\', \'None\')"',
            "}"
        ]
        analysis_prompt = "\n".join(prompt_parts)

        messages = [{"role": "user", "content": analysis_prompt}]
        response = await self.reasoning_llm.generate_response(
            messages=messages,
            system_prompt="You are a precise business analyst API. Output ONLY valid JSON.",
            temperature=0.2,
            max_tokens=500
        )
        
        try:
            # Clean up potential markdown code blocks
            clean_response = response.replace("```json", "").replace("```", "").strip()
            analysis = json.loads(clean_response)
            logger.info(f"🧠 Deep analysis complete: {analysis}")
            return analysis
        except Exception as exc:
            logger.warning(f"Failed to parse reasoning engine response: {exc}\nRaw: {response[:200]}...")
            # Try to extract JSON from the response if it contains extra text (thinking blocks, etc)
            import re
            
            # First, remove <think> tags and content
            cleaned = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
            
            # Try to find JSON object with balanced braces
            match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned, re.DOTALL)
            if match:
                json_str = match.group(0)
                try:
                    analysis = json.loads(json_str)
                    logger.info(f"🧠 Deep analysis (recovered from thinking block): {analysis}")
                    return analysis
                except Exception as exc2:
                    logger.warning(f"Still failed to parse recovered JSON: {exc2}")
            
            # Last resort: try to extract a simpler structure
            try:
                # Look for any line that starts with { and ends with }
                for line in response.split('\n'):
                    if line.strip().startswith('{') and line.strip().endswith('}'):
                        analysis = json.loads(line.strip())
                        logger.info(f"🧠 Deep analysis (recovered from line): {analysis}")
                        return analysis
            except Exception:
                pass
            
            logger.error(f"Failed to extract valid JSON from Qwen response")
            return {"error": "Analysis parsing failed", "raw": response[:500]}
            
    async def rag_knowledge_search(
        self,
        query: str,
        agent_id: str,
        db: SupabaseDB,
        context: Optional[str] = None
    ) -> Dict:
        """
        Smart RAG processing using reasoning model
        - Fetch relevant knowledge
        - Score relevance
        - Build intelligent summaries
        - Return structured answer
        """
        # Get knowledge base entries
        try:
            kb_results = await db.search_knowledge(agent_id, query, limit=5)
        except Exception as e:
            logger.error(f"Failed to do search: {e}")
            kb_results = []
        
        if not kb_results:
            return {"answer": None, "sources": [], "confidence": 0.0}
        
        # Build context for reasoning model
        kb_context = "\n\n".join([
            f"[SOURCE {i+1}] {kb['title']}:\n{kb['content']}"
            for i, kb in enumerate(kb_results)
        ])
        
        # Build prompt safely
        prompt_parts = [
            "You are a knowledge base expert. Answer the question using ONLY the provided sources.",
            "",
            f"QUESTION: {query}",
            "",
            f"CONTEXT: {context if context else 'None'}",
            "",
            "AVAILABLE KNOWLEDGE:",
            kb_context,
            "",
            "Tasks:",
            "1. Find the most relevant information",
            "2. Synthesize a clear, accurate answer",
            "3. If multiple sources conflict, note that",
            "4. If no sources answer the question, say so",
            "",
            "Return JSON:",
            "{",
            '  "answer": "",',
            '  "confidence": 0.0,',
            '  "sources_used": [],',
            '  "conflicting_info": false,',
            '  "needs_clarification": false',
            "}"
        ]
        rag_prompt = "\n".join(prompt_parts)
        
        messages = [{"role": "user", "content": rag_prompt}]
        response = await self.reasoning_llm.generate_response(
            messages=messages,
            system_prompt="You are a research assistant. Provide accurate, well-sourced answers.",
            temperature=0.2,
            max_tokens=400
        )
        
        try:
            result = json.loads(response)
            logger.info(f"🧠 Traditional RAG complete: Confidence {result.get('confidence')}")
            return result
        except:
            return {"answer": response, "confidence": 0.5, "sources_used": [], "error": "Parse failed"}
    
    async def generate_dynamic_prompt(
        self,
        agent_base_prompt: str,
        context: Dict,
        db: SupabaseDB
    ) -> str:
        """
        Generate intelligent, context-aware prompt for IVR
        The reasoning model writes the smart instructions
        The IVR model (Groq) executes them fast
        """
        # Build prompt safely
        prompt_parts = [
            "You are a prompt engineering expert. Generate an optimized system prompt for a phone call AI.",
            "",
            "BASE AGENT PURPOSE:",
            agent_base_prompt,
            "",
            "CURRENT CONTEXT:",
            f"- Call count today: {context.get('calls_today', 0)}",
            f"- Recent outcomes: {context.get('recent_outcomes', [])}",
            f"- User history: {context.get('user_history', 'None')}",
            f"- Time of day: {context.get('time_of_day', 'Unknown')}",
            "",
            "Generate a SHORT, CLEAR, ACTIONABLE prompt that:",
            "1. Maintains the core agent purpose",
            "2. Adapts to context (e.g., busy times -> be concise)",
            "3. Handles likely objections based on recent calls",
            "4. Includes specific examples if needed",
            "5. Is optimized for FAST execution (Groq will run it)",
            "",
            "Return ONLY the prompt text (no JSON, no explanation):"
        ]
        prompt_gen = "\n".join(prompt_parts)
        
        messages = [{"role": "user", "content": prompt_gen}]
        dynamic_prompt = await self.reasoning_llm.generate_response(
            messages=messages,
            system_prompt="You are a prompt optimization expert. Write clear, effective prompts.",
            temperature=0.5,
            max_tokens=400
        )
        
        logger.info("🧠 Dynamic prompt generated for IVR")
        return dynamic_prompt.strip()
    
    async def workflow_decision(
        self,
        call_analysis: Dict,
        agent_config: Dict
    ) -> List[str]:
        """
        Decide what workflows to trigger after call
        - Send SMS?
        - Send email?
        - Transfer to human?
        - Schedule callback?
        - Update CRM?
        """
        # Build prompt safely
        prompt_parts = [
            "Make workflow decisions based on this call analysis:",
            "",
            "CALL ANALYSIS:",
            json.dumps(call_analysis, indent=2),
            "",
            "AGENT CONFIG:",
            json.dumps(agent_config, indent=2),
            "",
            "Decide which workflows should trigger:",
            "- send_sms: Send follow-up SMS",
            "- send_email: Send email with details",
            "- human_handoff: Transfer to human agent",
            "- schedule_callback: Schedule a callback",
            "- update_crm: Update CRM with lead info",
            "- send_calendar: Send calendar invite",
            "- none: No action needed",
            "",
            "Return JSON array of workflow IDs:",
            "{",
            '  "workflows": ["workflow1", "workflow2"],',
            '  "reasoning": ""',
            "}"
        ]
        decision_prompt = "\n".join(prompt_parts)
        
        messages = [{"role": "user", "content": decision_prompt}]
        response = await self.reasoning_llm.generate_response(
            messages=messages,
            system_prompt="You are a workflow automation expert. Make smart decisions.",
            temperature=0.3,
            max_tokens=200
        )
        
        try:
            result = json.loads(response)
            workflows = result.get('workflows', [])
            logger.info(f"🧠 Workflows decided: {workflows}")
            return workflows
        except:
            return []
    
    async def lead_scoring(
        self,
        transcript: str,
        metadata: Dict
    ) -> int:
        """
        Score lead quality 0-100 using reasoning model
        """
        # Build prompt safely
        prompt_parts = [
            "Score this lead from 0-100:",
            "",
            "TRANSCRIPT:",
            transcript,
            "",
            "METADATA:",
            json.dumps(metadata, indent=2),
            "",
            "Consider:",
            "- Budget signals",
            "- Authority (decision maker?)",
            "- Need (urgent vs nice-to-have)",
            "- Timeline (when do they need it)",
            "- Engagement level",
            "- Objections raised",
            "",
            "Return ONLY a number 0-100:"
        ]
        score_prompt = "\n".join(prompt_parts)
        
        messages = [{"role": "user", "content": score_prompt}]
        response = await self.reasoning_llm.generate_response(
            messages=messages,
            system_prompt="You are a lead qualification expert.",
            temperature=0.2,
            max_tokens=10
        )
        
        try:
            score = int(response.strip())
            logger.info(f"🧠 Lead scored: {score}/100")
            return max(0, min(100, score))  # Clamp 0-100
        except:
            return 50  # Default mid-score

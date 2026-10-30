import os
import sys
import json
import tempfile
from pathlib import Path

# ── Make sure the backend directory is on sys.path so that
#    `from app_config import ...` works regardless of the working
#    directory the user launched from (e.g. repo root vs backend/).
_BACKEND_DIR = Path(__file__).resolve().parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uvicorn
import numpy as np
import io

from auth import router as auth_router, get_user_id

from app_config import (
    CRISIS_HELPLINE_NUMBER,
    CRISIS_HELPLINE_NAME,
    CRISIS_HELPLINE_DESCRIPTION,
    MAX_AUDIO_SIZE_MB,
    DATA_RETENTION_NOTE,
)

app = FastAPI(
    title="MindCare â€” Multimodal Mental Health Analysis API",
    description="Clinical-grade multimodal depression screening system.",
    version="2.0.0",
)

# CORS â€” allow all localhost ports in development + configurable production URL
_frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        _frontend_url,
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Auth router — provides POST /auth/token
app.include_router(auth_router)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Pydantic schemas
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class JournalEntry(BaseModel):
    user_id: str
    content: str
    timestamp: Optional[datetime] = None

class SentimentResponse(BaseModel):
    sentiment: str
    score: float
    risk_level: str
    recommendations: List[str]

class UserProfile(BaseModel):
    user_id: str
    name: str
    email: str
    age: Optional[int] = None
    emergency_contact: Optional[str] = None

class PHQ8Request(BaseModel):
    answers: List[int] = Field(..., min_length=8, max_length=8,
                               description="8 answers, each 0â€“3")
    user_id: Optional[str] = "anonymous"

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    model_config = {"arbitrary_types_allowed": True}

    def model_post_init(self, __context):
        for v in self.answers:
            if v not in (0, 1, 2, 3):
                raise ValueError("Each PHQ-8 answer must be 0, 1, 2, or 3.")

class PHQ8Response(BaseModel):
    score: int
    severity: str
    severity_description: str
    answers: List[int]
    timestamp: datetime


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# In-memory assessment store (replace with DB in production)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_assessments: List[Dict[str, Any]] = []
_phq8_results: List[Dict[str, Any]] = []


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Root / health
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.get("/")
async def root():
    return {"message": "MindCare API", "status": "active", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Configuration endpoint
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.get("/api/config/helpline")
async def get_helpline():
    """Return the configured crisis helpline details."""
    return {
        "number": CRISIS_HELPLINE_NUMBER,
        "name": CRISIS_HELPLINE_NAME,
        "description": CRISIS_HELPLINE_DESCRIPTION,
    }


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Journal endpoints (kept)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.post("/api/journal/entry")
async def create_journal_entry(entry: JournalEntry):
    return {
        "message": "Journal entry created",
        "entry": entry,
        "analysis": {"sentiment": "neutral", "score": 0.5, "risk_level": "low"},
    }

@app.get("/api/journal/entries/{user_id}")
async def get_journal_entries(user_id: str, limit: int = 10):
    return {"user_id": user_id, "entries": []}


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# User management (kept)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.post("/api/users/register")
async def register_user(user: UserProfile):
    return {"message": "User registered successfully", "user_id": user.user_id}

@app.get("/api/users/{user_id}")
async def get_user_profile(user_id: str):
    return {"user_id": user_id, "profile": {}}


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Chatbot â€” per-user conversation state + response pools
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

import random

# Per-user counters: { user_id: { category: call_count } }
_chat_counters: Dict[str, Dict[str, int]] = {}

# Response pools â€” multiple replies per category so nothing repeats back-to-back
_RESPONSES: Dict[str, List[str]] = {
    "crisis": [
        f"I'm very concerned about what you're sharing. Please reach out for help right now. "
        f"In India you can call {CRISIS_HELPLINE_NAME}: {CRISIS_HELPLINE_NUMBER} (free, 24/7). "
        f"You are not alone, and support is available immediately.",

        f"What you're sharing worries me deeply. You deserve immediate support â€” "
        f"please call {CRISIS_HELPLINE_NAME} {CRISIS_HELPLINE_NUMBER} right now. It is free and available 24/7. "
        f"Is there someone physically near you who you can be with right now?",

        f"Your safety matters more than anything else right now. Please reach out â€” "
        f"{CRISIS_HELPLINE_NAME} {CRISIS_HELPLINE_NUMBER} (free, 24/7, India). "
        f"If you feel unsafe, go to the nearest hospital emergency department.",
    ],
    "hopeless": [
        "It sounds like you're carrying a very heavy weight right now. "
        "Those feelings are real, but they can change with the right support. "
        "Have you been able to talk to anyone â€” a friend, family member, or counsellor?",

        "Feeling hopeless is one of the most exhausting experiences a person can have. "
        "You reached out here, and that matters. What has felt most unbearable recently?",

        "When everything feels pointless, it's a signal that you need more support â€” not a reflection of who you are. "
        "Have you spoken to a doctor or mental health professional about how you've been feeling?",
    ],
    "anxiety": [
        "Anxiety can feel overwhelming, but your body is safe even when your mind says otherwise. "
        "Try box breathing right now: inhale 4 counts, hold 4, exhale 4, hold 4. Repeat 3 times. "
        "Would you like to tell me what's been triggering it?",

        "When anxiety spikes, your nervous system is in overdrive. "
        "A quick reset: plant both feet flat on the floor, name 5 things you can see, then take one slow breath. "
        "How long have you been feeling this way?",

        "Anxiety often comes with a specific trigger, even when it feels general. "
        "What's the one thought or situation that keeps coming back to your mind?",

        "It's exhausting to feel anxious all the time. Have you tried any grounding techniques before, "
        "like the 5-4-3-2-1 method? (5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste.) "
        "It can interrupt the spiral quickly.",
    ],
    "stress": [
        "Stress is your mind's signal that something needs attention â€” you're not weak for feeling it. "
        "Try writing down the one thing bothering you most. Breaking it into smaller pieces makes it manageable. "
        "What's been weighing on you the most?",

        "When everything piles up, it's hard to know where to start. "
        "Try this: pick the single smallest task you can finish in 10 minutes and just do that one thing. "
        "Sometimes one small win is enough to shift the feeling. What's on your plate right now?",

        "Chronic stress takes a real physical toll â€” tight shoulders, poor sleep, low energy. "
        "Have you had any moments to rest or step away lately, even briefly?",

        "Stress often comes from feeling out of control. "
        "What's one thing in your current situation that you actually have some control over?",
    ],
    "depression": [
        "I'm sorry you're feeling this way. Depression is a real condition, not a weakness or a choice. "
        "If these feelings have lasted more than two weeks, please consider speaking to a doctor. "
        "What has been hardest for you day to day?",

        "Depression can make even small things feel impossible. "
        "Is there one tiny thing â€” even just drinking a glass of water or stepping outside for 5 minutes â€” "
        "that you might be able to do today?",

        "You don't have to carry this alone. Have you spoken to anyone about how you've been feeling â€” "
        "a friend, a family member, or a professional?",

        "Sometimes depression lies to us â€” it tells us nothing will help and nothing will change. "
        "But that's the illness talking, not the truth. What did life feel like before this started?",
    ],
    "loneliness": [
        "Feeling lonely is painful â€” and more common than people admit. "
        "Is there one person you could send a simple message to today? "
        "Connection doesn't have to be deep to be meaningful.",

        "Loneliness can feel invisible because people around you might not know you're struggling. "
        "Have you been able to tell anyone how isolated you've been feeling?",

        "Sometimes loneliness is about the quality of connection, not just the quantity. "
        "Is there someone in your life you used to feel close to that you've drifted from?",
    ],
    "sleep": [
        "Poor sleep and low mood are closely linked â€” each makes the other worse. "
        "Try this tonight: no screens 30 minutes before bed, keep the room dark, "
        "and do 4-7-8 breathing (inhale 4, hold 7, exhale 8). How long has sleep been difficult?",

        "Sleep problems are one of the earliest signs that something needs attention mentally. "
        "Are you struggling to fall asleep, staying asleep, or waking too early?",

        "A consistent wind-down routine makes a real difference. "
        "Even just 15 minutes of the same calm activity each night â€” reading, light stretching, dim lighting â€” "
        "signals your brain that sleep is coming. What does your evening usually look like?",
    ],
    "anger": [
        "Anger is a valid signal â€” it usually means a boundary was crossed or something feels deeply unfair. "
        "Before reacting, try stepping away for just 2 minutes and taking slow breaths. "
        "What happened that triggered this?",

        "The emotion under anger is almost always something softer â€” hurt, fear, or helplessness. "
        "What do you think is really underneath what you're feeling right now?",
    ],
    "positive": [
        "That's genuinely great to hear. Positive moments are worth pausing on. "
        "What's been going well for you?",

        "It's really good to hear you're doing well. "
        "What do you think has made the biggest difference lately?",

        "Hold onto that feeling â€” and consider writing it down. "
        "Noting what went well each day builds resilience for harder times. What's made today good?",
    ],
    "mindfulness": [
        "Mindfulness is one of the most evidence-backed tools for mental wellbeing. "
        "Here's a 1-minute grounding exercise: name 5 things you can see, 4 you can touch, "
        "3 you can hear, 2 you can smell, 1 you can taste. Would you like more techniques?",

        "A simple starting point: set a timer for 5 minutes, sit comfortably, and just notice your breath. "
        "When your mind wanders â€” and it will â€” gently bring it back without judging yourself. "
        "That's the whole practice. Have you tried anything like this before?",

        "Body scan meditation is great for releasing physical tension from stress. "
        "Starting at the top of your head, slowly move your attention down through each part of your body, "
        "just noticing any tightness without trying to change it. "
        "Would you like a step-by-step guide?",
    ],
    "coping": [
        "Here are 5 evidence-based coping strategies:\n"
        "1. Box breathing (inhale 4s â†’ hold 4s â†’ exhale 4s â†’ hold 4s)\n"
        "2. A 10-minute walk â€” it genuinely shifts brain chemistry\n"
        "3. Journaling â€” write 3 sentences about how you feel\n"
        "4. Grounding â€” name 5 things you can see right now\n"
        "5. Reach out â€” send one message to someone you trust\n\n"
        "Which would you like to explore more?",

        "When you're overwhelmed, the most effective coping tools are usually physical: "
        "cold water on your face, a brisk walk, or slow deep breathing. "
        "These work by directly calming the nervous system. "
        "What have you tried before that's helped, even a little?",

        "Long-term coping is about building small, consistent habits rather than big dramatic changes. "
        "What does your current daily routine look like? Sometimes one small adjustment makes a big difference.",
    ],
    "default": [
        "Thank you for sharing that with me. I'm here to listen without judgment. "
        "Can you tell me more about how you've been feeling?",

        "I hear you. Can you say more about what's been going on?",

        "That sounds like it's been weighing on you. "
        "What's been the hardest part of what you're going through?",

        "I want to make sure I understand what you're experiencing. "
        "How long have you been feeling this way?",

        "Thank you for trusting me with this. "
        "Is this something that came on recently, or has it been building for a while?",
    ],
}


def _pick(category: str, user_id: str) -> str:
    """Return the next response from the pool for this category, cycling round-robin."""
    counters = _chat_counters.setdefault(user_id, {})
    idx = counters.get(category, 0)
    pool = _RESPONSES[category]
    response = pool[idx % len(pool)]
    counters[category] = idx + 1
    return response


def _chat_response(message: str, user_id: str = "anonymous") -> str:
    m = message.lower()

    if any(kw in m for kw in ["suicide", "kill myself", "end my life", "want to die",
                               "no reason to live", "better off dead", "harm myself"]):
        return _pick("crisis", user_id)

    if any(kw in m for kw in ["hopeless", "worthless", "can't go on", "give up",
                               "unbearable", "no point", "pointless", "meaningless"]):
        return _pick("hopeless", user_id)

    if any(kw in m for kw in ["anxious", "anxiety", "panic", "worried", "fear", "nervous"]):
        return _pick("anxiety", user_id)

    if any(kw in m for kw in ["stress", "stressed", "overwhelmed", "pressure", "burnout"]):
        return _pick("stress", user_id)

    if any(kw in m for kw in ["depressed", "depression", "sad", "unhappy",
                               "miserable", "empty", "numb", "hopeless"]):
        return _pick("depression", user_id)

    if any(kw in m for kw in ["lonely", "alone", "isolated", "no one cares", "nobody"]):
        return _pick("loneliness", user_id)

    if any(kw in m for kw in ["can't sleep", "insomnia", "tired", "exhausted",
                               "no energy", "fatigue", "sleep"]):
        return _pick("sleep", user_id)

    if any(kw in m for kw in ["angry", "anger", "furious", "rage", "frustrated",
                               "irritated", "annoyed"]):
        return _pick("anger", user_id)

    if any(kw in m for kw in ["happy", "great", "wonderful", "grateful",
                               "better", "good day", "excited", "good"]):
        return _pick("positive", user_id)

    if any(kw in m for kw in ["mindful", "mindfulness", "meditation",
                               "calm", "breathe", "breathing", "relax"]):
        return _pick("mindfulness", user_id)

    if any(kw in m for kw in ["coping", "strategies", "tips", "advice",
                               "help me", "what should i do", "how to deal"]):
        return _pick("coping", user_id)

    return _pick("default", user_id)


class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "anonymous"


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """
    Mental health chatbot. Accepts a JSON body: {"message": "...", "user_id": "..."}.
    Also supports legacy query-param style (?message=&user_id=) via the /api/chat/query alias.
    """
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=422, detail="'message' cannot be empty.")
    return {
        "user_message": req.message,
        "bot_response": _chat_response(req.message.strip(), req.user_id or "anonymous"),
        "timestamp": datetime.now(),
    }


@app.post("/api/chat/query")
async def chat_query(message: str, user_id: str = "anonymous"):
    """Legacy query-param variant kept for backward compatibility."""
    if not message or not message.strip():
        raise HTTPException(status_code=422, detail="'message' cannot be empty.")
    return {
        "user_message": message,
        "bot_response": _chat_response(message.strip()),
        "timestamp": datetime.now(),
    }


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# PHQ-8 scoring
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

PHQ8_SEVERITY = [
    (0,  4,  "Minimal",  "Little or no depression is indicated."),
    (5,  9,  "Mild",     "Mild depressive symptoms. Self-monitoring recommended."),
    (10, 14, "Moderate", "Moderate depressive symptoms. Consider professional consultation."),
    (15, 19, "Moderately Severe",
             "Moderately severe depression. Professional evaluation recommended."),
    (20, 24, "Severe",   "Severe depression. Prompt professional evaluation strongly advised."),
]


def _phq8_severity(score: int):
    for lo, hi, label, desc in PHQ8_SEVERITY:
        if lo <= score <= hi:
            return label, desc
    return "Severe", "Severe depression detected."


@app.post("/api/phq8/score", response_model=PHQ8Response)
async def score_phq8(req: PHQ8Request):
    """Score an 8-item PHQ-8 questionnaire and return severity band."""
    total = sum(req.answers)
    severity, description = _phq8_severity(total)
    result = {
        "score": total,
        "severity": severity,
        "severity_description": description,
        "answers": req.answers,
        "timestamp": datetime.now(),
        "user_id": req.user_id,
    }
    _phq8_results.append(result)
    return result


@app.get("/api/phq8/history/{user_id}")
async def get_phq8_history(user_id: str):
    user_results = [r for r in _phq8_results if r.get("user_id") == user_id]
    return {"user_id": user_id, "results": user_results}


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Assessment history
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.get("/api/assessments/{user_id}")
async def get_assessment_history(user_id: str, page: int = 1, page_size: int = 5):
    user_assessments = [a for a in _assessments if a.get("user_id") == user_id]
    user_assessments.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    total = len(user_assessments)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "user_id": user_id,
        "total": total,
        "page": page,
        "page_size": page_size,
        "assessments": user_assessments[start:end],
    }


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Delete my data
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.delete("/api/users/{user_id}/data")
async def delete_user_data(user_id: str):
    """Hard-delete all assessments and PHQ-8 results for this user."""
    global _assessments, _phq8_results
    before_assess = len(_assessments)
    before_phq8 = len(_phq8_results)
    _assessments = [a for a in _assessments if a.get("user_id") != user_id]
    _phq8_results = [r for r in _phq8_results if r.get("user_id") != user_id]
    return {
        "message": "All user data deleted.",
        "assessments_deleted": before_assess - len(_assessments),
        "phq8_deleted": before_phq8 - len(_phq8_results),
        "timestamp": datetime.now(),
    }




# ─────────────────────────────────────────────────────────────────────────────
# Model metrics endpoint
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/model/metrics")
async def get_model_metrics():
    """
    Return model performance metrics.

    Priority:
      1. ml/results/metrics.json  (canonical, version-controlled)
      2. backend/model_metrics.json  (legacy fallback)
    """
    _candidates = [
        Path(__file__).parent.parent / "ml" / "results" / "metrics.json",
        Path(__file__).parent / "model_metrics.json",
    ]
    for p in _candidates:
        if p.exists():
            with open(p, encoding="utf-8") as f:
                return json.load(f)
    raise HTTPException(status_code=404, detail="metrics.json not found. Run training first.")


# ─────────────────────────────────────────────────────────────────────────────
# Audio feature extraction helpers
# ─────────────────────────────────────────────────────────────────────────────

_ALLOWED_AUDIO_TYPES = {
    "audio/wav", "audio/x-wav", "audio/wave",
    "audio/mpeg", "audio/mp3",
    "audio/webm", "audio/ogg",
    "application/octet-stream",   # some browsers send this for .wav
}

_ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".webm", ".ogg", ".m4a"}


def _validate_audio_upload(upload: UploadFile, raw_bytes: bytes) -> None:
    """Raise HTTPException for invalid audio file type or size."""
    ext = Path(upload.filename or "").suffix.lower()
    ct  = (upload.content_type or "").lower().split(";")[0].strip()

    if ct not in _ALLOWED_AUDIO_TYPES and ext not in _ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=(
                f"Unsupported media type '{ct}' (extension '{ext}'). "
                f"Accepted types: WAV, MP3, WebM, OGG."
            ),
        )
    if len(raw_bytes) > MAX_AUDIO_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file exceeds the {MAX_AUDIO_SIZE_MB} MB size limit.",
        )


def _extract_audio_features(audio_bytes: bytes) -> dict:
    """
    Extract a rich set of audio features using librosa.

    Returns a dict with:
      mfcc_mean, mfcc_std  — MFCC-40 statistics
      pitch_mean, pitch_std — F0 statistics (pyin)
      energy_mean          — RMS energy mean
      speech_rate          — voiced frames / total frames
      pause_ratio          — fraction of silence frames
      depression_proxy     — heuristic [0-1] score from audio alone
    """
    try:
        import librosa
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000, duration=60)

        # MFCC (40 coefficients)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
        mfcc_mean = float(np.mean(mfcc))
        mfcc_std  = float(np.std(mfcc))

        # Pitch (F0) via pyin
        try:
            f0, voiced_flag, _ = librosa.pyin(y, fmin=50, fmax=500, sr=sr)
            voiced = f0[voiced_flag]
            pitch_mean = float(np.mean(voiced)) if len(voiced) > 0 else 0.0
            pitch_std  = float(np.std(voiced))  if len(voiced) > 0 else 0.0
            speech_rate = float(np.mean(voiced_flag)) if len(voiced_flag) > 0 else 0.0
        except Exception:
            pitch_mean  = 0.0
            pitch_std   = 0.0
            speech_rate = 0.0

        # RMS energy
        rms = librosa.feature.rms(y=y)[0]
        energy_mean = float(np.mean(rms))

        # Pause ratio — frames below 10% of max RMS
        silence_threshold = 0.10 * float(np.max(rms)) if np.max(rms) > 0 else 0
        pause_ratio = float(np.mean(rms < silence_threshold))

        # Simple depression proxy from audio:
        # Low F0 range, low energy, high pause ratio are associated with depression.
        dep_audio = 0.0
        if pitch_std < 20:   dep_audio += 0.2   # flat prosody
        if energy_mean < 0.02: dep_audio += 0.2  # low energy
        if pause_ratio > 0.4:  dep_audio += 0.2  # many pauses
        if speech_rate < 0.3:  dep_audio += 0.2  # slow speech
        dep_audio = min(dep_audio, 0.8)

        return {
            "mfcc_mean":       round(mfcc_mean, 4),
            "mfcc_std":        round(mfcc_std, 4),
            "pitch_mean":      round(pitch_mean, 2),
            "pitch_std":       round(pitch_std, 2),
            "energy_mean":     round(energy_mean, 6),
            "speech_rate":     round(speech_rate, 3),
            "pause_ratio":     round(pause_ratio, 3),
            "depression_proxy": round(dep_audio, 3),
        }
    except Exception as exc:
        print(f"[audio_features] Extraction failed: {exc}")
        return {
            "mfcc_mean": 0.0, "mfcc_std": 0.0,
            "pitch_mean": 0.0, "pitch_std": 0.0,
            "energy_mean": 0.0, "speech_rate": 0.0,
            "pause_ratio": 0.0, "depression_proxy": 0.0,
        }


def _mel_tensor_from_bytes(audio_bytes: bytes):
    """Return a (1, 1, 128, 128) torch tensor from raw audio bytes."""
    try:
        import torch
        import librosa as _lr
        N_MELS = 128
        y, sr = _lr.load(io.BytesIO(audio_bytes), sr=16000, duration=60)
        mel = _lr.feature.melspectrogram(y=y, sr=sr, n_mels=N_MELS)
        mel = _lr.power_to_db(mel, ref=np.max)
        mel = (mel - mel.min()) / (mel.max() - mel.min() + 1e-8)
        T = 128
        if mel.shape[1] >= T:
            mel = mel[:, :T]
        else:
            mel = np.pad(mel, ((0, 0), (0, T - mel.shape[1])))
        return torch.tensor(mel, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
    except Exception:
        import torch
        return torch.zeros(1, 1, 128, 128)


# ─────────────────────────────────────────────────────────────────────────────
# Heuristic text analysis helpers
# ─────────────────────────────────────────────────────────────────────────────

ACTION_PLAN_MAP = {
    "critical": {
        "summary": "Immediate professional support is strongly advised.",
        "categories": [
            {
                "category": "Immediate Help",
                "priority": "urgent",
                "steps": [
                    f"Call {CRISIS_HELPLINE_NAME}: {CRISIS_HELPLINE_NUMBER} (free, 24/7) right now.",
                    "Go to your nearest hospital emergency / psychiatry OPD if you feel unsafe.",
                    "Tell a trusted person what you are experiencing.",
                ],
            },
            {
                "category": "Professional Care",
                "priority": "high",
                "steps": [
                    "Book an emergency appointment with a psychiatrist or clinical psychologist today.",
                    "Ask your doctor about Cognitive Behavioural Therapy (CBT).",
                ],
            },
        ],
    },
    "high": {
        "summary": "Significant distress detected. Take action this week.",
        "categories": [
            {
                "category": "Professional Support",
                "priority": "high",
                "steps": [
                    "Schedule a session with a therapist or counsellor within 3-5 days.",
                    f"Contact {CRISIS_HELPLINE_NAME}: {CRISIS_HELPLINE_NUMBER} if you need to talk now.",
                ],
            },
            {
                "category": "Sleep and Body",
                "priority": "high",
                "steps": [
                    "Set a fixed sleep and wake time -- irregular sleep worsens depression.",
                    "Even a 20-minute brisk walk daily raises serotonin.",
                ],
            },
        ],
    },
    "moderate": {
        "summary": "Moderate distress signals detected. Take proactive steps.",
        "categories": [
            {
                "category": "Check-in with a Professional",
                "priority": "medium",
                "steps": [
                    "Book a session with a counsellor or therapist.",
                    "Talk to your college counsellor, HR, or GP about how you've been feeling.",
                ],
            },
            {
                "category": "Physical Wellbeing",
                "priority": "medium",
                "steps": [
                    "Walk or do light exercise for at least 20 minutes daily.",
                    "Prioritise 7-8 hours of sleep consistently.",
                ],
            },
        ],
    },
    "low": {
        "summary": "You appear to be in a good mental state. Keep it up.",
        "categories": [
            {
                "category": "Maintain What's Working",
                "priority": "low",
                "steps": [
                    "Continue your current self-care routines.",
                    "Keep journaling a few times a week to maintain self-awareness.",
                ],
            },
        ],
    },
}


def _score_text_heuristic(text: str) -> dict:
    """
    Return a depression-score dict for a single text fragment.

    Uses English word list matching for depressive and positive vocabulary.
    Note: For production, replace with a trained NLP model.
    """
    text_lower = text.lower()
    words = text_lower.split()
    word_count = max(len(words), 1)

    first_person = sum(1 for w in words if w in {"i", "me", "my", "myself", "mine"})
    first_person_ratio = first_person / word_count

    neg_words = {
        "sad", "hopeless", "worthless", "tired", "exhausted", "empty",
        "alone", "lonely", "depressed", "anxious", "worried", "stressed",
        "bad", "terrible", "awful", "miserable", "hate", "fear", "cry",
        "crying", "helpless", "desperate", "dark", "difficult", "hard",
        "can't", "cannot", "never", "nothing", "nobody", "no one",
    }
    pos_words = {
        "happy", "good", "great", "joy", "excited", "grateful", "wonderful",
        "love", "amazing", "excellent", "peaceful", "calm", "content",
        "motivated", "hopeful", "positive", "better", "improved",
    }

    neg_count = sum(1 for w in words if w in neg_words)
    pos_count = sum(1 for w in words if w in pos_words)
    neg_ratio = neg_count / word_count
    pos_ratio = pos_count / word_count

    crisis_high = ["suicide", "kill myself", "end my life", "want to die",
                   "no reason to live", "better off dead", "harm myself"]
    crisis_mid  = ["hopeless", "worthless", "can't go on", "give up",
                   "unbearable"]
    has_crisis_high = any(kw in text_lower for kw in crisis_high)
    has_crisis_mid  = any(kw in text_lower for kw in crisis_mid)

    score = 0.0
    score += min(first_person_ratio * 2.0, 0.3)
    score += min(neg_ratio * 3.0, 0.40)
    score -= min(pos_ratio * 2.0, 0.20)
    if has_crisis_high: score += 0.60
    elif has_crisis_mid: score += 0.30
    score = float(max(0.0, min(1.0, score)))

    return {
        "depression_score": score,
        "neg_ratio": round(neg_ratio, 3),
        "pos_ratio": round(pos_ratio, 3),
        "first_person_ratio": round(first_person_ratio, 3),
        "crisis_high": has_crisis_high,
        "crisis_mid": has_crisis_mid,
        "word_count": word_count,
    }


def _build_key_findings(scores: list, audio_feats: Optional[dict], has_audio: bool) -> list:
    """Generate up to 3 plain-language key findings from per-question scores + audio."""
    findings = []
    avg = float(np.mean([s["depression_score"] for s in scores]))

    if avg >= 0.60:
        findings.append("Strong negative affect language detected across the three question responses.")
    elif avg >= 0.35:
        findings.append("Moderate negative affect language observed in the question responses.")
    else:
        findings.append("Question responses show predominantly neutral to positive sentiment.")

    fp = float(np.mean([s["first_person_ratio"] for s in scores]))
    if fp > 0.10:
        findings.append(
            f"Elevated first-person pronoun use ({fp:.0%}) across responses -- a known linguistic marker of depression."
        )
    else:
        findings.append("First-person pronoun use is within typical range across all questions.")

    if has_audio and audio_feats:
        proxy = audio_feats.get("depression_proxy", 0)
        if proxy >= 0.4:
            findings.append(
                f"Audio prosody shows reduced expressiveness (pause ratio {audio_feats.get('pause_ratio', 0):.0%}, "
                f"speech rate {audio_feats.get('speech_rate', 0):.0%}) -- consistent with depressive presentation."
            )
        else:
            findings.append("Audio prosody features are within a normal range.")
    else:
        findings.append("No audio provided. Upload audio for bimodal analysis.")

    return findings[:3]


# ─────────────────────────────────────────────────────────────────────────────
# Model loading
# ─────────────────────────────────────────────────────────────────────────────

_CKPT_PRIORITY = [
    Path(__file__).parent / "checkpoints" / "eatd_fast" / "best.pt",
    Path(__file__).parent / "checkpoints" / "eatd"      / "best.pt",
    Path(__file__).parent / "checkpoints" / "synthetic" / "best.pt",
]

_model  = None
_tfidf  = None


def _load_model():
    global _model, _tfidf
    if _model is not None:
        return _model, _tfidf

    ckpt_path = next((p for p in _CKPT_PRIORITY if p.exists()), None)
    if ckpt_path is None:
        return None, None

    try:
        import torch
        import numpy as _np
        from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer as _TT
        import scipy.sparse as _sp

        ckpt = torch.load(str(ckpt_path), map_location="cpu", weights_only=False)
        has_tfidf = "tfidf_vocab" in ckpt

        if has_tfidf:
            from train_cpu_fast import FastMultimodalModel
            tfidf_dim = ckpt.get("args", {}).get("tfidf_dim", 500)
            m = FastMultimodalModel(tfidf_dim=tfidf_dim)
            state = ckpt["model_state"]
            key_map = {"audio.": "audio_enc.", "text.": "text_enc.", "facial.": "facial_enc."}
            remapped = {}
            for k, v in state.items():
                new_k = k
                for old, new_k_prefix in key_map.items():
                    if k.startswith(old):
                        new_k = new_k_prefix + k[len(old):]
                        break
                remapped[new_k] = v
            m.load_state_dict(remapped, strict=False)
            m.eval()

            idf_arr = _np.array(ckpt["tfidf_idf"], dtype=_np.float64)
            tv = TfidfVectorizer(max_features=len(ckpt["tfidf_vocab"]),
                                 sublinear_tf=True, ngram_range=(1, 2))
            tv.vocabulary_ = ckpt["tfidf_vocab"]
            tv.idf_        = idf_arr
            _tt = _TT(sublinear_tf=True)
            _tt.idf_ = idf_arr
            n = len(idf_arr)
            _tt._idf_diag = _sp.diags(idf_arr, offsets=0, shape=(n, n), format="csr", dtype=_np.float64)
            tv._tfidf = _tt
            _tfidf = tv
            _model = m
        else:
            from multimodal_model import build_model
            saved_args = ckpt.get("args", {})
            m = build_model(task=saved_args.get("task", "classification"),
                            embed_dim=saved_args.get("embed_dim", 256),
                            dropout=0.0)
            m.load_state_dict(ckpt["model_state"])
            m.eval()
            _model = m
            _tfidf = None

        return _model, _tfidf
    except Exception as exc:
        print(f"[multimodal] Model load failed (heuristic fallback): {exc}")
        return None, None


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/assess/multimodal  — EATD three-question endpoint
# ─────────────────────────────────────────────────────────────────────────────

class MultimodalTextRequest(BaseModel):
    text: str
    user_id: Optional[str] = "anonymous"


EATD_QUESTIONS = {
    "positive": "Describe a positive memory or a time you felt happy.",
    "neutral":  "Describe your daily routine.",
    "negative": "Describe a difficult or stressful experience.",
}


@app.post("/api/assess/multimodal")
async def assess_multimodal(
    # Per-question text (all required; minimum one non-empty)
    positive_text: str = Form(""),
    neutral_text:  str = Form(""),
    negative_text: str = Form(""),
    # Per-question audio (all optional)
    positive_audio: Optional[UploadFile] = File(None),
    neutral_audio:  Optional[UploadFile] = File(None),
    negative_audio: Optional[UploadFile] = File(None),
    # Caller identity (resolved from JWT when JWT_AUTH_REQUIRED=true)
    user_id: str = Depends(get_user_id),
):
    """
    EATD-Corpus three-question bimodal assessment endpoint.

    Accepts text + optional audio for each of the three EATD emotional
    questions (positive, neutral, negative).  Returns a fused risk assessment.

    Audio files: WAV / MP3 / WebM / OGG, max 50 MB each.
    Text: free-form; English accepted.
    Model fallback: returns demo_mode=true if no trained checkpoint is found.
    """
    # ── Validate at least one text field is non-empty ──────────────────────
    texts = {
        "positive": (positive_text or "").strip(),
        "neutral":  (neutral_text  or "").strip(),
        "negative": (negative_text or "").strip(),
    }
    if not any(texts.values()):
        raise HTTPException(
            status_code=422,
            detail="At least one of positive_text, neutral_text, negative_text is required.",
        )

    # ── Read + validate audio uploads ──────────────────────────────────────
    audio_map: dict[str, Optional[bytes]] = {}
    for q_key, upload in [
        ("positive", positive_audio),
        ("neutral",  neutral_audio),
        ("negative", negative_audio),
    ]:
        if upload and upload.filename:
            raw = await upload.read()
            _validate_audio_upload(upload, raw)   # raises 415 or 413 on error
            audio_map[q_key] = raw
        else:
            audio_map[q_key] = None

    has_any_audio = any(v is not None for v in audio_map.values())

    # ── Per-question text scoring ──────────────────────────────────────────
    q_text_scores = {k: _score_text_heuristic(v) for k, v in texts.items()}

    # ── Per-question audio features ────────────────────────────────────────
    q_audio_feats: dict[str, Optional[dict]] = {}
    for q_key, raw in audio_map.items():
        q_audio_feats[q_key] = _extract_audio_features(raw) if raw else None

    # ── Fuse scores ────────────────────────────────────────────────────────
    # Weighted average: positive (1x), neutral (1x), negative (1.5x)
    weights = {"positive": 1.0, "neutral": 1.0, "negative": 1.5}
    w_sum   = sum(weights[k] for k in texts if texts[k])

    text_dep = sum(
        q_text_scores[k]["depression_score"] * weights[k]
        for k in texts if texts[k]
    ) / max(w_sum, 1)

    audio_dep = 0.0
    n_audio   = 0
    for q_key, feats in q_audio_feats.items():
        if feats:
            audio_dep += feats["depression_proxy"]
            n_audio += 1
    audio_dep = audio_dep / max(n_audio, 1) if n_audio > 0 else 0.0

    # Fusion
    text_weight  = 0.65
    audio_weight = 0.35 if has_any_audio else 0.0
    w_total = text_weight + audio_weight
    fused_score = (text_dep * text_weight + audio_dep * audio_weight) / max(w_total, 1.0)
    fused_score = float(max(0.0, min(1.0, fused_score)))

    # Override if any crisis keyword detected
    any_crisis_high = any(q_text_scores[k]["crisis_high"] for k in q_text_scores)
    if any_crisis_high:
        fused_score = max(fused_score, 0.72)

    # ── Risk level ─────────────────────────────────────────────────────────
    if fused_score >= 0.70:   risk_level = "critical"
    elif fused_score >= 0.50: risk_level = "high"
    elif fused_score >= 0.30: risk_level = "moderate"
    else:                     risk_level = "low"

    # ── Try neural model if available ──────────────────────────────────────
    model_used = "heuristic"
    demo_mode  = True
    model, tfidf = _load_model()
    if model is not None:
        try:
            import torch
            combined_text = " ".join(v for v in texts.values() if v)
            audio_bytes_combined = next(
                (v for v in audio_map.values() if v is not None), None
            )
            audio_tensor = (
                _mel_tensor_from_bytes(audio_bytes_combined)
                if audio_bytes_combined
                else torch.zeros(1, 1, 128, 128)
            )
            with torch.no_grad():
                if tfidf is not None:
                    vec = tfidf.transform([combined_text]).toarray().astype("float32")
                    text_tensor = torch.tensor(vec, dtype=torch.float32)
                    out = model(audio_tensor, text_tensor, torch.zeros(1, 300, 17))
                else:
                    from transformers import BertTokenizer
                    from dataset import MAX_TEXT_LEN
                    tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-cased")
                    enc = tokenizer(combined_text, max_length=MAX_TEXT_LEN,
                                    padding="max_length", truncation=True,
                                    return_tensors="pt")
                    out = model(audio_tensor, enc["input_ids"], enc["attention_mask"],
                                torch.zeros(1, 300, 17))
                probs    = torch.softmax(out, dim=1)[0]
                fused_score = float(probs[1])
                if fused_score >= 0.70:   risk_level = "critical"
                elif fused_score >= 0.50: risk_level = "high"
                elif fused_score >= 0.30: risk_level = "moderate"
                else:                     risk_level = "low"
                model_used = "neural"
                demo_mode  = False
        except Exception as exc:
            print(f"[assess] Neural inference error, using heuristic: {exc}")

    # ── Derive confidence and modality contributions ───────────────────────
    confidence = round(0.70 + fused_score * 0.25, 3)  # heuristic confidence proxy

    text_contrib  = round(text_weight  / max(w_total, 1) * 100, 1)
    audio_contrib = round(audio_weight / max(w_total, 1) * 100, 1)

    # ── Per-question score summaries ───────────────────────────────────────
    per_question_scores = [
        {
            "question":    q_key,
            "prompt":      EATD_QUESTIONS[q_key],
            "text":        texts[q_key],
            "score":       round(q_text_scores[q_key]["depression_score"], 3),
            "has_audio":   audio_map[q_key] is not None,
            "audio_score": round(q_audio_feats[q_key]["depression_proxy"], 3)
                           if q_audio_feats[q_key] else None,
        }
        for q_key in ("positive", "neutral", "negative")
    ]

    # ── Key findings ───────────────────────────────────────────────────────
    key_findings = _build_key_findings(
        list(q_text_scores.values()),
        next((f for f in q_audio_feats.values() if f), None),
        has_any_audio,
    )

    # ── Action plan ────────────────────────────────────────────────────────
    plan = ACTION_PLAN_MAP.get(risk_level, ACTION_PLAN_MAP["low"])
    flat_recs = [step for cat in plan["categories"] for step in cat["steps"]]

    result = {
        "risk_level":              risk_level,
        "score":                   round(fused_score, 3),
        "confidence":              confidence,
        "sds_estimated":           round(fused_score * 80, 1),   # SDS scale 0-80
        "binary_prediction":       int(fused_score >= 0.40),
        "modality_contributions":  {"text": text_contrib, "audio": audio_contrib},
        "per_modality_confidence": {
            "text":  0.85,
            "audio": round(audio_dep, 3) if has_any_audio else None,
        },
        "per_question_scores":     per_question_scores,
        "key_findings":            key_findings,
        "crisis_flags": {
            "high_risk_detected":   any_crisis_high,
            "medium_risk_detected": any(q_text_scores[k]["crisis_mid"] for k in q_text_scores),
        },
        "recommendations": flat_recs,
        "action_plan":     plan,
        "model_used":      model_used,
        "demo_mode":       demo_mode,
        "input_type":      "audio+text" if has_any_audio else "text",
        "timestamp":       datetime.now().isoformat(),
        "user_id":         user_id,
    }

    _assessments.append(result)
    return result


# ── Legacy aliases (kept for backward compatibility) ──────────────────────────

@app.post("/api/multimodal/analyze")
async def multimodal_analyze_legacy(
    text: str = Form(...),
    user_id: str = Form("anonymous"),
    audio_file: Optional[UploadFile] = File(None),
):
    """Legacy single-text alias — routes to the EATD 3-question endpoint."""
    return await assess_multimodal(
        positive_text=text,
        neutral_text="",
        negative_text="",
        positive_audio=audio_file,
        neutral_audio=None,
        negative_audio=None,
        user_id=user_id,
    )


@app.post("/api/multimodal/analyze/text")
async def multimodal_analyze_text(req: MultimodalTextRequest):
    """JSON-body text-only analysis shortcut."""
    return await assess_multimodal(
        positive_text=req.text,
        neutral_text="",
        negative_text="",
        user_id=req.user_id,
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


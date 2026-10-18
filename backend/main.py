import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn
import numpy as np
import io

app = FastAPI(
    title="Mental Health AI Monitoring API",
    description="AI-powered mental health monitoring and support system",
    version="1.0.0"
)

# CORS — allow the React frontend origin (configurable via FRONTEND_URL env var)
_frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[_frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class MoodEntry(BaseModel):
    user_id: str
    mood_score: int  # 1-10 scale
    notes: Optional[str] = None
    timestamp: Optional[datetime] = None

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

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Mental Health AI Monitoring API",
        "status": "active",
        "version": "1.0.0"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# Mood tracking endpoints
@app.post("/api/mood/log")
async def log_mood(entry: MoodEntry):
    """Log a mood entry for a user"""
    # TODO: Save to database
    return {
        "message": "Mood logged successfully",
        "entry": entry,
        "timestamp": datetime.now()
    }

@app.get("/api/mood/history/{user_id}")
async def get_mood_history(user_id: str, days: int = 7):
    """Get mood history for a user"""
    # TODO: Fetch from database
    return {
        "user_id": user_id,
        "days": days,
        "entries": []  # Placeholder
    }

# Journal endpoints
@app.post("/api/journal/entry")
async def create_journal_entry(entry: JournalEntry):
    """Create a new journal entry with AI sentiment analysis"""
    # TODO: Implement sentiment analysis
    # TODO: Save to database
    return {
        "message": "Journal entry created",
        "entry": entry,
        "analysis": {
            "sentiment": "neutral",
            "score": 0.5,
            "risk_level": "low"
        }
    }

@app.get("/api/journal/entries/{user_id}")
async def get_journal_entries(user_id: str, limit: int = 10):
    """Get journal entries for a user"""
    # TODO: Fetch from database
    return {
        "user_id": user_id,
        "entries": []  # Placeholder
    }

# AI Analysis endpoints
@app.post("/api/analyze/sentiment")
async def analyze_sentiment(text: str):
    """Analyze sentiment of text using AI"""
    # TODO: Implement AI sentiment analysis
    return {
        "text": text,
        "sentiment": "neutral",
        "score": 0.5,
        "confidence": 0.8
    }

@app.get("/api/analyze/risk/{user_id}")
async def assess_risk(user_id: str):
    """Assess mental health risk level for a user"""
    # TODO: Implement risk assessment algorithm
    return {
        "user_id": user_id,
        "risk_level": "low",
        "factors": [],
        "recommendations": [
            "Continue regular check-ins",
            "Maintain healthy sleep schedule",
            "Practice mindfulness exercises"
        ]
    }

# User management endpoints
@app.post("/api/users/register")
async def register_user(user: UserProfile):
    """Register a new user"""
    # TODO: Implement user registration with password hashing
    return {
        "message": "User registered successfully",
        "user_id": user.user_id
    }

@app.get("/api/users/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile"""
    # TODO: Fetch from database
    return {
        "user_id": user_id,
        "profile": {}  # Placeholder
    }

# Recommendations endpoint
@app.get("/api/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    """Get personalized mental health recommendations"""
    # TODO: Implement AI-based recommendation engine
    return {
        "user_id": user_id,
        "recommendations": [
            {
                "type": "exercise",
                "title": "Morning Walk",
                "description": "Take a 20-minute walk in nature",
                "priority": "high"
            },
            {
                "type": "meditation",
                "title": "Breathing Exercise",
                "description": "5-minute guided breathing meditation",
                "priority": "medium"
            },
            {
                "type": "resource",
                "title": "Mental Health Hotline",
                "description": "24/7 support available",
                "priority": "info"
            }
        ]
    }

# ── Chatbot response engine ───────────────────────────────────────────────────

def _chat_response(message: str) -> str:
    """
    Rule-based mental health chatbot.
    Covers crisis, anxiety, stress, depression, happiness, mindfulness,
    coping strategies, sleep, loneliness, anger, and general fallback.
    """
    m = message.lower()

    # Crisis — highest priority
    if any(kw in m for kw in ["suicide", "kill myself", "end my life", "want to die",
                                "no reason to live", "better off dead", "harm myself"]):
        return (
            "I'm very concerned about what you're sharing. Please reach out for help right now. "
            "In India you can call iCall: 9152987821 or KIRAN: 1800-599-0019 (free, 24/7). "
            "You are not alone, and support is available immediately. "
            "Would you like me to share more helpline numbers?"
        )

    # Hopelessness / worthlessness
    if any(kw in m for kw in ["hopeless", "worthless", "can't go on", "give up", "unbearable",
                                "no point", "pointless", "meaningless"]):
        return (
            "It sounds like you're carrying a very heavy weight right now. "
            "Those feelings are real, but they can change with the right support. "
            "Have you been able to talk to anyone — a friend, family member, or counsellor — about how you're feeling? "
            "Sometimes just saying it out loud to someone helps more than we expect."
        )

    # Anxiety / panic
    if any(kw in m for kw in ["anxious", "anxiety", "panic", "panic attack", "worried", "fear", "nervous"]):
        return (
            "Anxiety can feel overwhelming, but your body is safe even when your mind says otherwise. "
            "Try box breathing right now: inhale for 4 counts → hold for 4 → exhale for 4 → hold for 4. "
            "Repeat 3 times. 🌬️ "
            "Would you like to tell me more about what's triggering your anxiety?"
        )

    # Stress / overwhelmed
    if any(kw in m for kw in ["stress", "stressed", "overwhelmed", "pressure", "burnout", "exhausted from work"]):
        return (
            "Stress is your mind's signal that something needs attention — you're not weak for feeling it. "
            "A few quick things that help: take a 5-minute walk, drink a glass of water, and write down the "
            "one thing that is bothering you most. Breaking it into smaller pieces makes it manageable. "
            "What is stressing you the most right now?"
        )

    # Depression / sadness
    if any(kw in m for kw in ["depressed", "depression", "sad", "unhappy", "miserable", "empty", "numb", "dark"]):
        return (
            "I'm sorry you're feeling this way. Depression is a real condition — not a weakness or a choice. "
            "A few small things that genuinely help: get some sunlight today, eat something nourishing, "
            "and try to do one tiny thing you used to enjoy. "
            "If these feelings have been lasting more than two weeks, please consider speaking to a doctor or therapist. "
            "Would you like me to share some mental health resources?"
        )

    # Loneliness
    if any(kw in m for kw in ["lonely", "alone", "isolated", "no one cares", "nobody", "no friends"]):
        return (
            "Feeling lonely is painful — and more common than people admit. "
            "You reached out here, and that takes courage. "
            "Is there one person — even someone you haven't spoken to in a while — you could send a simple message to today? "
            "Connection doesn't have to be deep to be meaningful. I'm also here to listen whenever you need."
        )

    # Anger
    if any(kw in m for kw in ["angry", "anger", "furious", "rage", "frustrated", "irritated", "annoyed"]):
        return (
            "Anger is a valid emotion — it's often telling us that a boundary was crossed or something feels unfair. "
            "Before reacting, try: step away for 2 minutes, take slow deep breaths, and ask yourself "
            "'What is the real feeling underneath this anger?' "
            "Would you like to talk about what happened?"
        )

    # Sleep problems
    if any(kw in m for kw in ["can't sleep", "insomnia", "sleep", "tired", "exhausted", "no energy", "fatigue"]):
        return (
            "Poor sleep and low energy are closely linked to mood. "
            "Try this tonight: no screens 30 minutes before bed, keep the room dark and cool, "
            "and do 4-7-8 breathing (inhale 4, hold 7, exhale 8) as you lie down. "
            "How long have you been struggling with sleep?"
        )

    # Happiness / positive
    if any(kw in m for kw in ["happy", "good", "great", "wonderful", "excited", "amazing", "grateful", "better"]):
        return (
            "That's genuinely great to hear! 😊 "
            "Positive moments are worth acknowledging — what's been going well for you? "
            "Holding onto these feelings and writing them down helps build resilience for harder days."
        )

    # Mindfulness / meditation
    if any(kw in m for kw in ["mindfulness", "meditation", "calm", "breathe", "breathing", "relax"]):
        return (
            "Mindfulness is one of the most evidence-backed tools for mental health. "
            "Here's a quick 1-minute grounding exercise — the 5-4-3-2-1 technique: "
            "Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste. "
            "This brings your mind back to the present. Want more techniques?"
        )

    # Coping strategies
    if any(kw in m for kw in ["coping", "strategies", "help me", "what should i do", "tips", "advice"]):
        return (
            "Here are 5 evidence-based coping strategies:\n"
            "1️⃣ Deep breathing (4-4-4 box breathing)\n"
            "2️⃣ Physical movement — even a 10-minute walk changes brain chemistry\n"
            "3️⃣ Journaling — write 3 sentences about how you feel\n"
            "4️⃣ Grounding — name 5 things you can see right now\n"
            "5️⃣ Social connection — send one message to someone you trust\n"
            "Which of these would you like to explore more?"
        )

    # Default
    return (
        "Thank you for sharing that with me. I'm here to listen without judgment. "
        "Can you tell me more about how you're feeling or what's been on your mind? "
        "The more you share, the better I can support you. 💙"
    )


@app.post("/api/chat")
async def chat(message: str, user_id: str):
    """
    Mental health chatbot endpoint.
    Uses a keyword-based response engine covering crisis, anxiety, depression,
    stress, loneliness, anger, sleep, and general wellbeing.
    """
    if not message or not message.strip():
        raise HTTPException(status_code=422, detail="'message' cannot be empty.")
    return {
        "user_message": message,
        "bot_response": _chat_response(message.strip()),
        "timestamp": datetime.now(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Multimodal Analysis endpoint
# ─────────────────────────────────────────────────────────────────────────────
#
# This endpoint works TODAY (no DAIC-WOZ dataset required).
# It accepts optional audio/video files and a required text transcript.
#
# When you have a trained model checkpoint (best.pt from train.py), set
#   MODEL_CHECKPOINT = Path("checkpoints/daic/best.pt")
# and the inference block below will load it automatically.
#
# ─────────────────────────────────────────────────────────────────────────────

from pathlib import Path
import json

# ── Model checkpoint priority ─────────────────────────────────────────────
# 1. eatd_fast/best.pt  — trained on real EATD-Corpus data (Colab-trained)
# 2. synthetic/best.pt  — trained on synthetic data (fallback)
_CKPT_PRIORITY = [
    Path(__file__).parent / "checkpoints" / "eatd_fast" / "best.pt",
    Path(__file__).parent / "checkpoints" / "eatd"      / "best.pt",
    Path(__file__).parent / "checkpoints" / "synthetic" / "best.pt",
]
MODEL_CHECKPOINT = next((p for p in _CKPT_PRIORITY if p.exists()), _CKPT_PRIORITY[-1])

_model   = None   # neural model (if checkpoint found)
_tfidf   = None   # TF-IDF vectorizer (used by eatd_fast model)


def _load_model():
    """
    Lazy-load whichever checkpoint exists (eatd_fast > eatd > synthetic).
    Handles both the fast TF-IDF model (train_cpu_fast.py) and the
    original BERT model (train.py) transparently.
    Returns (model, tfidf) — tfidf is None for the BERT-based model.
    """
    global _model, _tfidf
    if _model is not None:
        return _model, _tfidf

    # Re-evaluate which checkpoint exists now (may have been added after startup)
    ckpt_path = next((p for p in _CKPT_PRIORITY if p.exists()), None)
    if ckpt_path is None:
        return None, None

    try:
        import torch
        import numpy as _np
        from sklearn.feature_extraction.text import TfidfVectorizer
        import scipy.sparse as _sp
        from sklearn.feature_extraction.text import TfidfTransformer as _TT

        ckpt = torch.load(str(ckpt_path), map_location="cpu", weights_only=False)
        print(f"[multimodal] Loading checkpoint: {ckpt_path.name} from {ckpt_path.parent.name}/")

        # ── Detect model type from checkpoint keys ──────────────────────
        has_tfidf = "tfidf_vocab" in ckpt

        if has_tfidf:
            # Fast TF-IDF model (train_cpu_fast.py / Colab notebook)
            from train_cpu_fast import FastMultimodalModel
            tfidf_dim = ckpt.get("args", {}).get("tfidf_dim", 500)
            m = FastMultimodalModel(tfidf_dim=tfidf_dim)

            # Remap Colab checkpoint keys (audio/text/facial) to local names (audio_enc/text_enc/facial_enc)
            state = ckpt["model_state"]
            key_map = {"audio.": "audio_enc.", "text.": "text_enc.", "facial.": "facial_enc."}
            remapped = {}
            for k, v in state.items():
                new_k = k
                for old, new in key_map.items():
                    if k.startswith(old):
                        new_k = new + k[len(old):]
                        break
                remapped[new_k] = v
            m.load_state_dict(remapped, strict=False)
            m.eval()

            # Rebuild TF-IDF vectorizer from saved vocab + idf weights
            idf_arr = _np.array(ckpt["tfidf_idf"], dtype=_np.float64)
            tv = TfidfVectorizer(max_features=len(ckpt["tfidf_vocab"]),
                                 sublinear_tf=True, ngram_range=(1, 2))
            tv.vocabulary_ = ckpt["tfidf_vocab"]
            tv.idf_        = idf_arr
            _tt = _TT(sublinear_tf=True)
            _tt.idf_ = idf_arr
            n = len(idf_arr)
            _tt._idf_diag = _sp.diags(idf_arr, offsets=0,
                                       shape=(n, n), format="csr", dtype=_np.float64)
            tv._tfidf = _tt
            _tfidf = tv
            _model = m
            print(f"[multimodal] Fast TF-IDF model loaded. Vocab size={len(tv.vocabulary_)}")
        else:
            # Original BERT model (train.py)
            from multimodal_model import build_model
            saved_args = ckpt.get("args", {})
            m = build_model(
                task      = saved_args.get("task", "classification"),
                embed_dim = saved_args.get("embed_dim", 256),
                dropout   = 0.0,
            )
            m.load_state_dict(ckpt["model_state"])
            m.eval()
            _model = m
            _tfidf = None
            print("[multimodal] BERT model loaded.")

        return _model, _tfidf

    except Exception as e:
        print(f"[multimodal] Model load failed (will use heuristic fallback): {e}")
        return None, None


# ── Shared action plan (used by both heuristic and neural paths) ──────────────
ACTION_PLAN_MAP = {
    "critical": {
        "summary": "Immediate professional support is strongly advised.",
        "categories": [
            {
                "category": "🚨 Immediate Help",
                "priority": "urgent",
                "steps": [
                    "Call KIRAN Mental Health Helpline: 1800-599-0019 (India, free, 24/7) right now.",
                    "Call iCall: 9152987821 | Vandrevala Foundation: 1860-2662-345.",
                    "Go to your nearest hospital emergency / psychiatry OPD if you feel unsafe.",
                    "Tell a trusted person — family member, friend, or colleague — what you are experiencing.",
                ],
            },
            {
                "category": "🧠 Professional Care",
                "priority": "high",
                "steps": [
                    "Book an emergency appointment with a psychiatrist or clinical psychologist today.",
                    "If prescribed medication, take it regularly and do not stop without doctor advice.",
                    "Ask your doctor about Cognitive Behavioural Therapy (CBT) — it is proven effective for severe depression.",
                ],
            },
            {
                "category": "🏠 Immediate Safety",
                "priority": "high",
                "steps": [
                    "Remove or secure access to anything that could be used to self-harm.",
                    "Stay with someone you trust — avoid being alone for extended periods.",
                    "Inform a close contact about your current mental state so they can check in on you.",
                ],
            },
            {
                "category": "🌱 Daily Stabilisation",
                "priority": "medium",
                "steps": [
                    "Try to eat one nutritious meal today, even if appetite is low.",
                    "Get outside for at least 10 minutes — sunlight helps regulate mood.",
                    "Limit alcohol and caffeine; both worsen anxiety and depression.",
                    "Do one small task you can complete — it builds a tiny sense of achievement.",
                ],
            },
        ],
    },
    "high": {
        "summary": "Significant distress detected. Take action this week.",
        "categories": [
            {
                "category": "🏥 Professional Support",
                "priority": "high",
                "steps": [
                    "Schedule a session with a therapist or counsellor within the next 3–5 days.",
                    "Contact iCall: 9152987821 | KIRAN: 1800-599-0019 if you need to talk now.",
                    "Consider online therapy platforms (iCall, YourDOST, MindPeers) for quick access.",
                    "Share your PHQ-8 estimate with your doctor for a formal assessment.",
                ],
            },
            {
                "category": "💤 Sleep & Body",
                "priority": "high",
                "steps": [
                    "Set a fixed sleep and wake time — irregular sleep worsens depression significantly.",
                    "Avoid screens 30 minutes before bed; try the 4-7-8 breathing technique to fall asleep.",
                    "Eat regular meals. Omega-3 rich foods (walnuts, flaxseed, fish) support brain health.",
                    "Even a 20-minute brisk walk daily raises serotonin and reduces depressive symptoms.",
                ],
            },
            {
                "category": "🧘 Mind Practices",
                "priority": "medium",
                "steps": [
                    "Try 10 minutes of guided meditation daily (apps: Calm, Headspace, or YouTube).",
                    "Practice box breathing: inhale 4s → hold 4s → exhale 4s → hold 4s. Repeat 5×.",
                    "Write 3 things you felt during the day in a journal — this builds emotional awareness.",
                    "Identify and challenge one negative thought each day using CBT reframing.",
                ],
            },
            {
                "category": "👥 Social Connection",
                "priority": "medium",
                "steps": [
                    "Reach out to one trusted person today — even a short message counts.",
                    "Reduce time spent on social media; it tends to amplify negative feelings.",
                    "Join a peer support group (online or offline) for people dealing with similar challenges.",
                ],
            },
            {
                "category": "📋 Lifestyle Adjustments",
                "priority": "low",
                "steps": [
                    "Reduce workload if possible — burnout accelerates depression.",
                    "Set small, achievable goals each day to rebuild motivation and confidence.",
                    "Avoid alcohol; it is a depressant and will worsen your symptoms over time.",
                    "Spend time in nature — even a local park visit improves mood measurably.",
                ],
            },
        ],
    },
    "moderate": {
        "summary": "Moderate distress signals detected. Take proactive steps now.",
        "categories": [
            {
                "category": "🧑‍⚕️ Check-in with a Professional",
                "priority": "medium",
                "steps": [
                    "Book a session with a counsellor or therapist — even one session can help clarify your feelings.",
                    "Talk to your college counsellor, HR mental health support, or GP about how you have been feeling.",
                    "Online options: iCall (9152987821), YourDOST, MindPeers — low cost, easy to access.",
                ],
            },
            {
                "category": "🏃 Physical Wellbeing",
                "priority": "medium",
                "steps": [
                    "Walk or do light exercise for at least 20 minutes daily — it is one of the most evidence-backed mood boosters.",
                    "Prioritise 7–8 hours of sleep consistently; poor sleep doubles depressive symptoms.",
                    "Drink enough water and eat regular meals — skipping meals worsens energy and mood.",
                ],
            },
            {
                "category": "🧘 Stress & Mind",
                "priority": "medium",
                "steps": [
                    "Practice the 5-4-3-2-1 grounding technique when feeling overwhelmed: 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste.",
                    "Try box breathing for 5 minutes: inhale 4s → hold 4s → exhale 4s → hold 4s.",
                    "Use a free meditation app (Calm, Headspace, Insight Timer) for 10 minutes daily.",
                    "Schedule a daily 'worry window' — 15 minutes to think about problems, then close it.",
                ],
            },
            {
                "category": "📓 Journaling & Self-awareness",
                "priority": "low",
                "steps": [
                    "Write 3 sentences every evening: one feeling, one trigger, one thing you are grateful for.",
                    "Track your mood score each day — noticing patterns helps you act earlier next time.",
                    "Identify your top 2–3 stressors and brainstorm one small action you could take on each.",
                ],
            },
            {
                "category": "🤝 Stay Connected",
                "priority": "low",
                "steps": [
                    "Plan one social activity this week — lunch, a call, or a walk with someone you trust.",
                    "Volunteer or help someone else — it shifts focus and boosts your own mood.",
                    "Limit doom-scrolling; replace 15 minutes of social media with a hobby or a walk.",
                ],
            },
        ],
    },
    "low": {
        "summary": "You appear to be in a good mental state. Keep it up!",
        "categories": [
            {
                "category": "✅ Maintain What's Working",
                "priority": "low",
                "steps": [
                    "Continue your current self-care routines — sleep, exercise, and social connection.",
                    "Keep journaling a few times a week to maintain self-awareness.",
                    "Celebrate small wins — acknowledge your progress regularly.",
                ],
            },
            {
                "category": "🌿 Build Resilience",
                "priority": "low",
                "steps": [
                    "Practice mindfulness or guided meditation for 10 minutes daily as a preventive habit.",
                    "Read about mental health — understanding it reduces stigma and prepares you for harder days.",
                    "Build a strong support network — nurture relationships before you need them.",
                    "Learn one new stress-management technique: progressive muscle relaxation or cold-water breathing.",
                ],
            },
            {
                "category": "🎯 Growth & Purpose",
                "priority": "low",
                "steps": [
                    "Set one meaningful goal for the week and work towards it step by step.",
                    "Engage in a creative hobby — music, art, writing, cooking — for emotional expression.",
                    "Help or mentor someone else — contributing to others consistently raises subjective wellbeing.",
                ],
            },
        ],
    },
}


def _heuristic_analysis(text: str, has_audio: bool, has_video: bool) -> dict:
    """
    Pure text + linguistic-feature heuristic used when no trained model is
    available.  Returns the same schema as the model inference path so the
    frontend never needs to know the difference.
    """
    text_lower = text.lower()

    # ── Linguistic feature extraction ──────────────────────────────────────
    words = text_lower.split()
    word_count = len(words)

    # First-person pronouns (depression marker)
    first_person = sum(1 for w in words if w in {"i", "me", "my", "myself", "mine"})
    first_person_ratio = first_person / max(word_count, 1)

    # Negative / depressive vocabulary
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
    neg_ratio  = neg_count / max(word_count, 1)
    pos_ratio  = pos_count / max(word_count, 1)

    # Crisis keywords
    crisis_high = [
        "suicide", "kill myself", "end my life", "want to die",
        "no reason to live", "better off dead", "harm myself",
    ]
    crisis_mid = ["hopeless", "worthless", "can't go on", "give up", "unbearable"]
    has_crisis_high = any(kw in text_lower for kw in crisis_high)
    has_crisis_mid  = any(kw in text_lower for kw in crisis_mid)

    # ── Scoring ───────────────────────────────────────────────────────────
    depression_score = 0.0
    depression_score += min(first_person_ratio * 2.0, 0.3)   # ≤ 0.30
    depression_score += min(neg_ratio * 3.0, 0.40)            # ≤ 0.40
    depression_score -= min(pos_ratio * 2.0, 0.20)            # ≤ -0.20
    if has_crisis_high:
        depression_score += 0.60
    elif has_crisis_mid:
        depression_score += 0.30
    depression_score = float(max(0.0, min(1.0, depression_score)))

    # Modality confidence (mock values when files are absent)
    audio_conf  = 0.55 if has_audio else 0.0
    video_conf  = 0.50 if has_video else 0.0
    text_conf   = 0.85

    # Weighted fusion
    weights_sum  = text_conf + audio_conf + video_conf
    if weights_sum > 0:
        fused_score = (
            depression_score * text_conf +
            depression_score * 0.9 * audio_conf +   # audio slightly noisier
            depression_score * 0.85 * video_conf
        ) / weights_sum
    else:
        fused_score = depression_score

    # PHQ-8 estimate (scale 0–24)
    phq8_estimate = round(fused_score * 24, 1)

    # Risk bucket
    if has_crisis_high or fused_score >= 0.70:
        risk_level = "critical"
    elif fused_score >= 0.50:
        risk_level = "high"
    elif fused_score >= 0.30:
        risk_level = "moderate"
    else:
        risk_level = "low"

    # Pick action plan from module-level map
    plan = ACTION_PLAN_MAP[risk_level]
    flat_recs = [step for cat in plan["categories"] for step in cat["steps"]]

    return {
        "depression_probability": round(fused_score, 3),
        "phq8_estimate": phq8_estimate,
        "risk_level": risk_level,
        "binary_prediction": int(fused_score >= 0.40),  # 0=non-depressed, 1=depressed
        "modality_weights": {
            "text": round(text_conf / max(weights_sum, 1), 3),
            "audio": round(audio_conf / max(weights_sum, 1), 3),
            "video": round(video_conf / max(weights_sum, 1), 3),
        },
        "linguistic_features": {
            "word_count": word_count,
            "first_person_ratio": round(first_person_ratio, 3),
            "negative_word_ratio": round(neg_ratio, 3),
            "positive_word_ratio": round(pos_ratio, 3),
        },
        "crisis_flags": {
            "high_risk_detected": has_crisis_high,
            "medium_risk_detected": has_crisis_mid,
        },
        "recommendations": flat_recs,
        "action_plan": plan,
        "model_used": "heuristic",   # ← changes to "neural" when checkpoint loads
        "note": (
            "Results are based on linguistic analysis only. "
            "Connect a trained model checkpoint for full multimodal inference."
        ),
    }


class MultimodalTextRequest(BaseModel):
    """Body for the text-only multimodal endpoint variant."""
    text: str
    user_id: Optional[str] = "anonymous"


@app.post("/api/multimodal/analyze")
async def multimodal_analyze(
    text: str = Form(..., description="Interview/journal transcript text"),
    user_id: str = Form("anonymous"),
    audio_file: Optional[UploadFile] = File(None, description="Audio file (.wav/.mp3) — optional"),
    video_file: Optional[UploadFile] = File(None, description="Video file (.mp4/.avi) — optional"),
):
    """
    Multimodal mental health analysis.

    Works in three modes:
    - TEXT ONLY      : just pass 'text' form field (always available)
    - TEXT + AUDIO   : also upload audio_file
    - TEXT + AUDIO + VIDEO: upload both files

    When a trained model checkpoint exists at:
      backend/checkpoints/daic/best.pt   (real DAIC-WOZ model)
      backend/checkpoints/synthetic/best.pt  (synthetic-data model)
    it is loaded and used for inference.  Otherwise a linguistic heuristic
    is used that requires no additional dependencies.

    DATASET SWAP NOTE
    -----------------
    No changes needed in this file when you switch to the real DAIC-WOZ model.
    Just train with:
        python run_pipeline.py --mode daic --daic_root <path>
    The checkpoint at backend/checkpoints/daic/best.pt will be picked up
    automatically on the next request.
    """
    has_audio = audio_file is not None and audio_file.filename != ""
    has_video = video_file is not None and video_file.filename != ""

    if not text or not text.strip():
        raise HTTPException(status_code=422, detail="'text' field is required and cannot be empty.")

    # ── Try loading the trained neural model ──────────────────────────────
    model, tfidf = _load_model()

    if model is not None:
        try:
            import torch
            N_MELS_      = 128
            MAX_AU_FRAMES_ = 300
            N_AU_        = 17

            # Audio tensor
            if has_audio:
                audio_bytes = await audio_file.read()
                import librosa
                y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000, duration=60)
                mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=N_MELS_)
                mel = librosa.power_to_db(mel, ref=np.max)
                mel = (mel - mel.min()) / (mel.max() - mel.min() + 1e-8)
                mel = mel[:, :128] if mel.shape[1] >= 128 else np.pad(mel, ((0, 0), (0, 128 - mel.shape[1])))
                audio_tensor = torch.tensor(mel, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
            else:
                audio_tensor = torch.zeros(1, 1, N_MELS_, 128)

            # Facial tensor (zeros — OpenFace not available at runtime)
            facial_tensor = torch.zeros(1, MAX_AU_FRAMES_, N_AU_)

            with torch.no_grad():
                if tfidf is not None:
                    # ── Fast TF-IDF model (Colab-trained) ─────────────
                    vec = tfidf.transform([text.strip()]).toarray().astype("float32")
                    text_tensor = torch.tensor(vec, dtype=torch.float32)
                    out = model(audio_tensor, text_tensor, facial_tensor)
                else:
                    # ── BERT model ─────────────────────────────────────
                    from transformers import BertTokenizer
                    from dataset import MAX_TEXT_LEN, AU_COLS
                    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
                    enc = tokenizer(text, max_length=MAX_TEXT_LEN, padding="max_length",
                                    truncation=True, return_tensors="pt")
                    out = model(audio_tensor, enc["input_ids"], enc["attention_mask"], facial_tensor)

                probs      = torch.softmax(out, dim=1)[0]
                dep_prob   = float(probs[1])
                pred_class = int(probs.argmax())
                phq8_estimate = round(dep_prob * 24, 1)

            if dep_prob >= 0.70:   risk_level = "critical"
            elif dep_prob >= 0.50: risk_level = "high"
            elif dep_prob >= 0.30: risk_level = "moderate"
            else:                  risk_level = "low"

            # Build action plan from module-level map using neural risk_level
            plan = ACTION_PLAN_MAP[risk_level]
            flat_recs = [step for cat in plan["categories"] for step in cat["steps"]]
            return {
                "depression_probability": round(dep_prob, 3),
                "phq8_estimate": phq8_estimate,
                "risk_level": risk_level,
                "binary_prediction": pred_class,
                "modality_weights": {"text": 0.6, "audio": 0.25, "video": 0.15},
                "linguistic_features": {},
                "crisis_flags": {
                    "high_risk_detected": dep_prob >= 0.70,
                    "medium_risk_detected": dep_prob >= 0.50,
                },
                "recommendations": flat_recs,
                "action_plan": plan,
                "model_used": "neural",
                "note": "Inference from trained multimodal neural model (EATD-Corpus).",
            }
        except Exception as e:
            print(f"[multimodal] Neural inference error, falling back to heuristic: {e}")

    # ── Heuristic fallback (no checkpoint / inference error) ──────────────
    result = _heuristic_analysis(text, has_audio, has_video)
    return result


@app.post("/api/multimodal/analyze/text")
async def multimodal_analyze_text(req: MultimodalTextRequest):
    """
    JSON-body variant of /api/multimodal/analyze for text-only analysis.
    Useful for quick testing without multipart form uploads.

    Example:
        curl -X POST http://localhost:8000/api/multimodal/analyze/text \\
             -H 'Content-Type: application/json' \\
             -d '{"text": "I have been feeling very sad and hopeless lately."}'
    """
    result = _heuristic_analysis(req.text.strip(), has_audio=False, has_video=False)
    model, _ = _load_model()
    if model is not None:
        result["note"] = "Text-only JSON endpoint — use /api/multimodal/analyze with file uploads for full multimodal inference."
    return result


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# Made with Bob

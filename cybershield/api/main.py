"""
CyberShield AI — FastAPI backend

Modelni HTTP API sifatida taqdim etadi. Telegram bot, veb-frontend yoki
boshqa har qanday klient shu API orqali matnni tahlil qilishi mumkin.

Ishga tushirish:
    cd /home/claude/cybershield/api
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

Interaktiv hujjatlar (Swagger UI): http://localhost:8000/docs
"""

import sys
import os
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request

import joblib

# model/ papkasidagi modullarni import qilish uchun yo'lni qo'shamiz
MODEL_DIR = Path(__file__).resolve().parent.parent / "model"
sys.path.insert(0, str(MODEL_DIR))

from text_utils import normalize_text  # noqa: E402, F401 -- joblib pickle uchun kerak
from predict_with_confidence import classify_with_confidence  # noqa: E402
from url_utils import analyze_urls_in_text  # noqa: E402
from api_keys import (  # noqa: E402
    is_valid_key, get_owner, generate_api_key, revoke_key, list_keys,
    get_or_create_admin_key, is_admin_key,
)

# ---------------------------------------------------------------------------
# SOZLAMALAR
# ---------------------------------------------------------------------------

MODEL_PATH = MODEL_DIR / "cybershield_model.joblib"
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
REQUEST_LOG_PATH = LOG_DIR / "requests.jsonl"
FEEDBACK_LOG_PATH = LOG_DIR / "feedback.jsonl"

MAX_TEXT_LENGTH = 3000  # juda uzun matnlarni rad etish (DoS'dan himoya)

# ---------------------------------------------------------------------------
# RATE LIMITING SOZLAMALARI
# API kalit bo'yicha cheklaymiz (agar kalit bo'lmasa, IP bo'yicha) —
# bu bitta kalitning boshqalarga ta'sir qilmasligini ta'minlaydi.
# ---------------------------------------------------------------------------

def rate_limit_key(request: Request) -> str:
    api_key = request.headers.get("X-API-Key")
    return api_key if api_key else get_remote_address(request)


limiter = Limiter(key_func=rate_limit_key, default_limits=["60/minute"])

# ---------------------------------------------------------------------------
# MODELNI YUKLASH (server ishga tushganda BIR MARTA)
# ---------------------------------------------------------------------------

app = FastAPI(
    title="CyberShield AI API",
    description="O'zbek tilidagi phishing/scam matnlarni aniqlash xizmati",
    version="1.1.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — frontend/veb-demo boshqa domendan so'rov yubora olishi uchun
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # productionda aniq domenlar bilan cheklash tavsiya etiladi
    allow_methods=["*"],
    allow_headers=["*"],
)

_model = None  # global model obyekti, startup paytida yuklanadi


@app.on_event("startup")
def load_model():
    global _model
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model fayli topilmadi: {MODEL_PATH}")
    _model = joblib.load(MODEL_PATH)
    print(f"[CyberShield AI] Model yuklandi: {MODEL_PATH}")


# ---------------------------------------------------------------------------
# AUTENTIFIKATSIYA
# ---------------------------------------------------------------------------

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(api_key: str = Security(api_key_header)) -> str:
    """Har bir himoyalangan endpoint uchun API kalitni tekshiradi."""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API kalit kerak. X-API-Key headerini qo'shing.",
        )
    if not is_valid_key(api_key):
        raise HTTPException(status_code=403, detail="Noto'g'ri yoki bekor qilingan API kalit.")
    return api_key


def require_admin_key(api_key: str = Security(api_key_header)) -> str:
    """Admin panel endpointlari uchun alohida, kuchliroq tekshiruv."""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Admin kalit kerak. X-API-Key headerida admin kalitni yuboring.",
        )
    if not is_admin_key(api_key):
        raise HTTPException(status_code=403, detail="Bu admin kaliti emas yoki noto'g'ri.")
    return api_key


# ---------------------------------------------------------------------------
# SO'ROV / JAVOB SXEMALARI
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_TEXT_LENGTH, description="Tahlil qilinadigan matn")


class BatchAnalyzeRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=25, description="Tahlil qilinadigan matnlar ro'yxati (maks. 25 ta)")


class AnalyzeResponse(BaseModel):
    request_id: str
    text: str
    raw_label: str
    confidence: float
    risk_level: str
    message: str
    recommend_manual_review: bool


class FeedbackRequest(BaseModel):
    request_id: str = Field(..., description="Avvalgi /analyze so'rovining request_id qiymati")
    was_correct: bool = Field(..., description="Model bashorati to'g'ri bo'lganmi")
    correct_label: str | None = Field(None, description="Agar noto'g'ri bo'lsa, to'g'ri label ('phishing'/'safe')")


# ---------------------------------------------------------------------------
# YORDAMCHI: LOGLASH
# ---------------------------------------------------------------------------

def log_request(entry: dict, path: Path):
    """Har bir so'rovni JSONL formatida saqlaydi (keyinchalik tahlil/o'qitish uchun)."""
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        # Loglash xatosi asosiy funksiyani to'xtatmasligi kerak
        print(f"[OGOHLANTIRISH] Loglashda xato: {e}")


# ---------------------------------------------------------------------------
# ENDPOINTLAR
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Tizim"])
def health_check():
    """Server va model holatini tekshirish."""
    return {
        "status": "ok" if _model is not None else "model_not_loaded",
        "model_loaded": _model is not None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/analyze", response_model=AnalyzeResponse, tags=["Tahlil"])
@limiter.limit("20/minute")
def analyze_text(request: Request, payload: AnalyzeRequest, api_key: str = Depends(require_api_key)):
    """
    Matnni tahlil qilib, phishing/scam ekanligini ishonch darajasi bilan qaytaradi.

    Talab qilinadi: X-API-Key headeri.
    Cheklov: bir kalit uchun daqiqasiga 20 ta so'rov.

    Javobdagi risk_level qiymatlari:
      - "yuqori_xavf" -> aniq phishing, yuqori ishonch
      - "shubhali"    -> ehtiyot bo'lish tavsiya etiladi
      - "xavfsiz"     -> aniq xavfsiz, yuqori ishonch
      - "aniq_emas"   -> model ishonchi past, qo'lda tekshirish tavsiya etiladi
    """
    if _model is None:
        raise HTTPException(status_code=503, detail="Model hali yuklanmagan")

    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Matn bo'sh bo'lishi mumkin emas")

    result = classify_with_confidence(text, model=_model)
    request_id = str(uuid.uuid4())

    log_entry = {
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "client": get_owner(api_key),
        **result,
    }
    log_request(log_entry, REQUEST_LOG_PATH)

    return AnalyzeResponse(request_id=request_id, **result)


@app.post("/feedback", tags=["Feedback"])
@limiter.limit("30/minute")
def submit_feedback(request: Request, payload: FeedbackRequest, api_key: str = Depends(require_api_key)):
    """
    Foydalanuvchi (yoki bot) modelning bashorati to'g'ri/noto'g'ri ekanini
    bildirishi mumkin. Bu ma'lumot keyinchalik datasetni haqiqiy xatolar
    asosida kengaytirish uchun ishlatiladi (5-tsikldagi qo'lda topilgan
    xatolarga o'xshab, lekin endi REAL foydalanuvchilardan).
    """
    entry = payload.model_dump()
    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    entry["client"] = get_owner(api_key)
    log_request(entry, FEEDBACK_LOG_PATH)
    return {"status": "qabul qilindi", "request_id": payload.request_id}


@app.get("/stats", tags=["Tizim"])
def get_stats(api_key: str = Depends(require_api_key)):
    """Oddiy statistika: jami so'rovlar, taqsimot risk darajalari bo'yicha."""
    if not REQUEST_LOG_PATH.exists():
        return {"total_requests": 0}

    total = 0
    risk_counts = {}
    with open(REQUEST_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            total += 1
            level = entry.get("risk_level", "noma'lum")
            risk_counts[level] = risk_counts.get(level, 0) + 1

    return {"total_requests": total, "risk_level_distribution": risk_counts}


@app.get("/", tags=["Tizim"])
def root():
    return {
        "name": "CyberShield AI API",
        "docs": "/docs",
        "endpoints": [
            "/analyze (POST)", "/analyze/batch (POST)", "/analyze/urls (POST)",
            "/feedback (POST)", "/stats (GET)", "/health (GET)",
            "/admin/keys (GET, POST) (admin kalit kerak)",
        ],
    }


# ---------------------------------------------------------------------------
# BATCH TAHLIL — bir nechta matnni bitta so'rovda tekshirish
# ---------------------------------------------------------------------------

@app.post("/analyze/batch", tags=["Tahlil"])
@limiter.limit("5/minute")
def analyze_batch(request: Request, payload: BatchAnalyzeRequest, api_key: str = Depends(require_api_key)):
    """
    Bir nechta matnni (maks. 25 ta) bitta so'rovda tahlil qiladi.

    Bu Telegram bot uchun foydali: masalan, foydalanuvchi guruh chatidagi
    bir nechta xabarni birdaniga tekshirmoqchi bo'lsa.

    Cheklov: bir kalit uchun daqiqasiga 5 ta BATCH so'rov (har biri 25
    matngacha bo'lishi mumkin, shuning uchun umumiy yuklama nazorat qilinadi).
    """
    if _model is None:
        raise HTTPException(status_code=503, detail="Model hali yuklanmagan")

    results = []
    for text in payload.texts:
        text = text.strip()
        if not text:
            results.append({"text": text, "error": "Bo'sh matn o'tkazib yuborildi"})
            continue

        result = classify_with_confidence(text, model=_model)
        request_id = str(uuid.uuid4())

        log_entry = {
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "client": get_owner(api_key),
            "batch": True,
            **result,
        }
        log_request(log_entry, REQUEST_LOG_PATH)

        results.append({"request_id": request_id, **result})

    return {"count": len(results), "results": results}


# ---------------------------------------------------------------------------
# URL TAHLILI — matn ichidagi havolalarni ajratib, tekshirish
# ---------------------------------------------------------------------------

@app.post("/analyze/urls", tags=["Tahlil"])
@limiter.limit("30/minute")
def analyze_urls(request: Request, payload: AnalyzeRequest, api_key: str = Depends(require_api_key)):
    """
    Matn ichidagi havolalarni (URL/domen) ajratib oladi va har birini
    ma'lum ishonchli domenlar ro'yxati va shubhali naqshlar asosida tekshiradi.

    Eslatma: bu to'liq domen-obro'si bazasi emas, MVP darajasidagi evristik
    tekshiruv. "ishonchli" bo'lmagan domen albatta xavfli degani emas —
    lekin "shubhali" belgilangan domenlarga alohida ehtiyot bo'lish kerak.
    """
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Matn bo'sh bo'lishi mumkin emas")

    url_results = analyze_urls_in_text(text)
    return {
        "text": text,
        "urls_found": len(url_results),
        "urls": url_results,
    }


# ---------------------------------------------------------------------------
# ADMIN PANEL — API kalitlarni boshqarish
# Bu endpointlar oddiy mijoz kaliti bilan emas, faqat ADMIN kalit bilan ochiladi.
# ---------------------------------------------------------------------------

class CreateKeyRequest(BaseModel):
    owner: str = Field(..., min_length=1, max_length=100, description="Yangi kalit egasining nomi")


class RevokeKeyRequest(BaseModel):
    api_key: str = Field(..., description="Bekor qilinadigan kalit")


@app.get("/admin/keys", tags=["Admin"])
def admin_list_keys(admin_key: str = Depends(require_admin_key)):
    """Barcha mijoz kalitlarini ro'yxat qiladi (kalitning o'zi maskalangan holda)."""
    return {"keys": list_keys()}


@app.post("/admin/keys", tags=["Admin"])
def admin_create_key(payload: CreateKeyRequest, admin_key: str = Depends(require_admin_key)):
    """Yangi mijoz API kalitini yaratadi."""
    new_key = generate_api_key(payload.owner)
    return {"owner": payload.owner, "api_key": new_key, "note": "Bu kalitni xavfsiz joyda saqlang, qayta ko'rsatilmaydi."}


@app.post("/admin/keys/revoke", tags=["Admin"])
def admin_revoke_key(payload: RevokeKeyRequest, admin_key: str = Depends(require_admin_key)):
    """Mijoz kalitini bekor qiladi."""
    success = revoke_key(payload.api_key)
    if not success:
        raise HTTPException(status_code=404, detail="Bunday kalit topilmadi")
    return {"status": "bekor qilindi", "api_key_preview": payload.api_key[:8] + "..."}

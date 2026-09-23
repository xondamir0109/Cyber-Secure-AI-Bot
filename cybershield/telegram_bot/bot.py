"""
CyberShield AI — Telegram bot

Foydalanuvchi yuborgan matnni CyberShield AI API'ga ('/analyze') yuboradi
va natijani (ishonch darajasi bilan) chiroyli formatda qaytaradi.

Bot va API alohida jarayonlar sifatida ishlaydi:
    Telegram foydalanuvchisi -> Bot -> HTTP so'rov -> FastAPI backend -> Model

Ishga tushirish:
    1. .env faylida BOT_TOKEN va API_KEY ni to'ldiring (yoki muhit
       o'zgaruvchisi sifatida bering)
    2. API backend allaqachon ishlab turgan bo'lishi kerak (../api/main.py)
    3. python3 bot.py
"""

import os
import logging
import httpx

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SOZLAMALAR
# Haqiqiy qiymatlarni muhit o'zgaruvchisi orqali bering:
#   export BOT_TOKEN="123456:ABC-DEF..."
#   export CYBERSHIELD_API_KEY="cs_..."
#   export CYBERSHIELD_API_URL="http://localhost:8000"
# ---------------------------------------------------------------------------

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_KEY = os.environ.get("CYBERSHIELD_API_KEY", "")
API_URL = os.environ.get("CYBERSHIELD_API_URL", "http://localhost:8000")

MAX_MESSAGE_LENGTH = 3000

WELCOME_MESSAGE = (
    "🛡️ *CyberShield AI* ga xush kelibsiz!\n\n"
    "Men sizga phishing va scam xabarlarni aniqlashda yordam beraman.\n\n"
    "Shubhali SMS, Telegram xabari yoki emailni menga yuboring — men uni "
    "tahlil qilib, xavf darajasini aytib beraman.\n\n"
    "Buyruqlar:\n"
    "/start — botni qayta ishga tushirish\n"
    "/help — yordam"
)

HELP_MESSAGE = (
    "📖 *Qanday ishlatiladi:*\n\n"
    "Shubhali deb o'ylagan xabaringizni menga to'g'ridan-to'g'ri yuboring. "
    "Men uni tahlil qilib, quyidagi natijalardan birini qaytaraman:\n\n"
    "🔴 *YUQORI XAVF* — bu aniq phishing, hech qanday havolani ochmang\n"
    "🟡 *SHUBHALI* — ehtiyot bo'ling, shaxsiy ma'lumot yubormang\n"
    "🟢 *XAVFSIZ* — xavf aniqlanmadi\n"
    "⚪ *ANIQ EMAS* — tizim ishonchli xulosa chiqara olmadi, o'zingiz tekshiring\n\n"
    "Natijadan keyin \"To'g'ri\" yoki \"Noto'g'ri\" tugmasini bosib, "
    "botni yaxshilashimizga yordam bera olasiz."
)

RISK_EMOJI = {
    "yuqori_xavf": "🔴",
    "shubhali": "🟡",
    "xavfsiz": "🟢",
    "aniq_emas": "⚪",
}


# ---------------------------------------------------------------------------
# API BILAN ALOQA
# ---------------------------------------------------------------------------

async def call_analyze_api(text: str) -> dict:
    """CyberShield AI backendining /analyze endpointini chaqiradi."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{API_URL}/analyze",
            headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
            json={"text": text},
        )
        response.raise_for_status()
        return response.json()


async def call_feedback_api(request_id: str, was_correct: bool):
    """Foydalanuvchi feedbackini backendga yuboradi."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(
            f"{API_URL}/feedback",
            headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
            json={"request_id": request_id, "was_correct": was_correct},
        )


# ---------------------------------------------------------------------------
# BUYRUQ ISHLOVCHILARI
# ---------------------------------------------------------------------------

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_MESSAGE, parse_mode="Markdown")


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi yuborgan har qanday oddiy matnni tahlil qiladi."""
    text = update.message.text

    if not text or not text.strip():
        await update.message.reply_text("Iltimos, tahlil qilish uchun matn yuboring.")
        return

    if len(text) > MAX_MESSAGE_LENGTH:
        await update.message.reply_text(
            f"Matn juda uzun (maks. {MAX_MESSAGE_LENGTH} belgi). Qisqaroq qism yuboring."
        )
        return

    # Foydalanuvchiga tez javob berish uchun "yozmoqda..." holatini ko'rsatamiz
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        result = await call_analyze_api(text)
    except httpx.HTTPStatusError as e:
        logger.error(f"API xatosi: {e}")
        await update.message.reply_text(
            "⚠️ Tizimda vaqtinchalik xatolik. Birozdan so'ng qayta urinib ko'ring."
        )
        return
    except httpx.RequestError as e:
        logger.error(f"API bilan bog'lanishda xato: {e}")
        await update.message.reply_text(
            "⚠️ Xizmatga ulanib bo'lmadi. Administrator bilan bog'laning."
        )
        return

    emoji = RISK_EMOJI.get(result["risk_level"], "")
    response_text = f"{result['message']}"

    # "To'g'ri / Noto'g'ri" feedback tugmalari
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ To'g'ri", callback_data=f"fb_correct_{result['request_id']}"),
            InlineKeyboardButton("❌ Noto'g'ri", callback_data=f"fb_wrong_{result['request_id']}"),
        ]
    ])

    await update.message.reply_text(response_text, reply_markup=keyboard)


async def handle_feedback_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'To'g'ri'/'Noto'g'ri' tugmalari bosilganda ishlaydi."""
    query = update.callback_query
    await query.answer()

    data = query.data  # masalan: "fb_correct_b331b5ec-..."
    parts = data.split("_", 2)
    if len(parts) != 3:
        return

    _, verdict, request_id = parts
    was_correct = verdict == "correct"

    try:
        await call_feedback_api(request_id, was_correct)
        thanks = "Rahmat! Fikringiz qabul qilindi. 🙏" if was_correct else "Rahmat! Buni tuzatishga harakat qilamiz. 🙏"
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(thanks)
    except Exception as e:
        logger.error(f"Feedback yuborishda xato: {e}")


# ---------------------------------------------------------------------------
# ASOSIY ISHGA TUSHIRISH
# ---------------------------------------------------------------------------

def build_application() -> Application:
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN muhit o'zgaruvchisi topilmadi. "
            "export BOT_TOKEN='sizning_tokeningiz' orqali bering."
        )
    if not API_KEY:
        raise RuntimeError(
            "CYBERSHIELD_API_KEY muhit o'zgaruvchisi topilmadi. "
            "API'dan 'python3 api_keys.py telegram_bot' orqali kalit oling."
        )

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(CallbackQueryHandler(handle_feedback_callback))

    return application


def main():
    app = build_application()
    logger.info("CyberShield AI bot ishga tushmoqda...")
    app.run_polling()


if __name__ == "__main__":
    main()

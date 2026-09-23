"""
Bot handler funksiyalarini HAQIQIY Telegram serverisiz sinash.

Bu muhitda tarmoq faqat ma'lum domenlarga ruxsat etilgan (api.telegram.org
kirmaydi), shuning uchun botni jonli ishga tushirib bo'lmaydi. Buning o'rniga:
  1. Haqiqiy FastAPI backendni ishga tushiramiz (localhost)
  2. Telegram Update/Context obyektlarini soxta (mock) qilamiz
  3. bot.py dagi handler funksiyalarini to'g'ridan-to'g'ri chaqiramiz
  4. Ular botning reply_text() metodini nima bilan chaqirganini tekshiramiz

Bu bot -> API -> model butun zanjirini sinaydi, faqat Telegram
transport qatlamini soxtalashtiradi.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bot as bot_module


async def simulate_message(text: str):
    """Foydalanuvchi 'text' matnini yuborganini simulyatsiya qiladi."""
    update = MagicMock()
    update.message.text = text
    update.message.reply_text = AsyncMock()
    update.effective_chat.id = 12345

    context = MagicMock()
    context.bot.send_chat_action = AsyncMock()

    await bot_module.handle_text_message(update, context)

    # reply_text qanday chaqirilganini ko'ramiz
    call_args = update.message.reply_text.call_args
    return call_args


async def main():
    test_messages = [
        "Kartangiz bloklanadi, tasdiqlash kodini yuboring!",
        "Ertaga soat 15:00da uchrashamiz.",
        "",  # bo'sh matn holati
    ]

    print("=" * 80)
    print("BOT HANDLER SINOVI (Telegram serversiz, haqiqiy API bilan)")
    print("=" * 80)

    for text in test_messages:
        print(f"\n--- Foydalanuvchi yubordi: {text!r} ---")
        try:
            call_args = await simulate_message(text)
            if call_args:
                args, kwargs = call_args
                reply = args[0] if args else kwargs.get("text", "")
                print(f"Bot javobi: {reply}")
                if "reply_markup" in kwargs:
                    print("(Feedback tugmalari biriktirilgan: ✅ To'g'ri / ❌ Noto'g'ri)")
        except Exception as e:
            print(f"XATO: {e}")

    print("\n" + "=" * 80)
    print("/start va /help buyruqlarini sinash")
    print("=" * 80)

    update = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    await bot_module.start_command(update, context)
    print(f"\n/start javobi:\n{update.message.reply_text.call_args[0][0]}")

    update2 = MagicMock()
    update2.message.reply_text = AsyncMock()
    await bot_module.help_command(update2, context)
    print(f"\n/help javobi:\n{update2.message.reply_text.call_args[0][0]}")


if __name__ == "__main__":
    asyncio.run(main())

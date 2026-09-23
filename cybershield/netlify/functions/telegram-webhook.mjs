// CyberShield AI — Telegram webhook handler (Netlify Function)
//
// Telegram foydalanuvchi xabar yuborganda, Telegram bu funksiyaga POST
// so'rov yuboradi (webhook rejimi). Funksiya xabarni tahlil qilib,
// Telegram Bot API orqali javob qaytaradi.
//
// MUHIM CHEKLOV: Netlify Functions statedir (holatsiz) ishlaydi -- har bir
// chaqiriq mustaqil, hech narsa xotirada saqlanmaydi. Shuning uchun:
//   - Feedback tugmalari bosilganda javob beriladi, LEKIN natija hech
//     qayerga yozib qo'yilmaydi (agar buni xohlasangiz, Netlify Blobs
//     yoki tashqi baza -- masalan Supabase -- ulash kerak bo'ladi)
//   - Har bir so'rov modelni JSON fayllardan qaytadan yuklaydi (bu juda
//     tez, chunki fayllar kichik -- ~0.65MB)

import { predict } from "./lightweight_model/predict.mjs";
import wordFeatures from "./lightweight_model/word_features.mjs";
import charFeatures from "./lightweight_model/char_features.mjs";
import modelConfig from "./lightweight_model/config.mjs";

const BOT_TOKEN = Netlify.env.get("BOT_TOKEN");
const TELEGRAM_API = `https://api.telegram.org/bot${BOT_TOKEN}`;

const RISK_EMOJI = {
  yuqori_xavf: "🔴",
  shubhali: "🟡",
  xavfsiz: "🟢",
  aniq_emas: "⚪",
};

const HIGH_CONFIDENCE = 0.85;
const MEDIUM_CONFIDENCE = 0.65;

// classify_with_confidence (Python) bilan AYNAN bir xil mantiq
function classifyWithConfidence(text) {
  const { predicted, proba } = predict(text, wordFeatures, charFeatures, modelConfig);
  const confidence = proba[predicted];

  let riskLevel, message;

  if (confidence < MEDIUM_CONFIDENCE) {
    riskLevel = "aniq_emas";
    message = `⚪ ANIQ EMAS (${Math.round(confidence * 100)}% ishonch). Tizim bu xabarni ishonchli tasniflay olmadi. Iltimos, havola yoki jo'natuvchini qo'lda tekshiring.`;
  } else if (predicted === "phishing") {
    if (confidence >= HIGH_CONFIDENCE) {
      riskLevel = "yuqori_xavf";
      message = `🔴 YUQORI XAVF — PHISHING (${Math.round(confidence * 100)}% ishonch). Havolani ochmang, ma'lumot yubormang.`;
    } else {
      riskLevel = "shubhali";
      message = `🟡 SHUBHALI (${Math.round(confidence * 100)}% ishonch). Ehtiyot bo'ling, shaxsiy ma'lumot yubormang.`;
    }
  } else {
    if (confidence >= HIGH_CONFIDENCE) {
      riskLevel = "xavfsiz";
      message = `🟢 XAVFSIZ (${Math.round(confidence * 100)}% ishonch).`;
    } else {
      riskLevel = "shubhali";
      message = `🟡 EHTIYOT BO'LING (${Math.round(confidence * 100)}% ishonch). Xavfsiz ko'rinsada, to'liq ishonch yo'q.`;
    }
  }

  return { predicted, confidence, riskLevel, message };
}

async function telegramApiCall(method, body) {
  const response = await fetch(`${TELEGRAM_API}/${method}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return response.json();
}

async function sendMessage(chatId, text, options = {}) {
  const body = { chat_id: chatId, text, ...options };
  return telegramApiCall("sendMessage", body);
}

const WELCOME_MESSAGE = `🛡️ *CyberShield AI* ga xush kelibsiz!

Men sizga phishing va scam xabarlarni aniqlashda yordam beraman.

Shubhali SMS, Telegram xabari yoki emailni menga yuboring — men uni tahlil qilib, xavf darajasini aytib beraman.

Buyruqlar:
/start — botni qayta ishga tushirish
/help — yordam`;

const HELP_MESSAGE = `📖 *Qanday ishlatiladi:*

Shubhali deb o'ylagan xabaringizni menga to'g'ridan-to'g'ri yuboring.

🔴 *YUQORI XAVF* — aniq phishing
🟡 *SHUBHALI* — ehtiyot bo'ling
🟢 *XAVFSIZ* — xavf aniqlanmadi
⚪ *ANIQ EMAS* — o'zingiz tekshiring`;

export default async (req) => {
  if (req.method !== "POST") {
    return new Response("CyberShield AI Telegram webhook ishlayapti.", { status: 200 });
  }

  let update;
  try {
    update = await req.json();
  } catch {
    return new Response("Bad request", { status: 400 });
  }

  try {
    // --- Oddiy matnli xabar ---
    if (update.message && update.message.text) {
      const chatId = update.message.chat.id;
      const text = update.message.text.trim();

      if (text === "/start") {
        await sendMessage(chatId, WELCOME_MESSAGE, { parse_mode: "Markdown" });
      } else if (text === "/help") {
        await sendMessage(chatId, HELP_MESSAGE, { parse_mode: "Markdown" });
      } else if (text.length > 0) {
        const result = classifyWithConfidence(text);
        const keyboard = {
          inline_keyboard: [[
            { text: "✅ To'g'ri", callback_data: "fb_correct" },
            { text: "❌ Noto'g'ri", callback_data: "fb_wrong" },
          ]],
        };
        await sendMessage(chatId, result.message, { reply_markup: keyboard });
      }
    }

    // --- Feedback tugmasi bosilganda ---
    if (update.callback_query) {
      const callbackQuery = update.callback_query;
      const chatId = callbackQuery.message.chat.id;

      await telegramApiCall("answerCallbackQuery", { callback_query_id: callbackQuery.id });

      const thanks =
        callbackQuery.data === "fb_correct"
          ? "Rahmat! Fikringiz qabul qilindi. 🙏"
          : "Rahmat! Buni tuzatishga harakat qilamiz. 🙏";
      await sendMessage(chatId, thanks);

      // Eslatma: bu yerda feedback hech qayerga saqlanmaydi (Netlify
      // Functions holatsiz). Doimiy saqlash uchun Netlify Blobs yoki
      // tashqi baza (Supabase, Firebase) ulash kerak bo'ladi.
    }

    return new Response("OK", { status: 200 });
  } catch (error) {
    console.error("Xatolik:", error);
    return new Response("OK", { status: 200 }); // Telegramga har doim 200 qaytarish tavsiya etiladi
  }
};

export const config = {
  path: "/telegram-webhook",
};

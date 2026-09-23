/**
 * telegram-webhook.mjs mantiqini HAQIQIY Telegram serverisiz sinash.
 *
 * global.fetch ni soxtalashtiramiz (mock), shunda haqiqiy tarmoq so'rovi
 * yuborilmaydi, lekin funksiya nima yubormoqchi bo'lganini ko'ramiz.
 * Netlify global obyektini ham soxtalashtiramiz (BOT_TOKEN uchun).
 */

globalThis.Netlify = {
  env: { get: (key) => process.env[key] || "FAKE_TOKEN_FOR_TEST" },
};

const sentCalls = [];
const realFetch = globalThis.fetch;
globalThis.fetch = async (url, options) => {
  const body = options?.body ? JSON.parse(options.body) : null;
  sentCalls.push({ url, body });
  // Telegram API'ning muvaffaqiyatli javobini soxtalashtiramiz
  return {
    json: async () => ({ ok: true, result: { message_id: 1 } }),
  };
};

const { default: handler } = await import("./telegram-webhook.mjs");

function makeRequest(bodyObj) {
  return {
    method: "POST",
    json: async () => bodyObj,
  };
}

async function runTest(label, updateBody) {
  sentCalls.length = 0;
  const response = await handler(makeRequest(updateBody));
  console.log(`\n--- ${label} ---`);
  console.log(`Javob statusi: ${response.status}`);
  for (const call of sentCalls) {
    const method = call.url.split("/").pop();
    console.log(`  -> Telegram API chaqirildi: ${method}`);
    if (call.body.text) {
      console.log(`     Matn: ${call.body.text.slice(0, 100)}`);
    }
    if (call.body.reply_markup) {
      console.log(`     Tugmalar: ${JSON.stringify(call.body.reply_markup.inline_keyboard)}`);
    }
  }
  return sentCalls;
}

async function main() {
  await runTest("/start buyrug'i", {
    message: { chat: { id: 111 }, text: "/start" },
  });

  await runTest("/help buyrug'i", {
    message: { chat: { id: 111 }, text: "/help" },
  });

  await runTest("Phishing xabar", {
    message: { chat: { id: 111 }, text: "Kartangiz bloklanadi, tasdiqlash kodini yuboring!" },
  });

  await runTest("Xavfsiz xabar", {
    message: { chat: { id: 111 }, text: "Ertaga soat 15:00da uchrashamiz." },
  });

  await runTest("Feedback tugmasi (To'g'ri)", {
    callback_query: {
      id: "cb123",
      data: "fb_correct",
      message: { chat: { id: 111 } },
    },
  });

  await runTest("Bo'sh yangilanish (GET so'rov simulyatsiyasi)", {});

  console.log("\n\n✅ Barcha sinovlar xatosiz yakunlandi.");
}

main();

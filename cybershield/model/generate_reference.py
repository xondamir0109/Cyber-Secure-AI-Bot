"""
Sklearn modelidan katta hajmdagi test matnlari uchun ETALON natijalarni
saqlaydi. Bu fayl keyinchalik JavaScript (Node.js) versiyasini tekshirish
uchun "haqiqat manbai" (ground truth) sifatida ishlatiladi.
"""

import json
import joblib

model = joblib.load("/home/claude/cybershield/model/cybershield_model.joblib")

# Har xil uzunlik, mavzu va chegara-holatlarni qamrab oluvchi keng test to'plami
test_texts = [
    "Kartangiz bloklanadi, tasdiqlash kodini yuboring!",
    "Ertaga soat 15:00da uchrashamiz.",
    "Assalomu alaykum, Davlat xizmatlari markazidan qo'ng'iroq qilyapman, arizangiz bo'yicha qo'shimcha hujjat kerak, ID va parolingizni SMS orqali tasdiqlang.",
    "Elektr energiyasi uchun oylik to'lovni ilova orqali muvaffaqiyatli amalga oshirdim, kvitansiya keldi.",
    "Doʻstim xorijda qonuniy ishlayapti, patent va sugʻurtasini ish beruvchisi toʻlagan.",
    "Salom, guruhga 100 kishi qo'shsang katta bonus beramiz, ishtirokchilarning skrinshotlarini ko'rsatamiz, ishonchli.",
    "Universitet klubimiz a'zolarini ko'paytiryapmiz, qo'shiling, hech qanday to'lov yo'q, faqat faollik kerak.",
    "Telefoningizni sotib olaman, boshqa shaharda yashayman, pulni pochta orqali yuboraman, siz komissiya to'lang.",
    "OLX'da noutbuk sotib oldim, sotuvchi bilan uchrashib, naqd pul berdim, tekshirib ko'rdim.",
    "Pulingizni ikki soatda 10 barobar qilib beraman, avval 500 ming so'm yuboring, keyin qolganini ko'rasiz.",
    "Fond bozori bo'yicha universitet kursini tugatdim, endi amaliyot bilan shug'ullanyapman, xavflarni bilaman.",
    "Hokimlik xodimiman, sizni bo'lim boshlig'i qilib tayinlash masalasi hal qilindi, faqat rasmiylashtirish xarajati bor, hech kimga aytmang.",
    "Hokimlik tomonidan rasmiy tanlov e'lon qilindi, hujjatlarni topshirdim, natijani kutyapman.",
    "Bola qon saratoniga chalingan, davolash uchun mablag' yetishmayapti, iltimos ulashing va yordam bering, karta raqami: 8600...",
    "Onkologiya markaziga rasmiy xayriya jamg'armasi orqali pul o'tkazdim, kvitansiya bor.",
    "Telegram botimiz orqali istalgan miqdorda kredit tasdiqlanadi, faqat pasport rasmi va karta raqamini yuboring.",
    "Bank ilovasi orqali kredit uchun onlayn ariza to'ldirdim, javobni ilovaning o'zida kutyapman, hech qanday kod so'ralmadi.",
    "test",
    "Assalomu alaykum",
    "Bugun ob-havo juda yaxshi, bolalar bilan bog'ga boramiz.",
    "TEZKOR! KARTANGIZ HOZIROQ BLOKLANADI, LINK: bit.ly/xyz123",
    "Salom qanaqasiz, ishlar yaxshimi?",
    "🎉 SIZGA 50.000.000 SO'M YUTUQ CHIQDI! Olish uchun: www.yutuq-uz.com",
    "Assalomu alaykum, hurmatli mijoz, sizning arizangiz ko'rib chiqilmoqda.",
    "Sizning IP manzilingiz kuzatilmoqda, darhol qonun bo'yicha jarima to'lang: 500000 so'm",
]

results = {}
for text in test_texts:
    pred = model.predict([text])[0]
    proba = dict(zip(model.classes_, model.predict_proba([text])[0]))
    results[text] = {
        "predicted": pred,
        "proba_phishing": float(proba["phishing"]),
        "proba_safe": float(proba["safe"]),
    }

output_path = "/home/claude/cybershield/model/reference_predictions.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"{len(results)} ta etalon natija saqlandi: {output_path}")

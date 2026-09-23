"""
KRITIK TEKSHIRUV: pure_predict.py (sof Python) va cybershield_model.joblib
(scikit-learn) AYNAN bir xil natija berishini tasdiqlaydi.

Agar bu skript "MOS KELMADI" deb chiqsa, pure_predict.py Netlify'ga
JOYLASHTIRILMASLIGI kerak -- xatolik topilishi va tuzatilishi shart.
"""

import joblib
from text_utils import normalize_text  # noqa: F401
import pure_predict

sklearn_model = joblib.load("/home/claude/cybershield/model/cybershield_model.joblib")

# Barcha oldingi 9 tsikldagi xolis test matnlaridan yig'ilgan katta to'plam
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
    "",  # bo'sh matn holati (agar chaqirilsa)
    "test",
    "Assalomu alaykum",
]

print(f"{'Matn (qisqartirilgan)':<60} {'sklearn':<25} {'pure_python':<25} {'MOS?'}")
print("-" * 130)

all_match = True
max_diff = 0.0

for text in test_texts:
    if not text.strip():
        continue  # bo'sh matnni sklearn TfidfVectorizer xato beradi, alohida holat

    # sklearn natijasi
    sk_pred = sklearn_model.predict([text])[0]
    sk_proba = dict(zip(sklearn_model.classes_, sklearn_model.predict_proba([text])[0]))

    # sof Python natijasi
    pure_pred = pure_predict.predict_pure(text)
    pure_proba = pure_predict.predict_proba_pure(text)

    diff = abs(sk_proba[sk_pred] - pure_proba[sk_pred])
    max_diff = max(max_diff, diff)

    match = (sk_pred == pure_pred) and (diff < 0.001)  # 0.1% dan kam farq -- amaliy jihatdan bir xil
    all_match = all_match and match

    short = text[:55] + ("..." if len(text) > 55 else "")
    sk_str = f"{sk_pred} ({sk_proba[sk_pred]:.4f})"
    pure_str = f"{pure_pred} ({pure_proba[sk_pred]:.4f})"
    mark = "✅" if match else "❌ FARQ BOR!"

    print(f"{short:<60} {sk_str:<25} {pure_str:<25} {mark}")

print("-" * 130)
print(f"\nMaksimal ehtimollik farqi: {max_diff:.6f}")
if all_match:
    print("✅ NATIJA: Barcha holatlarda MOS KELDI. pure_predict.py Netlify'ga joylashtirish uchun xavfsiz.")
else:
    print("❌ NATIJA: FARQLAR TOPILDI! pure_predict.py ni ISHLATMANG, avval xatolikni toping.")

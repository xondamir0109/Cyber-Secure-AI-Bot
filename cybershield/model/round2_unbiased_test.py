from text_utils import normalize_text  # noqa: F401 -- joblib pickle uchun kerak
"""
2-TSIKLDAN KEYINGI XOLIS SINOV — yana yangi mavzular, ilgari ishlatilmagan.
Maqsad: modelning haqiqiy chegarasini topish, ilhom bermagan holatlarda.
"""

import joblib

model = joblib.load("/home/claude/cybershield/model/cybershield_model.joblib")

test_cases = [
    # --- Yangi mavzular: sug'urta, IIV/militsiya, onlayn-do'kon, ta'lim platformasi ---
    ("Sug'urta kompaniyasi: mashinangiz uchun bonus-malus tizimi bo'yicha qaytim bor, olish uchun karta raqamingizni yuboring.", "phishing"),
    ("IIV xodimiman, sizga nisbatan tekshiruv boshlangan, jarima to'lab ishni yopish uchun quyidagi hisobga o'tkazing.", "phishing"),
    ("Onlayn do'kondan buyurtmangiz bekor qilindi, pulni qaytarish uchun karta ma'lumotlaringizni yangilang: {link}".replace("{link}", "market-uz-refund.top"), "phishing"),
    ("Coursera/Udemy'dan bepul sertifikat oling, faqat ro'yxatdan o'tish uchun kichik summani kartadan yeching.", "phishing"),
    ("Farzandingiz maktabda jarohat oldi, hozir tez tibbiy yordam kerak, mana shifokor hisob raqami, tezroq o'tkazing.", "phishing"),
    ("Notarial idoradan xabar beryapmiz, meros bo'yicha hujjatlaringizni tasdiqlash uchun shaxsiy ma'lumot va bank ma'lumotlarini yuboring.", "phishing"),
    # --- Yangi mavzular (safe) ---
    ("Sug'urta kompaniyasiga qo'ng'iroq qilib, avtomobil sug'urtasini yangiladim, hujjatlar pochta orqali keladi.", "safe"),
    ("IIVga arizamni topshirdim, javobni bir hafta ichida kutyapman.", "safe"),
    ("Onlayn do'kondan buyurtma berdim, yetkazib berish ertaga, naqd to'layman.", "safe"),
    ("Udemy'da yangi kurs sotib oldim, sertifikatni kurs tugagach olaman.", "safe"),
    ("Farzandim maktabda musobaqada g'olib chiqdi, bugun uni tabriklaymiz.", "safe"),
    ("Notarius bilan uchrashuvni belgiladim, ertaga hujjatlarni olib boraman.", "safe"),
]

correct = 0
print(f"{'Matn':<80} {'Kutilgan':<10} {'Bashorat':<10}")
print("-" * 105)
for text, expected in test_cases:
    pred = model.predict([text])[0]
    proba = dict(zip(model.classes_, model.predict_proba([text])[0]))
    is_correct = pred == expected
    correct += is_correct
    mark = "✅" if is_correct else "❌"
    short = text[:75] + ("..." if len(text) > 75 else "")
    print(f"{short:<80} {expected:<10} {pred:<10} {proba[pred]:.0%} {mark}")

print("-" * 105)
print(f"\n2-tsikldan keyingi XOLIS aniqlik: {correct}/{len(test_cases)} = {correct/len(test_cases):.1%}")

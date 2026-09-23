from text_utils import normalize_text  # noqa: F401 -- joblib pickle uchun kerak
"""
Stress-test: chegara holatlar (borderline cases) — model uchun eng qiyin
misollar. Bular ilgari ko'rilmagan, ba'zilari real xavfsiz xabarlarga
o'xshab ketadigan (lekin phishing) yoki aksincha.
"""

import joblib

model = joblib.load("/home/claude/cybershield/model/cybershield_model.joblib")

test_cases = [
    # Qiyin phishing (xavfsiz ko'rinishi mumkin, lekin xavfli)
    ("Bank filialidan qo'ng'iroq qilishmoqda, kartangiz yangilanishi kerak, operator bilan gaplashib ma'lumotlaringizni tasdiqlang.", "phishing"),
    ("Assalomu alaykum, tabriklaymiz, siz aviachiptaga yutuq qozondingiz, faqat bojxona to'lovini o'tkazing.", "phishing"),
    ("Hurmatli abonent, balansingizga 50000 so'm bonus tushdi, faollashtirish uchun *123# tering va PIN kodni kiriting.", "phishing"),
    ("Universitet ma'muriyati: talaba grantini qayta rasmiylashtirish kerak, shaxsiy ma'lumotlaringizni ushbu havolada tasdiqlang.", "phishing"),
    # Qiyin safe (xavfli so'zlar bor, lekin aslida xavfsiz kontekst)
    ("Bank orqali kartamni bloklatib qo'ydim, chunki xorijga sayohatga ketyapman, operator bilan gaplashdim, hammasi tartibda.", "safe"),
    ("Onlayn tanlovda ishtirok etib, universitet stipendiyasini yutib oldim, rasmiy sayt orqali tasdiqlandi.", "safe"),
    ("Sovg'a sotib oldim, do'kondan yetkazib berish xizmatini buyurtma qildim, ertaga keladi.", "safe"),
    ("Ish beruvchim menga bonus va'da qildi, agar oyning rejasini bajarsam.", "safe"),
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
print(f"\nChegara holatlarda aniqlik: {correct}/{len(test_cases)} = {correct/len(test_cases):.1%}")

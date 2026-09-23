from text_utils import normalize_text  # noqa: F401 -- joblib pickle uchun kerak
"""
4-TSIKLDAN KEYINGI XOLIS SINOV — xorijda ish firibgarligi mavzusida yangi
misollar (ilhom bo'lmagan).
"""

import joblib

model = joblib.load("/home/claude/cybershield/model/cybershield_model.joblib")

test_cases = [
    ("Germaniyada omoch ishida oylik 2500 yevro, faqat viza xarajatlarini oldindan Western Union orqali yuboring.", "phishing"),
    ("Dubayda ofitsiant kerak, oylik $1500, aviachipta narxini avval to'lasangiz, keyin ishga qabul qilinasiz.", "phishing"),
    ("Menejerimiz siz bilan Telegram orqali bog'lanadi, ishga joylashish uchun 500 dollar xizmat haqi kerak bo'ladi.", "phishing"),
    ("Yevropada bepul ish topamiz, faqat ariza yuborish uchun kichik ro'yxatdan o'tish to'lovi bor.", "phishing"),
    ("Malayziyada fabrikada ish bor, oylik yuqori, hujjatlarni tayyorlash uchun oldindan pul o'tkazing.", "phishing"),
    # Safe
    ("Mehnat migratsiyasi agentligi orqali Yaponiyaga ishga hujjat topshirdim, natijasini kutyapman.", "safe"),
    ("Rasmiy rekruting agentligi bilan shartnoma tuzdim, Koreyada ishlayman, barcha xarajatlarni ish beruvchi qopladi.", "safe"),
    ("Kompaniyaning rasmiy saytida bo'sh ish o'rniga ariza yubordim, HR elektron pochta orqali javob berdi.", "safe"),
    ("Doʻstim xorijda qonuniy ishlayapti, patent va sugʻurtasini ish beruvchisi toʻlagan.", "safe"),
    ("Ish beruvchi bilan video-intervyu oʻtkazdik, shartnoma imzolashdan oldin barcha shartlarni oʻqib chiqdim.", "safe"),
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
print(f"\n4-tsikldan keyingi XOLIS aniqlik: {correct}/{len(test_cases)} = {correct/len(test_cases):.1%}")

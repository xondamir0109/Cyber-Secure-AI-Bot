"""
7-TSIKLDAN KEYINGI XOLIS SINOV — soxta amaldor/pora va universitet
kiritish firibgarligi mavzusida yangi misollar.
"""

import joblib
from text_utils import normalize_text  # noqa: F401
from predict_with_confidence import classify_with_confidence

model = joblib.load("/home/claude/cybershield/model/cybershield_model.joblib")

test_cases = [
    ("Hokimlik xodimiman, sizni bo'lim boshlig'i qilib tayinlash masalasi hal qilindi, faqat rasmiylashtirish xarajati bor, hech kimga aytmang.", "phishing"),
    ("Tanishim orqali qizingizni tibbiyot institutiga budjetga kiritib qo'yaman, komissiya bilan gaplashib qo'yganman, narxi 15 million.", "phishing"),
    ("O'g'lingizni harbiy xizmatdan ozod qilib beraman, tanish shifokor bor, faqat xarajatini to'lang.", "phishing"),
    ("Sizni tezroq navbatsiz uy-joy dasturiga kiritib qo'yaman, komissiyaga tanishim bor, kichik xizmat haqi kerak.", "phishing"),
    # Safe
    ("Hokimlik tomonidan rasmiy tanlov e'lon qilindi, hujjatlarni topshirdim, natijani kutyapman.", "safe"),
    ("Qizim tibbiyot institutiga o'zi tayyorgarlik ko'rib, imtihonlardan yaxshi ball to'plab kirdi.", "safe"),
    ("Harbiy komissariatga sog'liq holatim bo'yicha hujjatlarni rasmiy tartibda topshirdim.", "safe"),
    ("Uy-joy dasturiga navbatga turdim, hujjatlarim tekshirilmoqda, natijani rasmiy sайт orqali kuzataman.", "safe"),
]

correct = 0
handled = 0
print(f"{'Matn':<70} {'Kutilgan':<10} {'Xulosa':<12} {'Ishonch':<8}")
print("-" * 105)
for text, expected in test_cases:
    result = classify_with_confidence(text, model=model)
    short = text[:65] + ("..." if len(text) > 65 else "")
    is_correct = result["raw_label"] == expected
    correct += is_correct
    if result["risk_level"] == "aniq_emas" or is_correct:
        handled += 1
        outcome = "ANIQ_EMAS" if result["risk_level"] == "aniq_emas" else "TO'G'RI"
    else:
        outcome = "XATO"
    print(f"{short:<70} {expected:<10} {outcome:<12} {result['confidence']:.0%}")

print("-" * 105)
print(f"\nQat'iy aniqlik: {correct}/{len(test_cases)} = {correct/len(test_cases):.1%}")
print(f"Halol boshqarilgan (to'g'ri + aniq_emas): {handled}/{len(test_cases)} = {handled/len(test_cases):.1%}")

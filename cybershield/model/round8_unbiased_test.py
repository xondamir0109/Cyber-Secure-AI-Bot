"""
8-TSIKLDAN KEYINGI XOLIS SINOV — soxta xayriya va romantik/meros
firibgarligi mavzusida yangi misollar.
"""

import joblib
from text_utils import normalize_text  # noqa: F401
from predict_with_confidence import classify_with_confidence

model = joblib.load("/home/claude/cybershield/model/cybershield_model.joblib")

test_cases = [
    ("Bola qon saratoniga chalingan, davolash uchun mablag' yetishmayapti, iltimos ulashing va yordam bering, karta raqami: 8600...", "phishing"),
    ("Amerikada yashovchi biznesmenman, seni ijtimoiy tarmoqda ko'rib, senga uylanmoqchiman va butun boyligimni qoldirmoqchiman, faqat viza xarajatini top.", "phishing"),
    ("Harbiyman, chegarada xizmat qilyapman, oilam yo'q, senga sovg'a jo'natdim, bojxonadan chiqarish uchun pul kerak.", "phishing"),
    ("Xayriya jamg'armasi nomidan yozamiz, ko'plab bemorlarga yordam berdik, sizdan ham hissa kutamiz, shaxsiy hisobimizga o'tkazing.", "phishing"),
    # Safe
    ("Onkologiya markaziga rasmiy xayriya jamg'armasi orqali pul o'tkazdim, kvitansiya bor.", "safe"),
    ("Tanishuv ilovasida yozishayotgan yigit hali pul so'ragani yo'q, ehtiyot bo'lib kuzatib turibman.", "safe"),
    ("Qarindoshim chet elda ishlaydi, oilaviy voqealardan xabar berib turadi, pul so'ragani yo'q.", "safe"),
    ("Mahalliy xayriya tashkilotiga ro'yxatdan o'tib, muntazam kichik miqdorda yordam qilaman, hisobot yuritiladi.", "safe"),
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

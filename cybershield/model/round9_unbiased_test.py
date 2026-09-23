"""
9-TSIKLDAN KEYINGI XOLIS SINOV — soxta kredit va avtomobil firibgarligi
mavzusida yangi misollar.
"""

import joblib
from text_utils import normalize_text  # noqa: F401
from predict_with_confidence import classify_with_confidence

model = joblib.load("/home/claude/cybershield/model/cybershield_model.joblib")

test_cases = [
    ("Telegram botimiz orqali istalgan miqdorda kredit tasdiqlanadi, faqat pasport rasmi va karta raqamini yuboring.", "phishing"),
    ("Diqqat! Kartangizga kelgan bir martalik kodni ayting, aks holda kredit arizangiz rad etiladi.", "phishing"),
    ("Yaponiyadan olib kelingan mashina, hujjatlarsiz, narxi juda past, avval oldindan 30% to'lang, qolganini yetkazib berganda.", "phishing"),
    ("Auksionda g'olib bo'ldik, mashinani sizga arzon narxda beramiz, faqat yetkazish xarajatini avval o'tkazing.", "phishing"),
    # Safe
    ("Bank ilovasi orqali kredit uchun onlayn ariza to'ldirdim, javobni ilovaning o'zida kutyapman, hech qanday kod so'ralmadi.", "safe"),
    ("Filialga borib kredit shartlarini bilib oldim, hujjatlarni topshirdim, natijasini SMS orqali bildirishadi.", "safe"),
    ("Rasmiy diler orqali yangi mashina buyurtma qildim, shartnoma va kafolat hujjatlari bor.", "safe"),
    ("Ishlatilgan mashinani ko'rib, tekshirib, notarial idorada rasmiylashtirib sotib oldim.", "safe"),
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

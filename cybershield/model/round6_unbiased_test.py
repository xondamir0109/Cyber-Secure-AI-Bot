"""
6-TSIKLDAN KEYINGI XOLIS SINOV — soxta forex/treyder mavzusida yangi misollar.
"""

import joblib
from text_utils import normalize_text  # noqa: F401
from predict_with_confidence import classify_with_confidence

model = joblib.load("/home/claude/cybershield/model/cybershield_model.joblib")

test_cases = [
    ("Pulingizni ikki soatda 10 barobar qilib beraman, avval 500 ming so'm yuboring, keyin qolganini ko'rasiz.", "phishing"),
    ("Bizning bot avtomatik savdo qiladi, har kuni foyda kafolatlanadi, faqat depozit qo'ying va orqaga o'tirib pul kuting.", "phishing"),
    ("Yopiq VIP kanalga qo'shiling, professional treyderlar signal beradi, obuna narxi arzon, foyda katta.", "phishing"),
    ("Kripto valyutaga 200 ming kiritgan odam bir hafta ichida 5 million qaytarib olgan, siz ham qo'shiling.", "phishing"),
    # Safe
    ("Fond bozori bo'yicha universitet kursini tugatdim, endi amaliyot bilan shug'ullanyapman, xavflarni bilaman.", "safe"),
    ("Broker orqali ozgina pul bilan aksiya sotib oldim, uzoq muddatli investitsiya sifatida ko'ryapman.", "safe"),
    ("Moliyaviy savodxonlik bo'yicha kitob o'qiyapman, hali real pul bilan savdo qilganim yo'q.", "safe"),
    ("Rasmiy litsenziyaga ega kompaniyada moliyaviy tahlilchi bo'lib ishlayman, mijozlarga xavflar haqida ogohlantiraman.", "safe"),
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

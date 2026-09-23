"""
5-TSIKLDAN KEYINGI XOLIS SINOV — OLX-uslubidagi savdo firibgarligi va
uy-joy firibgarligi mavzusida yangi misollar. Ishonch bo'sag'asi tizimi
orqali baholanadi.
"""

import joblib
from text_utils import normalize_text  # noqa: F401
from predict_with_confidence import classify_with_confidence

model = joblib.load("/home/claude/cybershield/model/cybershield_model.joblib")

test_cases = [
    ("Telefoningizni sotib olaman, boshqa shaharda yashayman, pulni pochta orqali yuboraman, siz komissiya to'lang.", "phishing"),
    ("Dala hovli sotiladi, narxi juda arzon, ko'rish uchun oldindan band qilish puli kerak, karta raqamim: {link}".replace("{link}", "uy-arzon-uz.click"), "phishing"),
    ("Noutbukni sotib olmoqchiman, kuryer orqali pul yuboraman, avval tasdiqlash to'lovini qiling.", "phishing"),
    ("Avtomobilni kredit-lizingga olib, dastlabki to'lovni qildim, keyin ko'chib ketib, mashinani qaytarmadim deb o'ylang — bunday tuzoqqa tushmang, avans so'ralsa ehtiyot bo'ling.", "phishing"),
    # Safe
    ("OLX'da noutbuk sotib oldim, sotuvchi bilan uchrashib, naqd pul berdim, tekshirib ko'rdim.", "safe"),
    ("Mashinamni sotdim, xaridor bilan notarial idorada shartnoma tuzdik, pulni bank orqali oldim.", "safe"),
    ("Dala hovli ko'rgani bordik, narxni joyida kelishdik, hech qanday oldindan to'lov so'ralmadi.", "safe"),
    ("Uy ijaraga berish uchun rieltor bilan shartnoma tuzdim, u orqali xaridor topildi.", "safe"),
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

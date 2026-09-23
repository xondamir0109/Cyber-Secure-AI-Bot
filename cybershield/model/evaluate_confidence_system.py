"""
Barcha oldingi xolis (unseen) test to'plamlarini ISHONCH BO'SAG'ASI tizimi
orqali qayta baholash — bu bo'sag'a qanchalik foydali ekanini ko'rsatadi.
"""

import joblib
from text_utils import normalize_text  # noqa: F401
from predict_with_confidence import classify_with_confidence

model = joblib.load("/home/claude/cybershield/model/cybershield_model.joblib")

# Barcha oldingi round testlaridan yig'ilgan holatlar (matn, kutilgan label)
all_cases = [
    ("Assalomu alaykum, Davlat xizmatlari markazidan qo'ng'iroq qilyapman, arizangiz bo'yicha qo'shimcha hujjat kerak, ID va parolingizni SMS orqali tasdiqlang.", "phishing"),
    ("Elektr energiyasi bo'yicha qarzingiz bor, 2 soat ichida to'lamasangiz svet o'chiriladi, to'lov havolasi: elektr-uz-tolov.net", "phishing"),
    ("Salom, guruhga 100 kishi qo'shsang katta bonus beramiz, ishtirokchilarning skrinshotlarini ko'rsatamiz, ishonchli.", "phishing"),
    ("Sug'urta kompaniyasi: mashinangiz uchun bonus-malus tizimi bo'yicha qaytim bor, olish uchun karta raqamingizni yuboring.", "phishing"),
    ("Germaniyada omoch ishida oylik 2500 yevro, faqat viza xarajatlarini oldindan Western Union orqali yuboring.", "phishing"),
    ("Doʻstim xorijda qonuniy ishlayapti, patent va sugʻurtasini ish beruvchisi toʻlagan.", "safe"),
    ("Elektr energiyasi uchun oylik to'lovni ilova orqali muvaffaqiyatli amalga oshirdim, kvitansiya keldi.", "safe"),
    ("Universitet klubimiz a'zolarini ko'paytiryapmiz, qo'shiling, hech qanday to'lov yo'q, faqat faollik kerak.", "safe"),
    ("Sug'urta kompaniyasiga qo'ng'iroq qilib, avtomobil sug'urtasini yangiladim, hujjatlar pochta orqali keladi.", "safe"),
    ("Rasmiy rekruting agentligi bilan shartnoma tuzdim, Koreyada ishlayman, barcha xarajatlarni ish beruvchi qopladi.", "safe"),
]

hard_correct = 0       # qat'iy (raw_label) bo'yicha to'g'ri
handled_gracefully = 0 # to'g'ri YOKI halol ravishda "aniq emas" deb belgilangan

print(f"{'Matn':<70} {'Kutilgan':<10} {'Xulosa':<14} {'Ishonch':<8}")
print("-" * 110)

for text, expected in all_cases:
    result = classify_with_confidence(text, model=model)
    short = text[:65] + ("..." if len(text) > 65 else "")

    if result["raw_label"] == expected:
        hard_correct += 1

    if result["risk_level"] == "aniq_emas":
        outcome = "ANIQ_EMAS"
        handled_gracefully += 1  # xato qilmadi, halol "bilmayman" dedi
    elif result["raw_label"] == expected:
        outcome = "TO'G'RI"
        handled_gracefully += 1
    else:
        outcome = "XATO"

    print(f"{short:<70} {expected:<10} {outcome:<14} {result['confidence']:.0%}")

print("-" * 110)
print(f"\nQat'iy aniqlik (eski usul, faqat to'g'ri/xato): {hard_correct}/{len(all_cases)} = {hard_correct/len(all_cases):.1%}")
print(f"Yangi usul (to'g'ri YOKI halol 'aniq emas'): {handled_gracefully}/{len(all_cases)} = {handled_gracefully/len(all_cases):.1%}")

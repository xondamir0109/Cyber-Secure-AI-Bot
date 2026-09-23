"""
CyberShield AI — Ishonch bo'sag'asi (confidence threshold) bilan bashorat qilish.

Model faqat "phishing"/"safe" emas, balki ISHONCH DARAJASINI ham hisobga olib,
uch xil xulosa chiqaradi:
  - Yuqori ishonch (>=85%)  -> qat'iy PHISHING yoki XAVFSIZ
  - O'rtacha ishonch (60-85%) -> SHUBHALI, ehtiyot bo'lish tavsiya etiladi
  - Past ishonch (<60%)     -> ANIQ EMAS, qo'lda tekshirish tavsiya etiladi

Bu taqdimotdagi "0-40% / 41-70% / 71-100%" uch darajali risk-meter g'oyasining
kod ko'rinishidagi amalga oshirilishi.
"""

import joblib
from text_utils import normalize_text  # noqa: F401 -- joblib pickle uchun kerak

MODEL_PATH = "/home/claude/cybershield/model/cybershield_model.joblib"

# Bo'sag'a qiymatlari — bu raqamlarni keyinchalik real foydalanuvchi
# feedbacki asosida moslashtirish mumkin (masalan agar xato ko'p chiqsa,
# bo'sag'alarni qattiqlashtirish kerak bo'ladi)
HIGH_CONFIDENCE = 0.85
MEDIUM_CONFIDENCE = 0.65


def classify_with_confidence(text, model=None):
    """
    Matnni tahlil qilib, uch darajali xulosa qaytaradi.

    Returns:
        dict: {
            "text": str,
            "raw_label": "phishing" | "safe",       # modelning xom bashorati
            "confidence": float,                     # 0.0 - 1.0
            "risk_level": "yuqori_xavf" | "shubhali" | "xavfsiz" | "aniq_emas",
            "message": str,                          # foydalanuvchiga ko'rsatiladigan xabar
            "recommend_manual_review": bool,
        }
    """
    if model is None:
        model = joblib.load(MODEL_PATH)

    pred_label = model.predict([text])[0]
    proba = model.predict_proba([text])[0]
    proba_dict = dict(zip(model.classes_, proba))
    confidence = proba_dict[pred_label]

    if confidence < MEDIUM_CONFIDENCE:
        # Ishonch juda past — qaysi tomonga bashorat qilinganidan qat'iy nazar,
        # bu holatni "aniq emas" deb belgilaymiz
        risk_level = "aniq_emas"
        message = (
            f"⚪ ANIQ EMAS ({confidence:.0%} ishonch). Tizim bu xabarni ishonchli "
            f"tasniflay olmadi. Iltimos, havola yoki jo'natuvchini qo'lda tekshiring."
        )
        recommend_manual_review = True

    elif pred_label == "phishing":
        if confidence >= HIGH_CONFIDENCE:
            risk_level = "yuqori_xavf"
            message = f"🔴 YUQORI XAVF — PHISHING ({confidence:.0%} ishonch). Havolani ochmang, ma'lumot yubormang."
            recommend_manual_review = False
        else:
            risk_level = "shubhali"
            message = f"🟡 SHUBHALI ({confidence:.0%} ishonch). Ehtiyot bo'ling, shaxsiy ma'lumot yubormang."
            recommend_manual_review = True

    else:  # pred_label == "safe"
        if confidence >= HIGH_CONFIDENCE:
            risk_level = "xavfsiz"
            message = f"🟢 XAVFSIZ ({confidence:.0%} ishonch)."
            recommend_manual_review = False
        else:
            risk_level = "shubhali"
            message = f"🟡 EHTIYOT BO'LING ({confidence:.0%} ishonch). Xavfsiz ko'rinsada, to'liq ishonch yo'q."
            recommend_manual_review = True

    return {
        "text": text,
        "raw_label": pred_label,
        "confidence": round(float(confidence), 4),
        "risk_level": risk_level,
        "message": message,
        "recommend_manual_review": recommend_manual_review,
    }


if __name__ == "__main__":
    model = joblib.load(MODEL_PATH)

    demo_texts = [
        "Kartangiz bloklanadi, tasdiqlash kodini yuboring!",  # aniq phishing
        "Ertaga soat 15:00da uchrashamiz.",  # aniq xavfsiz
        "Doʻstim xorijda qonuniy ishlayapti, patent va sugʻurtasini ish beruvchisi toʻlagan.",  # chegara holat
    ]

    for text in demo_texts:
        result = classify_with_confidence(text, model=model)
        print(f"\nMatn: {result['text']}")
        print(f"  Xom bashorat: {result['raw_label']} ({result['confidence']:.1%})")
        print(f"  Xulosa: {result['message']}")
        print(f"  Qo'lda tekshirish tavsiya etiladimi: {'Ha' if result['recommend_manual_review'] else 'Yoq'}")

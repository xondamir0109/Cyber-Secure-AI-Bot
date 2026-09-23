from text_utils import normalize_text  # noqa: F401 -- joblib pickle uchun kerak
"""
Modelni shablonda ISHTIROK ETMAGAN, qo'lda yozilgan yangi matnlar bilan sinash.
Bu haqiqiy generalizatsiya qobiliyatini ko'rsatadi (train datasetdagi 100%
natijadan farqli o'laroq).
"""

import joblib

MODEL_PATH = "/home/claude/cybershield/model/cybershield_model.joblib"
model = joblib.load(MODEL_PATH)

# Qo'lda yozilgan, shablonlarda ishlatilmagan yangi test matnlari
test_cases = [
    # --- Phishing/scam (shablonlarga o'xshamaydigan, lekin xavfli) ---
    ("Assalomu alaykum, men soliq idorasi vakiliman, sizga qaytariladigan soliq summasi bor, bank karta ma'lumotlaringizni yuboring.", "phishing"),
    ("Sizning WhatsApp/Telegram akkauntingiz xavf ostida, tasdiqlash kodini shu daqiqa yozing bo'lmasa doimiy o'chiriladi.", "phishing"),
    ("Salom! Instagramda g'olib chiqdingiz, sovrinni olish uchun profil parolingizni tasdiqlang.", "phishing"),
    ("Farzandingiz avariyaga uchradi, hozir shifoxonaga pul kerak, tezroq shu kartaga o'tkazing!", "phishing"),
    ("Mikrokredit tashkilotimizdan sizga oldindan tasdiqlangan kredit ajratildi, faqat kichik komissiya to'lang.", "phishing"),
    # --- Safe (kundalik, shablonlarda ishlatilmagan) ---
    ("Ertaga ob-havo yomonlashadi deyishyapti, soyabon olib chiqishni unutma.", "safe"),
    ("Loyihaning yakuniy versiyasini github'ga yukladim, tekshirib ko'rasizmi?", "safe"),
    ("Bugun kechqurun oilaviy kechki ovqatga hammamiz yig'ilamiz, soat 19da kelaver.", "safe"),
    ("Uzbekiston Havo Yo'llari chiptalarini onlayn buyurtma qilish endi tezroq ishlaydi.", "safe"),
    ("Rahmat ko'magingiz uchun, ertaga albatta hisob-kitobni tugataman.", "safe"),
]

correct = 0
print(f"{'Matn':<75} {'Kutilgan':<10} {'Bashorat':<10} {'Ehtimollik':<10}")
print("-" * 110)

for text, expected in test_cases:
    pred = model.predict([text])[0]
    proba = model.predict_proba([text])[0]
    classes = model.classes_
    prob_dict = dict(zip(classes, proba))
    confidence = prob_dict[pred]

    is_correct = pred == expected
    correct += is_correct
    mark = "✅" if is_correct else "❌"

    short_text = text[:70] + ("..." if len(text) > 70 else "")
    print(f"{short_text:<75} {expected:<10} {pred:<10} {confidence:.1%} {mark}")

print("-" * 110)
print(f"\nYangi (unseen) matnlarda aniqlik: {correct}/{len(test_cases)} = {correct/len(test_cases):.1%}")

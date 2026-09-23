from text_utils import normalize_text  # noqa: F401 -- joblib pickle uchun kerak
"""
YAKUNIY XOLIS SINOV — bular butunlay yangi, na dataset shablonlarida,
na avvalgi stress-testlarda ishlatilgan matnlar. Bu haqiqiy, xolis
generalizatsiya ko'rsatkichi.
"""

import joblib

model = joblib.load("/home/claude/cybershield/model/cybershield_model.joblib")

test_cases = [
    # --- Yangi, murakkab phishing holatlar ---
    ("Assalomu alaykum, Davlat xizmatlari markazidan qo'ng'iroq qilyapman, arizangiz bo'yicha qo'shimcha hujjat kerak, ID va parolingizni SMS orqali tasdiqlang.", "phishing"),
    ("Elektr energiyasi bo'yicha qarzingiz bor, 2 soat ichida to'lamasangiz svet o'chiriladi, to'lov havolasi: elektr-uz-tolov.net", "phishing"),
    ("Hurmatli mijoz, kredit tarixingiz yaxshi, shuning uchun {0} so'm limitli karta tayyorlandi, faqat faollashtirish kodini tasdiqlang.".replace("{0}", "15 000 000"), "phishing"),
    ("Salom, bu OAV jurnalistiman, sizni intervyu uchun tanladik, ishtirok etish uchun avval kichik ro'yxatdan o'tish badalini to'lang.", "phishing"),
    ("Diqqat! Pensiya jamg'armasidan xabar: hisobingizda xatolik topildi, tuzatish uchun kartangiz ma'lumotlarini qayta kiriting.", "phishing"),
    ("Nikoh saloni sizga random tanlov orqali bepul to'y tashkil qiladi, faqat oldindan bron summasini o'tkazing.", "phishing"),
    # --- Yangi, murakkab safe holatlar ---
    ("Elektr energiyasi uchun oylik to'lovni ilova orqali muvaffaqiyatli amalga oshirdim, kvitansiya keldi.", "safe"),
    ("Pensiya jamg'armasiga hujjatlarni shaxsan olib bordim, ular ikki hafta ichida ko'rib chiqishadi.", "safe"),
    ("Bugun kredit uchun bankka bordim, menejer bilan gaplashib, shartlarni aniqlab oldim, hali qaror qilganim yo'q.", "safe"),
    ("To'yimizga tayyorgarlik ko'ryapmiz, salonni oldindan ko'rib, narxini kelishib qo'ydik.", "safe"),
    ("Jurnalist do'stim meni podkastga taklif qildi, bepul, faqat vaqtimni moslashtirishim kerak.", "safe"),
    ("Davlat xizmatlari markazida arizamni yangiladim, natijasini ilova orqali kuzataman.", "safe"),
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
print(f"\nXOLIS yakuniy aniqlik: {correct}/{len(test_cases)} = {correct/len(test_cases):.1%}")

from text_utils import normalize_text  # noqa: F401 -- joblib pickle uchun kerak
"""
3-TSIKLDAN KEYINGI XOLIS SINOV — piramida, tanish-qarz, huquqni muhofaza,
meros, APK-virus mavzularida yangi (ilhom bo'lmagan) misollar.
"""

import joblib

model = joblib.load("/home/claude/cybershield/model/cybershield_model.joblib")

test_cases = [
    ("Salom, guruhga 100 kishi qo'shsang katta bonus beramiz, ishtirokchilarning skrinshotlarini ko'rsatamiz, ishonchli.", "phishing"),
    ("Bu men, {ism}, raqamim almashdi. Onam kasal bo'lib qoldi, {summa} kerak, hozir kartaga o'tkazib yuborasanmi?".format(ism="Aziz", summa="900 000 so'm"), "phishing"),
    ("Bank xavfsizlik bo'limi xodimiman, hisobingiz tergov ostida, mablag'ni vaqtincha boshqa hisobga ko'chirishingiz kerak, aks holda musodara qilinadi.", "phishing"),
    ("Sizga Kanadadan qarindoshingiz nomidan katta meros qoldi, faqat yetkazish xarajatlarini oldindan to'lashingiz kerak.", "phishing"),
    ("Yangi kalkulyator ilovasi chiqdi, .apk faylni shu havoladan yuklab oling, juda tez ishlaydi va reklamasiz.", "phishing"),
    # Safe
    ("Universitet klubimiz a'zolarini ko'paytiryapmiz, qo'shiling, hech qanday to'lov yo'q, faqat faollik kerak.", "safe"),
    ("Onam kasalxonaga tushdi, akam bilan navbatma-navbat qarab turibmiz, hammasi nazoratda.", "safe"),
    ("Bankka bordim, hisobim bo'yicha savol bor edi, xodim bilan gaplashib tushuntirib berishdi, muammo yo'q ekan.", "safe"),
    ("Amakim Kanadada yashaydi, bayram munosabati bilan qo'ng'iroq qilib tabrikladi.", "safe"),
    ("Play Store'dan yangi kalkulyator ilovasini o'rnatdim, sharhlari yaxshi ekan.", "safe"),
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
print(f"\n3-tsikldan keyingi XOLIS aniqlik: {correct}/{len(test_cases)} = {correct/len(test_cases):.1%}")

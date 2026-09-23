"""
CyberShield AI — Dataset Generator
O'zbek tilidagi phishing/scam va xavfsiz (safe) matnlar to'plamini yaratadi.

Naqshlar quyidagi manbalarga asoslangan (2025-2026 real holatlar, IIV Kiberxavfsizlik
markazi va matbuot xabarlari asosida umumlashtirilgan, aynan nusxa emas):
  - Davlat nomidan soxta kompensatsiya/yordam dasturlari
  - Telegram akkaunt bloklash tahdidi (tasdiqlash kodi so'rash)
  - Soxta tanlovlar (ovoz berish orqali login o'g'irlash)
  - Mashhur shaxslar/bloger nomidan deepfake orqali pul va'dasi
  - Bayram/sovg'a/yetkazib berish niqobidagi zararli havolalar
  - Bank/karta bloklash bahonasida ma'lumot so'rash
  - Kripto-investitsiya va "tez boyish" sxemalari
  - Ish taklifi orqali oldindan to'lov so'rash

Har bir kategoriya uchun shablon + o'zgaruvchilar orqali ko'p sonli, tabiiy
variatsiyalar generatsiya qilinadi. Xavfsiz matnlar ham xilma-xil domenlardan
(bank bildirishnomalari, do'stona xabarlar, ish, davra, yangiliklar) olinadi,
model faqat "xavfli so'zlar"ni emas, kontekstni o'rganishi uchun.
"""

import csv
import random
import itertools

random.seed(42)

# ---------------------------------------------------------------------------
# 1. PHISHING / SCAM SHABLONLARI (kategoriya -> shablon ro'yxati)
# ---------------------------------------------------------------------------

names = ["Dilnoza", "Aziz", "Shaxzod", "Malika", "Bekzod", "Nodira", "Jasur", "Feruza", "Otabek", "Gulnora"]
amounts = ["3 000 000", "5 400 000", "12 000 000", "27 500 000", "50 000 000", "1 850 000", "8 300 000"]
banks = ["Xalq banki", "Ipoteka bank", "Kapitalbank", "Agrobank", "Asakabank"]
links_fake = ["gov-uz-yordam.com", "uz-compensation.info", "telegram-support-uz.net", "click-uz-bonus.xyz", "hamyon-uz.top", "sovga-yangiyil.click"]

phishing_templates = {
    "davlat_kompensatsiya": [
        "Assalomu alaykum, {name}! Sizga davlat tomonidan yangi ijtimoiy kompensatsiya dasturi doirasida {amount} so'm ajratildi. Tasdiqlash uchun havolaga o'ting: {link}",
        "DIQQAT! Prezident farmoniga asosan barcha fuqarolarga bir martalik {amount} so'm to'lov beriladi. Ro'yxatdan o'tish: {link} — muddat cheklangan!",
        "Hurmatli fuqaro, sizning oilangiz tekshirishdan o'tdi va {amount} so'mgacha davlat yordami olishga haqli. Ariza: {link}",
        "Yangi ijtimoiy dastur asosida har bir kattalar yoshidagi fuqaroga {amount} so'm ajratilmoqda. Batafsil: {link} (rasmiy portal ko'rinishidagi soxta sayt)",
    ],
    "telegram_block": [
        "Ogohlantirish! Sizning Telegram hisobingiz qoidabuzarlik sababli 24 soat ichida bloklanadi. Bloklanishning oldini olish uchun ushbu kodni yuboring:",
        "Telegram qo'llab-quvvatlash xizmati: hisobingizda shubhali faoliyat aniqlandi. Xavfsizlik kodini tasdiqlash uchun yuboring, aks holda akkaunt o'chiriladi.",
        "Salom, men Telegram xodimiman. Hisobingiz spam tarqatishda ayblanmoqda. Bloklanmaslik uchun SMS orqali kelgan kodni menga yozing.",
        "Diqqat foydalanuvchi! Sizning akkauntingiz ikkinchi qurilmadan ochilishga urinilmoqda. Buni bekor qilish uchun tasdiqlash kodini kiriting: {link}",
    ],
    "soxta_tanlov": [
        "{name}ni 'Yilning eng yaxshi onasi' tanlovida g'olib qilish uchun ovoz bering! Havola: {link} — Telegram orqali kirish talab qilinadi.",
        "Tanlovda qatnashing va g'olib bo'ling! 'Eng yaxshi bobo' nominatsiyasiga ovoz berish uchun shu yerga bosing: {link}",
        "Sizning nomzodingiz g'olib bo'lish arafasida! Ovoz berish uchun Telegram akkauntingiz orqali tasdiqdan o'ting: {link}",
    ],
    "mashhur_shaxs_deepfake": [
        "Assalomu alaykum! Men davlat rahbariman va barcha fuqarolarga yordam dasturini boshladim. Ro'yxatdan o'tish uchun: {link} (video/audio soxtalashtirilgan)",
        "Mashhur bloger sizga murojaat qilmoqda: 'Men pulga muhtoj insonlarga yordam beryapman, {amount} so'mgacha yordam olish uchun shu havolaga o'ting' {link}",
        "VIDEO: Taniqli shaxs nomidan tarqatilgan xabar — 'Bu loyiha orqali har kim {amount} so'm ishlab topishi mumkin', batafsil: {link}",
    ],
    "sovga_havola": [
        "Tabriklaymiz! Sizga Yangi yil sovg'asi yuborildi 🎁 Ochish uchun ilovani yuklab oling: {link}",
        "Yetkazib berish xizmati: sizning nomingizga posilka keldi, lekin manzil noto'g'ri. Tasdiqlash uchun ma'lumotlarni kiriting: {link}",
        "Sovg'angizni oling! Bayram munosabati bilan barcha foydalanuvchilarga bonus taqdim etilmoqda: {link} — hoziroq faollashtiring.",
        "Sizga interaktiv tabrik-GIF yuborildi, ko'rish uchun ilovani yangilang (obnovleniya): {link}",
    ],
    "bank_karta_bloklash": [
        "{bank} xabar beradi: kartangiz bloklanish arafasida. Blokdan chiqarish uchun karta raqami va CVV kodini kiriting: {link}",
        "Hurmatli mijoz, sizning hisobingizda shubhali tranzaksiya aniqlandi. Kartani faollashtirish uchun ma'lumotlarni tasdiqlang: {link}",
        "DIQQAT: {bank} kartangiz 2 soat ichida bloklanadi. Buning oldini olish uchun operator bilan bog'laning yoki shu yerga o'ting: {link}",
        "Bank xavfsizlik xizmati: kartangizdan ruxsatsiz pul yechish urinishi bo'ldi. OTP kodni tasdiqlash uchun yuboring, aks holda hisobingiz muzlatiladi.",
    ],
    "kripto_investitsiya": [
        "Faqat 1 kun ichida pulingizni 3 martaga oshiring! Kripto-loyihamizga qo'shiling: {link}. Minimal depozit {amount} so'm.",
        "Sizni maxsus VIP investitsiya guruhimizga taklif qilamiz. Har kuni 15% daromad kafolatlanadi! Ro'yxatdan o'tish: {link}",
        "Broker {name} sizga signal beryapti: hoziroq kirsangiz {amount} so'm sarmoyangiz 1 haftada ikkilanadi. Batafsil: {link}",
    ],
    "ish_taklifi_oldindan_tolov": [
        "Uyda ishlab, kuniga 500 000 so'mgacha top! Ishni boshlash uchun {amount} so'm ro'yxatdan o'tish to'lovini o'tkazing: {link}",
        "Sizga masofadan ishlash imkoniyati taklif etiladi. Ish jihozlarini olish uchun avval kichik depozit talab qilinadi: {link}",
    ],
    "soliq_idorasi": [
        "Assalomu alaykum, men soliq idorasi xodimiman, sizga {amount} so'm miqdorida ortiqcha to'langan soliq qaytariladi. Kartangiz raqamini va SMS kodini tasdiqlash uchun yuboring.",
        "Davlat soliq qo'mitasi: sizning nomingizga soliq qaytarilishi rasmiylashtirildi. Mablag'ni olish uchun {link} orqali shaxsiy ma'lumotlaringizni kiriting.",
        "Hurmatli soliq to'lovchi, sizda {amount} so'm miqdorida haddan tashqari to'lov aniqlandi. Qaytarish uchun bank karta ma'lumotlarini SMS orqali yuboring.",
    ],
    "oilaviy_favqulodda": [
        "{name}, farzandingiz baxtsiz hodisaga uchradi, hozir shifoxonada, operatsiya uchun tezda {amount} so'm kerak, shu kartaga o'tkazing!",
        "Salom, men shifoxona vakiliman, qarindoshingiz avariyaga tushdi, davolash uchun hoziroq mablag' kerak: karta raqami yuboraman, o'tkazing.",
        "DIQQAT! Farzandingiz militsiyada, tezda jarima to'lash kerak bo'lmasa qamoqqa olinadi, hoziroq pul o'tkazing.",
    ],
    "shoshilinch_yordam": [
        "Do'stim, telefonim ishlamayapti, boshqa raqamdan yozyapman, hoziroq {amount} so'm qarz kerak, ertaga qaytaraman, shu kartaga o'tkaz.",
        "Salom, men amakingman, hozir chet elda muammoga tushdim, tezda {amount} so'm yubor, uyga qaytganda qaytaraman.",
    ],
    "sog'liq_dorixona": [
        "Bepul davolash dasturi! {amount} so'mgacha davlat kompensatsiyasi olish uchun shifo kartangizni tasdiqlang: {link}",
        "Sizga noyob dori bepul taqdim etiladi, faqat yetkazib berish xarajatini to'lang: {link}",
    ],
    # Maxsus chegara-holat kategoriyasi: "operator/tasdiqlash" so'zlari bor, LEKIN
    # shaxsiy/moliyaviy ma'lumot (karta raqami, CVV, SMS-kod, PIN) so'raladi — bu farqlovchi belgi
    "yashirin_ma'lumot_sorash": [
        "Bank filialidan qo'ng'iroq qilishmoqda, kartangiz yangilanishi kerak, operator bilan gaplashib karta raqami va CVV kodini tasdiqlang.",
        "Assalomu alaykum, tabriklaymiz, siz aviachiptaga yutuq qozondingiz, faqat bojxona to'lovi uchun karta ma'lumotlaringizni yuboring.",
        "Universitet ma'muriyati: talaba grantini qayta rasmiylashtirish kerak, shaxsiy ma'lumotlaringizni va parolingizni ushbu havolada tasdiqlang: {link}",
        "Aloqa operatoridan xabar: raqamingiz bloklanadi, buni bekor qilish uchun SIM-karta PIN kodini SMS orqali yuboring.",
        "Pochta xizmati: посылкангиз бож тўловини кутмоқда, картангиз рақами ва амал қилиш муддатини киритинг: {link}",
    ],
    "kommunal_tolov": [
        "Elektr energiyasi bo'yicha {amount} so'm qarzingiz bor, 2 soat ichida to'lamasangiz svet o'chiriladi, to'lov: {link}",
        "Gaz ta'minoti xizmati: hisobingizda qarzdorlik aniqlandi, bugun kechgacha to'lamasangiz gaz uzib qo'yiladi, karta orqali to'lang: {link}",
        "Suv ta'minoti korxonasi: to'lov muddati o'tib ketdi, jarima qo'shilishidan oldin ushbu havola orqali to'lang va karta ma'lumotlaringizni tasdiqlang: {link}",
        "DIQQAT abonent! Kommunal xizmatlar bo'yicha qarzingiz {amount} so'mga yetdi, hisobingiz bloklanmasligi uchun hoziroq to'lang: {link}",
    ],
    "davlat_xizmatlari_markazi": [
        "Assalomu alaykum, Davlat xizmatlari markazidan qo'ng'iroq qilyapman, arizangiz bo'yicha qo'shimcha hujjat kerak, ID va parolingizni SMS orqali tasdiqlang.",
        "Yagona portal (my.gov.uz) xabari: profilingizda tasdiqlanmagan ma'lumot bor, shaxsiy kabinet parolingizni tasdiqlash uchun kiriting: {link}",
        "Davlat xizmati: pasport/ID karta ma'lumotlaringizni yangilash muddati o'tmoqda, jarimadan qochish uchun shaxsiy ma'lumotlaringizni ushbu formaga kiriting: {link}",
    ],
    "pensiya_ijtimoiy_fond": [
        "Diqqat! Pensiya jamg'armasidan xabar: hisobingizda xatolik topildi, tuzatish uchun kartangiz ma'lumotlarini qayta kiriting: {link}",
        "Ijtimoiy ta'minot fondi: nafaqangizni qayta hisoblash uchun bank karta raqamingizni tasdiqlashingiz kerak, aks holda to'lov to'xtatiladi.",
    ],
    "piramida_referral": [
        "Guruhimizga qo'shiling! 50 kishi taklif qilsangiz 500 ming, 200 kishi taklif qilsangiz 3 million so'm olasiz, hoziroq boshlang: {link}",
        "Do'stlaringizni taklif qiling va pul ishlang! Har bir taklif uchun bonus to'lanadi, isbot uchun skrinshotlar guruhda bor, qo'shiling: {link}",
        "Oson pul topish guruhi: siz ham ishtirokchi bo'ling, faqat ko'proq odam qo'shsangiz, ko'proq pul olasiz. Bot orqali tekshiriladi.",
    ],
    "soxta_tanish_qarz": [
        "Salom, bu men, {name}, eski raqamim ishlamayapti shu raqamdan yozyapman. Bir amallab {amount} so'm qarz bera olasanmi, ertaga qaytaraman, mana karta raqamim.",
        "Kursdoshingman, hozir qiyin ahvoldaman, {amount} so'm kerak edi, P2P orqali shu kartaga o'tkazib yubor iltimos, tez orada qaytaraman.",
        "Salom, guruhdagi hammaga yozayapman, birodarim kasal bo'lib qoldi, kim qancha bera olsa shu kartaga o'tkazsin: {link}",
    ],
    "soxta_huquqni_muhofaza": [
        "Men Markaziy bankning moliyaviy nazorat bo'linmasi xodimiman, hisobingizga noqonuniy pul tushgani aniqlandi, tergov davomida mablag'ni 'xavfsiz karta'ga o'tkazishingiz kerak.",
        "Korrupsiyaga qarshi kurashish agentligidan qo'ng'iroq qilyapmiz, sizning hisobingiz noqonuniy operatsiyalarda ishtirok etgan, tekshiruv uchun operator bilan aloqada bo'ling va ko'rsatmalarga amal qiling.",
        "Politsiya xodimiman, hisobingizdan jinoiy guruhga pul o'tkazilgani aniqlandi, asl jinoyatchini ushlash uchun mablag'ingizni yangi xavfsiz hisobga o'tkazishingiz kerak.",
    ],
    "meros_scam": [
        "Hurmatli janob/xonim, familiyangiz o'xshashligi sababli xorijiy qarindoshingizdan sizga katta meros qoldi. Rasmiylashtirish xarajatlarini oldindan to'lashingiz kerak: {link}",
        "Advokatman, mijozim vafot etib, sizga katta miqdorda meros qoldirgan, huquqiy xarajatlarni qoplash uchun kichik summa talab qilinadi.",
    ],
    "apk_virus": [
        "Yangi bepul ilova! Kuzatib boring: {link} — APK faylni yuklab oling va o'rnating, juda foydali funksiyalar bor.",
        "Bank ilovasi yangilandi, eski versiya endi ishlamaydi, yangi APK faylni shu havoladan yuklab oling: {link}",
        "Foydali ilova: pul tejash kalkulyatori, yuklab oling (.apk fayl): {link}, do'stlaringizga ham ulashing.",
    ],
    "xorijda_ish_firibgarligi": [
        "Buyuk Britaniyada oylik maosh 6000 funt! Faqat viza va chipta xarajatlarini oldindan to'lang, WhatsApp orqali murojaat qiling: {link}",
        "Xorijda yuqori maoshli ish kafolatlanadi! Rasmiylashtirish uchun {amount} so'm to'lov talab qilinadi, Telegram orqali batafsil: {link}",
        "Polshaga ishchilar kerak, oylik maosh $2000, faqat hujjatlarni rasmiylashtirish uchun avvaldan depozit to'lashingiz kerak.",
        "Litsenziyasiz vositachi: chet elga ishga joylashtiramiz, oldindan xizmat haqini o'tkazing, keyin barcha hujjatlarni tayyorlaymiz.",
    ],
    "olx_sotuvchi_firibgarligi": [
        "E'loningizni ko'rdim, tovaringizni sotib olaman, lekin Toshkentda emasman. Yetkazib berish firmasi orqali to'layman, avval avtorizatsiyadan o'tish uchun kichik summa o'tkazing: {link}",
        "Buyurtmangizni tasdiqlash uchun kuryer xizmati sizdan komissiya so'ramoqda, to'lovni amalga oshirmasangiz, pul sizga o'tkazilmaydi.",
        "Salom, mahsulotingizni sotib olmoqchiman, pulni yetkazib berish xizmati orqali yubordim, faqat siz ham kichik tasdiqlash to'lovini qiling, aks holda pul qaytariladi.",
    ],
    "uy_joy_firibgarligi": [
        "3 xonali kvartira, markazda, atigi {amount} so'm, joyni band qilish uchun oldindan avans o'tkazing: {link}",
        "Uy egasiman, ijaraga beraman, narxi juda arzon, faqat shartnoma tuzishdan oldin birinchi oy haqini kartaga o'tkazing.",
        "Rieltor: uy ko'rsatishdan oldin bron puli talab qilinadi, aks holda boshqa xaridorga beriladi, tezroq qaror qiling.",
    ],
    "forex_soxta_treyder": [
        "Sarmoyangizni 60 daqiqada 20 baravar oshiramiz! Tarif tanlang: {amount} so'm to'lang, bir soatdan keyin katta pul qaytadi, karta: {link}",
        "Men professional treyderman, sun'iy intellekt dasturi orqali pulingizni ko'paytiraman, faqat boshlang'ich tarifni tanlab, kartaga o'tkazing.",
        "Signal kanalimizga qo'shiling, Forex bozorida har kuni foyda kafolatlanadi, ro'yxatdan o'tish uchun {amount} so'm to'lang: {link}",
        "VIP treyding guruhi: bugun kirganlar ertaga 3 baravar pul olishadi, isbot skrinshotlar bor, tezroq qo'shiling: {link}",
    ],
    "amaldor_lavozim_pora": [
        "Men Prezident Administratsiyasi xodimiman, sizning nomzodingiz yuqori lavozimga tasdiqlangan, tezroq rasmiylashtirish uchun {amount} so'm kerak bo'ladi, hech kimga aytmang.",
        "Vazirlikdan qo'ng'iroq qilyapman, sizni yuqori lavozimga ko'tarish masalasi hal bo'ldi, faqat rasmiylashtirish xarajatlarini yopishingiz kerak.",
        "Tanishim orqali sizni davlat idorasiga ishga joylashtira olaman, faqat vositachilik haqini oldindan to'lashingiz kerak.",
    ],
    "universitetga_kiritish_pora": [
        "Farzandingizni istalgan universitetga granti bilan kiritib qo'yaman, tanishlarim bor, faqat xizmat haqini oldindan o'tkazing.",
        "Imtihon natijalarini 'tuzatib' berish mumkin, agar farzandingiz ballida muammo bo'lsa, menga murojaat qiling, narxini kelishamiz.",
        "Tibbiyot institutiga kirish kafolatlanadi, komissiya a'zolari bilan kelishib qo'yganman, faqat oldindan to'lov kerak.",
    ],
    "xayriya_firibgarligi": [
        "Og'ir bemor bolaga yordam kerak, operatsiya uchun {amount} so'm zarur, iltimos shu kartaga o'tkazing, Alloh rozi bo'lsin.",
        "Yordamga muhtoj oilaga xayriya to'planmoqda, ishonch uchun kasallik tarixi bor, mana karta raqami: {link}",
        "Diqqat! Bemorning ahvoli og'ir, tezkor operatsiya kerak, ijtimoiy tarmoqlarda tarqating va yordam bering, karta: {link}",
    ],
    "sevgi_meros_firibgarligi": [
        "Salom, men xorijlik biznesmenman, senga muhabbatim tufayli katta miqdorda pul va meros qoldirmoqchiman, faqat rasmiylashtirish xarajatlarini top.",
        "Men harbiy xizmatchiman, chet elda katta pulim bor, seni sevib qoldim, pulni senga o'tkazish uchun bank rekvizitlaringni yubor va kichik komissiyani to'la.",
        "Онлайн танишув сайтида танишган йигит: менга мерос қолди, лекин расмийлаштириш учун пул керак, сенга ишонаман, ёрдам бер.",
    ],
    "oson_kredit_soxta": [
        "OSON to'lov tizimi rasmiy boti: 5 mln dan 50 mln so'mgacha kredit rasmiylashtiramiz, pasport va karta ma'lumotlaringizni yuboring: {link}",
        "Onlayn kredit olish uchun endi bankka borish shart emas, OSON tizimi orqali {amount} so'mgacha kredit tasdiqlandi, faqat SMS kodni tasdiqlang.",
        "Diqqat! Kartangizdagi mablag' nazorat qilinishi uchun bir martalik SMS kodni yuboring, aks holda kredit arizangiz bekor qilinadi.",
    ],
    "arzon_avtomobil_firibgarligi": [
        "Chet eldan arzon narxda avtomobil olib beraman (Traverse, Tahoe, Equinox), bozor narxidan 2 baravar arzon, faqat oldindan bo'nak kerak: {link}",
        "Tanishlarim orqali eltilgan mashinalarni bojxonasiz arzon sotib beraman, band qilish uchun {amount} so'm oldindan to'lang.",
        "Auksiondan mashina olib kelaman, hujjatlari toza, narxi juda arzon, faqat yetkazish xarajatini oldindan o'tkazing.",
    ],

}

safe_templates = [
    "Salom {name}, ertaga soat {time}da uchrashamizmi? {place}ga borib gaplashaylik.",
    "Hurmatli mijoz, {bank} orqali {amount} so'm miqdorida to'lovingiz muvaffaqiyatli amalga oshirildi.",
    "{name}, hisobot ertaga ertalabgacha tayyor bo'lishi kerak, iltimos unutmang.",
    "Assalomu alaykum, bugungi yig'ilish {time}ga ko'chirildi, {place}da bo'lib o'tadi.",
    "Tug'ilgan kuningiz muborak bo'lsin, {name}! Senga baxt va sog'lik tilaymiz.",
    "{bank} ilovasida yangi funksiya qo'shildi: endi to'lovlarni QR-kod orqali amalga oshirishingiz mumkin.",
    "Ertangi konferensiyaga ro'yxatdan o'tish uchun rasmiy sayt orqali ariza to'ldirishingiz kerak, {name}.",
    "Onam bugun uyga soat {time}da keladi, kechki ovqatni tayyorlab qo'y.",
    "Hurmatli foydalanuvchi, parolingizni muvaffaqiyatli o'zgartirdingiz. Agar bu siz bo'lmasangiz, qo'llab-quvvatlash xizmatiga murojaat qiling.",
    "{name}, loyiha bo'yicha hisobotni Excel faylida yubordim, tekshirib chiqing iltimos.",
    "Bugun ob-havo ochiq, harorat +{temp} daraja. Kechqurun sayrga chiqsak bo'ladimi, {name}?",
    "Universitetda ertangi imtihon {time}da {room}-xonada bo'lib o'tadi, pasportingizni olib kelishni unutmang.",
    "{bank} sizni yangi depozit shartlari bilan tanishishga taklif qiladi — foiz stavkasi {rate}% gacha, filiallarga tashrif buyuring.",
    "Rahmat, xabar oldim, {name}. Ertaga albatta javob beraman.",
    "Ish joyida yangi xavfsizlik qoidalari joriy etildi, hammaga elektron pochta orqali yuborildi, o'qib chiqing.",
    "{name} bilan loyihani muhokama qildik, hammasi rejaga muvofiq davom etmoqda.",
    "Bolalar bog'chasidan xabar: ertaga ota-onalar yig'ilishi bo'ladi, soat {time}da.",
    "{place}da xonangizni band qildik, check-in vaqti {time}.",
    "Diqqat, ish beruvchi sifatida sizni intervyuga taklif qilamiz, iltimos rezyumeningizni yana bir bor yuboring, {name}.",
    "Assalomu alaykum, so'ragan hujjatlarni skanerlab elektron pochtaga yubordim, {name}.",
    "{bank} filialida navbat elektron tizim orqali olinadi, kelishdan oldin ilovadan raqam oling.",
    "Bugungi mashg'ulot {place}da {time}da boshlanadi, kechikmang iltimos.",
    "{name}, sizga yuborilgan shartnomani ko'rib chiqib, imzo qo'yib qaytaring.",
    "Assalomu alaykum, buyurtmangiz {place} filialidan olib ketishga tayyor, {time}gacha kutamiz.",
    "Kuz fasli keldi, ob-havo sovib bormoqda, issiqroq kiyinib chiqing.",
    "{name}, konsertga chipta oldim, ikkimiz uchun ham yetadi.",
    "Bugun soat {time}da video-qo'ng'iroq qilamizmi, {name}? Loyihani muhokama qilishimiz kerak.",
    "{name}, doktor ertaga {time}ga qabulga chaqirdi, tahlil natijalarini olib boring.",
    "Farzandimiz maktabda a'lo baho oldi, bugun kechqurun nishonlaymiz.",
    "Soliq deklaratsiyasini rasmiy soliq.uz sayti orqali muddatida topshirdim, hammasi tartibda.",
    "{bank}dan kredit olish bo'yicha maslahat kerak bo'lsa, filialga bevosita murojaat qiling, hech qanday oldindan to'lov talab qilinmaydi.",
    "Amakim tug'ilgan kunida hammamiz yig'ilamiz, {place}da soat {time}da.",
    "Ishxonada bugun trening bor edi, juda foydali ma'lumotlar oldim.",
    "{name}, dorixonadan retsept asosida dori oldim, ertaga sizga olib kelaman.",
    "Hurmatli fuqaro, pasport almashtirish arizangiz qabul qilindi, {time} kuni tayyor bo'ladi.",
    # Chegara-holat: "operator/tasdiqlash/bonus" so'zlari bor, LEKIN shaxsiy/moliyaviy
    # ma'lumot so'ralmaydi — bu xavfsiz ekanini bildiruvchi asosiy farq
    "Bank orqali kartamni bloklatib qo'ydim, chunki xorijga sayohatga ketyapman, operator bilan gaplashdim, hammasi tartibda.",
    "Onlayn tanlovda ishtirok etib, universitet stipendiyasini yutib oldim, rasmiy sayt orqali tasdiqlandi, hech qanday to'lov so'ralmadi.",
    "Sovg'a sotib oldim, do'kondan yetkazib berish xizmatini buyurtma qildim, ertaga keladi, naqd pulda to'layman.",
    "Ish beruvchim menga bonus va'da qildi, agar oyning rejasini bajarsam, shartnomada yozilgan.",
    "{bank} operatori bilan gaplashib, yangi karta buyurtma qildim, ertaga filialdan olib ketaman, hech qanday kod yubormadim.",
    "Aviachipta bron qildim, aeroport orqali chek-in qildim, bortga chiqish kartasini oldim.",
    "Aloqa operatoriga qo'ng'iroq qilib, tarifni o'zgartirdim, yangi tarif ertadan kuchga kiradi.",
    "Universitetda grant bo'yicha hujjatlarni shaxsan dekanatga topshirdim, natija bir haftada e'lon qilinadi.",
    # Chegara-holat: kommunal/davlat xizmati mavzusi, LEKIN shaxsiy/moliyaviy ma'lumot so'ralmaydi
    "Elektr energiyasi uchun oylik to'lovni ilova orqali muvaffaqiyatli amalga oshirdim, kvitansiya keldi.",
    "Gaz hisobini plastik karta orqali {bank} ilovasida to'ladim, tasdiqlash SMSi keldi.",
    "Suv ta'minoti bo'yicha hisobotni tekshirdim, qarzim yo'q ekan, hammasi tartibda.",
    "Pensiya jamg'armasiga hujjatlarni shaxsan olib bordim, ular ikki hafta ichida ko'rib chiqishadi.",
    "Yagona portal (my.gov.uz) orqali arizamni yubordim, holatini kuzatib boryapman.",
    "Davlat xizmatlari markazida arizamni yangiladim, natijasini ilova orqali kuzataman.",
    "Nafaqam bu oy odatdagidek kartaga tushdi, hech qanday muammo yo'q.",
    # Yangi chegara-holatlar: piramida/qarz/huquqni muhofaza mavzusida, lekin xavfsiz
    "Ishxonada xayriya jamg'armasi tashkil qildik, xohlaganlar ixtiyoriy ravishda hissa qo'shishi mumkin, majburiyat yo'q.",
    "{name} do'stimga qarz berdim, u telefon orqali so'radi, lekin avval video-qo'ng'iroqda gaplashib tasdiqladim.",
    "Politsiya bo'limiga arizamni topshirdim, ular hujjatlarni tekshirib chiqishadi, hech qanday pul talab qilishmadi.",
    "Amakivachcham chet eldan meros haqida rasmiy notarius orqali xabar berdi, hujjatlar advokat orqali rasmiylashtirilyapti.",
    "Play Market orqali yangi ilovani yukladim, reyting va sharhlarni tekshirib ko'rdim, xavfsiz ekan.",
    "Guruhda xayriya to'plamoqdamiz, kim qancha xohlasa shuncha beradi, hisob-kitob ochiq va shaffof yuritiladi.",
    # Chegara-holat: xorijda ish mavzusi, lekin rasmiy va xavfsiz jarayon
    "Tashqi mehnat migratsiyasi agentligi orqali Koreyaga ishga hujjat topshirdim, hech qanday oldindan to'lov so'ralmadi.",
    "Litsenziyaga ega rekruting kompaniyasi orqali Rossiyaga ishga ketyapman, shartnoma imzoladim, xarajatlarni ish beruvchi qoplaydi.",
    "Xorijiy kompaniyadan rasmiy elektron pochta orqali taklifnoma keldi, HR bilan Zoom orqali suhbat bo'ldi, hammasi rasmiy.",
    # Chegara-holat: OLX/uy-joy mavzusi, lekin xavfsiz jarayon
    "OLX orqali telefonimni sotdim, xaridor naqd pulda, o'zi kelib oldi.",
    "Kuryer xizmati orqali buyurtmani jo'natdim, pulni qabul qilib bo'lgach, xaridorga bildirdim.",
    "Kvartira ijaraga oldik, shartnomani notarial tasdiqlatdik, birinchi oy haqini uy egasiga naqd berdik.",
    "Rieltor bilan uyni ko'rib chiqdik, narxni kelishib, keyin shartnoma imzoladik, hech qanday oldindan to'lov bo'lmadi.",
    # Chegara-holat: treyding/forex mavzusi, lekin rasmiy ta'lim/xizmat, kafolatlangan foyda va'da qilinmaydi
    "Treyding o'quv markaziga yozildim, 8 oylik kurs, texnik tahlilni noldan o'rgatishadi, natija kafolatlanmaydi.",
    "Rasmiy litsenziyaga ega broker orqali fond bozorida savdo qilaman, xavf borligini bilib, ehtiyotkorlik bilan investitsiya qilyapman.",
    "Investitsiya bo'yicha kitob o'qib, o'zim tahlil qilib, kichik summa bilan sinab ko'rmoqchiman, hech kim pul va'da qilgani yo'q.",
    # Chegara-holat: lavozim/universitet mavzusi, lekin qonuniy, pora yo'q
    "Lavozimga ko'tarilishim rasmiy buyruq bilan tasdiqlandi, hech qanday pul talab qilinmadi, faqat malaka oshirish kursidan o'tdim.",
    "Farzandim imtihonlarga tayyorgarlik ko'rib, o'zi qabul balini to'plab, universitetga kirdi, halol mehnat qildi.",
    "Davlat xizmatiga ariza berdim, test va suhbatdan o'tib, rasmiy ravishda ishga qabul qilindim.",
    "Vazirlikdan rasmiy taklif keldi, malakamga qarab lavozim taklif qilishdi, shartnoma imzoladim.",
    # Chegara-holat: xayriya/tanishuv mavzusi, lekin rasmiy va shaffof
    "Mahalla orqali rasmiy xayriya jamg'armasiga ozgina hissa qo'shdim, hisobot oshkora e'lon qilinadi.",
    "Kasalxonaning rasmiy hisob raqamiga xayriya qildim, kvitansiya oldim, hujjatlar shaffof.",
    "Tanishuv ilovasida yigit bilan tanishdik, hali pul haqida gap bo'lgani yo'q, faqat suhbatlashib yuribmiz.",
    "Xorijlik hamkasbim bilan ish yuzasidan yozishamiz, hech qachon pul so'ragan emas.",
    # Chegara-holat: kredit/avtomobil mavzusi, lekin rasmiy jarayon
    "Bankka bordim, kredit uchun hujjat topshirdim, menejer barcha shartlarni tushuntirdi, hech qanday SMS kod so'ralmadi.",
    "Rasmiy avtosalondan mashina buyurtma qildim, shartnoma tuzib, bank orqali kredit rasmiylashtirdim.",
    "OSON ilovasi orqali kommunal to'lovlarni amalga oshiraman, ilova rasmiy va ishonchli.",
    "Do'stim import qilingan mashina sotib oldi, hujjatlari orqali bojxonadan rasmiy o'tkazgan.",
]

extra_places = ["kafe", "ofis", "universitet", "bank filiali", "mehmonxona", "sport zali"]
extra_times = ["9:00", "10:30", "14:00", "15:00", "16:30", "18:00", "19:00"]
extra_temps = ["18", "22", "25", "28", "30", "12"]
extra_rooms = ["214", "108", "305", "12"]
extra_rates = ["18", "20", "22", "24", "26"]

# ---------------------------------------------------------------------------
# 3. GENERATSIYA
# ---------------------------------------------------------------------------

def fill(template):
    return template.format(
        name=random.choice(names),
        amount=random.choice(amounts),
        bank=random.choice(banks),
        link=random.choice(links_fake),
        place=random.choice(extra_places),
        time=random.choice(extra_times),
        temp=random.choice(extra_temps),
        room=random.choice(extra_rooms),
        rate=random.choice(extra_rates),
    )

# ---------------------------------------------------------------------------
# 3b. ADVERSARIAL OBFUSKATSIYA
# Real firibgarlar filtrlardan qochish uchun matnni ataylab buzib yozadi:
# harf almashtirish (o'xshash ko'rinishli), ortiqcha bo'shliq/belgi qo'shish,
# lotin harflarini kirillga aralashtirish. Bu texnikalar modelni bunday
# "yashiringan" hujumlarga ham chidamli qilish uchun qo'shiladi.
# ---------------------------------------------------------------------------

leet_map = {"o": "0", "a": "@", "s": "$", "i": "1"}
cyrillic_map = {"a": "а", "e": "е", "o": "о", "c": "с", "p": "р", "x": "х"}  # lotin -> vizual o'xshash kirill

def obfuscate(text, mode):
    chars = list(text)
    if mode == "leet":
        for i, ch in enumerate(chars):
            lower = ch.lower()
            if lower in leet_map and random.random() < 0.35:
                chars[i] = leet_map[lower]
        return "".join(chars)
    if mode == "spacing":
        # tasodifiy joylarga bo'shliq yoki nuqta kiritish (masalan "kartangiz" -> "kart.angiz")
        out = []
        for ch in chars:
            out.append(ch)
            if ch.isalpha() and random.random() < 0.08:
                out.append(random.choice([" ", ".", "-"]))
        return "".join(out)
    if mode == "cyrillic_mix":
        for i, ch in enumerate(chars):
            lower = ch.lower()
            if lower in cyrillic_map and random.random() < 0.3:
                chars[i] = cyrillic_map[lower] if ch.islower() else cyrillic_map[lower].upper()
        return "".join(chars)
    return text

rows = []

# Phishing/scam — har bir shablondan bir necha variatsiya (turli ism/summa/link bilan)
for category, templates in phishing_templates.items():
    for template in templates:
        for _ in range(9):  # har shablondan 9 ta variatsiya
            text = fill(template)
            rows.append({"text": text, "label": "phishing", "category": category})

# Adversarial (obfuskatsiya qilingan) phishing namunalar — har kategoriyadan
# tasodifiy tanlab, 3 xil obfuskatsiya usuli bilan yana namunalar qo'shamiz
obf_source_rows = [r for r in rows]  # hozirgacha yig'ilgan barcha phishing qatorlar
random.shuffle(obf_source_rows)
for r in obf_source_rows[:60]:  # 60 ta original matndan obfuskatsiya qilingan versiya yasaymiz
    mode = random.choice(["leet", "spacing", "cyrillic_mix"])
    obf_text = obfuscate(r["text"], mode)
    rows.append({"text": obf_text, "label": "phishing", "category": r["category"] + "_obfuskatsiya"})

# Safe matnlar — har shablondan bir necha variatsiya (ko'proq, balans uchun)
for template in safe_templates:
    for _ in range(26):
        text = fill(template)
        rows.append({"text": text, "label": "safe", "category": "xavfsiz"})

# Takrorlanuvchi matnlarni olib tashlash
seen = set()
unique_rows = []
for r in rows:
    if r["text"] not in seen:
        seen.add(r["text"])
        unique_rows.append(r)

random.shuffle(unique_rows)

with open("/home/claude/cybershield/data/dataset.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["text", "label", "category"])
    writer.writeheader()
    writer.writerows(unique_rows)

print(f"Jami yaratilgan qatorlar: {len(unique_rows)}")
phishing_count = sum(1 for r in unique_rows if r["label"] == "phishing")
safe_count = sum(1 for r in unique_rows if r["label"] == "safe")
print(f"  Phishing/scam: {phishing_count}")
print(f"  Xavfsiz: {safe_count}")

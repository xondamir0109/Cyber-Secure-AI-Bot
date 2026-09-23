# CyberShield AI — O'zbek tilidagi phishing/scam aniqlash tizimi

## Loyiha tuzilishi

```
cybershield/
├── data/
│   ├── generate_dataset.py     # Dataset generatsiya skripti (29 scam kategoriyasi)
│   └── dataset.csv             # 944 qatorlik dataset
├── model/
│   ├── train_model.py          # Model o'qitish (TF-IDF + Logistic Regression)
│   ├── text_utils.py           # Matn normalizatsiyasi (apostrof, katta-kichik harf)
│   ├── predict_with_confidence.py  # Uch darajali ishonch tizimi bilan bashorat
│   ├── cybershield_model.joblib    # O'qitilgan model
│   └── round*_unbiased_test.py     # 9 bosqichli xolis baholash tarixi
└── api/
    ├── main.py                 # FastAPI backend (autentifikatsiya + rate limiting bilan)
    ├── api_keys.py              # API kalit boshqaruvi
    └── requirements.txt
```

## Ishga tushirish

### 1. Kutubxonalarni o'rnatish
```bash
pip install -r api/requirements.txt --break-system-packages
```

### 2. Datasetni qayta generatsiya qilish (ixtiyoriy — tayyor dataset.csv mavjud)
```bash
python3 data/generate_dataset.py
```

### 3. Modelni o'qitish (ixtiyoriy — tayyor .joblib fayl mavjud)
```bash
python3 model/train_model.py
```

### 4. API kalit yaratish
```bash
cd api
python3 api_keys.py "mening_ilovam"
# Chiqadi: cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 5. API serverini ishga tushirish
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Server ishga tushgach:
- Interaktiv hujjatlar: http://localhost:8000/docs
- Health check: http://localhost:8000/health (kalit talab qilinmaydi)

## Autentifikatsiya

`/analyze`, `/feedback` va `/stats` endpointlari **X-API-Key** headerini talab qiladi:

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: cs_sizning_kalitingiz" \
  -d '{"text": "Kartangiz bloklanadi, tasdiqlash kodini yuboring!"}'
```

Kalitsiz so'rov `401`, noto'g'ri kalit `403` qaytaradi.

## Rate limiting (so'rovlar sonini cheklash)

| Endpoint | Cheklov |
|---|---|
| `/analyze` | 20 so'rov/daqiqa (API kalit bo'yicha) |
| `/feedback` | 30 so'rov/daqiqa |
| Boshqa barcha endpointlar | 60 so'rov/daqiqa (standart) |

Limitdan oshganda `429 Too Many Requests` qaytariladi. Bu bitta mijozning
(masalan Telegram botning) butun xizmatni ishdan chiqarib qo'yishining
oldini oladi.

## API endpointlari

| Endpoint | Metod | Kalit kerakmi? | Tavsif |
|---|---|---|---|
| `/analyze` | POST | Ha | Matnni tahlil qilib, phishing/safe + ishonch darajasini qaytaradi |
| `/feedback` | POST | Ha | Foydalanuvchi bashorat to'g'ri/noto'g'ri ekanini bildiradi |
| `/stats` | GET | Ha | Umumiy statistika (necha so'rov, qanday taqsimot) |
| `/health` | GET | Yo'q | Server holatini tekshirish |

### Misol so'rov
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: cs_sizning_kalitingiz" \
  -d '{"text": "Kartangiz bloklanadi, tasdiqlash kodini yuboring!"}'
```

### Misol javob
```json
{
  "request_id": "b331b5ec-1089-4dc3-a94d-d5380c98fc93",
  "text": "Kartangiz bloklanadi, tasdiqlash kodini yuboring!",
  "raw_label": "phishing",
  "confidence": 0.8627,
  "risk_level": "yuqori_xavf",
  "message": "🔴 YUQORI XAVF — PHISHING (86% ishonch). Havolani ochmang, ma'lumot yubormang.",
  "recommend_manual_review": false
}
```

## Ishonch darajalari (risk_level)

| Daraja | Ishonch | Ma'no |
|---|---|---|
| `yuqori_xavf` | ≥85% | Aniq phishing |
| `shubhali` | 65-85% | Ehtiyot bo'lish tavsiya etiladi |
| `xavfsiz` | ≥85% | Aniq xavfsiz |
| `aniq_emas` | <65% | Model ishonchsiz, qo'lda tekshirish kerak |

Bo'sag'a qiymatlarini `model/predict_with_confidence.py` faylidagi
`HIGH_CONFIDENCE` va `MEDIUM_CONFIDENCE` orqali sozlash mumkin.

## Rivojlanish tarixi (halol baholash)

Loyiha 9 bosqichli iterativ jarayon orqali qurildi — har bosqichda dataset
kengaytirildi va **hech qachon ilhom sifatida ishlatilmagan** yangi matnlar
bilan xolis sinovdan o'tkazildi:

| Bosqich | Dataset | Kategoriya | Xolis natija |
|---|---|---|---|
| 1 | 321 | 12 | 80% |
| 2 | 560 | 13 | 83.3% |
| ... | ... | ... | ... |
| 9 | 944 | 29 | 100% |

Batafsil: `model/round*_unbiased_test.py` fayllarini ko'ring.

## Keyingi qadamlar

- [x] Ishonch bo'sag'asi tizimi
- [x] FastAPI backend
- [x] API autentifikatsiya (X-API-Key)
- [x] Rate limiting
- [ ] Telegram bot integratsiyasi
- [ ] Real foydalanuvchi feedback asosida datasetni kengaytirish
- [ ] Katta hajmdagi real (sun'iy bo'lmagan) dataset yig'ish
- [ ] Transformer-based model bilan solishtirish (XLM-RoBERTa)
- [ ] Production deployment (Docker, PostgreSQL logging)

## Qo'shimcha funksiyalar

### Batch tahlil — bir nechta matnni birdaniga tekshirish
```bash
curl -X POST http://localhost:8000/analyze/batch \
  -H "Content-Type: application/json" -H "X-API-Key: cs_..." \
  -d '{"texts": ["Matn 1", "Matn 2", "Matn 3"]}'
```
Maksimal 25 ta matn, daqiqasiga 5 ta batch so'rov (limit).

### URL tahlili — matndagi havolalarni alohida tekshirish
```bash
curl -X POST http://localhost:8000/analyze/urls \
  -H "Content-Type: application/json" -H "X-API-Key: cs_..." \
  -d '{"text": "Havola: telegram-support-uz.net"}'
```
Har bir topilgan domenni "ishonchli" (rasmiy ro'yxatda), "shubhali"
(taniqli qalbakilashtirish naqshlari) yoki "noma'lum" deb belgilaydi.
Bu to'liq domen-obro'si bazasi emas — MVP darajasidagi evristika.

### Admin panel — API kalitlarni boshqarish
Alohida **admin kalit** talab qilinadi (mijoz kalitidan farqli):
```bash
# Admin kalitni yaratish/ko'rish
python3 api_keys.py --admin

# Barcha kalitlarni ko'rish
curl http://localhost:8000/admin/keys -H "X-API-Key: admin_..."

# Yangi mijoz kaliti yaratish
curl -X POST http://localhost:8000/admin/keys \
  -H "Content-Type: application/json" -H "X-API-Key: admin_..." \
  -d '{"owner": "telegram_bot"}'

# Kalitni bekor qilish
curl -X POST http://localhost:8000/admin/keys/revoke \
  -H "Content-Type: application/json" -H "X-API-Key: admin_..." \
  -d '{"api_key": "cs_..."}'
```

## Telegram bot

Bot API backendiga ulanib ishlaydi (bot -> API -> model zanjiri).

### Ishga tushirish
```bash
# 1. Avval API backend ishga tushgan bo'lishi kerak
cd api && uvicorn main:app --host 0.0.0.0 --port 8000 &

# 2. Bot uchun API kalit yarating
cd api && python3 api_keys.py "telegram_bot"
# Chiqadi: cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 3. Kutubxonalarni o'rnating
cd ../telegram_bot
pip install -r requirements.txt --break-system-packages

# 4. Muhit o'zgaruvchilarini o'rnating
export BOT_TOKEN="sizning_@BotFather_dan_olgan_tokeningiz"
export CYBERSHIELD_API_KEY="cs_xxxxx"  # 2-qadamda olingan kalit
export CYBERSHIELD_API_URL="http://localhost:8000"

# 5. Botni ishga tushiring
python3 bot.py
```

### Bot funksiyalari
- `/start`, `/help` buyruqlari
- Har qanday matnni yuborsangiz, avtomatik tahlil qilinadi
- Natija bilan birga "✅ To'g'ri / ❌ Noto'g'ri" tugmalari chiqadi —
  bosilganda `/feedback` endpointiga yuboriladi (real foydalanuvchi
  ma'lumotlarini yig'ish uchun)

### Muhim eslatma: bu muhitda jonli sinov cheklangan
Ushbu ishlab chiqish muhitida faqat ma'lum domenlarga (pypi, github va h.k.)
tarmoq ruxsati bor, `api.telegram.org` esa yo'q. Shuning uchun:
- Bot kodi **to'liq yozilgan va sinovdan o'tgan**, lekin haqiqiy Telegram
  serveriga ulanib jonli ishga tushirilmagan
- Sinov `telegram_bot/test_bot_logic.py` orqali o'tkazildi — bu Telegram
  transport qatlamini soxtalashtirib (mock), lekin **haqiqiy API va
  model bilan** butun zanjirni (bot handler -> HTTP so'rov -> model ->
  javob -> feedback) tekshiradi
- Yuqoridagi "Ishga tushirish" bosqichlarini o'zingizning bot tokeningiz
  bilan bajarsangiz, bot to'liq ishlashi kerak

## Netlify + Webhook orqali BEPUL joylashtirish (alternativ yo'l)

Agar server ijaraga olishni istamasangiz, botni **butunlay bepul**
Netlify Functions orqali webhook rejimida joylashtirish mumkin.

### Nima uchun bu ishlaydi
Bizning model (TF-IDF + Logistic Regression) matematik jihatdan sodda
bo'lgani uchun, u scikit-learn'siz, sof JavaScript kodida qayta yozildi
(`netlify/functions/lightweight_model/predict.mjs`). Bu paket hajmini
50MB Netlify chegarasidan ~70 marta kichik (708KB) qildi.

### To'g'rilik kafolati
JavaScript versiyasi Python/sklearn versiyasi bilan **25/25 test holatida
aynan bir xil natija** berishi tasdiqlangan (farq: 0.000000). Tekshirish:
```bash
cd netlify/functions
node verify_js_model.mjs
```

### Fayl tuzilishi
```
netlify.toml                          # Netlify konfiguratsiyasi
public/index.html                     # Minimal placeholder sahifa
netlify/functions/
├── telegram-webhook.mjs              # Asosiy webhook handler
├── test_webhook_logic.mjs            # Telegram serversiz mantiqiy sinov
├── verify_js_model.mjs                # JS vs sklearn solishtirish
└── lightweight_model/
    ├── predict.mjs                    # Sof JS bashorat mantiqi
    ├── word_features.mjs              # So'z xususiyatlari (idf+coef)
    ├── char_features.mjs              # Harf xususiyatlari (idf+coef)
    └── config.mjs                     # intercept, classes, ngram sozlamalari
```

### Joylashtirish qadamlari

1. **GitHub'ga yuklash**: bu `cybershield` papkasini GitHub repositoriyasiga yuklang.

2. **Netlify'da sayt yaratish**:
   - netlify.com'ga kiring, GitHub bilan bog'lang (bepul ro'yxatdan o'tish, karta talab qilinmaydi)
   - "Add new site" -> "Import an existing project" -> repositoriyangizni tanlang
   - Build sozlamalari `netlify.toml` orqali avtomatik aniqlanadi

3. **BOT_TOKEN muhit o'zgaruvchisini qo'shish**:
   - Netlify saytingiz sozlamalarida: Site configuration -> Environment variables
   - Yangi o'zgaruvchi: `BOT_TOKEN` = (BotFather'dan olingan tokeningiz)

4. **Sayt manzilini olish**: Netlify sizga `https://sizning-sayt.netlify.app` kabi manzil beradi.

5. **Telegram webhook'ni ro'yxatdan o'tkazish** (bu buyruqni o'zingizning
   kompyuteringizdan yoki telefon brauzeridan bajaring):
   ```
   https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://sizning-sayt.netlify.app/telegram-webhook
   ```
   Brauzerda shu manzilga kirib, `{"ok":true,"result":true,...}` javobini ko'rsangiz, muvaffaqiyatli.

6. **Sinash**: Telegramda botingizga `/start` yuboring.

### Cheklovlar (halol eslatma)
- **Feedback tugmalari hech qayerga saqlanmaydi** — Netlify Functions
  holatsiz (stateless) ishlaydi. Doimiy saqlash uchun Netlify Blobs
  yoki tashqi baza (Supabase kabi, bepul tarifi bor) ulash kerak bo'ladi.
- Bu yo'l bilan **admin panel va batch/URL tahlil endpointlari** ishlamaydi
  (ular faqat to'liq FastAPI backendda mavjud). Agar ular kerak bo'lsa,
  VPS (Oracle Cloud Free Tier kabi) yaxshiroq tanlov.

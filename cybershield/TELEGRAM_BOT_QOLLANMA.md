# CyberShield AI Telegram Botini Ishga Tushirish — To'liq Qo'llanma

Bu qo'llanma sizni hech qanday oldindan tajriba talab qilmasdan, boshidan
oxirigacha olib boradi. Har bir qadamni ketma-ket bajaring, hech birini
o'tkazib yubormang.

---

## QADAM 1: BotFather orqali bot yaratish va token olish

1. Telefoningizda yoki kompyuteringizda Telegram ilovasini oching.
2. Qidiruv qutisiga yozing: `@BotFather` — bu Telegramning rasmiy bot yaratish xizmati (ko'k tasdiqlash belgisi bor bo'ladi).
3. `@BotFather` chatini oching va **Start** tugmasini bosing (yoki `/start` yozing).
4. Endi `/newbot` buyrug'ini yozing va yuboring.
5. BotFather sizdan botning **to'liq nomini** so'raydi (masalan: `CyberShield AI`). Bu odamlar ko'radigan nom, istalgan bo'lishi mumkin. Yozing va yuboring.
6. Keyin **username** so'raydi — bu **majburiy ravishda** `bot` bilan tugashi kerak (masalan: `CyberShieldAI_bot` yoki `cybershield_uz_bot`). Agar username band bo'lsa, BotFather sizga aytadi, boshqasini sinab ko'ring.
7. Muvaffaqiyatli bo'lgach, BotFather sizga shunga o'xshash xabar yuboradi:

   ```
   Done! Congratulations on your new bot...
   Use this token to access the HTTP API:
   7123456789:AAHkZ3x9pL2m...
   ```

8. **Bu token — sizning botingizning "kaliti"**. Uni nusxalab, xavfsiz joyga (masalan, telefoningizdagi "Eslatmalar" ilovasiga yoki parol menejeriga) saqlab qo'ying.

   ⚠️ **Muhim ogohlantirish**: Bu tokenni hech kimga bermang, hech qaerga (GitHub, forum, skrinshot ijtimoiy tarmoqlarda) joylashtirmang. Kim bu tokenni bilsa, sizning botingiz nomidan xabar yubora oladi.

9. Keyinroq foydalanish uchun botingizning username'ini ham eslab qoling (masalan `@CyberShieldAI_bot`) — foydalanuvchilar botni shu nom orqali topadi.

**Natija**: Sizda endi `BOT_TOKEN` bor bo'ladi — buni 4-qadamda ishlatamiz.

---

## QADAM 2: Serverga joylashtirish (hosting tanlash)

Bot va API doim ishlab turishi uchun, kompyuteringiz emas, **doim yoqilgan server** kerak. Bu — internetdagi kichik "kompyuter ijaraga olish" xizmati.

### Tavsiya etiladigan variantlar (arzondan qulayigacha):

| Xizmat | Narxi (taxminan) | Izoh |
|---|---|---|
| **Hetzner Cloud** | ~$4-5/oy | Yevropada, arzon va ishonchli |
| **DigitalOcean** | ~$6/oy | Boshlang'ich uchun eng oson, ko'p qo'llanma bor |
| **Timeweb / Beget** | ~$3-5/oy | Rossiya/O'zbekiston hududiga yaqinroq, kirill interfeys |

### Server sotib olishda tanlash kerak bo'lgan parametrlar:
- **Operatsion tizim**: Ubuntu 22.04 (eng ko'p qo'llab-quvvatlanadigan)
- **Hajmi**: eng kichik/arzon tarif yetarli (1 CPU, 1GB RAM) — chunki bizning model juda yengil (u og'ir sun'iy intellekt emas, sodda statistik model)
- **Joylashuv**: agar tanlov bo'lsa, Yevropa yoki O'zbekistonga yaqinroq mintaqani tanlang (tezroq ishlaydi)

### Server sotib olgandan keyin sizga beriladi:
- IP-manzil (masalan: `195.201.XX.XX`)
- Root parol (yoki SSH kalit fayli)

### Serverga ulanish:
Kompyuteringizda terminal (Mac/Linux) yoki PowerShell/PuTTY (Windows) orqali:

```bash
ssh root@195.201.XX.XX
```

(IP-manzil o'rniga sizga berilgan manzilni yozing). Parolni so'raganda, sizga berilgan parolni kiriting (yozilganda ko'rinmaydi, bu normal).

**Natija**: Endi siz serverning ichida "turasiz" — undan keyingi barcha buyruqlar shu yerda bajariladi.

---

## QADAM 3: Serverni tayyorlash va kodni yuklash

Serverga ulangandan keyin, ketma-ket quyidagi buyruqlarni bajaring:

### 3.1. Tizimni yangilash
```bash
apt update && apt upgrade -y
```
(Bu bir necha daqiqa vaqt olishi mumkin, kutib turing)

### 3.2. Python va kerakli vositalarni o'rnatish
```bash
apt install -y python3 python3-pip git nano
```

### 3.3. Loyiha uchun papka yaratish
```bash
mkdir -p /opt/cybershield
cd /opt/cybershield
```

### 3.4. Kodni serverga yuklash

Men sizga bergan fayllarni serverga yuklashning ikkita usuli bor:

**Usul A (agar fayllarni kompyuteringizga yuklab olgan bo'lsangiz):**

Kompyuteringizda (server ichida EMAS, o'zingizning kompyuteringizda) yangi terminal oching va:
```bash
scp -r /kompyuteringizdagi/cybershield/yo'l root@195.201.XX.XX:/opt/cybershield/
```

**Usul B (agar fayllarni GitHub'ga joylashtirgan bo'lsangiz):**
```bash
cd /opt/cybershield
git clone https://github.com/sizning_username/cybershield.git .
```

Agar fayllarni qanday yuklashni bilmasangiz — menga aytsangiz, aniq usulni birga hal qilamiz.

### 3.5. Fayllar to'g'ri joyda ekanini tekshirish
```bash
cd /opt/cybershield
ls
```
Natijada `api`, `model`, `data`, `telegram_bot` papkalarini ko'rishingiz kerak.

### 3.6. Python kutubxonalarini o'rnatish
```bash
cd /opt/cybershield
pip install -r api/requirements.txt --break-system-packages
pip install -r telegram_bot/requirements.txt --break-system-packages
```

**Natija**: Endi serveringizda barcha kod va kerakli kutubxonalar bor.

---

## QADAM 4: API kalit yaratish va muhit o'zgaruvchilarini sozlash

### 4.1. Bot uchun API kalit yaratish
```bash
cd /opt/cybershield/api
python3 api_keys.py telegram_bot
```
Natijada shunga o'xshash chiqadi:
```
Yangi API kalit yaratildi (telegram_bot uchun):
cs_AbCdEfGh123456...
```
Bu qatorni (`cs_` bilan boshlanadigan) nusxalab oling.

### 4.2. Admin kalitni yaratish (o'zingiz uchun, kelajakda kerak bo'ladi)
```bash
python3 api_keys.py --admin
```
Bu ham bir qatorli kalit chiqaradi (`admin_` bilan boshlanadi) — buni ham saqlab qo'ying.

### 4.3. `.env` faylini yaratish (barcha maxfiy ma'lumotlarni bir joyda saqlash uchun)

```bash
cd /opt/cybershield
nano .env
```

Ochilgan tahrirlovchida quyidagini yozing (o'zingizning haqiqiy qiymatlaringiz bilan):

```
BOT_TOKEN=7123456789:AAHkZ3x9pL2m...
CYBERSHIELD_API_KEY=cs_AbCdEfGh123456...
CYBERSHIELD_API_URL=http://localhost:8000
```

Yozib bo'lgach: `Ctrl+O` (saqlash), `Enter`, keyin `Ctrl+X` (chiqish).

### 4.4. `.env` faylini himoyalash
```bash
chmod 600 /opt/cybershield/.env
```
(Bu fayl faqat siz o'qiy olishingizni ta'minlaydi)

**Natija**: Barcha maxfiy kalitlar bitta xavfsiz faylda saqlanadi.

---

## QADAM 5: API va Botni doimiy ishlaydigan qilib sozlash (systemd)

Oddiy `python3 bot.py` deb yozsangiz, terminal yopilganda bot ham to'xtaydi.
Buning oldini olish uchun **systemd** — Linux'ning "doim ishga tushirib
turish" tizimidan foydalanamiz.

### 5.1. API uchun systemd fayl yaratish
```bash
nano /etc/systemd/system/cybershield-api.service
```

Quyidagini yozing:
```ini
[Unit]
Description=CyberShield AI API
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/cybershield/api
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
Saqlang (`Ctrl+O`, `Enter`, `Ctrl+X`).

### 5.2. Bot uchun systemd fayl yaratish
```bash
nano /etc/systemd/system/cybershield-bot.service
```

Quyidagini yozing:
```ini
[Unit]
Description=CyberShield AI Telegram Bot
After=network.target cybershield-api.service

[Service]
Type=simple
WorkingDirectory=/opt/cybershield/telegram_bot
EnvironmentFile=/opt/cybershield/.env
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
Saqlang (`Ctrl+O`, `Enter`, `Ctrl+X`).

### 5.3. Ikkalasini ishga tushirish
```bash
systemctl daemon-reload
systemctl enable cybershield-api cybershield-bot
systemctl start cybershield-api
sleep 3
systemctl start cybershield-bot
```

### 5.4. Ishlab turganini tekshirish
```bash
systemctl status cybershield-api
systemctl status cybershield-bot
```
Ikkalasida ham yashil `active (running)` yozuvini ko'rishingiz kerak.

Agar xato chiqsa, sabab-natijasini ko'rish uchun:
```bash
journalctl -u cybershield-api -n 50
journalctl -u cybershield-bot -n 50
```

**Natija**: Endi API va bot serverni qayta yuklasangiz ham, terminal yopilsa
ham, avtomatik ishlab turadi.

---

## QADAM 6: Haqiqiy Telegramda sinab ko'rish

1. Telefoningizda Telegram'ni oching.
2. Qidiruv orqali botingizni toping (masalan `@CyberShieldAI_bot`).
3. **Start** tugmasini bosing yoki `/start` yozing.
4. Xush kelibsiz xabari kelishi kerak.
5. Endi sinov xabarlarini yuboring:
   - `Kartangiz bloklanadi, tasdiqlash kodini yuboring!` → 🔴 YUQORI XAVF chiqishi kerak
   - `Ertaga soat 15:00da uchrashamiz.` → 🟢 XAVFSIZ chiqishi kerak
6. Har bir natija ostida "✅ To'g'ri / ❌ Noto'g'ri" tugmalari chiqishi kerak — bosib ko'ring, "Rahmat!" degan javob kelishi kerak.
7. `/help` buyrug'ini yuborib, yordam xabari chiqishini tekshiring.

Agar biror narsa ishlamasa yoki xato chiqsa — **aynan qaysi xabarni yuborganingizni va nima chiqqanini** menga aytsangiz, birga tuzatamiz.

**Natija**: Bot endi haqiqiy foydalanuvchilar uchun ishlaydi! 🎉

---

## QADAM 7: BotFather orqali botni "silliqlashtirish" (ixtiyoriy, lekin tavsiya etiladi)

`@BotFather` chatiga qaytib, quyidagilarni sozlang:

1. `/setdescription` — botni birinchi marta ochganda ko'rinadigan tasvir (masalan: "O'zbek tilidagi phishing va scam xabarlarni aniqlash bo'yicha AI yordamchi")
2. `/setabouttext` — bot profilida ko'rinadigan qisqa matn
3. `/setuserpic` — bot uchun logotip/rasm yuklash
4. `/setcommands` — buyruqlar menyusini sozlash, quyidagini yuboring:
   ```
   start - Botni ishga tushirish
   help - Yordam va foydalanish qo'llanmasi
   ```

**Natija**: Bot professional ko'rinishga ega bo'ladi.

---

## QADAM 8: Xavfsizlik va monitoring

### 8.1. `.env` faylini hech qachon oshkora joyga qo'ymang
Agar kodni GitHub'ga yuklasangiz, albatta `.gitignore` fayl yarating:
```bash
cd /opt/cybershield
echo ".env" >> .gitignore
echo "api/api_keys.json" >> .gitignore
echo "api/admin_key.txt" >> .gitignore
echo "api/logs/" >> .gitignore
```

### 8.2. Loglarni muntazam ko'rib turing
Haftada bir marta shu buyruq orqali so'nggi so'rovlarni ko'ring:
```bash
tail -50 /opt/cybershield/api/logs/requests.jsonl
```
Bu yerda `"risk_level": "aniq_emas"` deb belgilangan holatlarga alohida
e'tibor bering — bular model ishonchsiz bo'lgan holatlar, va aynan shular
keyingi dataset kengaytirish uchun eng qimmatli material bo'ladi.

### 8.3. Serverni yangilab turish
Oyda bir marta:
```bash
apt update && apt upgrade -y
```

---

## Muammo yuzaga kelsa nima qilish kerak?

Agar biror qadamda xatolik chiqsa:
1. Xato xabarining **to'liq matnini** nusxalab oling
2. Qaysi qadamda va qaysi buyruqni bajarayotganda chiqganini eslab qoling
3. Menga shu ma'lumotlarni yuborsangiz, birga tezda hal qilamiz

Bu — bir martalik ish emas, shuning uchun shoshilmang. Har bir qadamni
tinch bajarib, natijasini tekshirib, keyingisiga o'tsangiz bo'ldi.

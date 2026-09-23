"""
CyberShield AI — URL ajratish va tekshirish moduli.

Matn ichidan havolalarni topib, ularni O'zbekistondagi rasmiy (ishonchli)
domenlar ro'yxati bilan solishtiradi. Bu to'liq domen-obro'si (reputation)
bazasi emas — MVP darajasidagi evristik tekshiruv, lekin foydali signal beradi:
agar xabarda "bank" so'zi bilan birga rasmiy bo'lmagan domen bo'lsa, bu kuchli
shubha belgisi.
"""

import re

URL_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?"
    r"([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+)"
    r"(?:/[^\s]*)?",
    re.IGNORECASE,
)

# O'zbekistondagi rasmiy va keng tanilgan ishonchli domenlar (to'liq emas,
# lekin eng ko'p qalbakilashtiriladigan tashkilotlarni qamrab oladi)
TRUSTED_DOMAINS = {
    "gov.uz", "my.gov.uz", "soliq.uz", "pens.uz", "e-ish.uz",
    "cbu.uz", "mnp.uz",
    "xb.uz", "ipotekabank.uz", "kapitalbank.uz", "agrobank.uz", "asakabank.uz",
    "oson.uz", "click.uz", "payme.uz",
    "telegram.org", "t.me",
    "olx.uz",
    "uzairways.com", "uzairways.uz",
    "mygov.uz",
}

# Shubhali belgilar: qisqartirilgan havola xizmatlari, imlo o'yinlari,
# yoki taniqli brendni taqlid qiluvchi domen naqshlari
SUSPICIOUS_PATTERNS = [
    r"\.(top|click|xyz|info|online|site|club|work|live)$",  # arzon/tez-tez suiiste'mol qilinadigan TLD'lar
    r"-uz\b",       # "bank-uz.com" kabi rasmiy ko'rinish yaratishga urinish
    r"uz-",         # "uz-support.net" kabi
    r"support",     # "telegram-support" kabi taqlid so'zlar
    r"verify",
    r"secure",
    r"bonus",
    r"gift",
]


def extract_urls(text: str) -> list[str]:
    """Matn ichidan barcha domen/URL ko'rinishidagi qatorlarni topadi."""
    matches = URL_PATTERN.findall(text)
    # Faqat haqiqiy domenga o'xshaganlarini qoldiramiz (kamida bitta nuqta bor)
    domains = [m.lower() for m in matches if "." in m]
    return list(dict.fromkeys(domains))  # tartibni saqlab, takrorlanishni olib tashlash


def check_domain(domain: str) -> dict:
    """Bitta domenni tekshirib, xulosa qaytaradi."""
    domain_clean = domain.lower().strip(".")

    if domain_clean in TRUSTED_DOMAINS:
        return {"domain": domain, "status": "ishonchli", "reason": "Rasmiy/tanilgan domen ro'yxatida"}

    for base in TRUSTED_DOMAINS:
        if domain_clean.endswith("." + base):
            return {"domain": domain, "status": "ishonchli", "reason": f"{base} subdomeni"}

    suspicious_reasons = []
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, domain_clean):
            suspicious_reasons.append(pattern)

    if suspicious_reasons:
        return {
            "domain": domain,
            "status": "shubhali",
            "reason": f"Shubhali naqsh(lar) topildi: {', '.join(suspicious_reasons)}",
        }

    return {
        "domain": domain,
        "status": "noma'lum",
        "reason": "Ishonchli ro'yxatda emas, lekin aniq shubhali belgi ham yo'q — ehtiyot bo'ling",
    }


def analyze_urls_in_text(text: str) -> list[dict]:
    """Matndagi barcha URL/domenlarni topib, har birini tekshiradi."""
    urls = extract_urls(text)
    return [check_domain(u) for u in urls]

"""
CyberShield AI — umumiy matn normalizatsiya funksiyasi.
Bu modul train_model.py, predict/test skriptlari va (kelajakda) API tomonidan
bir xilda ishlatiladi, shunda model o'qitilgan va ishlatilgan vaqtda AYNAN
bir xil tozalash mantig'i qo'llaniladi (bu ML loyihalarda juda muhim qoida —
"training-serving skew"ning oldini olish).
"""

import re

# O'zbek tilida apostrof (tutuq belgisi) turli Unicode ko'rinishlarda yoziladi:
# ' (U+0027 oddiy), ' (U+2019 "smart quote"), ʻ (U+02BB), ʼ (U+02BC), ` (U+0060) va h.k.
APOSTROPHE_VARIANTS = ["'", "'", "ʻ", "ʼ", "`", "´", "‘"]


def normalize_text(text):
    """Matnni model uchun standart ko'rinishga keltiradi."""
    text = str(text)
    for variant in APOSTROPHE_VARIANTS:
        text = text.replace(variant, "'")
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text

"""
CyberShield AI — API kalit boshqaruvi.

Oddiy MVP darajasidagi autentifikatsiya: kalitlar JSON faylida saqlanadi
(production'da bu albatta PostgreSQL/Redis kabi haqiqiy bazaga ko'chirilishi
kerak, lekin MVP uchun bu yetarli va tez ishga tushiriladi).

Har bir kalit quyidagilarni o'z ichiga oladi:
  - key: kalitning o'zi (tasodifiy generatsiya qilingan)
  - owner: kalit egasi (masalan "telegram_bot", "demo_client")
  - active: kalit faolmi
  - created_at: yaratilgan sana
"""

import json
import secrets
from pathlib import Path
from datetime import datetime, timezone

KEYS_FILE = Path(__file__).resolve().parent / "api_keys.json"


def _load_keys() -> dict:
    if not KEYS_FILE.exists():
        return {}
    with open(KEYS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_keys(keys: dict):
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(keys, f, ensure_ascii=False, indent=2)


def generate_api_key(owner: str) -> str:
    """Yangi API kalit yaratadi va saqlaydi."""
    keys = _load_keys()
    new_key = "cs_" + secrets.token_urlsafe(32)
    keys[new_key] = {
        "owner": owner,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_keys(keys)
    return new_key


def is_valid_key(api_key: str) -> bool:
    """Kalit mavjud va faolligini tekshiradi."""
    keys = _load_keys()
    entry = keys.get(api_key)
    return entry is not None and entry.get("active", False)


def revoke_key(api_key: str) -> bool:
    """Kalitni bekor qiladi (o'chirmaydi, faqat faolsizlantiradi)."""
    keys = _load_keys()
    if api_key in keys:
        keys[api_key]["active"] = False
        _save_keys(keys)
        return True
    return False


# ---------------------------------------------------------------------------
# ADMIN KALIT
# Admin panel endpointlariga kirish uchun alohida, bitta "master" kalit.
# Bu oddiy mijoz kalitlaridan farqli — faqat kalitlarni boshqarish huquqini beradi.
# ---------------------------------------------------------------------------

ADMIN_KEY_FILE = Path(__file__).resolve().parent / "admin_key.txt"


def get_or_create_admin_key() -> str:
    """Admin kalitni qaytaradi, agar mavjud bo'lmasa yangi yaratadi."""
    if ADMIN_KEY_FILE.exists():
        return ADMIN_KEY_FILE.read_text(encoding="utf-8").strip()
    new_key = "admin_" + secrets.token_urlsafe(32)
    ADMIN_KEY_FILE.write_text(new_key, encoding="utf-8")
    return new_key


def is_admin_key(key: str) -> bool:
    if not ADMIN_KEY_FILE.exists():
        return False
    return key == ADMIN_KEY_FILE.read_text(encoding="utf-8").strip()


def get_owner(api_key: str) -> str | None:
    keys = _load_keys()
    entry = keys.get(api_key)
    return entry.get("owner") if entry else None


def list_keys() -> list[dict]:
    """Barcha kalitlarni (kalitning o'zi maskalangan holda) ro'yxat qiladi."""
    keys = _load_keys()
    result = []
    for key, meta in keys.items():
        result.append({
            "key_preview": key[:8] + "..." + key[-4:],
            "owner": meta.get("owner"),
            "active": meta.get("active"),
            "created_at": meta.get("created_at"),
        })
    return result


if __name__ == "__main__":
    # Demo/boshlang'ich kalitlarni yaratish uchun qulay skript sifatida ham ishlaydi
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--admin":
        key = get_or_create_admin_key()
        print(f"Admin kalit (mavjud bo'lsa qaytariladi, yo'q bo'lsa yaratiladi):\n{key}")
    elif len(sys.argv) > 1:
        owner_name = sys.argv[1]
        key = generate_api_key(owner_name)
        print(f"Yangi API kalit yaratildi ({owner_name} uchun):\n{key}")
    else:
        print("Foydalanish:\n  python3 api_keys.py <owner_nomi>   # mijoz kaliti yaratish\n  python3 api_keys.py --admin        # admin kalitni ko'rish/yaratish")

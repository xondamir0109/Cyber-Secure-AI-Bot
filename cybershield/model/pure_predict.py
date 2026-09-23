"""
CyberShield AI — Sof Python (hech qanday tashqi kutubxonasiz) bashorat moduli.

Bu modul export_lightweight_model.py orqali yaratilgan JSON fayllardan
foydalanib, scikit-learn pipeline aynan qanday hisoblashini QADAM-BAQADAM
qayta yaratadi:

  1. Matnni normalizatsiya qilish (text_utils.normalize_text bilan bir xil)
  2. So'z tokenlarini ajratish (regex: kamida 2 harfdan iborat so'zlar)
  3. 1-2 gramlar yasash (bitta so'z, ikki so'z birikmasi)
  4. Harf 2-5 gramlarini yasash (har bir so'z ichida, so'zlar orasidan o'tmaydi)
  5. TF-IDF hisoblash (sublinear_tf=True formula: 1 + log(count))
  6. L2 normalizatsiya (har ikki qism -- so'z va harf -- alohida)
  7. Logistic Regression: chiziqli yig'indi + intercept -> sigmoid

Faqat Python standart kutubxonasi (re, json, math) ishlatiladi -- hech qanday
tashqi paket kerak emas. Shuning uchun bu Netlify Functions kabi qattiq
hajm cheklovi bo'lgan muhitlarda ishlatilishi mumkin.
"""

import re
import json
import math
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent / "lightweight_model"

# ---------------------------------------------------------------------------
# MATN NORMALIZATSIYASI (text_utils.py bilan AYNAN bir xil bo'lishi shart)
# ---------------------------------------------------------------------------

APOSTROPHE_VARIANTS = ["'", "'", "ʻ", "ʼ", "`", "´", "‘"]


def normalize_text(text):
    text = str(text)
    for variant in APOSTROPHE_VARIANTS:
        text = text.replace(variant, "'")
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ---------------------------------------------------------------------------
# TOKENIZATSIYA (sklearn TfidfVectorizer standart sozlamalarini takrorlaydi)
# ---------------------------------------------------------------------------

WORD_TOKEN_PATTERN = re.compile(r"(?u)\b\w\w+\b")


def word_tokenize(text):
    return WORD_TOKEN_PATTERN.findall(text)


def word_ngrams(tokens, ngram_range):
    """Berilgan tokenlardan (min_n, max_n) gramlarini yasaydi."""
    min_n, max_n = ngram_range
    ngrams = []
    n_tokens = len(tokens)
    for n in range(min_n, min(max_n, n_tokens) + 1):
        for i in range(n_tokens - n + 1):
            ngrams.append(" ".join(tokens[i:i + n]))
    return ngrams


def char_wb_ngrams(text, ngram_range):
    """sklearn analyzer='char_wb' mantig'ini takrorlaydi: har bir so'z bo'shliq
    bilan o'raladi, so'zlar orasidan n-gram o'tmaydi."""
    text = re.sub(r"\s+", " ", text)
    min_n, max_n = ngram_range
    ngrams = []
    for w in text.split():
        w = " " + w + " "
        w_len = len(w)
        for n in range(min_n, min(max_n + 1, w_len + 1)):
            offset = 0
            ngrams.append(w[offset:offset + n])
            while offset + n < w_len:
                offset += 1
                ngrams.append(w[offset:offset + n])
            if offset == 0:
                break
    return ngrams


# ---------------------------------------------------------------------------
# MODELNI YUKLASH
# ---------------------------------------------------------------------------

_word_features = None
_char_features = None
_config = None


def _load():
    global _word_features, _char_features, _config
    if _word_features is None:
        with open(MODEL_DIR / "word_features.json", "r", encoding="utf-8") as f:
            _word_features = json.load(f)
        with open(MODEL_DIR / "char_features.json", "r", encoding="utf-8") as f:
            _char_features = json.load(f)
        with open(MODEL_DIR / "config.json", "r", encoding="utf-8") as f:
            _config = json.load(f)
    return _word_features, _char_features, _config


# ---------------------------------------------------------------------------
# TF-IDF + L2 NORMALIZATSIYA + CHIZIQLI YIG'INDI
# ---------------------------------------------------------------------------

def _tfidf_weighted_sum(ngrams, features_dict):
    """
    Berilgan n-gramlar ro'yxati uchun:
      1. Har bir n-gramning takrorlanish sonini (term frequency) hisoblaydi
      2. sublinear_tf formulasini qo'llaydi: tf = 1 + log(count)
      3. idf bilan ko'paytiradi -> xom tfidf qiymati
      4. Butun vektorning L2 normini hisoblaydi
      5. Normallashtirilgan qiymatni koeffitsient bilan ko'paytirib yig'adi

    Qaytaradi: (chiziqli_yigindi, faol_xususiyatlar_soni)
    """
    counts = {}
    for ng in ngrams:
        if ng in features_dict:  # faqat o'qitishda ko'rilgan xususiyatlar hisobga olinadi
            counts[ng] = counts.get(ng, 0) + 1

    if not counts:
        return 0.0, 0

    raw_tfidf = {}
    for ng, count in counts.items():
        idf, _coef = features_dict[ng]
        tf = 1.0 + math.log(count)  # sublinear_tf=True
        raw_tfidf[ng] = tf * idf

    l2_norm = math.sqrt(sum(v * v for v in raw_tfidf.values()))
    if l2_norm == 0:
        return 0.0, 0

    weighted_sum = 0.0
    for ng, raw_value in raw_tfidf.items():
        normalized = raw_value / l2_norm
        _idf, coef = features_dict[ng]
        weighted_sum += normalized * coef

    return weighted_sum, len(counts)


def predict_proba_pure(text: str) -> dict:
    """
    Matnni tahlil qilib, {class_name: probability} lug'atini qaytaradi.
    Bu funksiya scikit-learn'ga UMUMAN bog'liq emas.
    """
    word_features, char_features, config = _load()

    normalized = normalize_text(text)

    tokens = word_tokenize(normalized)
    ngrams_word = word_ngrams(tokens, config["word_ngram_range"])
    ngrams_char = char_wb_ngrams(normalized, config["char_ngram_range"])

    word_sum, _ = _tfidf_weighted_sum(ngrams_word, word_features)
    char_sum, _ = _tfidf_weighted_sum(ngrams_char, char_features)

    decision = word_sum + char_sum + config["intercept"]

    # classes_ har doim alifbo tartibida: ['phishing', 'safe']
    # decision > 0 -> classes_[1] ('safe') tomonga og'adi
    p_safe = 1.0 / (1.0 + math.exp(-decision))
    p_phishing = 1.0 - p_safe

    classes = config["classes"]
    return {classes[0]: p_phishing, classes[1]: p_safe}


def predict_pure(text: str) -> str:
    proba = predict_proba_pure(text)
    return max(proba, key=proba.get)

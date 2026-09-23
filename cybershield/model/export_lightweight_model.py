"""
CyberShield AI — Modelni "yengil" (lightweight) formatga eksport qilish.

Netlify Functions kabi serverless muhitlarda scikit-learn/numpy/scipy
paketlari hajm chegarasidan (50MB) oshib ketishi mumkin. Bizning model
(TF-IDF + Logistic Regression) matematik jihatdan sodda bo'lgani uchun,
uni sof Python (hech qanday tashqi kutubxonasiz) formatga aylantiramiz:

  - Har bir so'z/harf-kombinatsiya uchun (idf, coefficient) juftligini
    bitta JSON faylida saqlaymiz
  - Ishlash vaqtida faqat oddiy dict qidirish va arifmetika kerak bo'ladi

Bu fayl ishga tushirilgandan keyin, natijani asl (sklearn) model bilan
solishtirib tekshirish MAJBURIY — buni verify_lightweight_model.py orqali
qiling.
"""

import json
import joblib
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent / "cybershield_model.joblib"
OUTPUT_DIR = Path(__file__).resolve().parent / "lightweight_model"
OUTPUT_DIR.mkdir(exist_ok=True)


def main():
    pipeline = joblib.load(MODEL_PATH)
    features = pipeline.named_steps["features"]
    clf = pipeline.named_steps["clf"]

    word_vec = features.transformer_list[0][1]  # TfidfVectorizer(analyzer="word", ...)
    char_vec = features.transformer_list[1][1]  # TfidfVectorizer(analyzer="char_wb", ...)

    n_word = len(word_vec.vocabulary_)
    coef = clf.coef_[0]  # shape (n_word + n_char,)

    # So'z xususiyatlari: {token: [idf, coefficient]}
    word_features = {}
    for token, idx in word_vec.vocabulary_.items():
        word_features[token] = [round(float(word_vec.idf_[idx]), 6), round(float(coef[idx]), 6)]

    # Harf xususiyatlari: {ngram: [idf, coefficient]}  -- indekslar n_word dan boshlanadi
    char_features = {}
    for ngram, idx in char_vec.vocabulary_.items():
        char_features[ngram] = [round(float(char_vec.idf_[idx]), 6), round(float(coef[n_word + idx]), 6)]

    config = {
        "intercept": round(float(clf.intercept_[0]), 6),
        "classes": list(clf.classes_),  # ['phishing', 'safe'] -- alifbo tartibida
        "word_ngram_range": list(word_vec.ngram_range),
        "char_ngram_range": list(char_vec.ngram_range),
    }

    with open(OUTPUT_DIR / "word_features.json", "w", encoding="utf-8") as f:
        json.dump(word_features, f, ensure_ascii=False)
    with open(OUTPUT_DIR / "char_features.json", "w", encoding="utf-8") as f:
        json.dump(char_features, f, ensure_ascii=False)
    with open(OUTPUT_DIR / "config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False)

    # Hajmni tekshirish
    total_size = sum((OUTPUT_DIR / fn).stat().st_size for fn in ["word_features.json", "char_features.json", "config.json"])
    print(f"So'z xususiyatlari: {len(word_features)} ta")
    print(f"Harf xususiyatlari: {len(char_features)} ta")
    print(f"Jami fayl hajmi: {total_size / 1024:.1f} KB ({total_size / 1024 / 1024:.2f} MB)")
    print(f"Saqlandi: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

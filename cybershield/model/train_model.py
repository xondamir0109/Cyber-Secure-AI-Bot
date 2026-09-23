"""
CyberShield AI — Baseline model o'qitish
TF-IDF (so'z va harf n-gram) + Logistic Regression
"""

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline, FeatureUnion
from text_utils import normalize_text

DATA_PATH = "/home/claude/cybershield/data/dataset.csv"
MODEL_PATH = "/home/claude/cybershield/model/cybershield_model.joblib"

def main():
    df = pd.read_csv(DATA_PATH)
    print(f"Jami namunalar: {len(df)}")
    print(df["label"].value_counts())
    print()

    X = df["text"]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Ikki xil xususiyat birlashtiriladi:
    #  1) so'z-darajasidagi 1-2 gramlar -> "otkazing", "kartangiz raqami" kabi so'z birikmalari,
    #     ijtimoiy-muhandislik iboralarini yaxshi ushlaydi
    #  2) harf-darajasidagi 2-5 gramlar -> imlo variatsiyalari, qisqartmalarga chidamli
    # Ikkalasi ham matnni avval normalize_text orqali tozalaydi (apostrof, katta-kichik harf).
    features = FeatureUnion([
        ("word", TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=1, sublinear_tf=True, preprocessor=normalize_text)),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=1, sublinear_tf=True, preprocessor=normalize_text)),
    ])

    pipeline = Pipeline([
        ("features", features),
        ("clf", LogisticRegression(max_iter=2000, class_weight="balanced", C=2.0)),
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print("=" * 50)
    print(f"TEST ANIQLIK (accuracy): {acc:.2%}")
    print("=" * 50)
    print()
    print("Klassifikatsiya hisoboti:")
    print(classification_report(y_test, y_pred))
    print("Chalkashlik matritsasi (confusion matrix):")
    print(confusion_matrix(y_test, y_pred, labels=["phishing", "safe"]))
    print()

    # Cross-validation orqali barqarorlikni tekshirish
    cv_scores = cross_val_score(pipeline, X, y, cv=5)
    print(f"5-fold Cross-Validation aniqligi: {cv_scores.mean():.2%} (+/- {cv_scores.std():.2%})")

    # Modelni saqlash
    joblib.dump(pipeline, MODEL_PATH)
    print(f"\nModel saqlandi: {MODEL_PATH}")

if __name__ == "__main__":
    main()

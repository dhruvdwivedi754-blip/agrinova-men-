import os
import csv
from pathlib import Path
from collections import Counter

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import joblib

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "ml_assets" / "data" / "crop_advisory_dataset.csv"
MODEL_DIR = BASE_DIR / "ml_assets" / "models"
MODEL_PATH = MODEL_DIR / "crop_prediction_model.pkl"


def load_csv(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for r in reader:
            rows.append({k: (v.strip() if isinstance(v, str) else v) for k, v in r.items()})
    return rows


def prepare_dataset(rows):
    X = []
    y = []
    for r in rows:
        target = r.get("Recommended_Crop")
        if not target:
            continue
        # features: the selected input columns
        X.append({
            "State_UT": r.get("State_UT", "").strip(),
            "Soil_Type": r.get("Soil_Type", "").strip(),
            "Temperature_Range_C": r.get("Temperature_Range_C", "").strip(),
            "Water_Availability": r.get("Water_Availability", "").strip(),
            "Season": r.get("Season", "").strip(),
        })
        y.append(target.strip())
    return X, y


def train():
    print("Loading data from:", DATA_PATH)
    rows = load_csv(DATA_PATH)
    print("Rows loaded:", len(rows))
    X, y = prepare_dataset(rows)
    print("Examples after cleaning:", len(X))
    # Quick label pruning: keep labels with at least 3 examples to avoid unseen errors
    label_counts = Counter(y)
    allowed = {lab for lab, cnt in label_counts.items() if cnt >= 3}
    X2, y2 = [], []
    for xi, yi in zip(X, y):
        if yi in allowed:
            X2.append(xi)
            y2.append(yi)
    print("Labels kept:", len(allowed))

    X_train, X_test, y_train, y_test = train_test_split(X2, y2, test_size=0.2, random_state=42, stratify=y2)

    pipeline = Pipeline([
        ("vec", DictVectorizer(sparse=False)),
        ("clf", RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)),
    ])

    print("Training model...")
    pipeline.fit(X_train, y_train)
    print("Training complete. Evaluating...")
    preds = pipeline.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, preds))
    print(classification_report(y_test, preds))

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print("Saved model to:", MODEL_PATH)


if __name__ == "__main__":
    train()

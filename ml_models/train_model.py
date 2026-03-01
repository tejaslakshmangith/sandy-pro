"""Train and save the RandomForest ML classifier from the minerals dataset."""

import os
import sys

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import Config

COLOR_MAP = {
    "red": 0, "orange": 1, "yellow": 2, "green": 3, "blue": 4,
    "purple": 5, "brown": 6, "black": 7, "white": 8, "gray": 9,
    "silver": 10, "gold": 11, "pink": 12, "colorless": 13, "multicolor": 14,
}
LUSTER_MAP = {
    "metallic": 0, "vitreous": 1, "resinous": 2, "waxy": 3, "pearly": 4,
    "silky": 5, "adamantine": 6, "dull": 7, "earthy": 8, "submetallic": 9,
}
FORMATION_MAP = {
    "igneous": 0, "sedimentary": 1, "metamorphic": 2, "hydrothermal": 3,
    "evaporite": 4, "placer": 5,
}


def encode_color(c):
    c = str(c).lower()
    for k, v in COLOR_MAP.items():
        if k in c:
            return v
    return 14


def encode_luster(l):
    l = str(l).lower()
    for k, v in LUSTER_MAP.items():
        if k in l:
            return v
    return 7


def encode_formation(f):
    f = str(f).lower()
    for k, v in FORMATION_MAP.items():
        if k in f:
            return v
    return 0


def train():
    dataset_path = Config.DATASET_PATH
    if not os.path.exists(dataset_path):
        print(f"ERROR: Dataset not found at {dataset_path}")
        sys.exit(1)

    df = pd.read_csv(dataset_path)
    print(f"Loaded {len(df)} rows from {dataset_path}")

    df["color_code"] = df["color"].apply(encode_color)
    df["luster_code"] = df["luster"].apply(encode_luster)
    df["formation_code"] = df["formation_type"].apply(encode_formation)
    df["hardness"] = pd.to_numeric(df["hardness_mohs"], errors="coerce").fillna(5.0)

    features = ["color_code", "hardness", "luster_code", "formation_code"]
    target = "category"

    X = df[features].values
    y = df[target].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test accuracy: {acc:.2%}")

    os.makedirs(os.path.dirname(Config.ML_MODEL_PATH), exist_ok=True)
    joblib.dump(clf, Config.ML_MODEL_PATH)
    print(f"Model saved to {Config.ML_MODEL_PATH}")


if __name__ == "__main__":
    train()

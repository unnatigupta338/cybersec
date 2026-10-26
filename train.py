# train.py
# This file reads the URL dataset, extracts features, trains a Random Forest,
# prints evaluation metrics, and saves the model.
# Run this SECOND (after make_data.py).

import os
import re
import csv                                         # standard library CSV reader (no pandas needed)
import pickle                                      # for saving the trained model
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, confusion_matrix)

# ── Feature extraction ───────────────────────────────────────────────────────
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "ow.ly", "goo.gl",
              "is.gd", "buff.ly", "rebrand.ly"}

PHISH_WORDS = ["login", "verify", "secure", "account", "update",
               "signin", "banking", "confirm", "password", "urgent"]


def extract_features(url: str) -> list:
    """
    Given one URL string, return a list of 10 numbers.
    Each number is one 'clue' about whether the URL might be phishing.
    """
    url_lower = url.lower()

    # Feature 1: total length of the URL
    f1 = len(url)

    # Feature 2: number of dots
    f2 = url.count(".")

    # Feature 3: number of hyphens
    f3 = url.count("-")

    # Feature 4: 1 if URL has an @ symbol, else 0
    f4 = 1 if "@" in url else 0

    # Feature 5: 1 if URL contains an IP address
    f5 = 1 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url) else 0

    # Feature 6: 1 if URL uses HTTPS
    f6 = 1 if url_lower.startswith("https") else 0

    # Feature 7: count of digit characters
    f7 = sum(c.isdigit() for c in url)

    # Feature 8: how many phishing 'trigger words' appear
    f8 = sum(word in url_lower for word in PHISH_WORDS)

    # Feature 9: number of subdomains
    try:
        host = url.split("//", 1)[1].split("/")[0].split("@")[-1]
        f9 = max(0, host.count(".") - 1)
    except IndexError:
        f9 = 0

    # Feature 10: 1 if URL uses a known URL shortener
    try:
        host10 = url.split("//", 1)[1].split("/")[0].lower()
        f10 = 1 if any(s in host10 for s in SHORTENERS) else 0
    except IndexError:
        f10 = 0

    return [f1, f2, f3, f4, f5, f6, f7, f8, f9, f10]


FEATURE_NAMES = [
    "url_length", "dot_count", "hyphen_count", "has_at",
    "has_ip", "is_https", "digit_count", "phish_word_count",
    "subdomain_count", "is_shortened",
]


def load_data(csv_path: str):
    """
    Load the CSV using the standard library (no pandas needed).
    Returns X (list of feature lists) and y (list of labels).
    Accepts both our generated file and a Kaggle CSV with url/label columns.
    """
    X, y = [], []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)              # reads header row automatically
        for row in reader:
            url   = row.get("url", "").strip()
            label = row.get("label", "").strip()
            if url and label:
                try:
                    y.append(int(float(label)))  # convert "0" or "1" to int
                    X.append(extract_features(url))
                except ValueError:
                    pass                         # skip rows with invalid labels
    return X, y


def main():
    # ── 1. Load data ─────────────────────────────────────────────────────────
    csv_path = "data/urls.csv"
    if not os.path.exists(csv_path):
        print("ERROR: data/urls.csv not found. Run make_data.py first.")
        return

    X, y = load_data(csv_path)
    print(f"Loaded {len(X)} rows from {csv_path}")

    # ── 2. Split into training (80%) and testing (20%) sets ──────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"\nTraining rows : {len(X_train)}  |  Test rows: {len(X_test)}")

    # ── 3. Train the Random Forest ────────────────────────────────────────────
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)                  # the model 'learns' here

    # ── 4. Evaluate on the test set ───────────────────────────────────────────
    y_pred = model.predict(X_test)

    acc  = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec  = recall_score(y_test, y_pred)
    cm   = confusion_matrix(y_test, y_pred)

    print(f"\n--- Results -------------------------------------------")
    print(f"Accuracy  : {acc:.2%}")
    print("  -> Out of all URLs tested, this % were classified correctly.\n")

    print(f"Precision : {prec:.2%}")
    print("  -> When the model says 'Phishing', this % of the time it is right.\n")

    print(f"Recall    : {rec:.2%}")
    print("  -> Out of all real phishing links, this % were caught by the model.\n")

    print("Confusion Matrix:")
    print("  Rows = Actual label, Columns = Predicted label")
    print("  [True Safe, False Phishing]")
    print("  [Missed Phishing, Caught Phishing]")
    print(cm, "\n")

    # ── 5. Save the model ─────────────────────────────────────────────────────
    os.makedirs("model", exist_ok=True)
    model_path = "model/rf_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)                    # save as binary file
    print(f"[OK] Model saved to {model_path}")


if __name__ == "__main__":
    main()

# Phishing URL Detector

A simple educational project that checks whether a URL looks safe or like a phishing attempt.
Built with Python, scikit-learn (Random Forest), and Streamlit.

---

## Step-by-Step Setup (Windows)

### 1. Make sure Python is installed

Open **Command Prompt** (press `Win + R`, type `cmd`, press Enter) and type:

```
python --version
```

You should see something like `Python 3.9.x` or higher.
If you get an error, download Python from https://www.python.org/downloads/ — tick **"Add Python to PATH"** during install.

---

### 2. Navigate to the project folder

In the same Command Prompt window, type (replace the path with wherever you saved this folder):

```
cd C:\Users\YourName\Documents\phishing_detector
```

---

### 3. Install the required libraries

```
pip install -r requirements.txt
```

This installs pandas, scikit-learn, and streamlit. Wait until it finishes (may take a minute or two).

---

### 4. Generate the training dataset

```
python make_data.py
```

Expected output:
```
✓ Saved 2000 URLs to data/urls.csv
  Safe (0): 1000
  Phishing (1): 1000
```

---

### 5. Train the model

```
python train.py
```

Expected output (numbers may vary slightly):
```
Loaded 2000 rows from data/urls.csv
Training rows : 1600  |  Test rows: 400

── Results ──────────────────────────────────────────
Accuracy  : ~99%
  → Out of all URLs tested, this % were classified correctly.

Precision : ~99%
  → When the model says 'Phishing', this % of the time it is right.

Recall    : ~99%
  → Out of all real phishing links, this % were caught by the model.

✓ Model saved to model/rf_model.pkl
```

---

### 6. Launch the web app

```
streamlit run app.py
```

Your browser should open automatically at **http://localhost:8501**.
If it does not, copy that address and paste it in your browser.

To stop the app, go back to Command Prompt and press **Ctrl + C**.

---

## Using a Real Kaggle Dataset (optional)

1. Download a URL phishing dataset from Kaggle (search "phishing URL dataset").
2. Make sure it has two columns named exactly `url` and `label` (0 = safe, 1 = phishing).
3. Save it as `data/urls.csv` (replace the generated file).
4. Run `python train.py` again.

---

## Project Files

| File | Purpose |
|------|---------|
| `make_data.py` | Generates 2,000 fake training URLs |
| `train.py` | Trains the Random Forest model and saves it |
| `app.py` | Streamlit web app for checking URLs |
| `requirements.txt` | Python libraries needed |
| `README.md` | This file |
| `VIVA_NOTES.md` | Study notes and Q&A for your viva |
| `data/urls.csv` | Generated after running make_data.py |
| `model/rf_model.pkl` | Saved model after running train.py |

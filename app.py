# app.py
# This is the web app. Run it with:  streamlit run app.py
# It shows a text box where you type a URL and it tells you if it looks safe or phishing.

import re
import pickle
import streamlit as st   # streamlit builds the web page for us

# ── Re-use the same feature extraction code from train.py ───────────────────
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "ow.ly", "goo.gl",
              "is.gd", "buff.ly", "rebrand.ly"}

PHISH_WORDS = ["login", "verify", "secure", "account", "update",
               "signin", "banking", "confirm", "password", "urgent"]

FEATURE_NAMES = [
    "url_length", "dot_count", "hyphen_count", "has_at",
    "has_ip", "is_https", "digit_count", "phish_word_count",
    "subdomain_count", "is_shortened",
]


def extract_features(url: str) -> list:
    """Same 10 features as train.py — must match exactly."""
    url_lower = url.lower()
    f1 = len(url)
    f2 = url.count(".")
    f3 = url.count("-")
    f4 = 1 if "@" in url else 0
    f5 = 1 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url) else 0
    f6 = 1 if url_lower.startswith("https") else 0
    f7 = sum(c.isdigit() for c in url)
    f8 = sum(word in url_lower for word in PHISH_WORDS)
    try:
        host = url.split("//", 1)[1].split("/")[0].split("@")[-1]
        f9 = max(0, host.count(".") - 1)
    except IndexError:
        f9 = 0
    try:
        host10 = url.split("//", 1)[1].split("/")[0].lower()
        f10 = 1 if any(s in host10 for s in SHORTENERS) else 0
    except IndexError:
        f10 = 0
    return [f1, f2, f3, f4, f5, f6, f7, f8, f9, f10]


def build_reasons(features: list) -> list:
    """
    Turn the 10 feature numbers into plain-English sentences.
    Only include a reason if the feature value looks suspicious.
    """
    reasons = []
    vals = dict(zip(FEATURE_NAMES, features))   # pair name with value

    if vals["url_length"] > 75:
        reasons.append(f"🔴 Very long URL ({vals['url_length']} characters) — phishing links are often unusually long.")
    if vals["has_ip"]:
        reasons.append("🔴 Uses an IP address instead of a real domain name — a common phishing trick.")
    if vals["has_at"]:
        reasons.append("🔴 Contains '@' symbol — this can trick your browser into ignoring the real domain.")
    if vals["phish_word_count"] > 0:
        reasons.append(f"🔴 Contains {vals['phish_word_count']} suspicious word(s) like 'login', 'verify', or 'account'.")
    if vals["is_shortened"]:
        reasons.append("🟡 Uses a URL shortener — hides where the link actually goes.")
    if not vals["is_https"]:
        reasons.append("🟡 Does not use HTTPS — the connection is not encrypted.")
    if vals["hyphen_count"] >= 3:
        reasons.append(f"🟡 Has {vals['hyphen_count']} hyphens — suspicious domains often use many hyphens.")
    if vals["subdomain_count"] >= 3:
        reasons.append(f"🟡 Has {vals['subdomain_count']} subdomains — too many subdomains is suspicious.")
    if vals["digit_count"] > 8:
        reasons.append(f"🟡 Has {vals['digit_count']} digits in the URL — legitimate sites rarely need that many.")

    if not reasons:
        reasons.append("✅ No obvious warning signs found in the URL text.")

    return reasons


@st.cache_resource                              # load the model only once
def load_model():
    with open("model/rf_model.pkl", "rb") as f:
        return pickle.load(f)


def analyse(url: str):
    """Run the model on one URL and return (label, risk_pct, reasons)."""
    model    = load_model()
    feats    = extract_features(url)
    proba    = model.predict_proba([feats])[0]  # probability for each class
    risk_pct = int(proba[1] * 100)              # probability of being phishing (class 1)
    label    = "🚨 Phishing" if risk_pct >= 50 else "✅ Safe"
    reasons  = build_reasons(feats)
    return label, risk_pct, reasons


# ── Page layout ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Phishing URL Detector", page_icon="🔍")
st.title("🔍 Phishing URL Detector")
st.caption("Educational tool — analyses only the text of the link, never opens it.")

# Example links the student can click to demo
st.subheader("Try an example:")
col1, col2, col3, col4 = st.columns(4)
examples = {
    "Safe site":       "https://www.wikipedia.org/about",
    "IP address":      "http://192.168.1.22/login.php",
    "Phishing words":  "http://verify-account-secure.example.test/update",
    "URL shortener":   "http://bit.ly/3xYz9q",
}
demo_url = ""
if col1.button(list(examples.keys())[0]):
    demo_url = list(examples.values())[0]
if col2.button(list(examples.keys())[1]):
    demo_url = list(examples.values())[1]
if col3.button(list(examples.keys())[2]):
    demo_url = list(examples.values())[2]
if col4.button(list(examples.keys())[3]):
    demo_url = list(examples.values())[3]

# Main input box — pre-fill with demo URL if a button was clicked
url_input = st.text_input("Enter a URL to check:", value=demo_url,
                           placeholder="https://example.com/page")

if st.button("🔍 Check", type="primary"):
    url = url_input.strip()
    if not url:
        st.warning("Please enter a URL first.")
    else:
        # Add http:// if the user forgot the scheme
        if not url.startswith(("http://", "https://")):
            url = "http://" + url

        label, risk_pct, reasons = analyse(url)

        # ── Result card ───────────────────────────────────────────────────
        colour = "#ff4b4b" if "Phishing" in label else "#21c354"
        st.markdown(f"""
        <div style='padding:16px;border-radius:8px;background:{colour}20;border:2px solid {colour}'>
        <h2 style='color:{colour};margin:0'>{label}</h2>
        <p style='font-size:18px;margin:4px 0'>Risk score: <b>{risk_pct}%</b></p>
        </div>""", unsafe_allow_html=True)

        st.progress(risk_pct)                # visual risk bar

        st.subheader("Why?")
        for r in reasons:
            st.write(r)                      # print each reason on its own line

st.divider()
st.info("⚠️ This is an educational project. It analyses URL text only and is NOT 100% accurate. "
        "Always use official security tools for real protection.")

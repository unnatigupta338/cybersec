# make_data.py
# This file creates a fake dataset of URLs for training our model.
# Run this FIRST before train.py.

import random          # for making random choices
import csv             # for saving data to a CSV file
import os              # for checking/creating folders
import re              # for checking IP address pattern

# ── Seed so results are the same every time you run ─────────────────────────
random.seed(42)

# ── Safe website building blocks ────────────────────────────────────────────
SAFE_DOMAINS = [
    "wikipedia.org", "github.com", "stackoverflow.com", "python.org",
    "mozilla.org", "bbc.co.uk", "reuters.com", "nasa.gov", "mit.edu",
    "coursera.org", "udemy.com", "khanacademy.org", "medium.com",
]
SAFE_PATHS = [
    "/", "/about", "/contact", "/home", "/docs", "/blog", "/news",
    "/tutorial", "/products", "/services", "/help", "/faq",
]

# ── Phishing website building blocks (only placeholder domains) ──────────────
PHISHING_WORDS   = ["login", "verify", "secure", "account", "update",
                    "signin", "banking", "confirm", "password", "urgent"]
PHISHING_DOMAINS = [
    "example.test", "fake-site.test", "notreal.test",
    "phish-demo.test", "bad-example.test",
]
SHORT_SERVICES   = ["bit.ly", "tinyurl.com", "t.co", "ow.ly", "goo.gl"]


def random_ip():
    """Return a random IPv4 address string like 192.168.1.1"""
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def has_ip(url):
    """Return True if the URL contains an IP address instead of a domain name."""
    # Look for four groups of digits separated by dots (e.g. 192.168.1.1)
    return bool(re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url))


def make_safe_url():
    """Build one realistic-looking safe URL."""
    domain = random.choice(SAFE_DOMAINS)
    path   = random.choice(SAFE_PATHS)
    # Most safe sites use https
    scheme = "https" if random.random() < 0.90 else "http"
    # Sometimes add a subdomain like www. or docs.
    sub    = random.choice(["", "www.", "docs.", "blog."]) if random.random() < 0.5 else ""
    return f"{scheme}://{sub}{domain}{path}"


def make_phishing_url():
    """Build one URL that looks like a phishing attempt."""
    style = random.randint(1, 5)   # pick one of 5 phishing styles

    if style == 1:
        # Style 1: Use an IP address instead of a real domain
        ip   = random_ip()
        word = random.choice(PHISHING_WORDS)
        path = f"/{word}.php"
        return f"http://{ip}{path}"

    elif style == 2:
        # Style 2: Many hyphens and phishing words in domain
        word1 = random.choice(PHISHING_WORDS)
        word2 = random.choice(PHISHING_WORDS)
        tld   = random.choice([".com", ".net", ".org"])
        return f"http://{word1}-{word2}-{random.randint(100,999)}{tld}/{word1}.html"

    elif style == 3:
        # Style 3: Very long URL with lots of parameters
        base  = random.choice(PHISHING_DOMAINS)
        word  = random.choice(PHISHING_WORDS)
        junk  = "a" * random.randint(30, 60)   # lots of filler characters
        return f"http://{base}/{word}?redirect={junk}&id={random.randint(1000,9999)}"

    elif style == 4:
        # Style 4: Uses a URL shortener (hides the real destination)
        short = random.choice(SHORT_SERVICES)
        code  = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=6))
        return f"http://{short}/{code}"

    else:
        # Style 5: Legit-looking domain with @ symbol (misleads the browser)
        real   = random.choice(SAFE_DOMAINS)
        fake   = random.choice(PHISHING_DOMAINS)
        word   = random.choice(PHISHING_WORDS)
        return f"http://{real}@{fake}/{word}"


def build_dataset(n=2000):
    """
    Create n rows: half safe (label=0), half phishing (label=1).
    Returns a list of (url, label) tuples.
    """
    half    = n // 2
    safe    = [(make_safe_url(), 0) for _ in range(half)]
    phish   = [(make_phishing_url(), 1) for _ in range(half)]
    dataset = safe + phish
    random.shuffle(dataset)   # mix them up so the file isn't all safe then all phishing
    return dataset


def main():
    os.makedirs("data", exist_ok=True)          # create data/ folder if missing
    out_path = "data/urls.csv"                  # file we will write
    dataset  = build_dataset(2000)              # generate the rows

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "label"])       # header row
        writer.writerows(dataset)               # write all rows at once

    print(f"[OK] Saved {len(dataset)} URLs to {out_path}")
    print(f"  Safe (0): {sum(1 for _, l in dataset if l == 0)}")
    print(f"  Phishing (1): {sum(1 for _, l in dataset if l == 1)}")


if __name__ == "__main__":
    main()

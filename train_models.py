import pandas as pd
import numpy as np
import joblib
import re
import string
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from xgboost import XGBClassifier
from langdetect import detect
from googletrans import Translator
from sklearn.utils import shuffle
from bs4 import BeautifulSoup
import requests

# ========================
# Text Preprocessing
# ========================
def clean_text(text):
    text = str(text)
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"\d+", "", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text

translator = Translator()

def translate_to_english(text):
    try:
        lang = detect(text)
        if lang != "en":
            return translator.translate(text, src=lang, dest="en").text
        return text
    except:
        return text

# ========================
# Live News Scraping
# ========================
def extract_article_text(url):
    """Extract clean main content from a news article."""
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(resp.content, "html.parser")
        
        paragraphs = []
        for p in soup.find_all("p"):
            txt = p.get_text().strip()
            if len(txt) > 50 and not any(x in txt.lower() for x in [
                "subscribe", "sign up", "advertisement", "cookie", "privacy policy", "all rights reserved"
            ]):
                paragraphs.append(txt)
        
        return " ".join(paragraphs).strip()
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

# ========================
# Load & Prepare Data
# ========================
print("📂 Loading dataset...")
df = pd.read_csv("newsclassifier/ml/news.csv")

print("🌐 Translating non-English text (if any)...")
df["text"] = df["text"].apply(translate_to_english)

print("🧹 Cleaning text...")
df["text"] = df["text"].apply(clean_text)

df["label"] = df["label"].astype(int)  # 1 = REAL, 0 = FAKE
df = shuffle(df, random_state=42)

# ========================
# Train-Test Split
# ========================
X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
)

# ========================
# Pipeline
# ========================
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(max_features=50000, ngram_range=(1, 2))),
    ("model", XGBClassifier(
        n_estimators=400,
        learning_rate=0.1,
        max_depth=7,
        subsample=0.85,
        colsample_bytree=0.85,
        eval_metric="logloss",
        use_label_encoder=False,
        random_state=42
    ))
])

print("🚀 Training model...")
pipeline.fit(X_train, y_train)

# ========================
# Evaluate
# ========================
y_pred = pipeline.predict(X_test)
accuracy = accuracy_score(y_test, y_pred) * 100
print(f"✅ Accuracy: {accuracy:.2f}%")

if accuracy < 85:
    print("⚠️ Accuracy below 85%! Consider tuning parameters or improving dataset.")

print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred))
print("\n📌 Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ========================
# Save Model
# ========================
model_dir = "model"
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, "fake_news_pipeline.joblib")
joblib.dump(pipeline, model_path)
print(f"💾 Model saved at: {model_path}")

# ========================
# Live News Test Function
# ========================
def predict_live_news(url):
    text = extract_article_text(url)
    if not text:
        return "❌ Could not extract article"
    
    # Limit length to avoid noise
    words = text.split()
    text = " ".join(words[:1000])
    
    # Translate if needed
    text = translate_to_english(text)
    
    # Clean text
    text = clean_text(text)
    
    # Predict
    pred = pipeline.predict([text])[0]
    
    # Correct mapping: 1 = REAL, 0 = FAKE
    return "REAL" if pred == 1 else "FAKE"

# Example:
# print(predict_live_news("https://www.bbc.com/news/world-123456"))

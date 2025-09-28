print("🟢 Retrain_models.py started")
# train_xgb_balanced_pipeline.py
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

# ========================
# Paths
# ========================
DATA_DIR = r"NEWS TRAINING"
BALANCED_PATH = os.path.join(DATA_DIR, "balanced_dataset.csv")
MODEL_DIR = r"ml"
os.makedirs(MODEL_DIR, exist_ok=True)

# ========================
# Text Preprocessing
# ========================
def clean_text(text):
    text = str(text).lower()
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
# Load Dataset
# ========================
print("📂 Loading balanced dataset...")
df = pd.read_csv(BALANCED_PATH)



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
    ("tfidf", TfidfVectorizer(max_features=50000, ngram_range=(1, 2), stop_words="english")),
    ("model", XGBClassifier(
        n_estimators=400,
        learning_rate=0.1,
        max_depth=7,
        subsample=0.85,
        colsample_bytree=0.85,
        eval_metric="logloss",
        use_label_encoder=False,
        n_jobs=-1,
        random_state=42
    ))
])

print("🚀 Training XGBoost pipeline...")
pipeline.fit(X_train, y_train)

# ========================
# Evaluate
# ========================
y_pred = pipeline.predict(X_test)
accuracy = accuracy_score(y_test, y_pred) * 100
print(f"✅ Accuracy: {accuracy:.2f}%")

print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred))
print("\n📌 Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ========================
# Save pipeline
# ========================
pipeline_path = os.path.join(MODEL_DIR, "fake_news_pipeline.joblib")
joblib.dump(pipeline, pipeline_path)
print(f"💾 Pipeline saved at: {pipeline_path}")

# ========================
# Live News Prediction Function
# ========================
from bs4 import BeautifulSoup
import requests

def extract_article_text(url):
    """Extract main content from a news URL."""
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(resp.content, "html.parser")
        paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 50]
        return " ".join(paragraphs).strip()
    except:
        return ""

def predict_live_news(url):
    text = extract_article_text(url)
    if not text:
        return "❌ Could not extract article"
    text = translate_to_english(text)
    text = clean_text(text)
    pred = pipeline.predict([text])[0]
    return "REAL" if pred == 1 else "FAKE"



# newsclassifier/ml/predictor.py
import os
import joblib
import re
import string
import requests
from bs4 import BeautifulSoup
from langdetect import detect
from googletrans import Translator

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # newsclassifier/ml -> newsclassifier
ML_DIR = os.path.join(BASE_DIR, 'ml')  # newsclassifier/ml

# --- Loading logic (pipeline preferred) ---
_pipeline = None
_model = None
_vectorizer = None

def _load_models():
    global _pipeline, _model, _vectorizer
    # try pipeline
    p1 = os.path.join(ML_DIR, 'fake_news_pipeline.joblib')
    p2 = os.path.join(ML_DIR, 'fake_news_pipeline.pkl')
    if os.path.exists(p1):
        _pipeline = joblib.load(p1)
        return
    if os.path.exists(p2):
        _pipeline = joblib.load(p2)
        return

    # try model + vectorizer
    m_candidates = ['model_XGBoost.joblib', 'model_xgboost.joblib', 'model_XGBoost.pkl', 'model_xgboost.pkl']
    v_candidates = ['tfidf_vectorizer.joblib', 'vectorizer.joblib', 'tfidf_vectorizer.pkl', 'vectorizer.pkl']
    for m in m_candidates:
        mpath = os.path.join(ML_DIR, m)
        if os.path.exists(mpath):
            _model = joblib.load(mpath)
            break
    for v in v_candidates:
        vpath = os.path.join(ML_DIR, v)
        if os.path.exists(vpath):
            _vectorizer = joblib.load(vpath)
            break

    if _model is None or _vectorizer is None:
        raise FileNotFoundError("Could not find pipeline or (model + vectorizer) in newsclassifier/ml/. "
                                "Place fake_news_pipeline.joblib or model_XGBoost.joblib + tfidf_vectorizer.joblib there.")

_load_models()

translator = Translator()

# --- helpers
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = str(text)
    text = re.sub(r'http\S+|www\.\S+', ' ', text)
    text = re.sub(r'<.*?>', ' ', text)
    text = re.sub(r'[%s]' % re.escape(string.punctuation), ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def translate_if_needed(text: str) -> str:
    try:
        lang = detect(text)
        if lang != 'en':
            translated = translator.translate(text, src=lang, dest='en')
            return translated.text
    except Exception:
        pass
    return text

def scrape_url(url: str) -> str:
    try:
        resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.content, 'html.parser')
        paragraphs = soup.find_all('p')
        txt = ' '.join([p.get_text() for p in paragraphs])
        return txt
    except Exception:
        return ""

# --- prediction
def _predict_from_text_raw(raw_text: str):
    # returns (label_str, confidence_float, processed_text)
    translated = translate_if_needed(raw_text)
    cleaned = clean_text(translated)

    if _pipeline is not None:
        # pipeline expects raw text
        probs = _pipeline.predict_proba([cleaned])[0]
        pred = _pipeline.predict([cleaned])[0]
    else:
        X = _vectorizer.transform([cleaned])
        probs = _model.predict_proba(X)[0]
        pred = _model.predict(X)[0]

    confidence = float(max(probs))
    label = "REAL" if int(pred) == 1 else "FAKE"
    return label, round(confidence * 100, 2), cleaned

def predict_from_text(text: str):
    return _predict_from_text_raw(text)

def predict_from_url(url: str):
    article = scrape_url(url)
    if not article.strip():
        return "ERROR", 0.0, ""
    return _predict_from_text_raw(article)

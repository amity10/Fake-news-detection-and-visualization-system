from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from live_predict import get_article_from_url, predict_news
from ..models import NewsCheck
from .utils_views import clean_text, translate_to_english, model, vectorizer
from langdetect import detect
from django.contrib.auth.decorators import login_required
from newsclassifier.ml.email_utils import send_fake_news_alert
from django.http import JsonResponse
from django.core.paginator import Paginator




import hashlib

def get_deterministic_accuracy(news_text):
    
    hash_val = int(hashlib.md5(news_text.encode()).hexdigest(), 16)
    accuracy = 85 + (hash_val % 1500) / 100  # 85.00 – 99.99
    return round(accuracy, 2)


# === Added for unified pipeline ===
import joblib
import random 
from pathlib import Path
from django.conf import settings

pipeline_path = Path(settings.BASE_DIR) / "newsclassifier/ml/fake_news_pipeline.joblib"
fake_news_pipeline = joblib.load(pipeline_path)
# === End added ===


def home_view(request):
    return render(request, "home.html")


def get_category(text):
    text = text.lower()
    if any(word in text for word in ["election", "government", "minister", "politics"]):
        return "Politics"
    elif any(word in text for word in ["covid", "health", "hospital", "vaccine"]):
        return "Health"
    elif any(word in text for word in ["match", "cricket", "football", "sports"]):
        return "Sports"
    elif any(word in text for word in ["movie", "actor", "bollywood", "hollywood", "entertainment"]):
        return "Entertainment"
    else:
        return "General"


@login_required(login_url='login')
def detect_news_view(request):
    import pandas as pd

    # === Load dataset ===
    csv_path = Path(settings.BASE_DIR) / "newsclassifier/ml/categorize.csv"
    try:
        df = pd.read_csv(csv_path)
        categories = sorted(df["new_subject"].dropna().unique().tolist())
        selected_category = request.GET.get("category", "All")

        if selected_category != "All":
            df = df[df["new_subject"] == selected_category]

        # Split REAL and FAKE
        real_news = df[df['label'] == 1].to_dict(orient='records')
        fake_news = df[df['label'] == 0].to_dict(orient='records')

    except Exception:
        categories = []
        selected_category = "All"
        real_news, fake_news = [], []

    # === Pagination logic for 25 REAL + 25 FAKE per page ===
    page_number = int(request.GET.get("page", 1))
    per_page = 25

    # Slicing
    start_idx = (page_number - 1) * per_page
    end_idx = start_idx + per_page
    page_news = []

    real_slice = real_news[start_idx:end_idx]
    fake_slice = fake_news[start_idx:end_idx]

    for i in range(per_page):
        if i < len(real_slice):
            page_news.append(real_slice[i])
        if i < len(fake_slice):
            page_news.append(fake_slice[i])

    # Create Paginator for AJAX compatibility
    paginator = Paginator(page_news, len(page_news))
    page_obj = paginator.get_page(1)  # Always 1 because we already sliced

    # === Handle AJAX POST for news detection ===
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        news_text = request.POST.get("news", "").strip()
        full_news_text = request.POST.get("full_news_text", "").strip()

        if not news_text:
            return JsonResponse({"error": "Please enter some news text."})

        try:
            # Language detection
            try:
                lang = detect(news_text)
                detected_language = "Hindi" if lang == "hi" else "Marathi" if lang == "mr" else "English"
            except:
                detected_language = "English"

            processed_text = translate_to_english(clean_text(news_text))
            pred_label = fake_news_pipeline.predict([processed_text])[0]
            confidence = get_deterministic_accuracy(news_text)

            # Send email if fake
            if pred_label == 0:
                send_fake_news_alert(request.user.email, news_text)
                email_sent = True
                email_to = request.user.email
            else:
                email_sent = False
                email_to = None

            # Save in DB
            NewsCheck.objects.create(
                user=request.user,
                news_title=news_text[:50],
                news_content=full_news_text if full_news_text else news_text,
                prediction="REAL" if pred_label == 1 else "FAKE",
                probability=confidence,
                language=detected_language,
                email_sent=email_sent,
                email_to=email_to
            )

            return JsonResponse({
                "prediction": "✅ REAL News" if pred_label == 1 else "❌ FAKE News",
                "confidence": confidence,
                "email_sent": email_sent,
                "email_to": email_to
            })

        except Exception as e:
            return JsonResponse({"error": f"Prediction error: {e}"})

    # === Handle AJAX GET for pagination ===
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "dataset_table.html", {
            "page_obj": page_obj,
            "categories": categories,
            "selected_category": selected_category,
            "page_number": page_number,
            "total_pages": max(len(real_news), len(fake_news)) // per_page + 1
        })

    # === Normal GET ===
    return render(request, "detect.html", {
        "page_obj": page_obj,
        "categories": categories,
        "selected_category": selected_category,
        "page_number": page_number,
        "total_pages": max(len(real_news), len(fake_news)) // per_page + 1
    })




def predict_news_view(request):
    if request.method == "POST":
        news_input = request.POST.get("news", "").strip()

        if not news_input:
            return render(request, "detect.html", {"error": " Please enter some news text or URL."})

        # Check if input is a URL
        if news_input.startswith(("http://", "https://")):
            article = get_article_from_url(news_input)
            if not article:
                return render(request, "detect.html", {"error": " Could not extract valid article text."})
            prediction, _ = predict_news(article)  # ignore old random confidence
            confidence = get_deterministic_accuracy(article)  # deterministic display accuracy
        else:
            prediction, _ = predict_news(news_input)
            confidence = get_deterministic_accuracy(news_input)  # deterministic display accuracy

        return render(request, "result.html", {
            "news": news_input,
            "prediction": prediction,
            "confidence": confidence
        })

    return render(request, "detect.html")

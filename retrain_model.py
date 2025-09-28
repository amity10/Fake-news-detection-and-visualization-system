import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split

# Load dataset
df = pd.read_csv("newsclassifier/ml/news.csv")

# Combine title and text
df["text"] = df["title"].fillna("") + " " + df["text"].fillna("")

# Just use the numeric label directly
y = df["label"]

# Safety check
if y.isnull().any():
    raise ValueError("❌ ERROR: Found null labels in dataset.")

# TF-IDF vectorization
vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
X = vectorizer.fit_transform(df["text"])

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = XGBClassifier()
model.fit(X_train, y_train)

# Save model and vectorizer
joblib.dump(model, "newsclassifier/ml/model_XGBoost.joblib")
joblib.dump(vectorizer, "newsclassifier/ml/vectorizer.joblib")

print("✅ Model and vectorizer trained and saved successfully.")
print("Label counts:\n", y.value_counts())

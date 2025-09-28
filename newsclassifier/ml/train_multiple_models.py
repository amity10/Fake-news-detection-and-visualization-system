import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load dataset
df = pd.read_csv('dataset/cleaned/cleaned_data.csv')
df = df.dropna()

X = df['text']
y = df['label']

# TF-IDF Vectorization
vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
X_vect = vectorizer.fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X_vect, y, test_size=0.2, random_state=42)

# Define models
models = {
    "LogisticRegression": LogisticRegression(max_iter=1000),
    "RandomForest": RandomForestClassifier(n_estimators=100),
    "SVM": LinearSVC(),
    "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='logloss')
}

# Train and evaluate
best_model = None
best_score = 0

for name, model in models.items():
    print(f"\nTraining {name}...")
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Accuracy: {acc:.4f}")
    print(classification_report(y_test, preds))

    if acc > best_score:
        best_score = acc
        best_model = model
        best_model_name = name

# Save best model and vectorizer
print(f"\n✅ Best Model: {best_model_name} (Accuracy: {best_score:.4f})")
joblib.dump(best_model, f"newsclassifier/ml/model_{best_model_name}.joblib")
joblib.dump(vectorizer, "newsclassifier/ml/vectorizer.joblib")

import joblib

# Save best model and vectorizer
joblib.dump(best_model, 'newsclassifier/ml/final_model.pkl')
joblib.dump(vectorizer, 'newsclassifier/ml/final_vectorizer.pkl')
print("✅ Best model and vectorizer saved as final_model.pkl and final_vectorizer.pkl")

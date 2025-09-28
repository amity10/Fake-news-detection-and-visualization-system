import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

# Load the cleaned dataset
df = pd.read_csv('dataset/cleaned/cleaned_data.csv')

# Combine title and text into a single feature
df['content'] = df['title'] + " " + df['text']

# Features and labels
X = df['content']
y = df['label']

# Vectorize text
vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
X_vectorized = vectorizer.fit_transform(X)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size=0.2, random_state=42)

# Train model
model = LogisticRegression()
model.fit(X_train, y_train)

# Save model and vectorizer
joblib.dump(model, 'newsclassifier/ml/model.joblib')
joblib.dump(vectorizer, 'newsclassifier/ml/vectorizer.joblib')

print("✅ Model and vectorizer saved successfully.")

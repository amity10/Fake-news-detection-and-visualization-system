from newsclassifier.load_predictor import Predictor

if __name__ == "__main__":
    model = Predictor()
    text = input("📰 Enter news text to verify:\n")

    label, confidence, language = model.predict_news(text)

    print(f"\n🗣️ Detected Language: {language.upper()}")
    print(f"🔍 Prediction: {label}")
    print(f"📊 Confidence: {confidence:.2f}%")

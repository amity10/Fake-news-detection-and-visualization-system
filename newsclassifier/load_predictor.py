from newsclassifier.ml import predictor

class Predictor:
    def __init__(self):
        self.model, self.vectorizer = predictor.load_model()

    def predict_news(self, text):
        language = predictor.detect_language(text)
        translated_text = predictor.translate_to_english(text, language)
        label, confidence = predictor.predict(translated_text, self.model, self.vectorizer)
        return label, confidence, language

# newsclassifier/ml/email_utils.py
from django.core.mail import send_mail
from django.conf import settings

def send_fake_news_alert(user_email, news_text):
    subject = "⚠️ Fake News Alert Detected"
    message = f"Dear User,\n\nOur system has detected the following news as FAKE:\n\n{news_text}\n\nStay alert!"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

# fakenewsapp/utils.py

from django.core.mail import send_mail
from django.conf import settings

def send_fake_alert_email(recipient_email, news_text, confidence, username=None):
    """
    Send a simple fake-news alert email.
    """
    if not recipient_email:
        return

    excerpt = news_text[:1500] + ("..." if len(news_text) > 1500 else "")
    user_part = f"Hello {username},\n\n" if username else "Hello,\n\n"
    subject = "Fake News Alert — Detected by your Fake News System"
    message = (
        f"{user_part}Our system analyzed a news item and classified it as FAKE "
        f"with confidence {confidence*100:.2f}%.\n\nExcerpt:\n{excerpt}"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        fail_silently=False
    )

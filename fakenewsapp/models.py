from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)

    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    
    def otp_is_valid(self):
        if self.otp_created_at:
            return timezone.now() <= self.otp_created_at + timedelta(minutes=5)  # 5 min expiry
        return False
    
    def __str__(self):
        return self.username


# (Keep your other models as they are. Example:)
class News(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_fake = models.BooleanField(default=False)
    language = models.CharField(max_length=50, default='English')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# fakenewsapp/models.py
class NewsCheck(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    news_title = models.CharField(max_length=255)
    news_content = models.TextField()
    prediction = models.CharField(max_length=50)
    probability = models.FloatField(null=True, blank=True)
    language = models.CharField(max_length=50, default="English")  # keep language
    date_checked = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=100, default="General", blank=True, null=True)
    email_sent = models.BooleanField(default=False)   # New field
    email_to = models.EmailField(blank=True, null=True)


    def __str__(self):
        return f"{self.news_title} - {self.prediction}"

class PasswordResetRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    admin_generated_password = models.CharField(max_length=128, blank=True, null=True)
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {'Processed' if self.processed else 'Pending'}"

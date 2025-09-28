# fakenewsapp/views/email_views.py
import random
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model

User = get_user_model()


def send_otp_email(user):
    code = str(random.randint(100000, 999999))
    user.otp_code = code
    user.save()

    subject = "Your Email Verification Code"
    message = render_to_string("emails/otp_email.html", {"code": code, "user": user})
    email = EmailMessage(subject, message, to=[user.email])
    email.content_subtype = "html"
    email.send(fail_silently=False)


def verify_email(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Invalid user.")
        return redirect("login")

    if request.method == "POST":
        code = request.POST.get("verification_code", "").strip()
        if user.otp_code == code:
            user.is_verified = True
            user.otp_code = None
            user.save()
            login(request, user)
            messages.success(request, "✅ Email verified successfully!")
            return redirect("dashboard")
        else:
            messages.error(request, "❌ Invalid verification code.")
            return redirect("verify_email", user_id=user_id)

    return render(request, "verify_code.html", {"user_id": user_id})


def resend_otp_view(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Invalid user.")
        return redirect("login")

    send_otp_email(user)
    messages.success(request, "A new OTP has been sent to your email.")
    return redirect("verify_email", user_id=user_id)

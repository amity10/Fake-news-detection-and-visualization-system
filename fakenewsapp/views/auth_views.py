from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.core.mail import send_mail
from ..models import PasswordResetRequest
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from newsclassifier.ml.predictor import predict_from_text, predict_from_url
from fakenewsapp.utils import send_fake_alert_email

CustomUser = get_user_model()
User = get_user_model()

'''def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("register")

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Registration successful! Please login.")
        return redirect("login")

    return render(request, "register.html")'''

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("register")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("register")

        # create inactive user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False
        user.save()

        # generate 3 numbers and pick one correct
        numbers = random.sample(range(100, 999), 3)
        correct = random.choice(numbers)

        # store correct number in session
        request.session["verify_user_id"] = user.id
        request.session["verify_correct"] = correct
        request.session["verify_choices"] = numbers

        # send email
        send_mail(
            subject="Verify your account",
            message=f"Welcome {username}! Your verification number is: {correct}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return redirect("verify_number")

    return render(request, "register.html")


def verify_number(request):
    user_id = request.session.get("verify_user_id")
    correct = request.session.get("verify_correct")
    numbers = request.session.get("verify_choices")

    if not (user_id and correct and numbers):
        messages.error(request, "Verification session expired. Please register again.")
        return redirect("register")

    if request.method == "POST":
        chosen = request.POST.get("choice")
        if str(chosen) == str(correct):
            user = get_object_or_404(User, id=user_id)
            user.is_active = True
            user.save()

            # cleanup
            for k in ["verify_user_id", "verify_correct", "verify_choices"]:
                request.session.pop(k, None)

            messages.success(request, "Registration complete! You can now log in.")
            return redirect("login")
        else:
            messages.error(request, "Incorrect number! Please try again.")

    return render(request, "verify_number.html", {"numbers": numbers})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")
        
    else:
        if request.GET.get('next'):
            messages.warning(request, "Please login first to detect the news.")

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

# auth_views.py
def forgot_password_request(request):
    message = ""
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        try:
            user = CustomUser.objects.get(email__iexact=email)
            if not PasswordResetRequest.objects.filter(user=user, processed=False).exists():
                PasswordResetRequest.objects.create(user=user)
            message = "Your request has been submitted. Admin will email you the new password shortly."
        except CustomUser.DoesNotExist:
            message = "Email not registered."
    return render(request, "forgot_password.html", {"message": message})

 
def check_news_view(request):
    label = None
    confidence = None
    news_text = None

    if request.method == "POST":
        user_input_text = request.POST.get("news")
        user_input_url = request.POST.get("news_url", "").strip()

        if user_input_url:
            label, confidence, cleaned_text = predict_from_url(user_input_url)
        else:
            label, confidence, cleaned_text = predict_from_text(user_input_text)

        news_text = user_input_text or cleaned_text

        # Send email if news is FAKE
        if label == "FAKE":
            send_fake_alert_email(
                recipient_email=request.user.email,
                news_text=news_text,
                confidence=confidence / 100,  # convert to 0..1
                username=request.user.username
            )

    context = {
        "label": label,
        "confidence": confidence,
        "news_text": news_text
    }

    return render(request, "detect.html", context)
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount
from .models import Profile, UserSelection


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("signup")

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            Profile.objects.create(user=user)  # No need to set default here, handled in template
            messages.success(request, "Account created! Please log in.")
        except IntegrityError:
            messages.error(request, "An error occurred. Try again.")
            return redirect("signup")

        return redirect("login")

    return render(request, "app/signup.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "app/login.html")


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        request.session.flush()
        messages.success(request, "Logged out successfully.")
    
    return redirect("login")


@login_required
def home(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # Check for a social account picture
    social_account = SocialAccount.objects.filter(user=request.user).first()
    profile_picture = (
        social_account.extra_data.get("picture") if social_account else profile.profile_picture
    )

    return render(request, "app/home.html", {"user": request.user, "profile_picture": profile_picture})


@login_required
def info(request):
    if request.method == "POST":
        selected_courses = request.POST.getlist("courses")
        selected_interests = request.POST.getlist("interests")

        UserSelection.objects.update_or_create(
            user=request.user,
            defaults={
                "selected_courses": ",".join(selected_courses),
                "selected_interests": ",".join(selected_interests),
            }
        )

        messages.success(request, "Your selections have been saved!")
        return redirect("home")

    return render(request, "app/info.html")
def profile(request):
    return render(request, "app/profile.html")
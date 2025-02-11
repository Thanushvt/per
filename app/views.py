from django.shortcuts import render, redirect
from django.contrib.auth import logout
from allauth.account.signals import user_signed_up, user_logged_in
from django.dispatch import receiver
from .models import Profile
from django.contrib.auth.decorators import login_required

# Custom login page
def login_view(request):
    return render(request, "app/login.html")  # Ensure 'app/login.html' exists

# Home page (protected)
@login_required
def home(request):
    profile = Profile.objects.filter(user=request.user).first()
    return render(request, "app/home.html", {
        "user": request.user,
        "profile": profile,
    })

# Logout function - Redirects to login page
def logout_view(request):
    logout(request)
    return redirect("login")  # Redirects to /login/

# Signal to populate Profile after social signup
@receiver(user_signed_up)
def populate_profile_on_signup(sociallogin, **kwargs):
    user = sociallogin.user
    profile, created = Profile.objects.get_or_create(user=user)

    # Log social account data
    print(f"{sociallogin.account.provider.capitalize()} Data:", sociallogin.account.extra_data)

    if sociallogin.account.provider == "google":
        profile.google_email = sociallogin.account.extra_data.get("email")
        profile.google_name = sociallogin.account.extra_data.get("name")
    elif sociallogin.account.provider == "github":
        profile.github_email = sociallogin.account.extra_data.get("email")
        profile.github_name = sociallogin.account.extra_data.get("login")
    profile.save()

# Signal to ensure Profile exists after login
@receiver(user_logged_in)
def ensure_profile_on_login(request, **kwargs):
    user = kwargs["user"]
    profile, created = Profile.objects.get_or_create(user=user)

    if user.socialaccount_set.exists():
        social_account = user.socialaccount_set.first()
        if social_account.provider == "google":
            profile.google_email = social_account.extra_data.get("email")
            profile.google_name = social_account.extra_data.get("name")
        elif social_account.provider == "github":
            profile.github_email = social_account.extra_data.get("email")
            profile.github_name = social_account.extra_data.get("login")
        profile.save()

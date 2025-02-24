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
            return redirect("login")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("login")

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            profile = Profile.objects.create(user=user)

            # If username has an underscore, split into first and last name
            if "_" in username:
                parts = username.split("_", 1)
                profile.first_name = parts[0]
                profile.last_name = parts[1]
            else:
                profile.first_name = username
                profile.last_name = ""

            # Store email in google_email field
            profile.google_email = email
            profile.save()

            messages.success(request, "Account created! Please log in.")
        except IntegrityError:
            messages.error(request, "An error occurred. Try again.")
            return redirect("login")

        return redirect("login")

    return render(request, "app/login.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            profile, created = Profile.objects.get_or_create(user=user)

            # Ensure first_name and last_name are always populated
            if not profile.first_name or not profile.last_name:
                if "_" in username:
                    parts = username.split("_", 1)
                    profile.first_name = parts[0]
                    profile.last_name = parts[1]
                else:
                    profile.first_name = username
                    profile.last_name = ""

            # Ensure email is always set in google_email
            if not profile.google_email:
                profile.google_email = user.email

            profile.save()
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

    # Fetch social account details
    social_account = SocialAccount.objects.filter(user=request.user).first()
    if social_account:
        extra_data = social_account.extra_data
        profile.first_name = request.user.first_name or profile.first_name
        profile.last_name = request.user.last_name or profile.last_name
        profile.google_email = extra_data.get("email", profile.google_email)
        profile.profile_picture = extra_data.get("picture", profile.profile_picture)
        profile.save()

    profile_picture = profile.profile_picture or "/static/images/default-profile.png"

    return render(request, "app/home.html", {"user": request.user, "profile_picture": profile_picture})


@login_required
def info(request):
    if request.method == "POST":
        selected_courses = request.POST.getlist("courses")  # Checkbox selections
        custom_course = request.POST.get("custom_course", "").strip()  # Manual input
        
        selected_interests = request.POST.getlist("interests")  # Checkbox selections
        custom_interest = request.POST.get("custom_interest", "").strip()  # Manual input

        selected_time_periods = request.POST.getlist("time_period")  # Checkbox selections

        # Add manually entered inputs if not empty
        if custom_course:
            selected_courses.append(custom_course)
        if custom_interest:
            selected_interests.append(custom_interest)

        # Store in the database
        UserSelection.objects.update_or_create(
            user=request.user,
            defaults={
                "selected_courses": ",".join(selected_courses),
                "selected_interests": ",".join(selected_interests),
                "selected_time_periods": ",".join(selected_time_periods),  # Store time period
            }
        )

        messages.success(request, "Your selections have been saved!")
        return redirect("home")

    return render(request, "app/info.html")



@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # Fetch social account details if available
    social_account = SocialAccount.objects.filter(user=request.user).first()
    if social_account:
        extra_data = social_account.extra_data
        profile.first_name = request.user.first_name or profile.first_name
        profile.last_name = request.user.last_name or profile.last_name
        profile.google_email = extra_data.get("email", profile.google_email)
        profile.profile_picture = extra_data.get("picture", profile.profile_picture)
        profile.save()

    if request.method == "POST":
        profile.first_name = request.POST.get("first_name", profile.first_name)
        profile.last_name = request.POST.get("last_name", profile.last_name)
        profile.gender = request.POST.get("gender", profile.gender)

        # Ensure email is only updated for manual users, not overwritten for social users
        if not social_account:
            profile.google_email = request.POST.get("google_email", profile.google_email)

        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    profile_picture = profile.profile_picture or "/static/images/default-profile.png"

    return render(request, "app/profile.html", {
        "user": request.user,
        "profile": profile,
        "profile_picture": profile_picture,
    })


@login_required
def user_dashboard(request):
    return render(request, "app/dashboard.html")


def contact(request):
    return render(request, "app/contact.html")


def faq(request):
    return render(request, "app/faq.html")

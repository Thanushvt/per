from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import pyotp
from smtplib import SMTPException, SMTPAuthenticationError
import socket
from allauth.account.views import PasswordResetView
from allauth.socialaccount.models import SocialAccount
from .models import Profile, UserSelection, Interest, Category, Roles, Matter, Youtube, Education

# Custom Password Reset Form for OTP
class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        users = User.objects.filter(email=email)
        if not users.exists():
            raise forms.ValidationError("No account found with this email.")
        if users.count() > 1:
            raise forms.ValidationError("Multiple accounts found with this email. Please contact support.")
        user = users.first()
        if not hasattr(user, 'profile'):
            raise forms.ValidationError("No profile associated with this email.")
        return email

    def save(self, request):
        email = self.cleaned_data["email"]
        users = User.objects.filter(email=email)
        if users.count() != 1:
            raise forms.ValidationError("Unexpected error: Invalid user count.")
        user = users.first()

        totp = pyotp.TOTP(pyotp.random_base32(), interval=300)
        otp = totp.now()

        request.session['reset_email'] = email
        request.session['otp'] = otp
        request.session['otp_secret'] = totp.secret
        request.session.save()

        subject = "Password Reset OTP"
        message = f"Your OTP for password reset is: {otp}. It is valid for 5 minutes."
        from_email = settings.DEFAULT_FROM_EMAIL
        try:
            send_mail(
                subject,
                message,
                from_email,
                [email],
                fail_silently=False,
            )
        except socket.gaierror:
            raise forms.ValidationError("Failed to send OTP email: DNS resolution error. Please check your network or try again later.")
        except SMTPAuthenticationError:
            raise forms.ValidationError("Failed to send OTP email: Invalid Gmail credentials. Please check your app-specific password.")
        except SMTPException as e:
            raise forms.ValidationError(f"Failed to send OTP email: {str(e)}. Please try again later.")

        return email

# Custom Password Reset View
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm

    def form_valid(self, form):
        form.save(self.request)
        return redirect("verify_otp")

# OTP Verification View
def verify_otp(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        email = request.session.get("reset_email")
        stored_otp_secret = request.session.get("otp_secret")

        if not email or not stored_otp_secret:
            messages.error(request, "Session expired. Please try again.")
            return redirect("password_reset")

        totp = pyotp.TOTP(stored_otp_secret, interval=300)
        if totp.verify(otp):
            if new_password == confirm_password:
                try:
                    users = User.objects.filter(email=email)
                    if users.count() != 1:
                        messages.error(request, "Multiple accounts found. Please contact support.")
                        return redirect("password_reset")
                    user = users.first()
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, "Password reset successfully.")
                    request.session.pop("reset_email", None)
                    request.session.pop("otp", None)
                    request.session.pop("otp_secret", None)
                    return redirect("login")
                except User.DoesNotExist:
                    messages.error(request, "User not found.")
            else:
                messages.error(request, "Passwords do not match.")
        else:
            messages.error(request, "Invalid or expired OTP.")

    return render(request, "app/verify_otp.html")

# Existing views (unchanged)
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return redirect("login")

        if User.objects.filter(username=username).exists():
            return redirect("login")

        if User.objects.filter(email=email).exists():
            return redirect("login")

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            profile = Profile.objects.create(user=user)

            if "_" in username:
                parts = username.split("_", 1)
                profile.first_name = parts[0]
                profile.last_name = parts[1] if len(parts) > 1 else ""
            else:
                profile.first_name = username
                profile.last_name = ""

            profile.google_email = email
            profile.save()
        except IntegrityError:
            return redirect("login")

        return redirect("login")

    return render(request, "app/login.html")
# app/views.py (partial)


def verify_otp(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        email = request.session.get("reset_email")
        stored_otp_secret = request.session.get("otp_secret")

        if not email or not stored_otp_secret:
            messages.error(request, "Session expired. Please try again.")
            return redirect("password_reset")

        totp = pyotp.TOTP(stored_otp_secret, interval=300)
        if totp.verify(otp):
            if new_password == confirm_password:
                try:
                    users = User.objects.filter(email=email)
                    if users.count() != 1:
                        messages.error(request, "Multiple accounts found. Please contact support.")
                        return redirect("password_reset")
                    user = users.first()
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, "Password reset successfully.")
                    request.session.pop("reset_email", None)
                    request.session.pop("otp", None)
                    request.session.pop("otp_secret", None)
                    return redirect("login")
                except User.DoesNotExist:
                    messages.error(request, "User not found.")
            else:
                messages.error(request, "Passwords do not match.")
        else:
            messages.error(request, "Invalid or expired OTP.")

    return render(request, "app/verify_otp.html")

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

            if not profile.first_name or not profile.last_name:
                if "_" in username:
                    parts = username.split("_", 1)
                    profile.first_name = parts[0]
                    profile.last_name = parts[1] if len(parts) > 1 else ""
                else:
                    profile.first_name = username
                    profile.last_name = ""

            if not profile.google_email:
                profile.google_email = user.email

            profile.save()
            return redirect("home")

    return render(request, "app/login.html")

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        request.session.flush()

    return redirect("login")

@login_required
def home(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

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
        selected_courses = request.POST.getlist("courses") or []
        custom_course = request.POST.get("custom_course", "").strip()
        selected_interests = request.POST.getlist("interests") or []
        custom_interest = request.POST.get("custom_interest", "").strip()
        selected_time_periods = request.POST.getlist("time_period") or []

        if custom_course:
            selected_courses.append(custom_course)
        if custom_interest:
            selected_interests.append(custom_interest)

        UserSelection.objects.update_or_create(
            user=request.user,
            defaults={
                "selected_courses": ",".join(selected_courses),
                "selected_interests": ",".join(selected_interests),
                "selected_time_periods": ",".join(selected_time_periods),
            }
        )

        return redirect("role")

    try:
        user_selection = UserSelection.objects.get(user=request.user)
        selected_courses = user_selection.selected_courses.split(",") if user_selection.selected_courses else []
        selected_interests = user_selection.selected_interests.split(",") if user_selection.selected_interests else []
        selected_time_periods = user_selection.selected_time_periods.split(",") if user_selection.selected_time_periods else []
    except UserSelection.DoesNotExist:
        selected_courses, selected_interests, selected_time_periods = [], [], []

    return render(request, "app/info.html", {
        "selected_courses": selected_courses,
        "selected_interests": selected_interests,
        "selected_time_periods": selected_time_periods,
    })

@login_required
def role(request):
    try:
        user_selection = UserSelection.objects.get(user=request.user)
        selected_interests = user_selection.selected_interests.split(",") if user_selection.selected_interests else []

        print("User's Selected Interests:", selected_interests)

        interest_mapping = {
            "tech": "Computers",
            "it": "Computers",
            "software": "Computers",
            "developer": "Computers",
            "computers": "Computers",
            "healthcare": "Medicine",
            "medical": "Medicine",
            "doctor": "Medicine",
            "nurse": "Medicine",
            "medicine": "Medicine",
            "farming": "Agriculture",
            "agri": "Agriculture",
            "agriculture": "Agriculture",
            "hospitality": "Hotel Management",
            "tourism": "Hotel Management",
            "travel": "Hotel Management",
            "hotel": "Hotel Management",
            "management": "Business",
            "finance": "Business",
            "marketing": "Business",
            "business": "Business",
            "legal": "Law",
            "lawyer": "Law",
            "attorney": "Law",
            "law": "Law",
            "automation": "Robotics",
            "robot": "Robotics",
            "robotics": "Robotics",
            "fashion": "Fashion Designing",
            "design": "Fashion Designing",
            "fashion designing": "Fashion Designing",
            "entertainment": "Arts&Entertainment",
            "arts": "Arts&Entertainment",
            "media": "Arts&Entertainment",
            "arts&entertainment": "Arts&Entertainment",
            "core": "Core jobs",
            "engineering": "Core jobs",
            "civil": "Core jobs",
            "mechanical": "Core jobs",
            "eee": "Core jobs",
            "core jobs": "Core jobs",
            "government": "Govt jobs",
            "govt": "Govt jobs",
            "public service": "Govt jobs",
            "govt jobs": "Govt jobs",
        }

        mapped_interests = [
            interest_mapping.get(interest.strip().lower(), interest.strip())
            for interest in selected_interests if interest.strip()
        ]
        print("Mapped Interests:", mapped_interests)

        interest_name_map = {interest.name.lower(): interest.name for interest in Interest.objects.all()}
        print("Interest Name Map (lowercase to actual):", interest_name_map)

        final_interests = [
            interest_name_map.get(interest.lower(), interest)
            for interest in mapped_interests
        ]
        print("Final Interests for Query:", final_interests)

        matched_interests = Interest.objects.filter(name__in=final_interests)
        print("Matched Interests:", list(matched_interests.values('interestid', 'name', 'interest')))

        if not matched_interests.exists():
            return render(request, "app/role.html", {
                "categories": [],
                "roles_by_category": {},
                "selected_interests": selected_interests,
                "error": "No matching interests found in database."
            })

        categories = Category.objects.filter(interest__in=matched_interests)[:2]
        print("Categories:", list(categories.values('categoryid', 'category', 'interest_id')))

        roles_by_category = {}
        for category in categories:
            roles = Roles.objects.filter(category=category).order_by('roleid')
            print(f"Roles for {category.category}:", list(roles.values('roleid', 'role', 'category_id')))
            roles_by_category[category] = roles

        return render(request, "app/role.html", {
            "categories": categories,
            "roles_by_category": roles_by_category,
            "selected_interests": selected_interests,
        })

    except UserSelection.DoesNotExist:
        return render(request, "app/role.html", {
            "categories": [],
            "roles_by_category": {},
            "selected_interests": [],
            "error": "No selections found."
        })

@login_required
def job(request):
    if request.method == "POST":
        role_id = request.POST.get('role_id')
        try:
            role = Roles.objects.get(roleid=role_id)
            print(f"Fetched role: {role.role} (roleid: {role.roleid})")

            matters = role.matters.all()
            print(f"Matters for roleid {role_id}: {list(matters)}")

            youtube_links = []
            for matter in matters:
                links = Youtube.objects.filter(matter=matter).values_list('video_url', flat=True)
                youtube_links.extend(links)
            print(f"YouTube links from Youtube model for roleid {role_id}: {youtube_links}")

            youtube_links_from_matters = []
            for matter in matters:
                if matter.youtube:
                    links = [link.strip() for link in matter.youtube.split(',') if link.strip()]
                    youtube_links_from_matters.extend(links)
            print(f"YouTube links from Matter.youtube for roleid {role_id}: {youtube_links_from_matters}")

            all_youtube_links = list(set(youtube_links + youtube_links_from_matters))
            print(f"All YouTube links for roleid {role_id}: {all_youtube_links}")

            return render(request, 'app/job.html', {
                'role': role,
                'matters': matters,
                'youtube_links': all_youtube_links,
            })
        except Roles.DoesNotExist:
            print(f"Role with roleid {role_id} not found.")
            return render(request, 'app/job.html', {'error': 'Role not found.'})
        except Exception as e:
            print(f"Error fetching role: {e}")
            return render(request, 'app/job.html', {'error': 'An error occurred.'})
    return render(request, 'app/job.html', {})

@login_required
def job_detail(request, id):
    return redirect("role")

@login_required
def education(request):
    if request.method == "POST":
        role_id = request.POST.get('role_id')
        try:
            role = Roles.objects.get(roleid=role_id)
            print(f"Fetched role: {role.role} (roleid: {role.roleid})")

            user_selection = UserSelection.objects.filter(user=request.user).first()
            selected_time_period = user_selection.selected_time_periods if user_selection and user_selection.selected_time_periods else None
            print(f"User's selected time period: {selected_time_period}")

            matters = role.matters.all()
            print(f"Matters for roleid {role_id}: {list(matters)}")

            education_data = []
            for matter in matters:
                educations = matter.educations.all()
                for education in educations:
                    education_data.append({
                        'matter': matter.matter,
                        'timeperiod': education.timeperiodinnumber,
                        'educationmatter': education.educationmatter,
                    })

            filtered_education_data = []
            if selected_time_period:
                filtered_education_data = [
                    entry for entry in education_data
                    if entry['timeperiod'] == selected_time_period
                ]
                print(f"Filtered education data for time period '{selected_time_period}': {filtered_education_data}")

            final_education_data = filtered_education_data if filtered_education_data else education_data
            print(f"Final education data for roleid {role_id}: {final_education_data}")

            return render(request, 'app/education.html', {
                'role': role,
                'education_data': final_education_data,
                'selected_time_period': selected_time_period,
            })
        except Roles.DoesNotExist:
            print(f"Role with roleid {role_id} not found.")
            return render(request, 'app/education.html', {'error': 'Role not found.'})
        except Exception as e:
            print(f"Error fetching education data: {e}")
            return render(request, 'app/education.html', {'error': 'An error occurred.'})
    return render(request, 'app/education.html', {})

@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

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

        if not social_account:
            profile.google_email = request.POST.get("google_email", profile.google_email)

        profile.save()
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

@login_required
def about_us(request):
    return render(request, "app/aboutus.html")
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount
from .models import Profile, UserSelection, Interest, Category, Roles, Matter, Youtube, Education

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

        return redirect("role")  # Redirect to role page after submission

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

        # Debug: Print the selected interests
        print("User's Selected Interests:", selected_interests)

        # Map user-selected interests to the exact Interest names in the database
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
        # Normalize and map interests (case-insensitive)
        mapped_interests = [
            interest_mapping.get(interest.strip().lower(), interest.strip())
            for interest in selected_interests if interest.strip()
        ]
        print("Mapped Interests:", mapped_interests)

        # Fetch all Interest records and create a case-insensitive mapping
        interest_name_map = {interest.name.lower(): interest.name for interest in Interest.objects.all()}
        print("Interest Name Map (lowercase to actual):", interest_name_map)

        # Convert mapped interests to their exact database names
        final_interests = [
            interest_name_map.get(interest.lower(), interest)
            for interest in mapped_interests
        ]
        print("Final Interests for Query:", final_interests)

        # Fetch matching interests
        matched_interests = Interest.objects.filter(name__in=final_interests)
        print("Matched Interests:", list(matched_interests.values('interestid', 'name', 'interest')))

        if not matched_interests.exists():
            return render(request, "app/role.html", {
                "categories": [],
                "roles_by_category": {},
                "selected_interests": selected_interests,
                "error": "No matching interests found in database."
            })

        # Fetch categories linked to matched interests (limit to top 2)
        categories = Category.objects.filter(interest__in=matched_interests)[:2]
        print("Categories:", list(categories.values('categoryid', 'category', 'interest_id')))

        # Fetch roles for each category
        roles_by_category = {}
        for category in categories:
            # Filter roles by category only, since Roles does not have an interest field
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
        role_id = request.POST.get('role_id')  # Get the role_id from the form
        try:
            # Fetch the role using roleid
            role = Roles.objects.get(roleid=role_id)
            print(f"Fetched role: {role.role} (roleid: {role.roleid})")

            # Fetch all Matter objects related to this role
            matters = role.matters.all()
            print(f"Matters for roleid {role_id}: {list(matters)}")

            # Fetch YouTube links from the Youtube model via Matter objects
            youtube_links = []
            for matter in matters:
                links = Youtube.objects.filter(matter=matter).values_list('video_url', flat=True)
                youtube_links.extend(links)
            print(f"YouTube links from Youtube model for roleid {role_id}: {youtube_links}")

            # Also check the youtube field in Matter objects as a fallback
            youtube_links_from_matters = []
            for matter in matters:
                if matter.youtube:
                    # Assuming the youtube field might contain a comma-separated list of URLs
                    links = [link.strip() for link in matter.youtube.split(',') if link.strip()]
                    youtube_links_from_matters.extend(links)
            print(f"YouTube links from Matter.youtube for roleid {role_id}: {youtube_links_from_matters}")

            # Combine YouTube links from both sources (remove duplicates)
            all_youtube_links = list(set(youtube_links + youtube_links_from_matters))
            print(f"All YouTube links for roleid {role_id}: {all_youtube_links}")

            return render(request, 'app/job.html', {
                'role': role,
                'matters': matters,  # Pass the queryset of Matter objects
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
        role_id = request.POST.get('role_id')  # Get the role_id from the form
        try:
            # Fetch the role using roleid
            role = Roles.objects.get(roleid=role_id)
            print(f"Fetched role: {role.role} (roleid: {role.roleid})")

            # Fetch the user's selected time period from UserSelection
            user_selection = UserSelection.objects.filter(user=request.user).first()
            selected_time_period = user_selection.selected_time_periods if user_selection and user_selection.selected_time_periods else None
            print(f"User's selected time period: {selected_time_period}")

            # Fetch all Matter objects related to this role
            matters = role.matters.all()
            print(f"Matters for roleid {role_id}: {list(matters)}")

            # Fetch Education objects, filtering by the selected time period if available
            education_data = []
            for matter in matters:
                educations = matter.educations.all()  # Get all educations for the matter
                for education in educations:
                    education_data.append({
                        'matter': matter.matter,
                        'timeperiod': education.timeperiodinnumber,
                        'educationmatter': education.educationmatter,
                    })

            # Filter education data by the selected time period
            filtered_education_data = []
            if selected_time_period:
                filtered_education_data = [
                    entry for entry in education_data
                    if entry['timeperiod'] == selected_time_period
                ]
                print(f"Filtered education data for time period '{selected_time_period}': {filtered_education_data}")

            # If no education data matches the selected time period, fall back to all education data
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
# Add this to your existing views.py
@login_required
def about_us(request):
    return render(request, "app/aboutus.html")
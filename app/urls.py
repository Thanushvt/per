from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    # Custom login page
    path('', views.login_view, name="login"),

    # Home page (only accessible when logged in)
    path('home/', login_required(views.home), name="home"),

    # Logout - Redirects to login page
    path('logout/', views.logout_view, name="logout"),

    # Include allauth URLs
    path('accounts/', include('allauth.urls')),
]

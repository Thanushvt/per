from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("home/", views.home, name="home"),
    path("logout/", views.logout_view, name="logout"),
    path("info/", views.info, name="info"),
    path('profile/',views.profile,name="profile"),
]

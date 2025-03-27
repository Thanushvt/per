from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path("", views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('info/', views.info, name='info'),
    path('role/', views.role, name='role'),
    path('job/', views.job, name='job'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('education/', views.education, name='education'),
    path('about/', views.about_us, name='about'),
    path('', RedirectView.as_view(url='/info/', permanent=False)),
    path('job/<int:id>/', views.job_detail, name='job_detail'), 
]
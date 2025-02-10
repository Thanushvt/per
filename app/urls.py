from . import views
from django.urls import path
from django.contrib.auth.decorators import login_required

urlpatterns =[
    path('',views.login,name="login"),
    path('home/',login_required(views.home),name="home"),
]

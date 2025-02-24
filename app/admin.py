from django.contrib import admin
from .models import Profile,UserSelection

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display =('user','google_email','google_name','github_email','github_name')

@admin.register(UserSelection)
class UserSelection(admin.ModelAdmin):
    list_display=('user','selected_courses','selected_interests','selected_time_periods')
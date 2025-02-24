from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver 

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    google_email = models.EmailField(blank=True, null=True)
    google_name = models.CharField(max_length=150, blank=True, null=True)
    github_email = models.EmailField(blank=True, null=True)
    github_name = models.CharField(max_length=150, blank=True, null=True)
    profile_picture = models.URLField(null=True, blank=True, default="/static/images/default-profile.png")
    gender = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        first_name, last_name = instance.username, ""
        if "_" in instance.username:
            first_name, last_name = instance.username.split("_", 1)
        
        Profile.objects.create(
            user=instance, 
            first_name=first_name, 
            last_name=last_name
        )

class UserSelection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    selected_courses = models.TextField(blank=True, null=True)
    selected_interests = models.TextField(blank=True, null=True)
    selected_time_periods = models.TextField(blank=True, null=True)  # Add this field

    
    def __str__(self):
        return f"{self.user.username}'s Selections"

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver 

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    google_email = models.EmailField(blank=True, null=True)
    google_name = models.CharField(max_length=150, blank=True, null=True)
    github_email = models.EmailField(blank=True, null=True)
    github_name = models.CharField(max_length=150, blank=True, null=True)
    profile_picture = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

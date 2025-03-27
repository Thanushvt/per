from django.db import models
from django.contrib.auth.models import User

class Interest(models.Model):
    interestid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    interest = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'interests'
        managed = False

    def __str__(self):
        return self.name

class Category(models.Model):
    categoryid = models.IntegerField(primary_key=True)
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)

    class Meta:
        db_table = 'category'
        managed = False

    def __str__(self):
        return self.category

class Roles(models.Model):
    roleid = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='categoryid')  # Add db_column
    role = models.TextField(null=True, blank=True, db_column='rolename')

    class Meta:
        db_table = 'roles'
        managed = False

    def __str__(self):
        return self.role or f"Role {self.roleid}"

class Matter(models.Model):
    matterid = models.AutoField(primary_key=True, db_column='matterid')
    matter = models.TextField(null=True, blank=True)
    youtube = models.TextField(null=True, blank=True)
    role = models.ForeignKey(
        'Roles',
        on_delete=models.CASCADE,
        related_name='matters',
        db_column='role_id',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.matter or f"Matter {self.matterid}"

    class Meta:
        db_table = 'matter'
        managed = False

class Education(models.Model):
    matter = models.ForeignKey(
        'Matter',
        on_delete=models.CASCADE,
        related_name='educations',
        db_column='matterid'
    )
    timeperiodinnumber = models.TextField(null=True, blank=True)
    educationmatter = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'education'
        managed = False

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

    class Meta:
        db_table = 'app_profile'
        managed = False

class UserSelection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    selected_courses = models.TextField(blank=True, null=True)
    selected_interests = models.TextField(blank=True, null=True)
    selected_time_periods = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Selections"

    class Meta:
        db_table = 'app_userselection'
        managed = False

class Youtube(models.Model):
    id = models.AutoField(primary_key=True)
    matter = models.ForeignKey(
        'Matter',
        on_delete=models.CASCADE,
        related_name='youtube_entries',
        db_column='matterid'
    )
    role = models.ForeignKey(
        'Roles',
        on_delete=models.CASCADE,
        related_name='youtube_links',
        db_column='roleid'
    )
    video_url = models.TextField(db_column='youtube_link')

    def __str__(self):
        return self.video_url

    class Meta:
        db_table = 'youtube'
        managed = False
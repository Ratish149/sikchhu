from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class Organization(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=255)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('org_user', 'Org_user'),
        ('learner', 'Learner'),
    ]
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    user_type = models.CharField(max_length=255, choices=USER_TYPE_CHOICES)
    profile_picture = models.FileField(
        upload_to='profile_pictures/', null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

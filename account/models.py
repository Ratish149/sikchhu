from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('Student', 'Student'),
        ('Teacher', 'Teacher'),
        ('Admin', 'Admin'),
    ]
    user_type = models.CharField(max_length=255, choices=USER_TYPE_CHOICES)
    profile_picture = models.FileField(
        upload_to='profile_pictures/', null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

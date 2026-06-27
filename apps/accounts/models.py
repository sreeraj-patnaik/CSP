from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Administrator"),
        ("coordinator", "Project Coordinator"),
        ("volunteer", "Volunteer"),
        ("viewer", "Read-Only Viewer"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="viewer")
    avatar = models.ImageField(upload_to="accounts/avatars/", null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    @property
    def is_coordinator(self):
        return self.role in ("admin", "coordinator")

    @property
    def can_manage_data(self):
        return self.role in ("admin", "coordinator")

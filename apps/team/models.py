from django.db import models
from apps.core.models import TimeStampedModel


class TeamMember(TimeStampedModel):
    ROLE_CHOICES = [
        ("mentor", "Mentor"),
        ("lead", "Project Lead"),
        ("member", "Team Member"),
        ("volunteer", "Volunteer"),
    ]
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")
    designation = models.CharField(max_length=300, blank=True,
                                   help_text="e.g. B.Tech CSE, 3rd Year")
    photo = models.ImageField(upload_to="team/", null=True, blank=True)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    roll_number = models.CharField(max_length=30, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"

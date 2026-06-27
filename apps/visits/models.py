from django.db import models
from django.urls import reverse
from apps.core.models import TimeStampedModel
from apps.villages.models import Village


class FieldVisit(TimeStampedModel):
    day_number = models.PositiveIntegerField(unique=True, help_text="Day 1, Day 2, …")
    title = models.CharField(max_length=300)
    date = models.DateField()
    villages = models.ManyToManyField(
        Village, blank=True,
        related_name="visits",
        help_text="Villages visited on this day (select multiple if needed)"
    )
    team_members = models.ManyToManyField(
        "team.TeamMember", blank=True,
        related_name="field_visits",
        help_text="Team members who attended this visit"
    )
    summary = models.TextField()
    objectives = models.JSONField(default=list, blank=True)
    activities = models.JSONField(default=list, blank=True)
    attendance = models.PositiveIntegerField(default=0)
    surveys_collected = models.PositiveIntegerField(default=0)
    observations = models.TextField(blank=True)
    problems_faced = models.TextField(blank=True)
    solutions = models.TextField(blank=True)
    lessons_learned = models.TextField(blank=True)
    impact = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["day_number"]
        verbose_name = "Field Visit"
        verbose_name_plural = "Field Visits"

    def __str__(self):
        return f"Day {self.day_number} – {self.title}"

    def get_absolute_url(self):
        return reverse("visits:detail", kwargs={"day": self.day_number})


class VisitMedia(TimeStampedModel):
    MEDIA_TYPES = [
        ("photo", "Photo"),
        ("video", "Video"),
        ("document", "Document"),
    ]
    visit = models.ForeignKey(FieldVisit, on_delete=models.CASCADE, related_name="media")
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES, default="photo")
    file = models.FileField(upload_to="visits/media/%Y/%m/")
    caption = models.CharField(max_length=500, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.visit} – {self.media_type} – {self.pk}"

    @property
    def is_photo(self):
        return self.media_type == "photo"

    @property
    def is_video(self):
        return self.media_type == "video"

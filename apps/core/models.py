"""Shared abstract base models."""
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Abstract base with created/updated timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(TimeStampedModel):
    """Abstract base with soft-delete support."""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    class Meta:
        abstract = True


class SiteSettings(models.Model):
    """Singleton model for site-wide configuration."""
    project_name = models.CharField(max_length=200, default="Community Service Project")
    project_topic = models.TextField(default="Safe Usage of Internet and Cybercrime Awareness in Rural Areas")
    mentor_name = models.CharField(max_length=200, default="Dr. R. Rajender")
    college_name = models.CharField(max_length=300, default="")
    academic_year = models.CharField(max_length=20, default="2024–2025")
    logo = models.ImageField(upload_to="site/", null=True, blank=True)
    hero_video = models.FileField(upload_to="site/", null=True, blank=True)
    hero_tagline = models.CharField(max_length=300, default="Bridging the Digital Divide in Rural Communities")
    show_ai_assistant = models.BooleanField(default=True)
    survey_open = models.BooleanField(default=True, help_text="Allow new survey submissions")
    maintenance_mode = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.project_name

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

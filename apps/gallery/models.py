from django.db import models
from apps.core.models import TimeStampedModel
from apps.villages.models import Village


class Photo(TimeStampedModel):
    CATEGORY_CHOICES = [
        ("survey", "Survey Activity"),
        ("awareness", "Awareness Session"),
        ("village", "Village Life"),
        ("team", "Team Photo"),
        ("infrastructure", "Infrastructure"),
        ("event", "Event"),
        ("before_after", "Before vs After"),
        ("other", "Other"),
    ]
    image = models.ImageField(upload_to="gallery/%Y/%m/")
    thumbnail = models.ImageField(upload_to="gallery/thumbs/%Y/%m/", null=True, blank=True)
    caption = models.TextField(blank=True)
    village = models.ForeignKey(
        Village, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="photos"
    )
    visit = models.ForeignKey(
        "visits.FieldVisit", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="photos"
    )
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="other")
    date_taken = models.DateField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True, help_text="Bytes")
    exif_data = models.JSONField(null=True, blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    before_after_pair = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="after_photos", help_text="Link to 'before' photo for comparison"
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-date_taken", "-created_at"]
        verbose_name = "Photo"
        verbose_name_plural = "Photos"

    def __str__(self):
        return self.caption[:60] if self.caption else f"Photo #{self.pk}"

    @property
    def tags_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    def save(self, *args, **kwargs):
        if self.image and not self.width:
            try:
                from PIL import Image as PILImage
                with PILImage.open(self.image) as img:
                    self.width, self.height = img.size
            except Exception:
                pass
        super().save(*args, **kwargs)

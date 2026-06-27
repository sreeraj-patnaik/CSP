from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from apps.core.models import TimeStampedModel


class Village(TimeStampedModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    district = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True, default="Andhra Pradesh")
    description = models.TextField(blank=True)
    history = models.TextField(blank=True)
    population = models.PositiveIntegerField(null=True, blank=True)
    households = models.PositiveIntegerField(null=True, blank=True)
    area_sqkm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    hero_image = models.ImageField(upload_to="villages/heroes/", null=True, blank=True)
    thumbnail = models.ImageField(upload_to="villages/thumbnails/", null=True, blank=True)
    nearby_landmarks = models.TextField(blank=True, help_text="Comma-separated landmarks")
    primary_occupation = models.CharField(max_length=200, blank=True)
    internet_infrastructure = models.TextField(blank=True)
    challenges = models.TextField(blank=True)
    community_response = models.TextField(blank=True)
    color_accent = models.CharField(max_length=7, default="#06B6D4",
                                    help_text="Hex color for village card accent")
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Village"
        verbose_name_plural = "Villages"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("villages:detail", kwargs={"slug": self.slug})

    @property
    def survey_count(self):
        return self.survey_responses.count()

    @property
    def visit_count(self):
        return self.visits.count()

    @property
    def internet_users_count(self):
        return self.survey_responses.filter(uses_internet=True).count()

    @property
    def internet_usage_pct(self):
        total = self.survey_count
        if total == 0:
            return 0
        return round((self.internet_users_count / total) * 100, 1)


class VillageObservation(TimeStampedModel):
    village = models.ForeignKey(Village, on_delete=models.CASCADE, related_name="observations")
    title = models.CharField(max_length=300)
    content = models.TextField()
    observation_date = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=100, blank=True,
                                choices=[
                                    ("infrastructure", "Infrastructure"),
                                    ("awareness", "Awareness"),
                                    ("challenge", "Challenge"),
                                    ("positive", "Positive Finding"),
                                    ("recommendation", "Recommendation"),
                                ])
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return f"{self.village.name} – {self.title}"

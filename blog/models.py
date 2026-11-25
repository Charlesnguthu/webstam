import uuid
from pathlib import Path
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone


def validate_cover_image(image):
    if image.size > 5 * 1024 * 1024:
        raise ValidationError("Article images must be 5 MB or smaller.")
    try:
        from PIL import Image
        with Image.open(image) as photo:
            if photo.format not in {"JPEG", "PNG", "WEBP"}:
                raise ValidationError("Upload a JPEG, PNG, or WebP image.")
            if photo.width > 5000 or photo.height > 5000:
                raise ValidationError("Image dimensions must be 5000 × 5000 pixels or smaller.")
            photo.verify()
    except ValidationError:
        raise
    except Exception as exc:
        raise ValidationError("The uploaded file is not a valid image.") from exc
    image.seek(0)


def article_image_path(instance, filename):
    return f"blog/{uuid.uuid4().hex}{Path(filename).suffix.lower()}"


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    description = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class PublishedArticleManager(models.Manager):
    def get_queryset(self):
        now = timezone.now()
        return super().get_queryset().filter(Q(status=Article.Status.PUBLISHED) | Q(status=Article.Status.SCHEDULED), published_at__lte=now)


class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SCHEDULED = "scheduled", "Scheduled"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=190, unique=True)
    excerpt = models.CharField(max_length=320)
    body = models.TextField(help_text="Plain text article content. Separate paragraphs with a blank line; HTML is escaped.")
    featured_image = models.ImageField(upload_to=article_image_path, validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"]), validate_cover_image])
    image_alt = models.CharField(max_length=180)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="blog_articles")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="articles")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT, db_index=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    seo_title = models.CharField(max_length=180, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)
    social_image = models.ImageField(upload_to=article_image_path, blank=True, validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"]), validate_cover_image])
    related_articles = models.ManyToManyField("self", blank=True, symmetrical=False, related_name="related_to")

    objects = models.Manager()
    public = PublishedArticleManager()

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [models.Index(fields=["status", "-published_at"]), models.Index(fields=["category", "status", "-published_at"])]
        constraints = [models.CheckConstraint(condition=~models.Q(title=""), name="blog_article_title_not_empty")]

    def clean(self):
        super().clean()
        if self.status == self.Status.PUBLISHED and self.published_at and self.published_at > timezone.now():
            raise ValidationError({"published_at": "Published articles cannot have a future publication time. Choose Scheduled instead."})
        if self.status == self.Status.SCHEDULED and (not self.published_at or self.published_at <= timezone.now()):
            raise ValidationError({"published_at": "Scheduled articles need a future publication time."})

    def save(self, *args, **kwargs):
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def reading_minutes(self):
        words = len(self.body.split())
        return max(1, (words + 199) // 200)

    def __str__(self):
        return self.title

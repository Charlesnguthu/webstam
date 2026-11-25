import uuid
from pathlib import Path
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.core.files.base import ContentFile
from django.core.validators import URLValidator
from urllib.parse import urlparse


def validate_profile_image(image):
    if image.size > 4 * 1024 * 1024:
        raise ValidationError("Profile images must be 4 MB or smaller.")
    try:
        from PIL import Image
        with Image.open(image) as photo:
            if photo.format not in {"JPEG", "PNG", "WEBP"}:
                raise ValidationError("Upload a JPEG, PNG, or WebP image.")
            if photo.width > 3000 or photo.height > 3000:
                raise ValidationError("Image dimensions must be 3000 × 3000 pixels or smaller.")
            photo.verify()
    except ValidationError:
        raise
    except Exception as exc:
        raise ValidationError("The uploaded file is not a valid image.") from exc
    image.seek(0)


def profile_upload_path(instance, filename):
    return f"team/{uuid.uuid4().hex}{Path(filename).suffix.lower()}"


class TeamMember(models.Model):
    full_name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    role = models.CharField(max_length=120, default="Co-founder")
    professional_headline = models.CharField(max_length=180, blank=True)
    short_bio = models.CharField(max_length=320)
    biography = models.TextField(blank=True)
    seo_title = models.CharField(max_length=180, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)
    profile_photo = models.ImageField(upload_to=profile_upload_path, blank=True, validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"]), validate_profile_image])
    secondary_photo = models.ImageField(upload_to=profile_upload_path, blank=True, validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"]), validate_profile_image])
    profile_photo_360 = models.ImageField(upload_to="team/optimized/", blank=True, editable=False)
    profile_photo_720 = models.ImageField(upload_to="team/optimized/", blank=True, editable=False)
    skills = models.TextField(help_text="One skill per line.")
    responsibilities = models.TextField(blank=True, help_text="One area per line.")
    project_contributions = models.TextField(blank=True, help_text="One project per line; keep attribution verified.")
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_founder = models.BooleanField(default=False)

    class Meta:
        ordering = ["display_order", "full_name"]

    def __str__(self):
        return self.full_name

    @property
    def initials(self):
        return "".join(part[0] for part in self.full_name.split()[:2]).upper()

    @property
    def skill_list(self):
        return [line.strip() for line in self.skills.splitlines() if line.strip()]

    @property
    def responsibility_list(self):
        return [line.strip() for line in self.responsibilities.splitlines() if line.strip()]

    @property
    def project_list(self):
        return [line.strip() for line in self.project_contributions.splitlines() if line.strip()]

    def save(self, *args, **kwargs):
        is_fresh_upload = bool(self.profile_photo and getattr(self.profile_photo, "_file", None))
        super().save(*args, **kwargs)
        if is_fresh_upload:
            from PIL import Image, ImageOps
            with self.profile_photo.open("rb") as photo_file:
                image = ImageOps.exif_transpose(Image.open(photo_file))
                image.load()
            for width, field_name in ((360, "profile_photo_360"), (720, "profile_photo_720")):
                variant = image.copy()
                variant.thumbnail((width, width), Image.Resampling.LANCZOS)
                if variant.mode not in ("RGB", "RGBA"):
                    variant = variant.convert("RGB")
                output = BytesIO()
                variant.save(output, format="WEBP", quality=82, method=6)
                field = getattr(self, field_name)
                if field.name:
                    field.delete(save=False)
                field.save(f"member-{self.pk}-{width}.webp", ContentFile(output.getvalue()), save=False)
            super().save(update_fields=["profile_photo_360", "profile_photo_720"])
            self.profile_photo._file = None


class ExternalProfile(models.Model):
    class Owner(models.TextChoices):
        COMPANY = "company", "Webstam Technologies"
        CHARLES = "charles-nguthu", "Charles Nguthu"
        HEZRON = "hezron-njenga", "Hezron Njenga"

    owner = models.CharField(max_length=32, choices=Owner.choices)
    platform = models.CharField(max_length=40, help_text="For example LinkedIn, GitHub, or Upwork.")
    label = models.CharField(max_length=80)
    url = models.URLField(max_length=500, validators=[URLValidator(schemes=["https"])])
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["owner", "display_order", "platform"]
        constraints = [models.UniqueConstraint(fields=["owner", "platform"], name="unique_owner_external_platform")]

    def clean(self):
        super().clean()
        parsed = urlparse(self.url)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise ValidationError({"url": "Enter a secure public HTTPS profile URL."})

    def __str__(self):
        return f"{self.owner}: {self.label}"


class ProjectCaseStudy(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=180)
    content = models.JSONField(help_text="Structured case-study content. Preserve evidence notes and leave unknown URLs blank.")
    is_published = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Project case study"

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if not isinstance(self.content, dict):
            raise ValidationError({"content": "Case-study content must be a JSON object."})
        for key in ("demo_url", "source_url"):
            value = self.content.get(key, "")
            if value:
                if not isinstance(value, str):
                    raise ValidationError({"content": f"{key} must be a secure public HTTPS URL."})
                try:
                    URLValidator(schemes=["https"])(value)
                except ValidationError as exc:
                    raise ValidationError({"content": f"{key} must be a secure public HTTPS URL."}) from exc

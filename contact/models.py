from django.db import models

class Inquiry(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        REVIEWED = "reviewed", "Reviewed"
        QUALIFIED = "qualified", "Qualified"
        PROPOSAL = "proposal", "Proposal sent"
        WON = "won", "Won"
        LOST = "lost", "Lost"
        ARCHIVED = "archived", "Archived"
    SERVICE_CHOICES = [("web", "Custom web development"), ("app", "Full-stack application development"), ("ai", "AI and machine learning"), ("automation", "Business process automation"), ("mobile", "Mobile application development"), ("data", "Data analytics and engineering"), ("api", "API development and integration"), ("seo", "Technical SEO and performance"), ("deployment", "Deployment and maintenance"), ("other", "Something else")]
    TIMELINE_CHOICES = [("asap", "As soon as possible"), ("1_3_months", "Within 1–3 months"), ("3_6_months", "Within 3–6 months"), ("exploring", "Just exploring")]
    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=40, blank=True)
    organization = models.CharField(max_length=160, blank=True)
    service = models.CharField(max_length=80, choices=SERVICE_CHOICES)
    budget = models.CharField(max_length=60, blank=True)
    timeline = models.CharField(max_length=60, choices=TIMELINE_CHOICES, blank=True)
    contact_method = models.CharField(max_length=20, choices=[("email", "Email"), ("phone", "Phone"), ("either", "Either")], blank=True)
    description = models.TextField(max_length=5000)
    consent_confirmed_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=120, blank=True)
    medium = models.CharField(max_length=120, blank=True)
    campaign = models.CharField(max_length=120, blank=True)
    content = models.CharField(max_length=120, blank=True)
    term = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    internal_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, db_index=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"{self.name} — {self.created_at:%Y-%m-%d}"

    @property
    def attribution(self):
        return self.source or "Direct / unknown"


class BudgetBand(models.Model):
    code = models.SlugField(max_length=60, unique=True)
    label = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "label"]

    def __str__(self):
        return self.label

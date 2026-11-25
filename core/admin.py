from django.contrib import admin
from .models import ExternalProfile, ProjectCaseStudy, TeamMember


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "role", "is_founder", "is_active", "display_order")
    list_editable = ("is_active", "display_order")
    list_filter = ("is_active", "is_founder")
    search_fields = ("full_name", "short_bio", "skills")
    prepopulated_fields = {"slug": ("full_name",)}
    fieldsets = (
        ("Public profile", {"fields": ("full_name", "slug", "role", "professional_headline", "short_bio", "biography", "profile_photo", "secondary_photo")} ),
        ("Search metadata", {"fields": ("seo_title", "meta_description"), "classes": ("collapse",)}),
        ("Expertise and contributions", {"fields": ("skills", "responsibilities", "project_contributions")} ),
        ("Visibility", {"fields": ("is_founder", "is_active", "display_order")} ),
    )


@admin.register(ExternalProfile)
class ExternalProfileAdmin(admin.ModelAdmin):
    list_display = ("label", "owner", "platform", "url", "is_active")
    list_filter = ("owner", "platform", "is_active")
    search_fields = ("label", "url")


@admin.register(ProjectCaseStudy)
class ProjectCaseStudyAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("title", "slug")
    readonly_fields = ("updated_at",)

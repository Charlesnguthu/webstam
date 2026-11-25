from django.contrib import admin
from django.utils import timezone
from .models import Article, Category
from .formatting import render_article_body


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    change_form_template = "admin/blog/article/change_form.html"
    list_display = ("title", "category", "author", "status", "published_at", "is_featured", "created_at", "updated_at")
    list_filter = ("status", "category", "author", "is_featured")
    search_fields = ("title", "excerpt", "body", "category__name", "author__username")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("related_articles",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "published_at"
    fieldsets = (("Article", {"fields": ("title", "slug", "excerpt", "body", "author", "category")}), ("Image", {"fields": ("featured_image", "image_alt", "social_image")}), ("Publishing", {"fields": ("status", "published_at", "is_featured", "related_articles")}), ("Search metadata", {"fields": ("seo_title", "meta_description"), "classes": ("collapse",)}), ("Timestamps", {"fields": ("created_at", "updated_at")}))

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("category", "author")

    def get_urls(self):
        from django.urls import path
        return [path("<path:object_id>/preview/", self.admin_site.admin_view(self.preview_view), name="blog_article_preview")] + super().get_urls()

    def preview_view(self, request, object_id):
        from django.shortcuts import get_object_or_404, render
        article = get_object_or_404(Article.objects.select_related("category", "author"), pk=object_id)
        if not self.has_view_or_change_permission(request, article):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        response = render(request, "blog/detail.html", {"article": article, "body_html": render_article_body(article.body), "preview": True, "title": article.title, "meta_description": article.excerpt, "noindex": True, "canonical_url": ""})
        response["X-Robots-Tag"] = "noindex, nofollow"
        return response

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        if obj.status == Article.Status.PUBLISHED and not obj.published_at:
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)

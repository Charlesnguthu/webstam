import json
from datetime import timedelta
from io import BytesIO
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from .models import Article, Category
from .formatting import render_article_body


def image_upload(name="cover.png", fmt="PNG"):
    output = BytesIO()
    Image.new("RGB", (32, 20), "#236b69").save(output, format=fmt)
    return SimpleUploadedFile(name, output.getvalue(), content_type=f"image/{fmt.lower()}")


class BlogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(username="writer", first_name="Webstam", last_name="Writer")
        cls.category = Category.objects.create(name="Engineering", slug="engineering")

    def create_article(self, slug="first-article", status=Article.Status.PUBLISHED, published_at=None, **kwargs):
        if published_at is None and status == Article.Status.PUBLISHED:
            published_at = timezone.now() - timedelta(hours=1)
        category = kwargs.pop("category", self.category)
        return Article.objects.create(title=kwargs.pop("title", slug.replace("-", " ").title()), slug=slug, excerpt="A useful excerpt", body="A useful paragraph with enough detail.", featured_image=image_upload(), image_alt="Abstract green geometry", author=self.author, category=category, status=status, published_at=published_at, **kwargs)

    def test_creation_validation_and_unique_slug(self):
        article = self.create_article()
        self.assertEqual(article.reading_minutes, 1)
        with self.assertRaises(ValidationError):
            duplicate = Article(title="Duplicate", slug=article.slug, excerpt="Excerpt", body="Body", featured_image=image_upload(), image_alt="Alt", author=self.author, category=self.category)
            duplicate.full_clean()
        future = self.create_article(slug="future", status=Article.Status.PUBLISHED, published_at=timezone.now() + timedelta(days=2))
        with self.assertRaises(ValidationError):
            future.full_clean()
        scheduled = self.create_article(slug="scheduled-valid", status=Article.Status.SCHEDULED, published_at=timezone.now() + timedelta(days=1))
        scheduled.full_clean()

    def test_public_listing_detail_metadata_and_canonical(self):
        article = self.create_article(is_featured=True)
        with override_settings(PUBLIC_DOMAIN="www.webstam.example"):
            listing = self.client.get(reverse("blog:index"))
            self.assertContains(listing, article.title)
            response = self.client.get(reverse("blog:detail", kwargs={"slug": article.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<link rel="canonical" href="https://www.webstam.example/blog/first-article/">', html=True)
        self.assertContains(response, 'property="og:type" content="article"')
        self.assertContains(response, '"@type": "BlogPosting"')

    def test_draft_archived_and_future_scheduled_articles_are_private(self):
        for slug, status, date in [("draft", Article.Status.DRAFT, None), ("archived", Article.Status.ARCHIVED, timezone.now() - timedelta(days=1)), ("future", Article.Status.SCHEDULED, timezone.now() + timedelta(days=1))]:
            self.create_article(slug=slug, status=status, published_at=date)
        response = self.client.get(reverse("blog:index"))
        for secret_slug in ("draft", "archived", "future"):
            self.assertNotContains(response, secret_slug)
            self.assertEqual(self.client.get(reverse("blog:detail", kwargs={"slug": secret_slug})).status_code, 404)
        self.assertEqual(Article.public.count(), 0)

    def test_due_scheduled_article_is_public_without_a_scheduler(self):
        article = self.create_article(slug="due", status=Article.Status.SCHEDULED, published_at=timezone.now() - timedelta(seconds=1))
        self.assertTrue(Article.public.filter(pk=article.pk).exists())

    def test_draft_preview_requires_admin_and_is_noindex(self):
        article = self.create_article(slug="preview", status=Article.Status.DRAFT, published_at=None)
        url = reverse("admin:blog_article_preview", kwargs={"object_id": article.pk})
        self.assertEqual(self.client.get(url).status_code, 302)
        staff = get_user_model().objects.create_user(username="staff", password="pass", is_staff=True)
        self.client.force_login(staff)
        self.assertEqual(self.client.get(url).status_code, 403)
        staff.is_superuser = True
        staff.save()
        preview = self.client.get(url)
        self.assertEqual(preview.status_code, 200)
        self.assertEqual(preview.headers.get('X-Robots-Tag'), 'noindex, nofollow')

    def test_search_category_filter_validation_and_pagination(self):
        for i in range(11):
            self.create_article(slug=f"article-{i}", title=f"Searchable story {i}")
        other = Category.objects.create(name="Data", slug="data")
        self.create_article(slug="data-story", title="Data story", category=other)
        self.assertContains(self.client.get(reverse("blog:index") + "?q=Searchable"), "Searchable story 10")
        category = self.client.get(reverse("blog:category", kwargs={"slug": "data"}))
        self.assertContains(category, "Data story")
        self.assertNotContains(category, "Searchable story")
        self.assertEqual(self.client.get(reverse("blog:index") + "?q=" + "x" * 101).status_code, 400)
        self.assertContains(self.client.get(reverse("blog:index") + "?page=2"), "Page 2 of 2")

    def test_markdown_body_formats_content_and_escapes_html(self):
        rendered = str(render_article_body("## A heading\n\n- first\n- second\n\n`x = 1` <script>alert(1)</script>"))
        self.assertIn("<h3>A heading</h3>", rendered)
        self.assertIn("<ul><li>first</li><li>second</li></ul>", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertNotIn("<script>", rendered)

    def test_image_validation(self):
        invalid = SimpleUploadedFile("script.svg", b"<svg/>", content_type="image/svg+xml")
        article = Article(title="Bad", slug="bad", excerpt="Excerpt", body="Body", featured_image=invalid, image_alt="Bad", author=self.author, category=self.category)
        with self.assertRaises(ValidationError):
            article.full_clean()

    def test_feed_sitemap_admin_and_article_404(self):
        article = self.create_article()
        feed = self.client.get(reverse("blog:feed"))
        self.assertContains(feed, article.title)
        self.assertEqual(self.client.get(reverse("blog:detail", kwargs={"slug": "missing"})).status_code, 404)
        with override_settings(PUBLIC_DOMAIN="webstam.example"):
            sitemap = self.client.get(reverse("sitemap"))
        self.assertContains(sitemap, "/blog/first-article/")
        self.assertIn(Article, admin.site._registry)
        self.assertNotContains(self.client.get(reverse("blog:feed")), "draft")

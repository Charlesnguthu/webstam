import json
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import json_script
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_GET
from .models import Article, Category
from .formatting import render_article_body


def origin(request):
    domain = settings.PUBLIC_DOMAIN.strip().removeprefix("https://").removeprefix("http://").strip("/")
    return f"https://{domain}" if domain else request.build_absolute_uri("/").rstrip("/")


@require_GET
def index(request, category_slug=None, slug=None):
    category_slug = category_slug or slug
    query = request.GET.get("q", "").strip()
    if len(query) > 100:
        return render(request, "blog/list.html", {"articles": [], "query": "", "search_error": "Search terms must be 100 characters or fewer.", "categories": Category.objects.all(), "title": "Company Blog | Webstam Technologies", "meta_description": "Insights from Webstam Technologies on software, AI, and automation."}, status=400)
    articles = Article.public.select_related("category", "author")
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        articles = articles.filter(category=category)
    if query:
        articles = articles.filter(Q(title__icontains=query) | Q(excerpt__icontains=query) | Q(body__icontains=query))
    featured = articles.filter(is_featured=True).first() if not query else None
    if featured:
        articles = articles.exclude(pk=featured.pk)
    paginator = Paginator(articles, 9)
    page_obj = paginator.get_page(request.GET.get("page", "1"))
    canonical = f"{origin(request)}{reverse('blog:category', kwargs={'slug': category.slug}) if category else reverse('blog:index')}"
    return render(request, "blog/list.html", {"articles": page_obj, "page_obj": page_obj, "featured": featured, "categories": Category.objects.all(), "active_category": category, "query": query, "title": f"{category.name} Articles | Webstam Technologies" if category else "Company Blog | Webstam Technologies", "meta_description": (category.description if category else "") or "Insights from Webstam Technologies on software, AI, and automation.", "canonical_url": canonical, "og_type": "website", "noindex": bool(query)})


@require_GET
def detail(request, slug):
    article = get_object_or_404(Article.public.select_related("category", "author"), slug=slug)
    related = article.related_articles.filter(pk__in=Article.public.values("pk")).exclude(pk=article.pk).select_related("category", "author")[:3]
    if not related:
        related = Article.public.filter(category=article.category).exclude(pk=article.pk).select_related("category", "author")[:3]
    canonical = f"{origin(request)}{reverse('blog:detail', kwargs={'slug': article.slug})}"
    image = article.social_image or article.featured_image
    image_url = f"{origin(request)}{image.url}"
    article_schema = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": article.title, "description": article.excerpt, "datePublished": article.published_at.isoformat(), "dateModified": article.updated_at.isoformat(), "author": {"@type": "Person", "name": article.author.get_full_name() or article.author.get_username()}, "publisher": {"@id": f"{origin(request)}/#organization"}, "mainEntityOfPage": canonical, "image": image_url, "articleSection": article.category.name, "wordCount": len(article.body.split())}
    breadcrumb_schema = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": origin(request)}, {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{origin(request)}{reverse('blog:index')}"}, {"@type": "ListItem", "position": 3, "name": article.title, "item": canonical}]}
    return render(request, "blog/detail.html", {"article": article, "body_html": render_article_body(article.body), "related_articles": related, "title": article.seo_title or article.title, "meta_description": article.meta_description or article.excerpt, "canonical_url": canonical, "og_type": "article", "share_image_url": image_url, "article_jsonld": json.dumps(article_schema).replace("<", "\\u003c"), "article_breadcrumb_jsonld": json.dumps(breadcrumb_schema).replace("<", "\\u003c")})


class ArticleFeed(Feed):
    title = "Webstam Technologies Blog"
    link = "/blog/"
    description = "Insights on software, AI, and automation from Webstam Technologies."

    def items(self):
        return Article.public.select_related("category", "author")[:30]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt

    def item_link(self, item):
        return reverse("blog:detail", kwargs={"slug": item.slug})

    def item_pubdate(self, item):
        return item.published_at

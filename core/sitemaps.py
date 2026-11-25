from django.contrib.sitemaps import Sitemap
from django.conf import settings
from django.urls import reverse
from .project_data import project_items
from .service_pages import SERVICE_PAGES
from .models import TeamMember
from blog.models import Article

class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7
    def get_protocol(self, protocol=None):
        return "http" if settings.DEBUG else "https"
    def get_domain(self, site=None):
        # Do not let Django's default example.com Site leak into local output.
        return settings.PUBLIC_DOMAIN or "localhost"
    def items(self):
        profiles = [f"team-profile:{slug}" for slug in TeamMember.objects.filter(is_active=True, is_founder=True).values_list("slug", flat=True)]
        return ["home", "services", "solutions", "projects", "about", "team", "technologies", "ai-automation", "contact:contact", "blog:index"] + [f"service:{slug}" for slug in SERVICE_PAGES] + [f"project:{item['slug']}" for item in project_items()] + profiles + list(Article.public.all())
    def location(self, item):
        if isinstance(item, Article):
            return reverse("blog:detail", kwargs={"slug": item.slug})
        if item.startswith("project:"):
            return reverse("project-detail", kwargs={"slug": item.split(":", 1)[1]})
        if item.startswith("service:"):
            return reverse("service-detail", kwargs={"slug": item.split(":", 1)[1]})
        if item.startswith("team-profile:"):
            return reverse("team-profile", kwargs={"slug": item.split(":", 1)[1]})
        return reverse(item)

from django.contrib import admin
from django.urls import include, path
from django.contrib.sitemaps.views import sitemap as sitemap_response
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from core.sitemaps import StaticViewSitemap

handler404 = "core.views.not_found"
handler500 = "core.views.server_error"
sitemaps = {"pages": StaticViewSitemap}

def sitemap(request):
    if not settings.DEBUG and not settings.PUBLIC_DOMAIN:
        return HttpResponse("Sitemap unavailable until PUBLIC_DOMAIN is configured.\n", status=503, content_type="text/plain")
    return sitemap_response(request, sitemaps=sitemaps)

urlpatterns = [path("admin/", admin.site.urls), path("", include("core.urls")), path("blog/", include("blog.urls")), path("contact/", include("contact.urls")), path("sitemap.xml", sitemap, name="sitemap")]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

import json
from django.conf import settings
from django.utils.safestring import mark_safe
from django.templatetags.static import static
from django.urls import reverse
from .project_data import project_items
from .service_pages import SERVICE_PAGES
from .models import ExternalProfile


def _jsonld(value):
    # Escape HTML-significant characters before marking this JSON as safe in a script element.
    encoded = json.dumps(value, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return mark_safe(encoded)


def company(request):
    domain = settings.PUBLIC_DOMAIN.strip().removeprefix("https://").removeprefix("http://").strip("/")
    origin = f"https://{domain}" if domain else ""
    canonical = f"{origin}{request.path}" if origin else ""
    schema_origin = origin or request.build_absolute_uri("/").rstrip("/")
    organization = {"@context": "https://schema.org", "@type": "Organization", "@id": f"{schema_origin}/#organization", "name": "Webstam Technologies", "description": "We build intelligent software and automate business processes."}
    website = {"@context": "https://schema.org", "@type": "WebSite", "@id": f"{schema_origin}/#website", "name": "Webstam Technologies", "publisher": {"@id": f"{schema_origin}/#organization"}}
    if origin:
        organization["url"] = origin
        website["url"] = origin
    organization["logo"] = {"@type": "ImageObject", "url": f"{schema_origin}{static('images/webstam-share.png')}"}
    if settings.COMPANY_EMAIL or settings.COMPANY_PHONE:
        contact_point = {"@type": "ContactPoint", "contactType": "project inquiries"}
        if settings.COMPANY_EMAIL:
            organization["email"] = settings.COMPANY_EMAIL
            contact_point["email"] = settings.COMPANY_EMAIL
        if settings.COMPANY_PHONE:
            organization["telephone"] = settings.COMPANY_PHONE
            contact_point["telephone"] = settings.COMPANY_PHONE
        organization["contactPoint"] = contact_point
    company_profiles = list(ExternalProfile.objects.filter(owner=ExternalProfile.Owner.COMPANY, is_active=True))
    founder_profiles = {}
    for profile in ExternalProfile.objects.filter(
        owner__in=[ExternalProfile.Owner.CHARLES, ExternalProfile.Owner.HEZRON],
        is_active=True,
    ):
        founder_profiles.setdefault(profile.owner, []).append(profile)
    if company_profiles:
        organization["sameAs"] = [profile.url for profile in company_profiles]

    path = request.path.strip("/")
    crumbs = []
    if path:
        crumbs.append({"name": "Home", "url": f"{origin}{reverse('home')}" if origin else reverse("home")})
        if path.startswith("projects/"):
            crumbs.append({"name": "Projects", "url": f"{origin}{reverse('projects')}" if origin else reverse("projects")})
            slug = path.split("/")[-1]
            project = next((item for item in project_items() if item["slug"] == slug), None)
            if project:
                crumbs.append({"name": project["title"], "url": f"{origin}{reverse('project-detail', kwargs={'slug': slug})}" if origin else reverse("project-detail", kwargs={"slug": slug})})
        elif path.startswith("services/"):
            slug = path.split("/")[-1]
            if slug in SERVICE_PAGES:
                crumbs.extend([{"name": "Services", "url": f"{origin}{reverse('services')}" if origin else reverse("services")}, {"name": SERVICE_PAGES[slug]["heading"], "url": f"{origin}{request.path}" if origin else request.path}])
        elif path == "team" or path.startswith("team/"):
            if path.startswith("team/"):
                member = getattr(request, "profile_member", None)
                crumbs.append({"name": "Team", "url": f"{origin}{reverse('team')}" if origin else reverse("team")})
                if member:
                    crumbs.append({"name": member.full_name, "url": f"{origin}{request.path}" if origin else request.path})
            else:
                crumbs.append({"name": "Team", "url": f"{origin}{request.path}" if origin else request.path})
        else:
            labels = {"services": "Services", "solutions": "Solutions", "about": "About", "team": "Team", "contact": "Contact", "technologies": "Technologies", "ai-automation": "AI and automation", "privacy": "Privacy"}
            if path in labels:
                crumbs.append({"name": labels[path], "url": f"{origin}{request.path}" if origin else request.path})
    breadcrumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i, "name": crumb["name"], "item": crumb["url"]} for i, crumb in enumerate(crumbs, 1)]} if len(crumbs) > 1 else None
    return {
        "company": {"name": "Webstam Technologies", "tagline": "Software. AI. Automation.", "positioning": "We build intelligent software and automate business processes.", "email": settings.COMPANY_EMAIL, "phone": settings.COMPANY_PHONE, "domain": domain, "social_profiles": company_profiles, "analytics_id": settings.GA_MEASUREMENT_ID},
        "founder_profiles": founder_profiles,
        "canonical_url": canonical,
        "share_image_url": f"{origin}{static('images/webstam-share.png')}" if origin else request.build_absolute_uri(static("images/webstam-share.png")),
        "organization_jsonld": _jsonld(organization),
        "website_jsonld": _jsonld(website),
        "breadcrumb_jsonld": _jsonld(breadcrumb) if breadcrumb else "",
        "organization_id": f"{schema_origin}/#organization",
    }

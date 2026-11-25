from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.conf import settings
from django.templatetags.static import static
from .projects import PROJECT_CATEGORIES
from .project_data import project_items
from .models import TeamMember, ExternalProfile
from .service_pages import SERVICE_PAGES

def _site_origin(request):
    domain = settings.PUBLIC_DOMAIN.strip().removeprefix("https://").removeprefix("http://").strip("/")
    return f"https://{domain}" if domain else request.build_absolute_uri("/").rstrip("/")


def _person_data(request, member):
    profile_url = f"{_site_origin(request)}/team/{member.slug}/"
    person = {
        "@type": "Person", "@id": f"{profile_url}#person", "name": member.full_name,
        "url": profile_url, "jobTitle": member.role,
        "description": member.short_bio,
        "worksFor": {"@id": f"{_site_origin(request)}/#organization", "name": "Webstam Technologies"},
    }
    if member.skill_list:
        person["knowsAbout"] = member.skill_list
    if member.profile_photo:
        person["image"] = f"{_site_origin(request)}{member.profile_photo.url}"
    elif member.slug == "charles-nguthu":
        person["image"] = f"{_site_origin(request)}{static('images/Charles-nguthu.jpeg')}"
    elif member.slug == "hezron-njenga":
        person["image"] = f"{_site_origin(request)}{static('images/hezron-njenga.jpeg')}"
    same_as = list(ExternalProfile.objects.filter(owner=member.slug, is_active=True).values_list("url", flat=True))
    if same_as:
        person["sameAs"] = same_as
    return person


def _people_graph(request, members):
    return {"@context": "https://schema.org", "@graph": [_person_data(request, member) for member in members]}

PAGES = {
    "services": {"title": "Software services built around your goals", "description": "From web applications to AI and workflow automation, explore practical technology services from Webstam.", "eyebrow": "What we do", "intro": "Useful technology, built for the way your organization works.", "items": [("Custom web development", "Business websites, portals, dashboards, SaaS platforms, e-commerce, and internal systems.", "Django · HTML · Tailwind"), ("Full-stack applications", "Interfaces, backend services, REST APIs, authentication, databases, and integrations.", "Python · JavaScript · APIs"), ("AI and machine learning", "Predictive models and AI features shaped around suitable data and clearly defined use cases.", "Machine learning · Data"), ("Business automation", "Connect repetitive tasks, forms, approvals, notifications, and reporting into dependable workflows.", "Django · APIs · Python"), ("Mobile applications", "Cross-platform applications and connected business tools for mobile users.", "Flutter · Firebase"), ("Data analytics and engineering", "Clean, structure, and present data to support useful reporting and decision-making.", "SQL · PostgreSQL · Python"), ("API development and integration", "Build secure service interfaces and connect systems that need to exchange information.", "REST · Django · Integrations"), ("Technical SEO and performance", "Improve discoverability and usability with sound technical foundations and efficient assets.", "Semantic HTML · SEO · Web"), ("Deployment and maintenance", "Prepare applications for production and provide agreed troubleshooting and enhancements.", "Linux · Git · PostgreSQL")]},
    "solutions": {"title": "Technology for real-world challenges", "description": "Explore ways software, AI, and automation can support organizations at different stages.", "eyebrow": "Who we help", "intro": "The right solution starts with understanding the work behind the problem.", "items": [("Startups", "Turn an early product idea into a focused first release, with room to learn and grow.", "Product discovery · MVP · SaaS"), ("Small and medium businesses", "Replace repetitive manual steps with connected tools, clearer records, and useful dashboards.", "Process digitization · Integrations"), ("Institutions and NGOs", "Structure document submissions, reviews, approvals, and reporting around real roles.", "Workflow · Portals · Reporting"), ("E-commerce teams", "Build or improve online storefronts and the systems that support product and order workflows.", "Commerce · APIs · Analytics"), ("Agriculture", "Create digital tools that make useful agricultural information and workflows easier to access.", "Platforms · Data · Mobile"), ("Data-focused teams", "Explore whether analytics or a carefully evaluated AI feature can help answer a defined question.", "Analytics · ML · Decision support"), ("Connected organizations", "Reduce duplication by helping existing software systems exchange information.", "APIs · Data exchange · Automation")]},
    "technologies": {"title": "A practical technology ecosystem", "description": "Technologies are selected to fit each project's requirements, team, and operating context.", "eyebrow": "Technology", "intro": "We choose tools for the job, and build with maintainability in mind.", "items": [("Languages", "Python, JavaScript, TypeScript, PHP, SQL", ""), ("Web", "Django, HTML5, Tailwind CSS, React", ""), ("Mobile", "Flutter", ""), ("AI and data", "Machine learning, deep learning, predictive analytics, data processing", ""), ("Databases", "PostgreSQL, MySQL, SQLite, Firebase", ""), ("Infrastructure", "Linux, Git, APIs, cloud deployment", "")]},
    "ai-automation": {"title": "Practical AI and business automation", "description": "Understand where AI and automation can fit into everyday business workflows.", "eyebrow": "AI & automation", "intro": "Make repetitive work easier and help people find useful information sooner.", "items": [("Document processing", "Extract and organize information from documents, with review steps for uncertain results.", "Human review · Structured data"), ("Workflow automation", "Route forms, approvals, notifications, and follow-up tasks between the right people.", "Approvals · Notifications"), ("Predictive analytics", "Use historical data to explore patterns and support planning, with model limitations made clear.", "Forecasting · Evaluation"), ("AI-assisted search", "Help people retrieve relevant information from a defined collection of business knowledge.", "Search · Retrieval"), ("Data transformation", "Move information between formats and systems with repeatable, traceable steps.", "ETL · APIs"), ("Reporting and decision support", "Bring important measures into understandable reports so teams can ask better questions.", "Dashboards · Analytics")]},
}

def home(request):
    members = list(TeamMember.objects.filter(is_active=True, is_founder=True))
    projects = project_items()
    return render(request, "pages/home.html", {"title": "Webstam Technologies | Software, AI & Automation", "meta_description": "We build intelligent software and automate business processes. Explore custom software, AI, and practical automation with Webstam Technologies.", "projects": projects, "team_members": members, "people_jsonld": _people_graph(request, members)})

def page(request, slug):
    data = PAGES[slug]
    return render(request, f"pages/{slug}.html", {**data, "meta_description": data["description"], "active_page": slug, "all_service_pages": SERVICE_PAGES})

def about(request):
    return render(request, "pages/about.html", {"title": "About Webstam Technologies", "meta_description": "Meet the Webstam Technologies team and learn how we approach software, AI, and automation.", "team_members": TeamMember.objects.filter(is_active=True, is_founder=True)})

def team(request):
    members = list(TeamMember.objects.filter(is_active=True))
    return render(request, "pages/team.html", {"title": "Meet the Team | Webstam Technologies", "meta_description": "Meet the founders building Webstam Technologies and learn how we work with project teams.", "team_members": members, "people_jsonld": _people_graph(request, members)})


def team_profile(request, slug):
    member = get_object_or_404(TeamMember, slug=slug, is_active=True, is_founder=True)
    request.profile_member = member
    origin = _site_origin(request)
    canonical = f"{origin}/team/{member.slug}/"
    person = _person_data(request, member)
    profile_schema = {
        "@context": "https://schema.org", "@type": "ProfilePage", "@id": f"{canonical}#profilepage",
        "url": canonical, "name": member.seo_title or f"{member.full_name} | Webstam Technologies",
        "mainEntity": person,
    }
    featured_projects = [project for project in project_items() if project.get("developer_slug") == member.slug]
    profiles = ExternalProfile.objects.filter(owner=member.slug, is_active=True)
    return render(request, "pages/team_profile.html", {
        "member": member, "featured_projects": featured_projects, "external_profiles": profiles,
        "title": member.seo_title or f"{member.full_name} | Webstam Technologies",
        "meta_description": member.meta_description or member.short_bio,
        "og_type": "profile", "profile_jsonld": profile_schema,
    })

def service_detail(request, slug):
    data = SERVICE_PAGES.get(slug)
    if not data:
        raise Http404("Service not found")
    related = [item for item in project_items() if item["slug"] in data["projects"]]
    return render(request, "pages/service_detail.html", {**data, "slug": slug, "related_projects": related, "meta_description": data["description"], "all_service_pages": SERVICE_PAGES, "service_jsonld": {"@context": "https://schema.org", "@type": "Service", "name": data["heading"], "serviceType": data["service_type"], "description": data["description"], "provider": {"@id": f"{_site_origin(request)}/#organization", "name": "Webstam Technologies"}}})

def projects(request):
    projects = project_items()
    return render(request, "pages/projects.html", {"title": "Selected Projects | Webstam Technologies", "meta_description": "Explore documented projects across agriculture, education technology, e-commerce, and workflow automation.", "projects": projects, "categories": PROJECT_CATEGORIES})

def project_detail(request, slug):
    project = next((item for item in project_items() if item["slug"] == slug), None)
    if project is None:
        raise Http404("Project not found")
    related = [item for item in project_items() if item["slug"] in project["related"]]
    project_data = dict(project)
    if project.get("developer_slug"):
        project_data["developer_member"] = TeamMember.objects.filter(slug=project["developer_slug"], is_active=True, is_founder=True).first()
    return render(request, "pages/case_study.html", {"project": project_data, "related_projects": related, "title": f"{project['title']} Case Study | Webstam Technologies", "meta_description": project["summary"]})

def contact(request):
    from django.shortcuts import redirect
    return redirect("contact:contact")

def privacy(request):
    return render(request, "pages/privacy.html", {"title": "Privacy Notice | Webstam Technologies", "meta_description": "How Webstam Technologies handles project inquiry information.", "noindex": True})

def robots(request):
    from django.http import HttpResponse
    from django.conf import settings
    domain = settings.PUBLIC_DOMAIN.strip().removeprefix("https://").removeprefix("http://").strip("/")
    sitemap = f"Sitemap: https://{domain}/sitemap.xml\n" if domain else ""
    return HttpResponse(f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /contact/thanks/\nDisallow: /contact/staff-dashboard/\n{sitemap}", content_type="text/plain")

def not_found(request, exception):
    return render(request, "pages/404.html", status=404)

def server_error(request):
    return render(request, "pages/500.html", status=500)

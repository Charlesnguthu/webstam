from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
import json
import re
import xml.etree.ElementTree as ET
from html import unescape
from io import BytesIO
from tempfile import TemporaryDirectory
from PIL import Image
from .models import ExternalProfile, ProjectCaseStudy, TeamMember, validate_profile_image
from .service_pages import SERVICE_PAGES
from .projects import PROJECTS

class SitePageTests(TestCase):
    def test_main_pages_render(self):
        for name in ["home", "services", "solutions", "projects", "about", "technologies", "ai-automation", "privacy", "contact:contact"]:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)
    def test_navigation_links_resolve(self):
        for name in ["home", "services", "solutions", "projects", "about", "contact:contact"]:
            self.assertTrue(reverse(name))
    def test_shared_motion_system_is_loaded_without_replacing_page_content(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'href="/static/css/motion.css"')
        self.assertContains(response, 'src="/static/js/motion.js"')
        self.assertContains(response, 'data-motion-control')
        self.assertContains(response, 'class="hero"')
        self.assertContains(response, 'class="site-footer"')
    def test_each_project_has_a_case_study(self):
        for project in PROJECTS:
            with self.subTest(project=project["slug"]):
                response = self.client.get(reverse("project-detail", kwargs={"slug": project["slug"]}))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, project["title"])
    def test_unknown_project_returns_404(self):
        response = self.client.get(reverse("project-detail", kwargs={"slug": "unknown-project"}))
        self.assertEqual(response.status_code, 404)
    def test_404_handler_renders(self):
        response = self.client.get("/this-page-does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Not found", status_code=404)
    def test_sitemap_and_robots(self):
        with override_settings(PUBLIC_DOMAIN="testserver"):
            sitemap_response = self.client.get(reverse("sitemap"))
        self.assertEqual(sitemap_response.status_code, 200)
        self.assertContains(sitemap_response, "/services/django-python/")
        self.assertNotContains(sitemap_response, "/admin/")
        self.assertNotContains(sitemap_response, "/contact/thanks/")
        self.assertNotContains(sitemap_response, "/privacy/")
        robots_response = self.client.get(reverse("robots"))
        self.assertContains(robots_response, "User-agent: *")
        self.assertContains(robots_response, "Disallow: /admin/")
        self.assertContains(robots_response, "Disallow: /contact/thanks/")
        with override_settings(PUBLIC_DOMAIN="webstam.example"):
            sitemap_response = self.client.get(reverse("sitemap"))
            self.assertContains(sitemap_response, "https://webstam.example/services/django-python/")
            sitemap_xml = ET.fromstring(sitemap_response.content)
            self.assertEqual(sitemap_xml.tag, "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset")
            self.assertTrue(all(url.startswith("https://webstam.example/") for url in [node.text for node in sitemap_xml.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]))
            self.assertContains(self.client.get(reverse("robots")), "Sitemap: https://webstam.example/sitemap.xml")
        self.assertNotContains(self.client.get(reverse("robots")), "Sitemap:")

    def test_contact_confirmation_redirect_and_method_status(self):
        self.assertRedirects(self.client.get(reverse("contact:thanks")), reverse("contact:contact"), status_code=302)
        self.assertEqual(self.client.delete(reverse("contact:contact")).status_code, 405)

    def test_branded_server_error_handler_returns_http_500(self):
        from django.test import RequestFactory
        from .views import server_error
        response = server_error(RequestFactory().get("/"))
        self.assertEqual(response.status_code, 500)
        self.assertContains(response, "unexpected error", status_code=500)

    def test_csrf_trusted_origins_are_configurable(self):
        from django.conf import settings
        self.assertIsInstance(settings.CSRF_TRUSTED_ORIGINS, list)
    def test_service_pages_render_with_unique_heading_and_service_schema(self):
        for slug, data in SERVICE_PAGES.items():
            with self.subTest(service=slug):
                response = self.client.get(reverse("service-detail", kwargs={"slug": slug}))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, data["heading"])
                self.assertContains(response, '"@type": "Service"')
                self.assertContains(response, data["description"])
                if slug in {"django-python", "ai-machine-learning", "business-automation"}:
                    self.assertContains(response, "Who this helps")
                    self.assertContains(response, "Typical deliverables")

    def test_external_profiles_require_https_and_render_only_when_active(self):
        profile = ExternalProfile(owner="company", platform="GitHub", label="Webstam on GitHub", url="https://github.com/example")
        profile.full_clean()
        profile.save()
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Webstam on GitHub")
        self.assertContains(response, 'target="_blank" rel="noopener noreferrer"')
        profile.is_active = False
        profile.save()
        self.assertNotContains(self.client.get(reverse("home")), "Webstam on GitHub")
        with self.assertRaises(ValidationError):
            ExternalProfile(owner="company", platform="Bad", label="Bad link", url="http://example.com").full_clean()

    def test_case_studies_are_admin_managed_and_keep_project_identity(self):
        case = ProjectCaseStudy.objects.get(slug="agrilink")
        self.assertEqual(case.title, "AgriLink")
        case.content["summary"] = "Admin maintained summary for a verifiable project."
        case.save()
        response = self.client.get(reverse("project-detail", kwargs={"slug": "agrilink"}))
        self.assertContains(response, "Admin maintained summary for a verifiable project.")
        self.assertIn(ProjectCaseStudy, site._registry)

    def test_case_study_external_urls_require_https(self):
        case = ProjectCaseStudy(slug="invalid-demo", title="Invalid demo", content={"demo_url": "javascript:alert(1)"})
        with self.assertRaises(ValidationError):
            case.full_clean()

    def test_staff_only_dashboard_permissions_and_privacy(self):
        url = reverse("contact:dashboard")
        self.assertEqual(self.client.get(url).status_code, 302)
        staff = get_user_model().objects.create_user(username="dashboard-staff", password="test-only-password", is_staff=True)
        self.client.force_login(staff)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enquiry overview")
        self.assertNotContains(response, "ada@example.com")

    def test_analytics_is_optional_and_waits_for_consent(self):
        page = self.client.get(reverse("home"))
        self.assertNotContains(page, "data-analytics-consent")
        with override_settings(GA_MEASUREMENT_ID="G-TEST123456"):
            page = self.client.get(reverse("home"))
        self.assertContains(page, "data-analytics-consent")
        self.assertContains(page, "webstamAnalyticsId =")
        self.assertNotContains(page, "googletagmanager.com/gtag/js")
    def test_team_members_are_public_only_when_active(self):
        active = TeamMember.objects.create(full_name="Public Builder", slug="public-builder", role="Co-founder", short_bio="A public bio.", skills="Python", is_active=True, is_founder=True)
        TeamMember.objects.create(full_name="Private Builder", slug="private-builder", role="Developer", short_bio="Should remain private.", skills="Django", is_active=False)
        home = self.client.get(reverse("home"))
        team = self.client.get(reverse("team"))
        self.assertContains(home, active.full_name)
        self.assertNotContains(home, "Private Builder")
        self.assertContains(team, active.full_name)
        self.assertNotContains(team, "Private Builder")
    def test_founders_seeded_and_admin_registered(self):
        self.assertEqual(TeamMember.objects.filter(is_founder=True).count(), 2)
        self.assertIn(TeamMember, site._registry)
        self.assertRedirects(self.client.get(reverse("admin:core_teammember_changelist")), f"{reverse('admin:login')}?next={reverse('admin:core_teammember_changelist')}", fetch_redirect_response=False)
        staff = get_user_model().objects.create_superuser(username="team-admin", email="admin@example.test", password="test-only-password")
        self.client.force_login(staff)
        response = self.client.get(reverse("admin:core_teammember_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Charles Nguthu")
    def test_founder_profiles_have_unique_metadata_and_production_canonicals(self):
        profiles = [
            ("charles-nguthu", "Charles Nguthu | Python, Django & AI/ML Developer", "https://github.com/Ckhycharles", "https://charles-nguthu.netlify.app/"),
            ("hezron-njenga", "Hezron Njenga | Full-Stack, React & Flutter Developer", None, "https://hezron-njenga.vercel.app/"),
        ]
        titles, descriptions = set(), set()
        with override_settings(PUBLIC_DOMAIN="www.webstam.example"):
            for slug, expected_title, github, portfolio in profiles:
                response = self.client.get(reverse("team-profile", kwargs={"slug": slug}))
                self.assertEqual(response.status_code, 200)
                body = response.content.decode()
                title = unescape(re.search(r"<title>(.*?)</title>", body).group(1))
                description = re.search(r'<meta name="description" content="(.*?)">', body).group(1)
                titles.add(title)
                descriptions.add(description)
                self.assertEqual(title, expected_title)
                self.assertContains(response, f'<link rel="canonical" href="https://www.webstam.example/team/{slug}/">', html=True)
                self.assertContains(response, 'property="og:type" content="profile"')
                blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.S)
                schemas = [json.loads(block) for block in blocks]
                profile_schema = next(schema for schema in schemas if schema.get("@type") == "ProfilePage")
                person = profile_schema["mainEntity"]
                self.assertEqual(person["name"], "Charles Nguthu" if slug == "charles-nguthu" else "Hezron Njenga")
                self.assertEqual(person["url"], f"https://www.webstam.example/team/{slug}/")
                self.assertEqual(person["worksFor"]["@id"], "https://www.webstam.example/#organization")
                self.assertEqual(set(person["sameAs"]), {url for url in (github, portfolio) if url})
                self.assertContains(response, portfolio)
                if github:
                    self.assertContains(response, github)
                self.assertContains(response, f"/static/images/{'Charles-nguthu.jpeg' if slug == 'charles-nguthu' else 'hezron-njenga.jpeg'}")
                self.assertContains(response, "Portrait of " + person["name"])
                self.assertNotIn("noindex", body)
        self.assertEqual(len(titles), 2)
        self.assertEqual(len(descriptions), 2)
    def test_founder_profiles_link_to_relevant_case_studies(self):
        homepage = self.client.get(reverse("home"))
        self.assertContains(homepage, "https://hezron-njenga.vercel.app/")
        self.assertContains(homepage, "https://charles-nguthu.netlify.app/")
        self.assertContains(homepage, "/static/images/hezron-njenga.jpeg")
        self.assertContains(homepage, "/static/images/Charles-nguthu.jpeg")
        self.assertContains(homepage, reverse("team-profile", kwargs={"slug": "charles-nguthu"}))
        self.assertContains(homepage, reverse("team-profile", kwargs={"slug": "hezron-njenga"}))
        cases = {
            "charles-nguthu": ["graduate-documents", "onedrop-electronics"],
            "hezron-njenga": ["graduate-tracer"],
        }
        for founder, project_slugs in cases.items():
            response = self.client.get(reverse("team-profile", kwargs={"slug": founder}))
            self.assertEqual(response.status_code, 200)
            for project_slug in project_slugs:
                self.assertContains(response, reverse("project-detail", kwargs={"slug": project_slug}))
        for project_slug, founder in [("graduate-documents", "charles-nguthu"), ("graduate-tracer", "hezron-njenga"), ("onedrop-electronics", "charles-nguthu")]:
            response = self.client.get(reverse("project-detail", kwargs={"slug": project_slug}))
            self.assertContains(response, reverse("team-profile", kwargs={"slug": founder}))
    def test_graduate_tracer_lists_supplied_react_typescript_php_stack(self):
        response = self.client.get(reverse("project-detail", kwargs={"slug": "graduate-tracer"}))
        for technology in ("React", "TypeScript", "PHP"):
            self.assertContains(response, technology)
        self.assertNotContains(response, "technology stack</li>")
    def test_private_dashboard_is_not_indexable_and_excluded_from_robots(self):
        staff = get_user_model().objects.create_superuser(username="seo-staff", email="seo@example.test", password="test-only-password")
        self.client.force_login(staff)
        dashboard = self.client.get(reverse("contact:dashboard"))
        self.assertEqual(dashboard.status_code, 200)
        self.assertContains(dashboard, '<meta name="robots" content="noindex,follow">', html=True)
        self.assertContains(self.client.get(reverse("robots")), "Disallow: /contact/staff-dashboard/")
    @override_settings(DEBUG=False, PUBLIC_DOMAIN="", ALLOWED_HOSTS=["testserver"], SECURE_SSL_REDIRECT=False)
    def test_production_sitemap_is_disabled_until_real_domain_is_set(self):
        response = self.client.get(reverse("sitemap"))
        self.assertEqual(response.status_code, 503)
        self.assertContains(response, "PUBLIC_DOMAIN", status_code=503)
    def test_founder_profiles_are_only_public_when_active_and_listed_in_sitemap(self):
        with override_settings(PUBLIC_DOMAIN="webstam.example"):
            sitemap = self.client.get(reverse("sitemap"))
            for slug in ("charles-nguthu", "hezron-njenga"):
                profile_path = reverse("team-profile", kwargs={"slug": slug})
                self.assertContains(sitemap, f"https://webstam.example{profile_path}")
            hidden = TeamMember.objects.create(full_name="Hidden Founder", slug="hidden-founder", role="Co-founder", short_bio="Not public", skills="Python", is_founder=True, is_active=False)
            self.assertEqual(self.client.get(reverse("team-profile", kwargs={"slug": hidden.slug})).status_code, 404)
            sitemap = self.client.get(reverse("sitemap"))
            self.assertNotContains(sitemap, "hidden-founder")
    @override_settings(PUBLIC_DOMAIN="www.webstam.example")
    def test_production_canonical_and_jsonld(self):
        response = self.client.get(reverse("service-detail", kwargs={"slug": "django-python"}))
        self.assertContains(response, '<link rel="canonical" href="https://www.webstam.example/services/django-python/">', html=True)
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', response.content.decode(), re.S)
        schemas = [json.loads(block) for block in blocks]
        self.assertIn("Organization", [schema.get("@type") for schema in schemas])
        self.assertIn("Service", [schema.get("@type") for schema in schemas])
        self.assertIn("BreadcrumbList", [schema.get("@type") for schema in schemas])
        organization = next(schema for schema in schemas if schema.get("@type") == "Organization")
        self.assertEqual(organization["logo"]["url"], "https://www.webstam.example/static/images/webstam-share.png")
        self.assertNotIn("//static/", organization["logo"]["url"])
    def test_public_pages_have_title_description_and_canonical_when_configured(self):
        paths = [reverse("home"), reverse("services"), reverse("team"), reverse("contact:contact"), reverse("projects"), reverse("project-detail", kwargs={"slug": "graduate-documents"})]
        with override_settings(PUBLIC_DOMAIN="webstam.example"):
            for path in paths:
                with self.subTest(path=path):
                    response = self.client.get(path)
                    body = response.content.decode()
                    self.assertEqual(response.status_code, 200)
                    self.assertRegex(body, r"<title>[^<]+</title>")
                    self.assertRegex(body, r'<meta name="description" content="[^"]+">')
                    self.assertRegex(body, r'<link rel="canonical" href="https://webstam\.example')
    def test_private_success_page_is_noindex(self):
        response = self.client.get(reverse("contact:thanks"))
        self.assertRedirects(response, reverse("contact:contact"))
        from django.test import Client
        client = Client()
        session = client.session
        session["inquiry_saved"] = True
        session.save()
        response = client.get(reverse("contact:thanks"))
        self.assertContains(response, 'name="robots" content="noindex,follow"')

    def test_privacy_notice_is_noindex_and_not_in_sitemap(self):
        response = self.client.get(reverse("privacy"))
        self.assertContains(response, 'name="robots" content="noindex,follow"')
        with override_settings(PUBLIC_DOMAIN="testserver"):
            self.assertNotContains(self.client.get(reverse("sitemap")), reverse("privacy"))

    def test_public_pages_emit_single_canonical_and_valid_jsonld(self):
        with override_settings(PUBLIC_DOMAIN="www.webstam.example"):
            for path in [reverse("home"), reverse("services"), reverse("projects"), reverse("about"), reverse("team"), reverse("contact:contact"), reverse("project-detail", kwargs={"slug": "graduate-documents"})]:
                with self.subTest(path=path):
                    response = self.client.get(path)
                    body = response.content.decode()
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(len(re.findall(r'<link rel="canonical"', body)), 1)
                    self.assertNotIn('name="robots" content="noindex,follow"', body)
                    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.S):
                        json.loads(block)
    def test_profile_image_rejects_non_image_upload(self):
        upload = SimpleUploadedFile("bad.jpg", b"not really an image", content_type="image/jpeg")
        with self.assertRaises(ValidationError):
            validate_profile_image(upload)
    def test_profile_image_accepts_valid_small_png(self):
        image_data = BytesIO()
        Image.new("RGB", (12, 12), "teal").save(image_data, format="PNG")
        upload = SimpleUploadedFile("founder.png", image_data.getvalue(), content_type="image/png")
        validate_profile_image(upload)
    def test_profile_upload_generates_responsive_webp_variants(self):
        image_data = BytesIO()
        Image.new("RGB", (1200, 900), "teal").save(image_data, format="JPEG")
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            member = TeamMember.objects.create(full_name="Image Profile", slug="image-profile", role="Co-founder", short_bio="Bio.", skills="Python", profile_photo=SimpleUploadedFile("portrait.jpg", image_data.getvalue(), content_type="image/jpeg"))
            self.assertTrue(member.profile_photo.url.startswith("/media/team/"))
            self.assertTrue(member.profile_photo_360.name.endswith(".webp"))
            self.assertTrue(member.profile_photo_720.name.endswith(".webp"))
            with member.profile_photo_360.open("rb") as variant_file:
                with Image.open(variant_file) as variant:
                    self.assertEqual(variant.format, "WEBP")
                    self.assertEqual(variant.width, 360)

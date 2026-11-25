import json
from html.parser import HTMLParser
from urllib.parse import urlsplit

from django.conf import settings
from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse

from core.models import TeamMember
from core.projects import PROJECTS
from core.service_pages import SERVICE_PAGES


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.canonicals = []
        self.h1 = 0
        self.schemas = []
        self.links = []
        self._title = False
        self._jsonld = False
        self._script = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._title = True
        if tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content", "")
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href", ""))
        if tag == "h1":
            self.h1 += 1
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self._jsonld, self._script = True, []

    def handle_endtag(self, tag):
        if tag == "title":
            self._title = False
        if tag == "script" and self._jsonld:
            try:
                self.schemas.append(json.loads("".join(self._script)))
            except json.JSONDecodeError as exc:
                self.schemas.append({"_error": str(exc)})
            self._jsonld = False

    def handle_data(self, data):
        if self._title:
            self.title += data
        if self._jsonld:
            self._script.append(data)


class Command(BaseCommand):
    help = "Audit public routes for crawlability, metadata, canonical URLs, and JSON-LD."

    def handle(self, *args, **options):
        routes = ["home", "services", "solutions", "projects", "about", "team", "technologies", "ai-automation", "contact:contact"]
        urls = [reverse(name) for name in routes]
        urls += [reverse("service-detail", kwargs={"slug": slug}) for slug in SERVICE_PAGES]
        urls += [reverse("project-detail", kwargs={"slug": item["slug"]}) for item in PROJECTS]
        urls += [reverse("team-profile", kwargs={"slug": slug}) for slug in TeamMember.objects.filter(is_active=True, is_founder=True).values_list("slug", flat=True)]
        audit_host = settings.PUBLIC_DOMAIN or next((host for host in settings.ALLOWED_HOSTS if host not in {"*", ".localhost"}), "localhost")
        client = Client(HTTP_HOST=audit_host)
        findings = []
        internal_link_issues = set()
        for url in urls:
            response = client.get(url)
            parser = PageParser()
            parser.feed(response.content.decode(response.charset or "utf-8", errors="replace"))
            checks = [
                (response.status_code == 200, "fail", "Public route must return HTTP 200"),
                (bool(parser.title.strip()), "fail", "Missing page title"),
                (bool(parser.description.strip()), "fail", "Missing meta description"),
                (len(parser.canonicals) == 1, "fail", "Expected exactly one canonical link (configure PUBLIC_DOMAIN for production canonicals)"),
                (parser.h1 == 1, "warning", f"Expected one H1; found {parser.h1}"),
                (not any("_error" in schema for schema in parser.schemas), "fail", "Malformed JSON-LD"),
            ]
            for passed, severity, message in checks:
                if not passed:
                    findings.append({"url": url, "severity": severity, "result": severity, "message": message})
            for href in parser.links:
                parsed = urlsplit(href)
                if parsed.scheme or parsed.netloc or not parsed.path.startswith("/"):
                    continue
                target = parsed.path + (f"?{parsed.query}" if parsed.query else "")
                link_response = client.get(target, follow=False)
                if link_response.status_code == 404:
                    internal_link_issues.add((url, href, "broken internal link (404)"))
                elif 300 <= link_response.status_code < 400:
                    internal_link_issues.add((url, href, f"internal link redirects ({link_response.status_code})"))

        for source, href, message in sorted(internal_link_issues):
            findings.append({"url": source, "severity": "warning", "result": "warning", "message": f"{message}: {href}"})

        route_failures = [item for item in findings if item["severity"] == "fail"]
        status_failures = sum("HTTP 200" in item["message"] for item in route_failures)
        canonical_failures = sum("canonical" in item["message"].lower() for item in route_failures)
        metadata_failures = sum("title" in item["message"].lower() or "description" in item["message"].lower() or "H1" in item["message"] for item in findings)
        schema_failures = sum("JSON-LD" in item["message"] for item in route_failures)
        link_issues = sum("internal link" in item["message"] for item in findings)
        category_rows = [
            ("Crawlability and indexability", 15, max(0, 15 - status_failures), "Routes/status tested; external crawler access not measured"),
            ("Canonicalization and redirects", 10, max(0, 10 - canonical_failures), "Canonical count tested; host-level redirects not measured"),
            ("On-page SEO", 10, max(0, 10 - metadata_failures), "Title, description, and H1 tested"),
            ("Structured data", 10, max(0, 10 - schema_failures), "Rendered JSON-LD syntax tested; external eligibility not measured"),
            ("Internal links", 10, max(0, 10 - min(10, link_issues)), "Rendered root-relative links checked for 404s and redirects; external links not checked"),
            ("Mobile and accessibility", 10, 0, "Not measured by this command"),
            ("Performance", 15, 0, "Field Core Web Vitals and Lighthouse not measured"),
            ("Security and HTTPS", 10, 0, "Django settings inspected; deployed TLS and headers not measured"),
            ("Content quality", 5, 0, "Human editorial review required"),
            ("Monitoring readiness", 5, 0, "Search Console connection not measured"),
        ]
        automated_score = sum(earned for _, _, earned, _ in category_rows)
        self.stdout.write(f"SEO health score: {automated_score}/100 (automated local evidence only; unmeasured categories receive 0)")
        self.stdout.write(f"Routes checked: {len(urls)}; findings: {len(findings)}")
        for name, weight, earned, evidence in category_rows:
            self.stdout.write(f"- {name}: {earned}/{weight}; {evidence}")
        for finding in findings:
            self.stdout.write(self.style.WARNING(f"{finding['severity'].upper()} {finding['url']}: {finding['message']}"))
        if not findings:
            self.stdout.write(self.style.SUCCESS("No route-level metadata or JSON-LD failures found."))

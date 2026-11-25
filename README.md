# Webstam Technologies

A server-rendered Django website for Webstam Technologies. It presents the company's software, AI, and automation capabilities, four evidence-aware project case studies, project inquiry handling, and admin-managed founder profiles.

## Stack and requirements

- Python 3.11+
- Django templates and forms, SQLite for local development, PostgreSQL through `DATABASE_URL` in production
- Plain HTML, Tailwind CSS 4 build output, custom CSS, and vanilla JavaScript
- WhiteNoise and Gunicorn for conventional production hosting
- Pillow for validated founder image uploads and local WebP asset generation
- Node.js/npm only when rebuilding Tailwind CSS

The production CSS is committed, so running the Django site does not require Node. The public site has no frontend framework, tracking script, or external font request.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. Load `.env` into a Unix shell with `set -a; source .env; set +a` before starting Django, or set the variables in your terminal or hosting environment. The local SQLite database is created at `db.sqlite3`. The seed migration creates the two supplied founder profiles. Their supplied repository portraits are served from `static/images/`; verified profile URLs are maintained through **Django admin → Core → External profiles**.

Create an admin account when you need to manage inquiries or team profiles:

```bash
python manage.py createsuperuser
```

## Tailwind CSS

The compiled stylesheet is committed. When changing Tailwind utility classes in templates, rebuild it with:

```bash
npm install
npm run build:css
```

Custom site-specific styles are in `static/css/site.css`; generated Tailwind utilities are in `static/css/tailwind.css`. Avoid dynamically composing utility class names that the build scanner cannot see.

## Main routes

- `/` homepage
- `/services/` service directory
- `/services/django-python/`, `/services/ai-machine-learning/`, `/services/business-automation/`, `/services/ecommerce-development/`, `/services/frontend-react/`, `/services/mobile-app-development/`
- `/solutions/`, `/projects/`, and `/projects/<slug>/` case studies
- `/about/`, `/team/`, `/technologies/`, `/ai-automation/`, `/contact/`, `/privacy/`
- `/sitemap.xml` and `/robots.txt`
- `/admin/` restricted staff administration

Portfolio entries use admin-managed `ProjectCaseStudy` records and one reusable case-study template. The initial migration seeds AgriLink, Graduate Documents Submission and Approval Management System, Graduate Tracer, and OneDrop Electronics Shop with their supplied verification notes. Manage them in **Django admin → Core → Project case studies**. Edit the structured `content` JSON alongside title/status/visibility. Preserve keys such as `summary`, `problem`, `solution`, `features`, `technologies`, `developer`, `attribution_note`, `status_note`, `screenshots`, `demo_url`, `source_url`, and `related`; list fields are JSON arrays. Keep outcomes, attribution, technologies, demos, source links, and screenshots evidence-based; blank URLs remain unpublished. `core/projects.py` is the migration seed and fallback data.

## Contact inquiries

The contact form validates and saves submissions in the `Inquiry` database model. It includes optional phone, organization, budget, timeline, and contact preference fields; consent is required and its confirmation timestamp is recorded. Budget options are maintained in **Django admin → Contact → Budget bands**; seeded bands currently use USD labels and should be confirmed or adjusted before launch. A honeypot and cache-backed five submissions per IP per hour limit provide basic abuse mitigation. Configure a shared cache in production to share limits across workers. Campaign labels are length-limited and URL-safe, held in the existing session, and associated only when an enquiry is submitted. Authorized staff can review status, internal notes, and attribution in Django admin. `/contact/staff-dashboard/` summarizes counts and is staff-only. Email is optional; when configured, the site reports a notification was sent only after Django's send operation succeeds. Notification email content omits the enquiry body, and submission content is not written to application logs.

Set `COMPANY_EMAIL` and `COMPANY_PHONE` only when approved public details are available. Set `CONTACT_RECIPIENT` and SMTP settings to enable notifications. These public details are blank by default.

## Founder profiles and media

Manage profiles in **Django admin → Core → Team members**. Only active profiles are shown publicly. Staff can edit biographies, role, skills, areas of responsibility, verified project contributions, ordering, and visibility. Manage official company and founder URLs centrally in **Django admin → Core → External profiles**. Charles's verified GitHub and portfolio links and Hezron's verified portfolio link are published. No LinkedIn URLs or company social profiles are configured. The supplied portraits are `static/images/Charles-nguthu.jpeg` and `static/images/hezron-njenga.jpeg`; the latter is a tall portrait and is contained without stretching in profile cards. Both are collected with the rest of the static assets. The supplied Hezron photograph includes a visible “Tish” watermark; confirm usage rights and whether to publish it as-is or supply an approved clean image.

Profile uploads accept JPEG, PNG, or WebP images up to 4 MB and 3000 × 3000 pixels. Django/Pillow validate the actual image content, and upload paths use random identifiers. Saving a founder portrait also creates width-limited 360 px and 720 px WebP variants for responsive display while retaining the uploaded original. In local development, uploads are served from `MEDIA_ROOT` (default `media/`). For production, configure `MEDIA_ROOT` on durable persistent storage or add a compatible object-storage backend. Do not rely on an ephemeral container filesystem for uploaded portraits. Keep uploaded content public only when it is intended for public display.

## SEO and international setup

Read [the SEO and content plan](docs/seo-plan.md) for page-to-search-intent mapping, Search Console setup, and future knowledge-center topics. The site serves English-language pages internationally without implying offices in unverified countries. It has no translations and therefore emits no hreflang annotations.

At production launch:

1. Set `PUBLIC_DOMAIN` to the verified public hostname only, such as `www.example.com` (no scheme or trailing slash). Canonicals and sitemap links then use HTTPS.
2. Confirm the domain resolves to the deployment, TLS is active, and `DJANGO_ALLOWED_HOSTS` contains only appropriate hostnames.
3. Open `https://<domain>/robots.txt` and `https://<domain>/sitemap.xml` and inspect the homepage, a service page, a case study, `/team/`, and `/contact/` in Google Search Console.
4. Verify the domain property using a method available in Search Console and submit the sitemap. No verification token is included in the source.
5. Monitor indexed pages, crawl errors, canonical selection, search query impressions and clicks, and mobile/desktop field performance. Technical SEO establishes crawlable pages; rankings and indexing are not guaranteed.

The generated sitemap contains public pages, service detail pages, case studies, and active founder profiles. It excludes the admin and contact confirmation routes. Each founder profile has a self-canonical URL and `ProfilePage`/`Person` JSON-LD that references the company's stable `Organization` entity. Founder visibility, biographies, skills, SEO titles/descriptions, and uploaded photos are managed in **Core → Team members**. Official URLs are maintained separately in **Core → External profiles**. Inactive founders return 404 and are omitted from the sitemap. No LinkedIn URL is configured.

Add only confirmed profile links through **External profiles**. Inactive profiles are omitted from page links and structured data. Add genuine founder photographs using the admin image fields; no generated portraits are used. Ensure uploaded media is stored persistently and served over HTTPS in production.

Analytics is optional and remains unloaded unless `GA_MEASUREMENT_ID` is configured and the visitor accepts the site's analytics choice. It sends page views without query strings, successful enquiry events, consultation CTA clicks, and outbound profile clicks; no form contents or personal details are sent. Verify a real property before calling it connected. See [client acquisition setup](docs/client-acquisition-setup.md) for analytics and Search Console onboarding, platform profile checklists, attribution operations, and outstanding founder inputs. No Search Console verification token is included.

## Checks

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py collectstatic --noinput
node --check static/js/site.js
npm run build:css
python manage.py audit_seo
```

`collectstatic` writes to `staticfiles/`. WhiteNoise serves compressed, manifest-versioned assets in production. The homepage illustration is CSS/HTML; below-the-fold OneDrop product imagery has responsive WebP variants and explicit dimensions. No public deployment was available for Lighthouse or PageSpeed field measurement, so real-world Core Web Vitals must be reviewed after launch.

`audit_seo` checks public route responses, rendered titles/descriptions, canonical counts, H1 counts, and JSON-LD syntax. It prints evidence and a deliberately limited local score: unmeasured external, visual, field, and editorial categories receive no points. It is not an official search-engine score. See [the content audit](docs/content-audit.md) for page-level editorial status.

## Production deployment

1. Set `DJANGO_DEBUG=false`, a strong random `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `PUBLIC_DOMAIN`, and `DJANGO_CSRF_TRUSTED_ORIGINS` when legitimate cross-origin HTTPS form submissions require it. The latter is a comma-separated list of full origins such as `https://www.example.com`; leave it empty when same-origin submissions are used.
2. Set `DJANGO_ENV=production` and `DJANGO_DEBUG=false`. Set `DATABASE_URL` to the PostgreSQL internal connection URL copied from Render Dashboard → database → Connect/Info. Use the internal URL when the web service and database are in the same Render region. Configure the URL only in the Render web service environment; never put credentials in source or `render.yaml`. Production fails at startup when the URL is missing or malformed and will not fall back to SQLite. Connections use psycopg 3, a 60-second max age, connection health checks, and SSL required in production.
3. Configure durable `MEDIA_ROOT` storage for uploaded profile photos and configure the reverse proxy/web server to serve `MEDIA_URL`, or use a maintained Django object-storage backend. Keep cloud credentials in environment variables. Django does not expose uploaded media URLs publicly in production by default.
4. Set `COMPANY_EMAIL`, `COMPANY_PHONE`, and any profile/contact URLs only after they are approved. Configure `CONTACT_RECIPIENT`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, and `DEFAULT_FROM_EMAIL` if notifications are required.
5. Install Python dependencies, run `python manage.py migrate`, then `python manage.py collectstatic --noinput`.
6. Run `gunicorn config.wsgi:application` behind an HTTPS reverse proxy. WhiteNoise serves static files. If that trusted proxy terminates TLS and sets/overwrites `X-Forwarded-Proto`, set `TRUST_X_FORWARDED_PROTO=true`; do not trust this header when clients can provide it directly. Secure cookies, SSL redirect, and HSTS are environment-aware; subdomain HSTS and preload are disabled by default and should only be enabled when every affected hostname is HTTPS-ready.
7. Create a staff superuser through a secure one-off command. Restrict admin access and back up the database and persistent media.

SQLite is used only outside production when `DATABASE_URL` is unset. Local PostgreSQL can be selected by setting `DATABASE_URL` to a local connection URL; no credentials are embedded in this repository. Render PostgreSQL is configured through its Dashboard environment interface, and no `render.yaml` is present or needed for this existing service. Review security, privacy, backup, media persistence, email delivery, and domain configuration before launch.

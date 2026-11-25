# Client acquisition and profile setup

This checklist prepares Webstam's owned profiles and site integrations. Use accurate current information and only link accounts the founders control. Do not describe an account as verified, certified, highly rated, or featured unless the platform confirms it.

## LinkedIn

- Agree on a clear, factual headline and concise About section for each founder.
- Create or complete the Webstam Technologies company page and keep its name and website URL consistent with the website.
- List services and specialties the team can demonstrate (Django/Python software, carefully scoped AI integration, and Python/API workflow automation).
- Link relevant case studies and repositories; label academic work, prototypes, and unverified deployments accurately.
- Publish useful technical notes and case studies when there is new evidence or a useful lesson to share.
- Add each public LinkedIn URL in Django admin → Core → External profiles only after confirming the destination and account ownership.

## GitHub

- Add accurate founder and organization descriptions plus the verified website URL.
- Pin repositories that are useful to prospective clients and explain their status, role, and limitations.
- Give repositories clear descriptions, topics, setup instructions, and useful READMEs.
- Add genuine screenshots, architecture diagrams, or demo links when supplied and cleared for publication.
- State licensing and contribution information where appropriate.
- Review repository history and current files for secrets, credentials, personal data, and sensitive configuration before linking or publishing.
- Add verified profile, organization, and repository destinations in **Core → External profiles** only when the destination is public and appropriate.

## Upwork

- Maintain one well-structured primary profile with relevant truthful skills and portfolio examples.
- Describe deliverables and responsibilities clearly; tailor proposals to each job rather than sending generic claims.
- Link to the appropriate public case study and keep profile details consistent with Webstam's site.
- Do not create Specialized Profiles: Upwork discontinued them on May 28, 2026. Its [official update](https://support.upwork.com/hc/en-us/articles/115013750068-Update-to-Specialized-Profiles-What-to-know) says the main profile dynamically highlights relevant skills and work.
- Add an Upwork link to the site only after the team supplies and verifies its public profile URL.

## Fiverr

- Create clearly scoped gigs with accurate titles, descriptions, packages, tags, samples, FAQs, and realistic delivery expectations.
- Use professional, genuine gig images and portfolio samples the team has permission to share.
- Explain assumptions and exclusions; do not imply outcomes that have not been demonstrated.
- Tags can help describe a gig but do not guarantee ranking.
- Add public profile or gig URLs to the site only after the founders verify them.

## Clutch and B2B directories

- Keep company name, services, location, and contact details accurate and consistent.
- Choose only service categories the team genuinely offers.
- Use honest project descriptions and identify academic or prototype work.
- Request references and reviews only from real clients who consent; do not fabricate reviews or client outcomes.
- Clutch offers a [free company profile](https://clutch.co/get-listed); paid upgrades are optional and should be evaluated separately.

## Google Business Profile eligibility

- Check eligibility before creating or recommending a profile. Google requires eligible businesses to make in-person contact with customers during stated hours and excludes online-only businesses. Review [Google's eligibility guidance](https://support.google.com/business/answer/13763036).
- Do not use a virtual office or an address that does not meet Google's rules.
- If Webstam does not qualify, prioritize organic search, genuine professional profiles, and suitable B2B directories instead.

## Website profile-link maintenance

1. A staff member opens **Django admin → Core → External profiles**.
2. Add one row per owner and platform. Use a direct HTTPS public destination, a human-readable label, and an active state only after verification.
3. Review links quarterly and deactivate changed, inaccessible, or no-longer-controlled accounts.
4. Blank or inactive profiles are omitted from public pages and structured data. The site does not claim platform verification.

The site publishes the supplied portraits for Charles Nguthu and Hezron Njenga, Charles's supplied GitHub and portfolio destinations, and Hezron's supplied portfolio destination. No LinkedIn, company social, Upwork, Fiverr, or directory links are configured. Confirm founder approval for public photo display before release.

## Analytics and Search Console

- Google Analytics is optional. Set `GA_MEASUREMENT_ID` to a real `G-...` measurement ID only after the founders create/verify the property and decide that the site's consent approach is suitable. No ID is included in source control. Visitors must accept analytics before the Google script loads; Decline keeps it unloaded.
- The site sends page views without query strings, successful enquiry events after the server-side saved-inquiry flow, consultation CTA clicks, and outbound profile clicks. It does not pass enquiry contents or identity fields to analytics. Verify events in the real property before claiming the integration is connected.
- Verify the real production domain in Google Search Console using an approved method, submit `/sitemap.xml`, and inspect service pages, case studies, founder profiles, and mobile rendering. Do not commit verification tokens. Search Console is not connected by source code alone.
- The `GA_MEASUREMENT_ID` setting is optional and analytics remains unloaded if absent.

## Enquiries and attribution operations

- `/contact/staff-dashboard/` and Django admin are staff-only. The dashboard reports enquiry counts, service, source, status, and daily totals over the last 90 days. Counts are not revenue.
- Attribution values are short, URL-safe UTM labels held in the existing Django session until enquiry submission. They do not identify a platform as verified. No UTM data is required to submit.
- The cache-based rate limit allows five accepted submissions per IP per hour. Configure a shared Django cache such as Redis for consistent limits across multiple production workers; default local-memory cache is per process. The limiter uses `REMOTE_ADDR` by default. If the deployment requires a forwarded client-IP header, set `RATE_LIMIT_IP_HEADER` only when a trusted proxy overwrites and sanitizes that header; never trust a client-supplied forwarded value.
- Enquiries can be reviewed and status updated in **Django admin → Contact → Inquiries**. Internal notes are staff-only. Record only information needed for review.
- No automatic retention period is configured. Define one with the founders before launch. Staff can delete enquiry rows in Django admin; separately expire database backups under the hosting backup policy. See the public Privacy notice.

## Inputs still needed from the founders

- Confirm founder approval for public display of the supplied portraits and profile destinations.
- Confirm the inquiry budget ranges and currency; the seeded optional bands currently use USD labels and can be edited in Django admin.
- Supply verified LinkedIn, GitHub (including organization/repository), Upwork, Fiverr, and directory URLs that should appear publicly.
- Supply genuine founder portraits and any project screenshots, diagrams, public repositories, or demos approved for publication.
- Confirm biographies, responsibilities, project attribution, and the current status of all four case studies.
- Set a retention schedule and review the privacy notice against the organization's applicable obligations.
- Supply a real GA measurement ID and Search Console verification only if those accounts are created and the team wants them connected.
- Configure the production cache, email recipient, SMTP, domain, and a PostgreSQL `DATABASE_URL` where appropriate.

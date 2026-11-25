# Public content audit

This audit reflects repository inspection on 2026-10-20. Public routes are Django server-rendered and content is maintained in templates, `core/service_pages.py`, `core/projects.py`, and active `TeamMember` records.

| URL | Severity | Finding | Recommended action | Status |
|---|---|---|---|---|
| `/` | Low | Homepage contains the main service and portfolio discovery links; founder/project sections depend on seeded or active database profiles. | Keep; review links and profile accuracy when updating the portfolio. | Implemented |
| `/services/` and `/services/<slug>/` | Medium | Service pages describe capabilities and practical limits. Project associations are present for some services; other services have no verified case study. | Keep and improve with accurate examples as evidence becomes available; do not add unsupported outcomes. | Existing content retained |
| `/projects/agrilink/` | Medium | Backend implementation is documented; frontend, deployment, and individual contributor attribution are explicitly unverified. | Keep with current qualification; update only after source/deployment evidence. | Existing content retained |
| `/projects/graduate-documents/` | Medium | Application workflow and Charles Nguthu attribution are described from available project information; deployment/adoption are unverified. | Keep; verify any future outcome or institution claims before publication. | Existing content retained |
| `/projects/graduate-tracer/` | Medium | Supplied project information identifies React, TypeScript, and PHP; source implementation, detailed feature flows, and deployment remain unverified. | Keep the supplied stack visible and implementation status qualified; enrich only with reviewed source evidence. | Updated |
| `/projects/onedrop-electronics/` | Medium | Django shop implementation is described; recommender model, React source, and deployment are explicitly unverified. | Keep with these limitations visible; verify against intended repository before adding claims. | Existing content retained |
| `/about/`, `/team/`, `/team/<slug>/` | Medium | Founder bios, responsibilities, skills, and public profile links are editable database content; supplied founder portraits and verified portfolio links are used. | Keep; confirm biographies and founder approval for public profile display. Only active founders are public/indexed. | Updated |
| `/privacy/` | Low | Necessary utility content should remain accessible, but does not need search-result placement. | Keep accessible and mark `noindex`; omit from sitemap. | Implemented |
| `/contact/thanks/` | Low | Session-gated confirmation page should not be indexed. | Keep session gate and `noindex`; omit from sitemap. | Existing behavior retained |
| `/contact/staff-dashboard/` | Medium | Authenticated operational enquiry data must not be indexed. | Preserve staff authorization, add `noindex`, and exclude from robots guidance and sitemap. | Updated |

No blog/article routes, placeholder articles, customer reviews, ratings, office addresses, or search performance claims were found. Search Console, deployed response behavior, real-user performance, and external link validity require production access or human review.

## Automated audit baseline

The local `python manage.py audit_seo` run checked 21 intended public URLs. All returned HTTP 200 with page titles, descriptions, one H1, parseable JSON-LD, and no rendered root-relative links to 404s or redirects. It reported canonical failures for all 21 because `PUBLIC_DOMAIN` is unset in this checkout. In production, the sitemap now returns HTTP 503 until a real `PUBLIC_DOMAIN` is configured, preventing Django's default `example.com` host from appearing in sitemap URLs. Production canonicals and sitemap output must still be verified after the actual hostname is configured. The command's limited score is local evidence only, not a Google score.

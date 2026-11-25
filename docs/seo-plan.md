# International SEO and content plan

The site is English-first and intended for relevant international inquiries. It does not imply a local office or legal presence outside the locations actually established by the company. No translated versions exist, so the templates emit no `hreflang` annotations. If translations are added, create equivalent language URLs with reciprocal language codes, self-canonicals, and an appropriate `x-default` only when there is a real default destination.

## Search intent and primary destination

| Search intent | Primary page | Notes |
|---|---|---|
| Software development company, custom software, business applications | `/` and `/services/` | Company overview and service directory; homepage addresses the broad intent naturally. |
| Django/Python development, backend, REST APIs, database integration | `/services/django-python/` | Application and API focus; related graduate workflow case study. |
| AI development, machine learning, predictive analytics | `/services/ai-machine-learning/` | Emphasizes suitability, model evaluation, and limitations. |
| Business process automation and approval workflows | `/services/business-automation/` | Related graduate document workflow case study. |
| E-commerce website development, online stores | `/services/ecommerce-development/` | Related OneDrop case study, with implementation caveats. |
| React/frontend development | `/services/frontend-react/` | Capability page; does not claim the current company site uses React. |
| Flutter/mobile applications | `/services/mobile-app-development/` | Capability page based on the supplied team skill set. |
| Agricultural technology software | `/solutions/` and `/projects/agrilink/` | AgriLink implementation and contributor details are explicitly bounded by available evidence. |
| Graduate document approval workflow software | `/projects/graduate-documents/` | Case study describes repository-verified workflow features and no institutional adoption claim. |
| Alumni and graduate employment tracking | `/projects/graduate-tracer/` | Project relationship is supplied; implementation details are not yet verified. |
| E-commerce recommendations | `/projects/onedrop-electronics/` | Recommendation model, method, frontend, and deployment are not verified in the available source. |

Each focused service page has a distinct title, description, H1, use cases, capabilities, FAQs, related projects when relevant, and an inquiry action. Do not create country-swapped duplicates. Keep page copy useful, specific, and evidence-based; search terms above are research directions, not text to repeat verbatim.

## Technical implementation

- Production canonical URLs and sitemap URLs use `PUBLIC_DOMAIN` as a hostname and HTTPS. Leave it unset locally; configure the actual public hostname at launch.
- `robots.txt` permits public pages and leaves static assets crawlable while excluding admin and the form confirmation page.
- The sitemap includes public pages, focused service pages, and portfolio case studies only. It omits admin and confirmation routes.
- Organization, WebSite, Service, BreadcrumbList, and Person JSON-LD use known facts only. Project-specific assertions remain on case-study pages as text rather than broad structured claims.
- No noindex directive is applied to public content. The contact confirmation is noindex and is not in the sitemap.
- No Analytics or Search Console token is shipped. Social metadata uses a locally generated, brand-specific share image.

## Search Console and measurement checklist

After the real domain is deployed:

1. Verify the domain property in Google Search Console using DNS, or verify the URL-prefix property using a supported method. Keep verification values in deployment configuration; do not commit them or invent a token.
2. Submit `https://<configured-domain>/sitemap.xml` and confirm Google can fetch it.
3. Inspect the homepage, one important service page, one case study, `/team/`, and `/contact/` with URL Inspection. Check canonical selection, rendered HTML, and indexing eligibility.
4. Review indexing and crawl reports for excluded or error URLs. Investigate unexpected duplicates, redirects, and crawl failures.
5. Review search queries, impressions, clicks, and click-through rates by page and intent. Improve pages based on relevant visits and inquiry quality, not keyword counts alone.
6. Track service-page inquiry clicks and successful project inquiries only after selecting an analytics approach and implementing any required privacy notice and consent. Analytics remains optional and is not loaded by this website by default.
7. Review mobile and desktop field performance in Search Console's Core Web Vitals report and PageSpeed Insights. Lab results are diagnostic; field data reflects real visits.

Technical SEO makes pages crawlable and understandable; it does not guarantee indexing, rankings, or a position in search or answer engines. Search visibility develops through useful content, appropriate technical maintenance, and measurement over time.

## Future knowledge center topics

Publish an article only when it has a clear purpose, a human review, and accurate examples. Useful future topics include:

- When Django is a suitable choice for a business application
- Custom software compared with off-the-shelf tools
- Mapping a business process before automating it
- Practical AI use cases and limits for small organizations
- How recommendation approaches differ and what data they need
- Designing a graduate document submission and approval workflow
- How digital tools can support agricultural work
- Choosing between a mobile application and a responsive web product
- Database modeling for a business workflow
- Integrating APIs across existing systems

No placeholder articles, publication dates, authors, or credentials have been created. A blog can be added when reviewed material is ready.

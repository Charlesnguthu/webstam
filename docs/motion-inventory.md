# Webstam motion inventory

Motion is progressive enhancement over the server-rendered page. `static/js/motion.js` applies reveal attributes only when JavaScript and IntersectionObserver are available; CSS leaves all content visible otherwise. The persistent Motion control and `prefers-reduced-motion` remove nonessential movement. The hero canvas pauses offscreen and when the tab is hidden, caps device pixel ratio, and uses fewer nodes on mobile. No animation dependency or third-party runtime is used.

| Page / section | Motion and trigger | Mobile behavior | Reduced-motion / performance behavior |
|---|---|---|---|
| Shared first visit | Short, once-per-session SVG mark draw and progress line on load | Same short reveal | Skipped |
| Header and navigation | Glass treatment on scroll; logo path and active underline on hover/focus; animated menu icon and staggered drawer on click | Drawer is focus-contained, Escape closes it, touch does not use magnetic effects | Transitions removed; content and route links remain ordinary HTML |
| All pages | Scroll progress; native cross-document View Transition where supported; varied observer reveals | Same observer reveals with shorter hero density | Static content; no forced navigation or JS link interception |
| Home hero | Staggered copy, gradient headline, CSS orbit/core and diagram modules, canvas network, desktop pointer parallax | Reduced-density canvas and smaller diagram; no pointer-follow required | Canvas and shimmer disabled; text uses solid brand colors |
| Home capabilities and services | Service cards stagger and respond to pointer light/hover; icon and arrow feedback | Tap-accessible links; no tilt or hover-only content | Static cards |
| Home work and case studies | Portfolio cards use scale reveals, visual saturation and lift; case study sections and assets reveal in sequence | Normal single-column card flow | No reveal mask or movement |
| Home approach, process and workflow | Alternating left/right principles; process steps draw a top accent; workflow connectors glow | Natural document scrolling, no pinning | Static process and workflow remain complete |
| Technology pages and home technology strip | Technology groups stagger and lift; tags respond to hover | No hover dependency | Static, no proficiency values are animated |
| About and team | Values and founder cards stagger; genuine supplied portraits receive a restrained image zoom | Portrait sizing and normal flow retained | Static images and biographies |
| Services and service detail | Detail cards, service copy and inquiry panel enter from distinct directions; native FAQs animate when opened | Sticky panel becomes static per existing layout | FAQ native disclosure remains functional |
| Projects listing and project detail | Project cards, case-study artwork, content sections, related-project links and aside reveal in staggered groups | Existing responsive layout; all links remain direct | Static case-study text and images |
| Contact, thanks and privacy | Contact aside/form enter separately; input focus ring; real form submission disables duplicate submission while request navigates; confirmation content reveals | Same controls and existing one-column form | No loading animation or automatic CTA; server validation remains authoritative |
| Shared CTA and footer | CTA ambient ring; footer divider sweeps; content reveals on scroll | Ambient loop disabled on smaller screens | Static divider and ordinary footer links |

## Validation notes

The home page has the only continuously animated graphic: a lightweight Canvas 2D connected-node field with a deterministic lifecycle (intersection and visibility pause). Other motion is event-triggered or CSS transitions. CSS transitions primarily use transform and opacity. The system does not add fabricated data, autoplay media, pinned scroll sections, or 3D/WebGL dependencies.

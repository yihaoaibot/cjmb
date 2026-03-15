# cjmb Frontend Redesign Spec (Astro)

## Goal
Upgrade the current static HTML feed into an Astro-based content site with better visual quality, light/dark theme support, and more product-like feed presentation.

## Confirmed requirements
- Frontend stack target: Astro
- Support both light theme and dark theme
- Show full date only at group level, e.g. `3月15日`
- Individual feed items should show only time, e.g. `13:14`
- Remove the `查看原文` / source-post button from each item
- Keep a clean information-stream feel, not a dashboard-heavy feel
- Use a more mainstream premium editorial color/render style

## Information architecture
- Top header: site title, source description, last update time, theme toggle
- Feed grouped by date
- Within each date group:
  - group title: month/day
  - cards ordered by time descending
  - each card shows only `HH:MM`
- Search/filter can remain lightweight in early version

## UI direction
Target feel:
- clean editorial / modern news stream
- restrained premium color use
- strong readability
- comfortable whitespace
- mobile-friendly

## Theme direction
### Light theme
- background: warm off-white / light gray
- card: white with subtle border and shadow
- accent: muted blue / indigo
- text: dark gray, not pure black

### Dark theme
- background: deep charcoal / slate
- card: slightly lifted dark panel
- accent: soft blue / cyan or indigo
- text: cool light gray, not pure white

## Visual references to emulate
- Linear / Vercel style restraint
- Notion / Read.cv style whitespace
- modern editorial feed feel rather than admin dashboard feel

## Feed card rules
- no external-link CTA on card surface in the new version
- timestamp only for item-level meta
- tighter metadata line, stronger body text block
- long text can still support collapse/expand

## Data expectations
Current JSON remains usable:
- `data/messages.json`
- `data/meta.json`

Later possible additions:
- grouped daily JSON
- archive pages
- pagination / day pages

## Migration strategy
1. Keep existing fetch/update pipeline
2. Replace current `docs/index.html` generation with Astro build output
3. Add light/dark theme toggle
4. Convert feed into grouped-by-date presentation
5. Later add archives and richer navigation

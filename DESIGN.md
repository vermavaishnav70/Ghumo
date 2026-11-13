---
name: Ghumo
description: Sunlit Ivory, Burnt Terracotta, Coastal Sky & Teal-Pine Editorial Timetable design system for conversational trip planning and vetted booking handoffs.
colors:
  sandstone-ground: "#FAF8F4"
  ivory-folio: "#FFFFFF"
  aged-buff: "#F1EDE5"
  paper-white: "#FCFBF9"
  slate-ink: "#182328"
  slate-secondary: "#455359"
  slate-muted: "#5D6B71"
  warm-rule: "rgba(24, 35, 40, 0.12)"
  mid-rule: "rgba(24, 35, 40, 0.22)"
  saffron-ochre: "#C9491E"
  saffron-deep: "#B23D16"
  saffron-accent: "#E25B2D"
  saffron-tint: "#FDF0EA"
  saffron-ink: "#9E3310"
  sea-pine: "#155B4F"
  sea-pine-tint: "#E2F1EC"
  sea-pine-ink: "#0E453B"
  terracotta: "#CC4B21"
  terracotta-tint: "#FDECE6"
  terracotta-ink: "#9E310F"
  coastal-sky: "#1A6496"
  coastal-tint: "#E7F2FA"
  coastal-ink: "#124B73"
typography:
  display:
    fontFamily: "Fraunces, Georgia, Times New Roman, serif"
    fontSize: "clamp(2.5rem, 4.4vw, 3.85rem)"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "-0.028em"
  headline:
    fontFamily: "Fraunces, Georgia, Times New Roman, serif"
    fontSize: "clamp(1.75rem, 2.8vw, 2.3rem)"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Fraunces, Georgia, Times New Roman, serif"
    fontSize: "22px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.015em"
  body:
    fontFamily: "Plus Jakarta Sans, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: "0em"
  label:
    fontFamily: "Plus Jakarta Sans, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "13.5px"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0em"
  mono:
    fontFamily: "JetBrains Mono, ui-monospace, SFMono-Regular, monospace"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0.05em"
rounded:
  xs: "4px"
  sm: "6px"
  md: "10px"
  lg: "14px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "14px"
  lg: "20px"
  xl: "28px"
components:
  button-primary:
    backgroundColor: "{colors.saffron-ochre}"
    textColor: "{colors.paper-white}"
    rounded: "{rounded.sm}"
    padding: "12px 22px"
  button-primary-hover:
    backgroundColor: "{colors.saffron-deep}"
  button-secondary:
    backgroundColor: "{colors.sandstone-ground}"
    textColor: "{colors.slate-ink}"
    rounded: "{rounded.sm}"
    padding: "10px 18px"
  card-folio:
    backgroundColor: "{colors.ivory-folio}"
    textColor: "{colors.slate-ink}"
    rounded: "{rounded.md}"
    padding: "22px 24px"
  input-field:
    backgroundColor: "{colors.paper-white}"
    textColor: "{colors.slate-ink}"
    rounded: "{rounded.sm}"
    padding: "11px 14px"
  chip-filter:
    backgroundColor: "{colors.sandstone-ground}"
    textColor: "{colors.slate-secondary}"
    rounded: "{rounded.pill}"
    padding: "6px 12px"
  badge-verified:
    backgroundColor: "{colors.sea-pine-tint}"
    textColor: "{colors.sea-pine-ink}"
    rounded: "{rounded.sm}"
    padding: "4px 10px"
---

# Design System: Ghumo

## Overview

**Creative North Star: "Overland Timetable Folio"**

Ghumo's design system draws directly from mid-century overland rail timetables and sunlit printed travel folios. Rather than wrapping trip planning in a dark, glowing AI SaaS dashboard, every screen sits on warm sandstone paper, dividing journeys into crisp ink-ruled sheets, dashed ticket perforations, and clear tabular price and schedule columns.

The system balances human warmth with financial and logistical clarity. Editorial serif headings bring calm storytelling to the opening trip composer, while disciplined hairline borders and tabular monospace figures let travelers compare flights, stays, transit passes, cancellation rules, and total costs without visual fatigue.

**Key Characteristics:**
- Sunlit warm-ivory ground (`#FAF8F4`) layered with feathered coastal cliffside and wing-over-clouds travel photography so crisp white elevated cards (`#FFFFFF`) stand out cleanly.
- Vibrant burnt terracotta (`#C9491E`) reserved for primary commit actions, paired with deep Aegean teal-pine (`#155B4F`) for verified seals and active route pills, plus coastal cerulean (`#1A6496`) links.
- Editorial `Fraunces` headlines paired with `Plus Jakarta Sans` UI copy and tabular `JetBrains Mono` schedules and prices.
- Signature vertical route-leg track connecting stops, flights, and stays with circular markers and dashed ticket dividers.

## Colors

A bright sunlit paper-and-ink palette where crisp `#FAF8F4` ivory grounds faded scenic backdrops, `#FFFFFF` cards provide clear foreground contrast, and saturated terracotta, teal-pine, and coastal cerulean separate actions, verified facts, and links.

### Primary
- **Burnt Terracotta** (`#C9491E`): Primary interactive actions (`Build Timetable`, `Build Timetable & Compare Options`, `Select This Flight`, `Update trip`), darkened to `#B23D16` on hover (`#FDF0EA` tint with `#9E3310` text for fit scores and pending approval tags; `#E25B2D` accent underline).

### Secondary
- **Aegean Teal-Pine** (`#155B4F`): Live verification seals, active destination tabs, within-budget confirmations, selected booking states, and explicit approval controls (`#E2F1EC` tint with `#0E453B` text for verified badges).

### Tertiary & Scenic Accent
- **Terracotta Vermilion** (`#CC4B21`): Circular route-leg markers, trip dispatch tags, departure timing indicators, and estimate alerts (`#FDECE6` tint with `#9E310F` text).
- **Coastal Cerulean** (`#1A6496` / `#124B73` ink): Secondary studio links (`Open full studio`) and subtle skywash continuity harmonizing with coastal photography.

### Neutral
- **Sunlit Ivory Ground** (`#FAF8F4`): Clean bright page canvas underlying faded scenic backdrops.
- **Pure Elevated White** (`#FFFFFF`): Primary elevated card and timetable sheet surface, separated by hairline `rgba(24, 35, 40, 0.14)` borders and soft layered paper shadows.
- **Soft Ivory Well** (`#F1EDE5`): Secondary containers, tab bar wells, and flight arc wells.
- **Paper White** (`#FCFBF9`): Input fields and recessed option rows.
- **Ink Slate** (`#182328`): Primary headings and crisp display typography (`#455359` secondary, `#5D6B71` muted).

### Named Rules
**The Honest Signal Rule.** Teal-pine is reserved strictly for verified tariffs, within-budget checks, and confirmed selections; unverified market estimates and missing-detail alerts always use terracotta or amber-peach tints so synthetic estimates never masquerade as live confirmations.

**The Sunlit Daylight Rule.** Scenic coastal and cloud photography fades smoothly into `#FAF8F4` mist behind text regions so elevated `#FFFFFF` folio cards always keep razor-sharp legibility without muddy beige or dark neon slabs.

## Typography

**Display Font:** `Fraunces` (with Georgia, Times New Roman, serif fallback)
**Body Font:** `Plus Jakarta Sans` (with system sans-serif fallback)
**Label/Mono Font:** `JetBrains Mono` (with ui-monospace fallback)

**Character:** High-warmth editorial serif headings give Ghumo the approachability of a printed travel guide, while Plus Jakarta Sans handles dense policy and itinerary prose and JetBrains Mono keeps times, flight numbers, and dollar totals vertically aligned.

### Hierarchy
- **Display** (700, `clamp(2.5rem, 4.4vw, 3.85rem)`, line-height `1.05`, tracking `-0.028em`, `text-wrap: balance`): Hero headline on the landing screen.
- **Headline** (700, `clamp(1.75rem, 2.8vw, 2.3rem)`, line-height `1.15`, tracking `-0.02em`, `text-wrap: balance`): Route-level section titles and studio header.
- **Title** (700, `20px–28px`, line-height `1.15–1.2`): Card headers, day folio headings, and modal-free approval titles.
- **Body** (400–600, `13.5px–17px`, line-height `1.5–1.6`, max measure `58ch–68ch`): Itinerary descriptions, cancellation terms, and guidance prose.
- **Label & Mono** (600–700, `11px–13.5px`, uppercase `0.05em–0.08em` tracking for dispatch codes, `font-variant-numeric: tabular-nums`): Departure times, flight numbers, status seals, and currency totals.

### Named Rules
**The Tabular Fare Rule.** Every price, departure timestamp, duration, and trip subtotal sets `font-variant-numeric: tabular-nums` and uses `JetBrains Mono` on fare totals and schedule codes so rows scan cleanly down the column.

## Layout

Content sits inside a centered `1360px` container (`28px` horizontal padding on desktop, `16px` on mobile). On the landing page, an asymmetric `1.12fr / 0.88fr` grid pairs the direct trip composer with the live sample timetable, collapsing cleanly to a single column below `1024px`. On `/your-itinerary`, a `67% / 33%` split keeps the sticky AI Chat Copilot and Weather/Versions rail beside the 3-tab planner workspace (`Timeline`, `Bookings`, `Review & Book`).

Spacing follows a tight-within-groups, generous-between-sections rhythm (`4px`, `8px`, `14px`, `20px`, `28px`) with dashed `1.5px` dividers separating input controls from summaries and leg lists from totals.

## Elevation & Depth

Surfaces communicate hierarchy through tonal paper contrast (`#FBF8F3` ivory over `#F4ECE0` sandstone) and crisp `1.5px solid #1D262B` ink borders rather than heavy blur or dark drop shadows.

### Shadow Vocabulary
- **Paper Folio Shadow** (`box-shadow: 0 10px 28px -10px rgba(29, 38, 43, 0.12), 0 2px 6px -2px rgba(29, 38, 43, 0.06)`): Subtle warm lift on primary timetable cards, studio panels, and auth/loading folios.
- **Hover Lift Shadow** (`box-shadow: 0 16px 36px -12px rgba(29, 38, 43, 0.16), 0 4px 10px -2px rgba(29, 38, 43, 0.08)`): Applied sparingly on lifted interactive states alongside a `-1px` vertical translation.

### Named Rules
**The Ink-Ruled Paper Rule.** Cards never float on blurred glass or colored neon glows; crisp `1.5px` slate-ink borders define every primary paper sheet.

## Shapes

Containers use restrained editorial rounding (`6px` small controls and chips, `10px` primary folio panels and option cards, `14px` outer badges, `999px` filter pills and route markers). Timetable dividers feature semicircular side notches cut into `#F4ECE0` sandstone to evoke physical railway tickets without over-ornamenting operational screens.

## Components

### Buttons
- **Shape:** Subtle crisp rounding (`6px` radius) anchored by a `1.5px solid #1D262B` ink border.
- **Primary:** Saffron Ochre (`#B85C12`) fill with `#FFFDF9` bold label (`12px 22px` or `10px 16px` compact), darkening to `#9E4D0D` with a `-1px` hover lift.
- **Hover / Focus:** `2px solid #B85C12` keyboard focus outline with `2px` offset.
- **Secondary / Destructive:** Sandstone (`#F4ECE0`) fill with slate-ink text for secondary actions; terracotta tint (`#F9E8E2`) with `#943218` text for delete/revoke actions.

### Chips
- **Style:** Pill-shaped (`999px`) sample selectors, travel style tags, and booking filter tabs on `#F4ECE0` sandstone with `#D6C9B6` borders.
- **State:** Active filters switch to solid `#1D262B` slate-ink with `#FBF8F3` text, or `#E4EFEA` sea-pine tint for selected trip interests.

### Cards / Containers
- **Corner Style:** `10px` radius (`6px` for nested option rows).
- **Background:** `#FBF8F3` Ivory Folio for outer sheets; `#FFFDF9` Paper White for inner itinerary stops and flight/stay candidates (`#F6FAF8` with `1.5px solid #2E5E54` when selected).
- **Border:** `1.5px solid #1D262B` on outer folios; `1px solid #B9AA95` on inner items.
- **Internal Padding:** `20px–24px` on outer folios; `12px–18px` on inner rows.

### Inputs / Fields
- **Style:** `#FFFDF9` paper background, `1px solid #B9AA95` border, `6px` radius, `10px 13px` padding, and `#B85C12` text caret.
- **Focus:** Border shifts smoothly to `#B85C12` saffron ochre.

### Navigation
- **Style:** Sticky `#F4ECE0` sandstone masthead (`border-bottom: 1.5px solid #1D262B`) holding the geometric `GhumoMark` SVG, `Fraunces` wordmark, horizontal route links (`Trip Studio`, `Saved Trips`, `Booking Guide`), and account pill; links stay single-line on `390px` mobile screens with `Booking Guide` hidden below `680px`.

### Timetable Route-Leg Track
- **Behavior:** Circular `28px` terracotta markers housing crisp `1.75px`-stroke SVG transport icons connected by a continuous `2px` warm rule track (`#B9AA95`) down both the landing sample timetable and every day's `ActivityCard` schedule.

## Do's and Don'ts

### Do:
- **Do** keep all page canvases on `#F4ECE0` sandstone and primary folios on `#FBF8F3` ivory with `1.5px solid #1D262B` borders.
- **Do** use `JetBrains Mono` with `tabular-nums` for all prices, departure codes, and cost ledger totals.
- **Do** preserve continuous vertical route tracks between adjacent circular leg markers across desktop and mobile breakpoints.
- **Do** use consistent `1.75px`-stroke inline SVG icons from `Icons.jsx` and label synthetic previews honestly (`SAMPLE TIMETABLE`).

### Don't:
- **Don't** introduce dark backgrounds, glowing gradients, blurred glass panels, or neon accents.
- **Don't** place uppercase eyebrow/kicker labels above headings (`h1`, `h2`, `h3`) or decorative `01 / 02 / 03` section counters.
- **Don't** hide schedule codes on mobile viewports—stack them cleanly above the leg title instead.
- **Don't** mark unverified estimates as live-verified or render unicode emojis as UI icons.

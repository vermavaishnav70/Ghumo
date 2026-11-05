# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Independent leisure travelers (solo travelers, couples, and small groups) who want to plan, compare, and prepare a multi-day trip end-to-end in one place without spending hours juggling airline, hotel, transit, and itinerary tabs.

## Product Purpose

Ghumo turns a natural-language travel idea or structured trip brief into a complete, bookable trip plan. It clarifies missing trip essentials, generates a weather-aware day-by-day itinerary, researches and compares flights, stays, and local transport, checks prices and policies, and guides the traveler through an explicit approval checkpoint to verified provider booking links. Success means going from a rough trip idea to a confident, ready-to-book plan in minutes.

## Positioning

An all-in-one conversational travel agent that prioritizes speed and convenience from natural-language prompt to validated trip options and booking links—combining conversational refinement, side-by-side travel comparisons, and honest price/policy verification in a single flow.

## Operating Context

- **Natural-language & structured intake (`/fill-details`)**: Travelers describe a trip in plain language or fill structured trip specs (origin, destination, start date, 1–10 day duration, traveler count, budget tier/cap, style preferences). When essentials are missing, the intake assistant asks focused follow-up questions before planning.
- **Multi-stage trip workspace (`/your-itinerary`, `/saved-trips/:itineraryId`)**: Travelers inspect their day-by-day itinerary alongside compared flight, stay, and local transport options, cost breakdowns, live weather forecasts, validation flags/exclusions, and chat-based itinerary edits.
- **Explicit approval & guided booking handoff**: Travelers review total costs, exclusions, and cancellation terms and explicitly approve the plan before unlocking step-by-step booking guidance and provider links.
- **Account & versioned trip library (`/saved-trips`)**: Authenticated users save trips via Supabase, revisit saved plans, preview older versions, and restore previous versions.

## Capabilities and Constraints

- **Backend orchestration**: FastAPI + LangGraph `StateGraph` (`planning` → `research` → `evaluation` → `validation` → `review`), LangChain Gemini/Groq LLM providers, Open-Meteo weather forecasts, and optional live search APIs (Tavily, SerpApi, Amadeus) with route/budget-calibrated market estimation fallback.
- **Honest booking & verification boundary**: Booking and payment actions must never be marked complete unless a provider confirms success. When direct checkout/GDS APIs are unavailable, Ghumo explicitly flags estimates vs. live-verified items, states exclusions, and guides the traveler to external provider booking pages.
- **Technical & scope bounds**: Itineraries support 1–10 days and 1–20 travelers; backend API contract uses `/api/trips/*` and `/api/itineraries/*`; frontend is React 18 + Vite + React Router + Supabase JS.
- **Legacy assets**: Existing brand assets (`src/assets/*`, old "Wanderlust" branding) may be replaced as part of the rebrand to Ghumo.

## Brand Commitments

- **Product name**: Ghumo (replaces "Wanderlust").
- **Direction constraint (volunteered by user)**: Replace the current dark/neon "AI slop" interface with a **warm and genuine** design system.
- **Collaborative checkpoints (requested by user)**: Ask the user when deciding color themes and the new Ghumo logo, and generate custom images where appropriate.

## Evidence on Hand

- Real working FastAPI + LangGraph backend (`backend/app/services/agent_graph.py`, `travel_tools.py`, `weather.py`) with 29 passing automated tests.
- Real React + Vite frontend routes (`/`, `/fill-details`, `/your-itinerary`, `/saved-trips`, `/saved-trips/:itineraryId`) and Supabase auth/persistence (`supabase/schema.sql`).
- Real limitation on hand: live OTA/GDS booking execution is not connected by default; provider handoff links and market estimates are clearly labeled as such rather than fabricated confirmations.

## Product Principles

1. **Speed without guesswork**: Extract everything possible from natural language first, then ask only for missing essentials.
2. **Real-world travel clarity**: Present flights, stays, local transit, weather, and daily plans together so travelers can weigh cost, time, location, and cancellation terms at a glance.
3. **Never fake a booking or a price**: Clearly separate live-verified data from estimates, surface exclusions upfront, and require explicit traveler approval before booking handoffs.
4. **Conversational continuity**: Every refinement—whether editing Day 2 via chat or swapping a flight—re-evaluates the whole trip state cohesively.


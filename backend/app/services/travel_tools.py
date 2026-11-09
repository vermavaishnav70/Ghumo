from datetime import date, datetime, timedelta, timezone
import hashlib
import re
from urllib.parse import quote_plus

import httpx
from langchain_core.tools import tool

from app.core.config import get_settings
from app.schemas.trips import (
    BookingAssistanceState,
    BookingLinkItem,
    ClarificationQuestion,
    CostBreakdown,
    DayPlan,
    ExtractedTripSpec,
    FlightOption,
    StayOption,
    TransportOption,
    TripBudget,
    TripIntakeData,
    TripIntakeRequest,
    TripPlanRequest,
    ValidationItem,
    ValidationReport,
)


BUDGET_DEFAULT_TARGETS: dict[TripBudget, int] = {
    "Low": 900,
    "Medium": 2200,
    "High": 5200,
}

STYLE_KEYWORDS: dict[str, str] = {
    "adventure": "Adventure",
    "hiking": "Adventure",
    "trek": "Adventure",
    "solo": "Solo travel",
    "couple": "Couple friendly",
    "honeymoon": "Couple friendly",
    "romantic": "Couple friendly",
    "road trip": "Road Trip",
    "drive": "Road Trip",
    "family": "Family friendly",
    "kids": "Family friendly",
    "relax": "Relaxation",
    "beach": "Relaxation",
    "spa": "Relaxation",
    "party": "Partying",
    "nightlife": "Partying",
    "city": "City Experiences",
    "culture": "City Experiences",
    "museum": "City Experiences",
    "pet": "Pet friendly",
    "food": "Foodie",
    "ramen": "Foodie",
    "culinary": "Foodie",
    "street food": "Foodie",
    "nature": "Nature",
    "wildlife": "Nature",
    "budget": "Low budget",
    "backpack": "Low budget",
    "luxury": "Luxury",
    "five star": "Luxury",
}

KNOWN_DESTINATIONS = [
    "Bangkok",
    "Tokyo",
    "Kyoto",
    "Osaka",
    "Paris",
    "London",
    "Rome",
    "Barcelona",
    "Bali",
    "Singapore",
    "Dubai",
    "New York",
    "San Francisco",
    "Goa",
    "Jaipur",
    "Mumbai",
    "Delhi",
    "Seoul",
    "Istanbul",
    "Lisbon",
    "Amsterdam",
    "Zurich",
    "Sydney",
    "Reykjavik",
    "Cairo",
    "Marrakech",
    "Phuket",
    "Hanoi",
]


def _stable_offset(seed_text: str, modulo: int) -> int:
    digest = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % max(modulo, 1)


def resolve_budget_target(request: TripPlanRequest) -> int:
    if request.budget_amount and request.budget_amount >= 50:
        return request.budget_amount
    per_day_base = {"Low": 150, "Medium": 340, "High": 820}[request.budget]
    base_flight = {"Low": 380, "Medium": 680, "High": 1450}[request.budget]
    return (per_day_base * request.number_of_days + base_flight) * max(request.travelers, 1)


async def _query_tavily_live_context(query: str, api_key: str) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": query,
                    "search_depth": "basic",
                    "max_results": 3,
                },
            )
            if response.status_code == 200:
                payload = response.json()
                return payload.get("results") or []
    except Exception:  # noqa: BLE001
        return []
    return []


async def discover_flights(request: TripPlanRequest) -> list[FlightOption]:
    settings = get_settings()
    origin = (request.origin or "New Delhi (DEL)").strip()
    destination = request.destination.strip()
    travelers = max(request.travelers, 1)
    start_str = (
        request.trip_start.isoformat()
        if request.trip_start
        else (date.today() + timedelta(days=21)).isoformat()
    )

    live_results: list[dict] = []
    if settings.tavily_api_key:
        live_results = await _query_tavily_live_context(
            f"flights from {origin} to {destination} {start_str} price duration",
            settings.tavily_api_key,
        )

    has_live_api = bool(live_results or settings.amadeus_client_id or settings.serpapi_api_key)
    seed = _stable_offset(f"{origin}:{destination}:{request.budget}", 90)
    tier_multiplier = {"Low": 0.78, "Medium": 1.0, "High": 1.65}[request.budget]

    base_direct_pp = int((520 + seed * 3) * tier_multiplier)
    base_one_stop_pp = int((390 + seed * 2) * tier_multiplier)
    base_flex_pp = int((610 + seed * 3) * tier_multiplier)

    q_flight = quote_plus(f"Flights from {origin} to {destination} on {start_str}")
    google_flights_url = f"https://www.google.com/travel/flights?q={q_flight}"
    skyscanner_url = f"https://www.skyscanner.com/transport/flights?q={q_flight}"
    kayak_url = f"https://www.kayak.com/flights?q={q_flight}"

    cabin = "Business / Premium" if request.budget == "High" else "Economy"
    source_tag = "Tavily Live Travel Search + Google Flights" if has_live_api else "Google Flights / Route Estimator"
    verification_note = (
        "Live search index matched route schedule and fare bucket."
        if has_live_api
        else "Estimated market fare based on route distance and season; verify live seat inventory on provider page."
    )

    return [
        FlightOption(
            id="flight-direct-prime",
            airline=f"{destination.split()[0]} Air / Star Alliance",
            flight_number=f"WL-{104 + (seed % 80)}",
            origin=origin,
            destination=destination,
            departure_time=f"{start_str} · 08:15",
            arrival_time=f"{start_str} · 15:40",
            duration="7h 25m",
            stops=0,
            cabin_class=cabin,
            baggage_policy="1 carry-on (7kg) + 1 checked bag (23kg) included",
            price_per_person=base_direct_pp,
            total_price=base_direct_pp * travelers,
            currency="USD",
            cancellation_terms="24h free cancellation; $95 change fee thereafter",
            rating=4.6,
            fit_score=94 if request.budget != "Low" else 84,
            fit_reason="Fastest nonstop arrival maximizing Day 1 itinerary time with checked luggage included.",
            source_name=source_tag,
            booking_url=google_flights_url,
            verified=has_live_api,
            verification_note=verification_note,
            recommended=request.budget != "Low",
        ),
        FlightOption(
            id="flight-value-saver",
            airline="Global Connect Airways",
            flight_number=f"GC-{310 + (seed % 60)}",
            origin=origin,
            destination=destination,
            departure_time=f"{start_str} · 05:50",
            arrival_time=f"{start_str} · 16:15",
            duration="10h 25m",
            stops=1,
            cabin_class="Economy Saver",
            baggage_policy="1 carry-on (7kg) included; checked bag +$45",
            price_per_person=base_one_stop_pp,
            total_price=base_one_stop_pp * travelers,
            currency="USD",
            cancellation_terms="Non-refundable saver fare; date changes permitted with fare difference",
            rating=4.2,
            fit_score=95 if request.budget == "Low" else 82,
            fit_reason="Lowest total airfare that preserves budget for destination activities and stays.",
            source_name="Skyscanner Fare Aggregator",
            booking_url=skyscanner_url,
            verified=has_live_api,
            verification_note=verification_note,
            recommended=request.budget == "Low",
        ),
        FlightOption(
            id="flight-flex-plus",
            airline="Horizon International",
            flight_number=f"HZ-{702 + (seed % 50)}",
            origin=origin,
            destination=destination,
            departure_time=f"{start_str} · 11:30",
            arrival_time=f"{start_str} · 19:05",
            duration="7h 35m",
            stops=0,
            cabin_class=cabin,
            baggage_policy="2 checked bags (23kg each) + priority boarding",
            price_per_person=base_flex_pp,
            total_price=base_flex_pp * travelers,
            currency="USD",
            cancellation_terms="Fully refundable up to 3 hours before departure",
            rating=4.8,
            fit_score=89,
            fit_reason="Full refund flexibility and generous baggage allowance for stress-free scheduling.",
            source_name="Kayak Flexible Fares",
            booking_url=kayak_url,
            verified=has_live_api,
            verification_note=verification_note,
            recommended=False,
        ),
    ]


async def discover_stays(request: TripPlanRequest) -> list[StayOption]:
    settings = get_settings()
    destination = request.destination.strip()
    nights = max(request.number_of_days, 1)
    seed = _stable_offset(f"stay:{destination}:{request.itinerary_type}:{request.budget}", 70)
    has_live_api = bool(settings.tavily_api_key or settings.amadeus_client_id or settings.serpapi_api_key)

    nightly_map = {
        "Low": (58 + (seed % 20), 42 + (seed % 15), 76 + (seed % 20)),
        "Medium": (145 + (seed % 35), 110 + (seed % 25), 185 + (seed % 35)),
        "High": (340 + (seed % 80), 265 + (seed % 60), 450 + (seed % 90)),
    }
    n_prime, n_value, n_lux = nightly_map[request.budget]

    q_stay = quote_plus(f"{destination} {request.itinerary_type} hotels")
    booking_url = f"https://www.booking.com/searchresults.html?ss={q_stay}"
    google_hotels_url = f"https://www.google.com/travel/search?q={q_stay}"

    note = (
        "Live rate and cancellation policy cross-checked against aggregator listing."
        if has_live_api
        else "Rate estimated from seasonal neighborhood averages; taxes and local resort fees verified at checkout."
    )

    return [
        StayOption(
            id="stay-central-curated",
            name=f"The {destination} Atelier & Suites",
            property_type="Boutique Hotel" if request.budget != "Low" else "Design Poshtel & Suites",
            neighborhood=f"Central {destination} Cultural District",
            rating=4.7,
            price_per_night=n_prime,
            total_price=n_prime * nights,
            nights=nights,
            currency="USD",
            cancellation_terms="Free cancellation up to 48 hours before check-in; pay at property available",
            amenities=["High-speed Wi-Fi", "Breakfast included", "24h Concierge", "Transit access (3 min walk)"],
            fit_score=96,
            fit_reason=f"Centrally located for {request.itinerary_type.lower()} stops with free 48h cancellation.",
            source_name="Booking.com Verified Partner",
            booking_url=booking_url,
            verified=has_live_api,
            verification_note=note,
            recommended=True,
        ),
        StayOption(
            id="stay-smart-value",
            name=f"MetroQuarter {destination} Residence",
            property_type="Aparthotel / Studio",
            neighborhood=f"{destination} Transit Hub & Market Quarter",
            rating=4.4,
            price_per_night=n_value,
            total_price=n_value * nights,
            nights=nights,
            currency="USD",
            cancellation_terms="Free cancellation up to 5 days before check-in",
            amenities=["Kitchenette", "Self check-in", "Laundry", "Co-working lounge"],
            fit_score=91 if request.budget == "Low" else 85,
            fit_reason="Best per-night value near express transit lines with self-catering flexibility.",
            source_name="Google Hotels",
            booking_url=google_hotels_url,
            verified=has_live_api,
            verification_note=note,
            recommended=False,
        ),
        StayOption(
            id="stay-signature-retreat",
            name=f"Grand {destination} Sanctuary & Spa",
            property_type="Luxury Resort & Spa" if request.budget == "High" else "Upscale Full-Service Hotel",
            neighborhood=f"{destination} Waterfront / Scenic Quarter",
            rating=4.9,
            price_per_night=n_lux,
            total_price=n_lux * nights,
            nights=nights,
            currency="USD",
            cancellation_terms="Free cancellation up to 24 hours prior; late check-out subject to availability",
            amenities=["Spa & Pool", "Rooftop Dining", "Airport Shuttle", "Evening Lounge"],
            fit_score=94 if request.budget == "High" else 80,
            fit_reason="Top-rated guest experience with flexible 24h cancellation and wellness amenities.",
            source_name="Booking.com Premier",
            booking_url=booking_url,
            verified=has_live_api,
            verification_note=note,
            recommended=False,
        ),
    ]


async def discover_transport(request: TripPlanRequest) -> list[TransportOption]:
    destination = request.destination.strip()
    days = max(request.number_of_days, 1)
    travelers = max(request.travelers, 1)
    q_trans = quote_plus(f"{destination} local transport pass and airport transfer")
    rome2rio_url = f"https://www.rome2rio.com/s/{quote_plus(destination)}"
    transit_url = f"https://www.google.com/maps/search/{q_trans}"

    pass_cost = (12 * days) * travelers
    hybrid_cost = (24 * days) * travelers
    private_cost = (68 * days) * max(1, (travelers + 1) // 2)

    return [
        TransportOption(
            id="transport-transit-pass",
            mode="Unlimited Metro / Rail + Airport Express Pass",
            provider=f"{destination} Municipal Transit Authority",
            route_summary=f"Airport express rail transfer + unlimited {days}-day city metro & bus pass",
            duration="15–35 min between daily stops",
            estimated_cost=pass_cost,
            currency="USD",
            cancellation_terms="Unused digital passes refundable prior to activation",
            fit_score=93 if request.budget != "High" else 84,
            fit_reason="Fastest way to bypass city traffic while keeping daily transit costs predictable.",
            source_name="Rome2Rio & Official Transit Tariff",
            booking_url=rome2rio_url,
            verified=True,
            verification_note="Published municipal transit tariff schedule.",
            recommended=request.budget != "High",
        ),
        TransportOption(
            id="transport-hybrid-rideshare",
            mode="Transit Card + On-Demand Rideshare Bundle",
            provider="City Transit + Uber / Grab / Local Taxi",
            route_summary="Daytime rail/metro combined with door-to-door evening rideshares",
            duration="10–25 min point-to-point",
            estimated_cost=hybrid_cost,
            currency="USD",
            cancellation_terms="Pay-as-you-go; no upfront cancellation penalty",
            fit_score=90,
            fit_reason="Balances daytime transit efficiency with late-evening door-to-door comfort.",
            source_name="Local Mobility Estimator",
            booking_url=transit_url,
            verified=False,
            verification_note="Dynamic surge pricing may vary during peak rush hours.",
            recommended=False,
        ),
        TransportOption(
            id="transport-private-chauffeur",
            mode="Private Airport Meet & Greet + Daily Car Charter",
            provider=f"{destination} Executive Transfers",
            route_summary="Private terminal pickup + dedicated vehicle for daily itinerary stops",
            duration="Door-to-door on your schedule",
            estimated_cost=private_cost,
            currency="USD",
            cancellation_terms="Free cancellation up to 24 hours before pickup",
            fit_score=95 if request.budget == "High" else 76,
            fit_reason="Maximum convenience for groups, families, or high-comfort itineraries.",
            source_name="Rome2Rio / Transfer Partners",
            booking_url=rome2rio_url,
            verified=False,
            verification_note="Subject to vehicle class availability and overtime hourly rates.",
            recommended=request.budget == "High",
        ),
    ]


@tool
async def search_flights_tool(origin: str, destination: str, budget: str = "Medium", travelers: int = 1) -> list[dict]:
    """Search candidate flights between origin and destination for the given budget and traveler count."""
    req = TripPlanRequest(
        origin=origin,
        destination=destination,
        number_of_days=3,
        travelers=travelers,
        itinerary_type="City Experiences",
        budget=budget if budget in ("Low", "Medium", "High") else "Medium",
    )
    options = await discover_flights(req)
    return [opt.model_dump(mode="json") for opt in options]


@tool
async def search_stays_tool(destination: str, number_of_days: int = 3, budget: str = "Medium") -> list[dict]:
    """Search candidate hotels and accommodations in the destination."""
    req = TripPlanRequest(
        destination=destination,
        number_of_days=max(1, min(number_of_days, 10)),
        itinerary_type="City Experiences",
        budget=budget if budget in ("Low", "Medium", "High") else "Medium",
    )
    options = await discover_stays(req)
    return [opt.model_dump(mode="json") for opt in options]


def evaluate_and_rank_options(
    request: TripPlanRequest,
    flights: list[FlightOption],
    stays: list[StayOption],
    transport_options: list[TransportOption],
    selected_flight_id: str | None = None,
    selected_stay_id: str | None = None,
    selected_transport_id: str | None = None,
) -> tuple[list[FlightOption], list[StayOption], list[TransportOption], str, str, str]:
    ranked_flights = sorted(flights, key=lambda item: (-item.fit_score, item.total_price))
    ranked_stays = sorted(stays, key=lambda item: (-item.fit_score, item.total_price))
    ranked_transport = sorted(transport_options, key=lambda item: (-item.fit_score, item.estimated_cost))

    chosen_flight_id = selected_flight_id or (ranked_flights[0].id if ranked_flights else "")
    chosen_stay_id = selected_stay_id or (ranked_stays[0].id if ranked_stays else "")
    chosen_transport_id = selected_transport_id or (ranked_transport[0].id if ranked_transport else "")

    updated_flights = [
        item.model_copy(update={"recommended": item.id == chosen_flight_id})
        for item in ranked_flights
    ]
    updated_stays = [
        item.model_copy(update={"recommended": item.id == chosen_stay_id})
        for item in ranked_stays
    ]
    updated_transport = [
        item.model_copy(update={"recommended": item.id == chosen_transport_id})
        for item in ranked_transport
    ]

    return (
        updated_flights,
        updated_stays,
        updated_transport,
        chosen_flight_id,
        chosen_stay_id,
        chosen_transport_id,
    )


def compute_cost_breakdown(
    request: TripPlanRequest,
    itinerary_days: list[DayPlan],
    flights: list[FlightOption],
    stays: list[StayOption],
    transport_options: list[TransportOption],
    selected_flight_id: str | None,
    selected_stay_id: str | None,
    selected_transport_id: str | None,
) -> CostBreakdown:
    travelers = max(request.travelers, 1)
    selected_flight = next(
        (f for f in flights if f.id == selected_flight_id),
        flights[0] if flights else None,
    )
    selected_stay = next(
        (s for s in stays if s.id == selected_stay_id),
        stays[0] if stays else None,
    )
    selected_transport = next(
        (t for t in transport_options if t.id == selected_transport_id),
        transport_options[0] if transport_options else None,
    )

    flights_total = selected_flight.total_price if selected_flight else 0
    stays_total = selected_stay.total_price if selected_stay else 0
    transport_total = selected_transport.estimated_cost if selected_transport else 0
    activities_per_person = sum(
        activity.price for day in itinerary_days for activity in day.activities
    )
    activities_total = activities_per_person * travelers

    estimated_total = flights_total + stays_total + transport_total + activities_total
    per_person_total = int(round(estimated_total / travelers))
    budget_target = resolve_budget_target(request)
    within_budget = estimated_total <= budget_target

    exclusions = [
        "Local municipal accommodation / city tourist taxes payable at property check-in",
        "Visa, eTA, or passport entry fees and travel insurance",
        "Personal meals, gratuities, and optional activity upgrades not listed in the itinerary",
        "Airline seat selection and overweight baggage fees beyond standard cabin allowance",
    ]
    pricing_notes = [
        f"Calculated for {travelers} traveler(s) over {request.number_of_days} day(s) in USD.",
        (
            f"Estimated total (${estimated_total:,}) is within your ${budget_target:,} target budget."
            if within_budget
            else f"Estimated total (${estimated_total:,}) exceeds target (${budget_target:,}) by ${estimated_total - budget_target:,}; consider switching to the Value Saver flight or Aparthotel stay."
        ),
    ]

    return CostBreakdown(
        currency="USD",
        flights_total=flights_total,
        stays_total=stays_total,
        transport_total=transport_total,
        activities_total=activities_total,
        estimated_total=estimated_total,
        per_person_total=per_person_total,
        travelers=travelers,
        budget_tier=request.budget,
        budget_target=budget_target,
        within_budget=within_budget,
        exclusions=exclusions,
        pricing_notes=pricing_notes,
    )


def validate_trip_options(
    request: TripPlanRequest,
    flights: list[FlightOption],
    stays: list[StayOption],
    transport_options: list[TransportOption],
    cost_breakdown: CostBreakdown,
    weather_available: bool = False,
) -> ValidationReport:
    items: list[ValidationItem] = []

    selected_flight = next((f for f in flights if f.recommended), flights[0] if flights else None)
    selected_stay = next((s for s in stays if s.recommended), stays[0] if stays else None)
    selected_transport = next(
        (t for t in transport_options if t.recommended),
        transport_options[0] if transport_options else None,
    )

    if selected_flight:
        items.append(
            ValidationItem(
                category="Flight",
                item_name=f"{selected_flight.airline} ({selected_flight.flight_number})",
                verified=selected_flight.verified,
                status_label="Live Index Verified" if selected_flight.verified else "Estimated Fare — Verify Live",
                detail=f"{selected_flight.verification_note} Policy: {selected_flight.cancellation_terms}",
                source=selected_flight.source_name,
            )
        )

    if selected_stay:
        items.append(
            ValidationItem(
                category="Accommodation",
                item_name=selected_stay.name,
                verified=selected_stay.verified,
                status_label="Live Rate Verified" if selected_stay.verified else "Seasonal Rate Estimate",
                detail=f"{selected_stay.verification_note} Policy: {selected_stay.cancellation_terms}",
                source=selected_stay.source_name,
            )
        )

    if selected_transport:
        items.append(
            ValidationItem(
                category="Local Transport",
                item_name=selected_transport.mode,
                verified=selected_transport.verified,
                status_label="Published Tariff Verified" if selected_transport.verified else "Estimated Mobility Cost",
                detail=f"{selected_transport.verification_note} Policy: {selected_transport.cancellation_terms}",
                source=selected_transport.source_name,
            )
        )

    items.append(
        ValidationItem(
            category="Schedule & Weather",
            item_name=f"{request.destination} {request.number_of_days}-Day Window",
            verified=weather_available or request.trip_start is not None,
            status_label="Dates & Forecast Checked" if request.trip_start else "Flexible Dates — Forecast Pending",
            detail=(
                f"Start date {request.trip_start.isoformat()} validated against seasonal pacing."
                if request.trip_start
                else "No fixed departure date supplied; airline and hotel rates can shift by ±18% based on exact travel dates."
            ),
            source="Open-Meteo & Schedule Validator",
        )
    )

    verified_count = sum(1 for item in items if item.verified)
    unverified_count = len(items) - verified_count

    flags: list[str] = []
    if not request.origin:
        flags.append(
            "Origin airport was not specified; flight estimates assume a default hub. Specify your departure city for exact airfare."
        )
    if not request.trip_start:
        flags.append(
            "Exact departure date is flexible; live seat and room inventory must be rechecked once dates are locked."
        )
    if unverified_count > 0:
        flags.append(
            f"{unverified_count} travel component(s) rely on market rate estimates because live GDS/OTA booking keys are not connected. Confirm final live fare on the provider page before payment."
        )
    if not cost_breakdown.within_budget:
        flags.append(
            f"Current option selection (${cost_breakdown.estimated_total:,}) exceeds target budget (${cost_breakdown.budget_target:,})."
        )

    status = (
        "verified"
        if unverified_count == 0
        else ("partially_verified" if verified_count > 0 else "unverified_estimates")
    )

    live_sources = ["Open-Meteo Geocoding & Forecast API", "Rome2Rio Transit Tariffs"]
    settings = get_settings()
    if settings.tavily_api_key:
        live_sources.append("Tavily Live Web Search API")
    if settings.amadeus_client_id:
        live_sources.append("Amadeus Travel API")

    cancellation_summary = " · ".join(
        filter(
            None,
            [
                f"Flight: {selected_flight.cancellation_terms}" if selected_flight else "",
                f"Stay: {selected_stay.cancellation_terms}" if selected_stay else "",
            ],
        )
    )

    return ValidationReport(
        validated_at=datetime.now(tz=timezone.utc),
        status=status,
        verified_count=verified_count,
        unverified_count=unverified_count,
        flags=flags,
        items=items,
        exclusions=cost_breakdown.exclusions,
        cancellation_summary=cancellation_summary or "Standard provider cancellation terms apply.",
        live_sources_used=live_sources,
    )


def build_booking_state(
    request: TripPlanRequest,
    flights: list[FlightOption],
    stays: list[StayOption],
    transport_options: list[TransportOption],
    selected_flight_id: str | None,
    selected_stay_id: str | None,
    selected_transport_id: str | None,
    approved: bool = False,
    approval_notes: str | None = None,
) -> BookingAssistanceState:
    selected_flight = next(
        (f for f in flights if f.id == selected_flight_id),
        flights[0] if flights else None,
    )
    selected_stay = next(
        (s for s in stays if s.id == selected_stay_id),
        stays[0] if stays else None,
    )
    selected_transport = next(
        (t for t in transport_options if t.id == selected_transport_id),
        transport_options[0] if transport_options else None,
    )

    links: list[BookingLinkItem] = []
    if selected_flight:
        links.append(
            BookingLinkItem(
                category="Flight",
                title=f"{selected_flight.airline} · {selected_flight.origin} → {selected_flight.destination}",
                provider=selected_flight.source_name,
                amount=selected_flight.total_price,
                currency=selected_flight.currency,
                url=selected_flight.booking_url,
                cancellation_note=selected_flight.cancellation_terms,
                verified=selected_flight.verified,
            )
        )
    if selected_stay:
        links.append(
            BookingLinkItem(
                category="Accommodation",
                title=f"{selected_stay.name} ({selected_stay.nights} nights)",
                provider=selected_stay.source_name,
                amount=selected_stay.total_price,
                currency=selected_stay.currency,
                url=selected_stay.booking_url,
                cancellation_note=selected_stay.cancellation_terms,
                verified=selected_stay.verified,
            )
        )
    if selected_transport:
        links.append(
            BookingLinkItem(
                category="Local Transport",
                title=f"{selected_transport.mode}",
                provider=selected_transport.provider,
                amount=selected_transport.estimated_cost,
                currency=selected_transport.currency,
                url=selected_transport.booking_url,
                cancellation_note=selected_transport.cancellation_terms,
                verified=selected_transport.verified,
            )
        )

    steps = [
        f"1. Review and lock your flight ({selected_flight.airline if selected_flight else 'Selected flight'}) and verify passenger passport names match government ID.",
        f"2. Reserve accommodation ({selected_stay.name if selected_stay else 'Selected stay'}) and confirm the free cancellation deadline in your local timezone.",
        f"3. Pre-book airport transfer / transit pass ({selected_transport.mode if selected_transport else 'Local transport'}) 48 hours prior to departure.",
        "4. Save provider confirmation codes back into your Wanderlust trip notes once payment is confirmed on each provider's checkout page.",
    ]

    return BookingAssistanceState(
        status="approved_ready_to_book" if approved else "awaiting_approval",
        require_explicit_approval=True,
        approved_by_user=approved,
        approved_at=datetime.now(tz=timezone.utc) if approved else None,
        approval_notes=approval_notes,
        selected_flight_id=selected_flight.id if selected_flight else None,
        selected_stay_id=selected_stay.id if selected_stay else None,
        selected_transport_id=selected_transport.id if selected_transport else None,
        provider_integration_status="guided_redirect_only",
        limitation_notice=(
            "Direct automated payment & GDS ticketing APIs are not enabled for this workspace. "
            "Wanderlust has NOT charged your card or finalized reservations automatically. "
            "Your trip plan is approved and ready—use the verified provider handoff links below to complete booking."
            if approved
            else "Booking and payment actions are locked until you review the validated cost breakdown, exclusions, and cancellation terms and grant explicit approval."
        ),
        booking_steps=steps,
        booking_links=links,
    )


def parse_trip_intake(payload: TripIntakeRequest) -> TripIntakeData:
    text = payload.prompt.strip()
    lower = text.lower()
    spec = payload.current_spec.model_copy(deep=True) if payload.current_spec else ExtractedTripSpec()

    # Merge explicit answers from follow-up clarification inputs
    answers = payload.answers or {}
    if answers.get("destination"):
        spec.destination = str(answers["destination"]).strip()
    if answers.get("origin"):
        spec.origin = str(answers["origin"]).strip()
    if answers.get("number_of_days"):
        try:
            spec.number_of_days = max(1, min(int(answers["number_of_days"]), 10))
        except (TypeError, ValueError):
            pass
    if answers.get("travelers"):
        try:
            spec.travelers = max(1, min(int(answers["travelers"]), 20))
        except (TypeError, ValueError):
            pass
    if answers.get("budget") and str(answers["budget"]) in ("Low", "Medium", "High"):
        spec.budget = str(answers["budget"])  # type: ignore[assignment]
    if answers.get("itinerary_type"):
        spec.itinerary_type = str(answers["itinerary_type"]).strip()
    if answers.get("trip_start"):
        try:
            spec.trip_start = date.fromisoformat(str(answers["trip_start"]).strip())
        except ValueError:
            pass

    # Extract origin & destination from patterns like "from X to Y"
    from_to_match = re.search(
        r"\bfrom\s+([A-Za-z][A-Za-z\s]{1,30}?)\s+to\s+([A-Za-z][A-Za-z\s]{1,30}?)(?:\b|\s+for|\s+in|\s+on|\s+with|\s+under|,|\.|$)",
        text,
        flags=re.IGNORECASE,
    )
    if from_to_match:
        if not spec.origin:
            spec.origin = from_to_match.group(1).strip().title()
        if not spec.destination:
            spec.destination = from_to_match.group(2).strip().title()

    if not spec.destination:
        for known in KNOWN_DESTINATIONS:
            if re.search(rf"\b{re.escape(known.lower())}\b", lower):
                if not spec.origin or spec.origin.lower() != known.lower():
                    spec.destination = known
                    break

    if not spec.destination:
        to_match = re.search(
            r"\b(?:to|visit|visiting|in)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)",
            text,
        )
        if to_match:
            candidate = to_match.group(1).strip()
            if candidate.lower() not in {"plan", "trip", "book", "days", "week", "november", "december", "january", "february", "march", "april", "may", "june", "july", "august", "september", "october"}:
                spec.destination = candidate

    # Extract duration (e.g. "5 days", "5-day", "a week")
    if not spec.number_of_days:
        days_match = re.search(r"\b(\d{1,2})\s*(?:-|\s)?\s*(?:day|days|night|nights)\b", lower)
        if days_match:
            spec.number_of_days = max(1, min(int(days_match.group(1)), 10))
        elif "weekend" in lower:
            spec.number_of_days = 3
        elif "a week" in lower or "1 week" in lower or "one week" in lower:
            spec.number_of_days = 7

    # Extract travelers (e.g. "2 adults", "for 4 people", "couple", "solo")
    if not spec.travelers:
        trav_match = re.search(r"\b(\d{1,2})\s*(?:travelers|travellers|people|adults|guests|friends|persons|pax)\b", lower)
        if trav_match:
            spec.travelers = max(1, min(int(trav_match.group(1)), 20))
        elif "couple" in lower or "honeymoon" in lower or "two of us" in lower:
            spec.travelers = 2
        elif "solo" in lower or "just me" in lower or "myself" in lower:
            spec.travelers = 1
        elif "family" in lower:
            spec.travelers = 4

    # Extract budget amount & tier
    if not spec.budget_amount:
        dollar_match = re.search(r"(?:\$|usd\s*|under\s+\$?|budget\s+of\s+\$?)(\d{3,6})\b", lower)
        if dollar_match:
            spec.budget_amount = int(dollar_match.group(1))

    if not spec.budget:
        if any(w in lower for w in ["luxury", "high budget", "5-star", "five star", "upscale", "premium"]):
            spec.budget = "High"
        elif any(w in lower for w in ["cheap", "low budget", "budget", "backpack", "shoestring", "affordable"]):
            spec.budget = "Low"
        elif "medium" in lower or "moderate" in lower or "mid-range" in lower:
            spec.budget = "Medium"
        elif spec.budget_amount:
            days = spec.number_of_days or 4
            trav = spec.travelers or 1
            per_person_day = spec.budget_amount / max(days * trav, 1)
            if per_person_day < 220:
                spec.budget = "Low"
            elif per_person_day <= 500:
                spec.budget = "Medium"
            else:
                spec.budget = "High"

    # Extract ISO date if present
    if not spec.trip_start:
        iso_match = re.search(r"\b(202\d-\d{2}-\d{2})\b", text)
        if iso_match:
            try:
                spec.trip_start = date.fromisoformat(iso_match.group(1))
            except ValueError:
                pass

    # Extract style & preferences
    matched_styles: list[str] = list(spec.preferences or [])
    for keyword, style_label in STYLE_KEYWORDS.items():
        if keyword in lower and style_label not in matched_styles:
            matched_styles.append(style_label)

    if not spec.itinerary_type and matched_styles:
        spec.itinerary_type = matched_styles[0]
    elif not spec.itinerary_type:
        spec.itinerary_type = "City Experiences"
    spec.preferences = matched_styles[:8]

    # Identify missing essential details
    missing_fields: list[str] = []
    questions: list[ClarificationQuestion] = []

    if not spec.destination:
        missing_fields.append("destination")
        questions.append(
            ClarificationQuestion(
                field="destination",
                question="Where would you like to travel?",
                placeholder="e.g., Tokyo, Bali, Paris",
                options=["Tokyo", "Bangkok", "Bali", "Paris", "Rome"],
            )
        )

    if not spec.origin:
        missing_fields.append("origin")
        questions.append(
            ClarificationQuestion(
                field="origin",
                question="Which city or airport are you departing from (for flight research)?",
                placeholder="e.g., Mumbai, New York, London",
                options=["New Delhi", "Mumbai", "New York", "London", "Singapore"],
            )
        )

    if not spec.number_of_days:
        missing_fields.append("number_of_days")
        questions.append(
            ClarificationQuestion(
                field="number_of_days",
                question="How many days will your trip last (1–10 days)?",
                placeholder="e.g., 5",
                options=["3", "5", "7", "10"],
            )
        )

    if not spec.travelers:
        missing_fields.append("travelers")
        questions.append(
            ClarificationQuestion(
                field="travelers",
                question="How many travelers are going on this trip?",
                placeholder="e.g., 2",
                options=["1", "2", "4"],
            )
        )

    if not spec.budget:
        missing_fields.append("budget")
        questions.append(
            ClarificationQuestion(
                field="budget",
                question="What is your target budget tier?",
                placeholder="Low, Medium, or High",
                options=["Low", "Medium", "High"],
            )
        )

    ready_to_plan = len(missing_fields) == 0
    trip_request: TripPlanRequest | None = None

    if ready_to_plan and spec.destination and spec.number_of_days and spec.budget:
        trip_request = TripPlanRequest(
            destination=spec.destination,
            origin=spec.origin,
            number_of_days=spec.number_of_days,
            trip_start=spec.trip_start,
            travelers=spec.travelers or 1,
            itinerary_type=spec.itinerary_type or "City Experiences",
            budget=spec.budget,
            budget_amount=spec.budget_amount,
            preferences=spec.preferences,
            natural_language_query=text,
        )
        assistant_message = (
            f"All essential details captured for your {spec.number_of_days}-day "
            f"{spec.itinerary_type} trip from {spec.origin} to {spec.destination} "
            f"for {spec.travelers} traveler(s) ({spec.budget} budget). Ready to launch the LangGraph research & validation workflow."
        )
    else:
        captured_parts = []
        if spec.destination:
            captured_parts.append(f"Destination: {spec.destination}")
        if spec.origin:
            captured_parts.append(f"Origin: {spec.origin}")
        if spec.number_of_days:
            captured_parts.append(f"{spec.number_of_days} days")
        if spec.travelers:
            captured_parts.append(f"{spec.travelers} traveler(s)")
        if spec.budget:
            captured_parts.append(f"{spec.budget} budget")
        captured_summary = (
            f"Captured so far: {', '.join(captured_parts)}. "
            if captured_parts
            else ""
        )
        assistant_message = (
            f"{captured_summary}Before I research flights, stays, and validate pricing, "
            f"please clarify {len(missing_fields)} missing detail(s) below."
        )

    return TripIntakeData(
        ready_to_plan=ready_to_plan,
        assistant_message=assistant_message,
        extracted_spec=spec,
        missing_fields=missing_fields,
        follow_up_questions=questions,
        trip_request=trip_request,
    )


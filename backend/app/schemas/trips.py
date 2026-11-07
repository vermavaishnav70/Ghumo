from datetime import date, datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

TripBudget = Literal["Low", "Medium", "High"]
ValidationStatus = Literal["verified", "partially_verified", "unverified_estimates"]
CheckpointStep = Literal["planning", "research", "evaluation", "validation", "review", "booking"]
CheckpointStatus = Literal["completed", "active", "pending", "warning"]
BookingStatus = Literal["awaiting_approval", "approved_ready_to_book"]


class Activity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    time: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    location: str = Field(min_length=1, max_length=200)
    price: int = Field(ge=0)
    duration: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=600)


class DayPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day: str = Field(min_length=1, max_length=100)
    activities: list[Activity] = Field(min_length=1, max_length=8)


class FlightOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=80)
    airline: str = Field(min_length=1, max_length=120)
    flight_number: str = Field(min_length=1, max_length=40)
    origin: str = Field(min_length=1, max_length=120)
    destination: str = Field(min_length=1, max_length=120)
    departure_time: str = Field(min_length=1, max_length=80)
    arrival_time: str = Field(min_length=1, max_length=80)
    duration: str = Field(min_length=1, max_length=60)
    stops: int = Field(ge=0, le=5)
    cabin_class: str = Field(default="Economy", max_length=60)
    baggage_policy: str = Field(default="1 carry-on included", max_length=200)
    price_per_person: int = Field(ge=0)
    total_price: int = Field(ge=0)
    currency: str = Field(default="USD", max_length=10)
    cancellation_terms: str = Field(min_length=1, max_length=240)
    rating: float = Field(ge=0.0, le=5.0)
    fit_score: int = Field(ge=0, le=100)
    fit_reason: str = Field(min_length=1, max_length=300)
    source_name: str = Field(min_length=1, max_length=120)
    booking_url: str = Field(min_length=1, max_length=500)
    verified: bool = False
    verification_note: str = Field(default="", max_length=240)
    recommended: bool = False


class StayOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=160)
    property_type: str = Field(min_length=1, max_length=80)
    neighborhood: str = Field(min_length=1, max_length=120)
    rating: float = Field(ge=0.0, le=5.0)
    price_per_night: int = Field(ge=0)
    total_price: int = Field(ge=0)
    nights: int = Field(default=1, ge=1, le=30)
    currency: str = Field(default="USD", max_length=10)
    cancellation_terms: str = Field(min_length=1, max_length=240)
    amenities: list[str] = Field(default_factory=list, max_length=10)
    fit_score: int = Field(ge=0, le=100)
    fit_reason: str = Field(min_length=1, max_length=300)
    source_name: str = Field(min_length=1, max_length=120)
    booking_url: str = Field(min_length=1, max_length=500)
    verified: bool = False
    verification_note: str = Field(default="", max_length=240)
    recommended: bool = False


class TransportOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=80)
    mode: str = Field(min_length=1, max_length=80)
    provider: str = Field(min_length=1, max_length=120)
    route_summary: str = Field(min_length=1, max_length=200)
    duration: str = Field(min_length=1, max_length=80)
    estimated_cost: int = Field(ge=0)
    currency: str = Field(default="USD", max_length=10)
    cancellation_terms: str = Field(min_length=1, max_length=240)
    fit_score: int = Field(ge=0, le=100)
    fit_reason: str = Field(default="", max_length=240)
    source_name: str = Field(min_length=1, max_length=120)
    booking_url: str = Field(min_length=1, max_length=500)
    verified: bool = False
    verification_note: str = Field(default="", max_length=240)
    recommended: bool = False


class CostBreakdown(BaseModel):
    model_config = ConfigDict(extra="forbid")

    currency: str = Field(default="USD", max_length=10)
    flights_total: int = Field(default=0, ge=0)
    stays_total: int = Field(default=0, ge=0)
    transport_total: int = Field(default=0, ge=0)
    activities_total: int = Field(default=0, ge=0)
    estimated_total: int = Field(default=0, ge=0)
    per_person_total: int = Field(default=0, ge=0)
    travelers: int = Field(default=1, ge=1)
    budget_tier: TripBudget = "Medium"
    budget_target: int = Field(default=1500, ge=0)
    within_budget: bool = True
    exclusions: list[str] = Field(default_factory=list, max_length=12)
    pricing_notes: list[str] = Field(default_factory=list, max_length=10)


class ValidationItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: str = Field(min_length=1, max_length=60)
    item_name: str = Field(min_length=1, max_length=160)
    verified: bool
    status_label: str = Field(min_length=1, max_length=80)
    detail: str = Field(min_length=1, max_length=300)
    source: str = Field(min_length=1, max_length=120)


class ValidationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    validated_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    status: ValidationStatus = "partially_verified"
    verified_count: int = Field(default=0, ge=0)
    unverified_count: int = Field(default=0, ge=0)
    flags: list[str] = Field(default_factory=list, max_length=12)
    items: list[ValidationItem] = Field(default_factory=list, max_length=20)
    exclusions: list[str] = Field(default_factory=list, max_length=12)
    cancellation_summary: str = Field(default="", max_length=400)
    live_sources_used: list[str] = Field(default_factory=list, max_length=12)


class WorkflowCheckpoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step: CheckpointStep
    label: str = Field(min_length=1, max_length=80)
    status: CheckpointStatus
    summary: str = Field(min_length=1, max_length=260)


class BookingLinkItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: str = Field(min_length=1, max_length=60)
    title: str = Field(min_length=1, max_length=160)
    provider: str = Field(min_length=1, max_length=120)
    amount: int = Field(ge=0)
    currency: str = Field(default="USD", max_length=10)
    url: str = Field(min_length=1, max_length=500)
    cancellation_note: str = Field(default="", max_length=240)
    verified: bool = False


class BookingAssistanceState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: BookingStatus = "awaiting_approval"
    require_explicit_approval: bool = True
    approved_by_user: bool = False
    approved_at: datetime | None = None
    approval_notes: str | None = Field(default=None, max_length=400)
    selected_flight_id: str | None = Field(default=None, max_length=80)
    selected_stay_id: str | None = Field(default=None, max_length=80)
    selected_transport_id: str | None = Field(default=None, max_length=80)
    provider_integration_status: str = Field(
        default="guided_redirect_only", max_length=80
    )
    limitation_notice: str = Field(
        default=(
            "Direct payment and instant reservation confirmation APIs are not connected "
            "for these providers. No booking or charge has been made automatically; use "
            "the verified provider links below to complete reservation and payment."
        ),
        max_length=500,
    )
    booking_steps: list[str] = Field(default_factory=list, max_length=12)
    booking_links: list[BookingLinkItem] = Field(default_factory=list, max_length=12)


class TripPlanData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    itinerary: list[DayPlan] = Field(min_length=1, max_length=10)
    flights: list[FlightOption] = Field(default_factory=list, max_length=8)
    stays: list[StayOption] = Field(default_factory=list, max_length=8)
    transport_options: list[TransportOption] = Field(default_factory=list, max_length=8)
    cost_breakdown: CostBreakdown | None = None
    validation_report: ValidationReport | None = None
    booking_state: BookingAssistanceState | None = None
    checkpoints: list[WorkflowCheckpoint] = Field(default_factory=list, max_length=10)
    agent_summary: str | None = Field(default=None, max_length=800)


class ProviderActivity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    time: str
    name: str
    location: str
    price: int | float | str
    duration: str
    description: str


class ProviderDayPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day: str
    activities: list[ProviderActivity]


class ProviderTripPlanData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    itinerary: list[ProviderDayPlan]


class TripPlanMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(default_factory=lambda: str(uuid4()))
    provider: str | None = None
    model: str | None = None
    attempted_providers: list[str] = Field(default_factory=list)
    workflow_engine: str = "langgraph"
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )


class TripPlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    destination: str = Field(min_length=2, max_length=120)
    origin: str | None = Field(default=None, max_length=120)
    number_of_days: int = Field(ge=1, le=10)
    trip_start: date | None = None
    travelers: int = Field(default=1, ge=1, le=20)
    itinerary_type: str = Field(min_length=2, max_length=80)
    budget: TripBudget
    budget_amount: int | None = Field(default=None, ge=50, le=500000)
    preferences: list[str] = Field(default_factory=list, max_length=12)
    natural_language_query: str | None = Field(default=None, max_length=2000)

    @field_validator("destination", "itinerary_type", mode="before")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized_value = str(value).strip()
        if not normalized_value:
            raise ValueError("must not be empty")
        return normalized_value

    @field_validator("origin", "natural_language_query", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized_value = str(value).strip()
        return normalized_value if normalized_value else None


class TripPlanResponseEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool
    data: TripPlanData | None = None
    error: str | None = None
    meta: TripPlanMeta | None = None


class PlannedTripResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: TripPlanData
    meta: TripPlanMeta


class TripEditRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trip_request: TripPlanRequest
    current_itinerary: TripPlanData
    message: str = Field(min_length=1, max_length=2000)

    @field_validator("message", mode="before")
    @classmethod
    def normalize_message(cls, value: str) -> str:
        normalized_value = str(value).strip()
        if not normalized_value:
            raise ValueError("must not be empty")
        return normalized_value


class ClarificationQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str = Field(min_length=1, max_length=60)
    question: str = Field(min_length=1, max_length=240)
    placeholder: str = Field(default="", max_length=120)
    options: list[str] = Field(default_factory=list, max_length=8)


class ExtractedTripSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    destination: str | None = None
    origin: str | None = None
    number_of_days: int | None = None
    trip_start: date | None = None
    travelers: int | None = None
    itinerary_type: str | None = None
    budget: TripBudget | None = None
    budget_amount: int | None = None
    preferences: list[str] = Field(default_factory=list)


class TripIntakeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(min_length=2, max_length=2000)
    current_spec: ExtractedTripSpec | None = None
    answers: dict[str, str | int] = Field(default_factory=dict)

    @field_validator("prompt", mode="before")
    @classmethod
    def normalize_prompt(cls, value: str) -> str:
        normalized = str(value).strip()
        if not normalized:
            raise ValueError("must not be empty")
        return normalized


class TripIntakeData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ready_to_plan: bool
    assistant_message: str = Field(min_length=1, max_length=600)
    extracted_spec: ExtractedTripSpec
    missing_fields: list[str] = Field(default_factory=list)
    follow_up_questions: list[ClarificationQuestion] = Field(default_factory=list)
    trip_request: TripPlanRequest | None = None


class TripIntakeResponseEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool
    data: TripIntakeData | None = None
    error: str | None = None
    meta: TripPlanMeta | None = None


class TripOptionSelectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trip_request: TripPlanRequest
    current_itinerary: TripPlanData
    selected_flight_id: str | None = None
    selected_stay_id: str | None = None
    selected_transport_id: str | None = None


class TripBookingApprovalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trip_request: TripPlanRequest
    current_itinerary: TripPlanData
    approved: bool
    approval_notes: str | None = Field(default=None, max_length=400)


def normalize_provider_trip_plan(payload: ProviderTripPlanData | TripPlanData | dict) -> TripPlanData:
    if isinstance(payload, TripPlanData):
        return payload

    if isinstance(payload, dict) and (
        "flights" in payload
        or "stays" in payload
        or "cost_breakdown" in payload
        or "booking_state" in payload
    ):
        return TripPlanData.model_validate(payload)

    provider_data = (
        payload
        if isinstance(payload, ProviderTripPlanData)
        else ProviderTripPlanData.model_validate(payload)
    )

    normalized_days: list[dict] = []
    for day_index, day in enumerate(provider_data.itinerary[:10], start=1):
        normalized_activities: list[dict] = []
        for activity in day.activities[:8]:
            normalized_activities.append(
                {
                    "time": _normalize_text(activity.time, "09:00 AM"),
                    "name": _normalize_text(activity.name, "Planned activity"),
                    "location": _normalize_text(activity.location, "TBD"),
                    "price": _normalize_price(activity.price),
                    "duration": _normalize_text(activity.duration, "1 hour"),
                    "description": _normalize_text(
                        activity.description,
                        "Enjoy this stop as part of the trip.",
                    ),
                }
            )

        if not normalized_activities:
            normalized_activities.append(
                {
                    "time": "09:00 AM",
                    "name": "Planned activity",
                    "location": "TBD",
                    "price": 0,
                    "duration": "1 hour",
                    "description": "Enjoy this stop as part of the trip.",
                }
            )

        normalized_days.append(
            {
                "day": _normalize_day_label(day.day, day_index),
                "activities": normalized_activities,
            }
        )

    if not normalized_days:
        raise ValueError("Provider returned an empty itinerary.")

    return TripPlanData.model_validate({"itinerary": normalized_days})


def _normalize_text(value: str | None, fallback: str) -> str:
    normalized_value = str(value or "").strip()
    return normalized_value[:600] if normalized_value else fallback


def _normalize_price(value: int | float | str) -> int:
    try:
        normalized_value = int(float(value))
    except (TypeError, ValueError):
        return 0

    return max(normalized_value, 0)


def _normalize_day_label(value: str | None, day_index: int) -> str:
    normalized_value = str(value or "").strip()
    if not normalized_value:
        return f"Day {day_index}"
    if normalized_value.lower().startswith("day "):
        return normalized_value[:100]
    return normalized_value[:100]

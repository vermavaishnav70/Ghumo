import asyncio
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import ValidationError

from app.core.logging import get_logger, log_event
from app.schemas.trips import (
    BookingAssistanceState,
    CostBreakdown,
    DayPlan,
    FlightOption,
    PlannedTripResult,
    StayOption,
    TransportOption,
    TripBookingApprovalRequest,
    TripEditRequest,
    TripOptionSelectionRequest,
    TripPlanData,
    TripPlanMeta,
    TripPlanRequest,
    ValidationReport,
    WorkflowCheckpoint,
    normalize_provider_trip_plan,
)
from app.services.prompts import SYSTEM_INSTRUCTION, build_trip_edit_prompt, build_trip_prompt
from app.services.providers.base import AIProvider, ProviderError
from app.services.travel_tools import (
    build_booking_state,
    compute_cost_breakdown,
    discover_flights,
    discover_stays,
    discover_transport,
    evaluate_and_rank_options,
    validate_trip_options,
)
from app.services.weather import WeatherService, WeatherServiceError

logger = get_logger("wanderlust.agent_graph")


class TripAgentState(TypedDict, total=False):
    mode: str
    request: TripPlanRequest
    edit_request: TripEditRequest | None
    weather_summary: str
    weather_available: bool
    itinerary_days: list[DayPlan]
    flights: list[FlightOption]
    stays: list[StayOption]
    transport_options: list[TransportOption]
    selected_flight_id: str | None
    selected_stay_id: str | None
    selected_transport_id: str | None
    cost_breakdown: CostBreakdown | None
    validation_report: ValidationReport | None
    booking_state: BookingAssistanceState | None
    checkpoints: list[WorkflowCheckpoint]
    agent_summary: str
    meta: TripPlanMeta
    error_message: str | None
    error_status: int | None


class TripAgentWorkflow:
    def __init__(
        self,
        providers: list[AIProvider],
        weather_service: WeatherService | None = None,
    ):
        self._providers = providers
        self._weather_service = weather_service
        self._compiled_graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(TripAgentState)
        workflow.add_node("planning", self._planning_node)
        workflow.add_node("research", self._research_node)
        workflow.add_node("evaluation", self._evaluation_node)
        workflow.add_node("validation", self._validation_node)
        workflow.add_node("review", self._review_node)

        workflow.add_edge(START, "planning")
        workflow.add_conditional_edges(
            "planning",
            self._should_continue_after_planning,
            {
                "research": "research",
                "abort": END,
            },
        )
        workflow.add_edge("research", "evaluation")
        workflow.add_edge("evaluation", "validation")
        workflow.add_edge("validation", "review")
        workflow.add_edge("review", END)
        return workflow.compile()

    @staticmethod
    def _should_continue_after_planning(state: TripAgentState) -> str:
        if state.get("error_message"):
            return "abort"
        return "research"

    async def _planning_node(self, state: TripAgentState) -> dict:
        request = state["request"]
        mode = state.get("mode", "plan")
        edit_req = state.get("edit_request")
        request_id = state["meta"].request_id

        if not self._providers:
            return {
                "error_message": "No AI providers are configured on the backend.",
                "error_status": 503,
                "meta": TripPlanMeta(
                    request_id=request_id,
                    attempted_providers=[],
                ),
            }

        weather_summary = ""
        weather_available = False
        if self._weather_service:
            try:
                weather_summary = await self._weather_service.summarize_weather_for_trip(
                    request
                )
                weather_available = bool(weather_summary)
            except WeatherServiceError as error:
                log_event(
                    logger,
                    "warning",
                    "weather_context_unavailable",
                    destination=request.destination,
                    detail=str(error),
                )

        prompt = (
            build_trip_edit_prompt(edit_req, weather_summary)
            if mode == "edit" and edit_req is not None
            else build_trip_prompt(request, weather_summary)
        )

        attempted_providers: list[str] = []
        for provider in self._providers:
            attempted_providers.append(provider.name)
            try:
                provider_response = await provider.generate_itinerary(
                    system_instruction=SYSTEM_INSTRUCTION,
                    prompt=prompt,
                )
                normalized = normalize_provider_trip_plan(provider_response)
                meta = TripPlanMeta(
                    request_id=request_id,
                    provider=provider.name,
                    model=provider.model_name,
                    attempted_providers=attempted_providers,
                )
                checkpoints = list(state.get("checkpoints") or [])
                checkpoints.append(
                    WorkflowCheckpoint(
                        step="planning",
                        label="1. Planning & Spec",
                        status="completed",
                        summary=(
                            f"Structured {request.number_of_days}-day {request.itinerary_type} "
                            f"itinerary for {request.destination} ({request.travelers} traveler(s), {request.budget} budget)."
                        ),
                    )
                )
                return {
                    "weather_summary": weather_summary,
                    "weather_available": weather_available,
                    "itinerary_days": normalized.itinerary,
                    "meta": meta,
                    "checkpoints": checkpoints,
                }
            except (ProviderError, ValidationError, ValueError) as error:
                log_event(
                    logger,
                    "error",
                    "trip_edit_provider_failed" if mode == "edit" else "trip_provider_failed",
                    provider=provider.name,
                    detail=str(error),
                )

        default_msg = (
            "We couldn't update the itinerary right now. Please try again."
            if mode == "edit"
            else "We couldn't generate an itinerary right now. Please try again."
        )
        return {
            "error_message": default_msg,
            "error_status": 502,
            "meta": TripPlanMeta(
                request_id=request_id,
                attempted_providers=attempted_providers,
            ),
        }

    async def _research_node(self, state: TripAgentState) -> dict:
        request = state["request"]
        edit_req = state.get("edit_request")

        if edit_req and edit_req.current_itinerary.flights and edit_req.current_itinerary.stays:
            flights = edit_req.current_itinerary.flights
            stays = edit_req.current_itinerary.stays
            transport_options = (
                edit_req.current_itinerary.transport_options
                or await discover_transport(request)
            )
        else:
            flights, stays, transport_options = await asyncio.gather(
                discover_flights(request),
                discover_stays(request),
                discover_transport(request),
            )

        checkpoints = list(state.get("checkpoints") or [])
        checkpoints.append(
            WorkflowCheckpoint(
                step="research",
                label="2. Multi-Source Research",
                status="completed",
                summary=(
                    f"Discovered {len(flights)} flight routes, {len(stays)} stays, "
                    f"and {len(transport_options)} local transport options."
                ),
            )
        )
        return {
            "flights": flights,
            "stays": stays,
            "transport_options": transport_options,
            "checkpoints": checkpoints,
        }

    async def _evaluation_node(self, state: TripAgentState) -> dict:
        request = state["request"]
        flights, stays, transport_options, flight_id, stay_id, transport_id = (
            evaluate_and_rank_options(
                request=request,
                flights=state.get("flights") or [],
                stays=state.get("stays") or [],
                transport_options=state.get("transport_options") or [],
                selected_flight_id=state.get("selected_flight_id"),
                selected_stay_id=state.get("selected_stay_id"),
                selected_transport_id=state.get("selected_transport_id"),
            )
        )
        cost_breakdown = compute_cost_breakdown(
            request=request,
            itinerary_days=state.get("itinerary_days") or [],
            flights=flights,
            stays=stays,
            transport_options=transport_options,
            selected_flight_id=flight_id,
            selected_stay_id=stay_id,
            selected_transport_id=transport_id,
        )

        checkpoints = list(state.get("checkpoints") or [])
        checkpoints.append(
            WorkflowCheckpoint(
                step="evaluation",
                label="3. Option Comparison",
                status="completed",
                summary=(
                    f"Ranked candidates by fit score, cancellation terms, and total cost "
                    f"(${cost_breakdown.estimated_total:,} total / ${cost_breakdown.per_person_total:,} per person)."
                ),
            )
        )
        return {
            "flights": flights,
            "stays": stays,
            "transport_options": transport_options,
            "selected_flight_id": flight_id,
            "selected_stay_id": stay_id,
            "selected_transport_id": transport_id,
            "cost_breakdown": cost_breakdown,
            "checkpoints": checkpoints,
        }

    async def _validation_node(self, state: TripAgentState) -> dict:
        request = state["request"]
        cost_breakdown = state["cost_breakdown"]
        assert cost_breakdown is not None

        validation_report = validate_trip_options(
            request=request,
            flights=state.get("flights") or [],
            stays=state.get("stays") or [],
            transport_options=state.get("transport_options") or [],
            cost_breakdown=cost_breakdown,
            weather_available=bool(state.get("weather_available")),
        )

        checkpoints = list(state.get("checkpoints") or [])
        checkpoints.append(
            WorkflowCheckpoint(
                step="validation",
                label="4. Price & Policy Validation",
                status="completed" if validation_report.unverified_count == 0 else "warning",
                summary=(
                    f"{validation_report.verified_count} item(s) verified, "
                    f"{validation_report.unverified_count} market estimate(s) flagged for checkout confirmation."
                ),
            )
        )
        return {
            "validation_report": validation_report,
            "checkpoints": checkpoints,
        }

    async def _review_node(self, state: TripAgentState) -> dict:
        request = state["request"]
        flights = state.get("flights") or []
        stays = state.get("stays") or []
        transport_options = state.get("transport_options") or []
        cost_breakdown = state["cost_breakdown"]
        assert cost_breakdown is not None

        booking_state = build_booking_state(
            request=request,
            flights=flights,
            stays=stays,
            transport_options=transport_options,
            selected_flight_id=state.get("selected_flight_id"),
            selected_stay_id=state.get("selected_stay_id"),
            selected_transport_id=state.get("selected_transport_id"),
            approved=False,
        )

        checkpoints = list(state.get("checkpoints") or [])
        checkpoints.append(
            WorkflowCheckpoint(
                step="review",
                label="5. Review & Approval Gate",
                status="active",
                summary="Awaiting explicit user approval of selected options, exclusions, and cancellation terms.",
            )
        )
        checkpoints.append(
            WorkflowCheckpoint(
                step="booking",
                label="6. Guided Booking Handoff",
                status="pending",
                summary="Locked until explicit approval is granted.",
            )
        )

        origin_label = request.origin or "your departure hub"
        agent_summary = (
            f"Prepared a {request.number_of_days}-day {request.itinerary_type.lower()} plan "
            f"from {origin_label} to {request.destination} for {request.travelers} traveler(s). "
            f"Estimated total is ${cost_breakdown.estimated_total:,} (${cost_breakdown.per_person_total:,}/person) "
            f"against a ${cost_breakdown.budget_target:,} target budget. Review the compared flights, stays, "
            f"and validation flags before approving for booking."
        )

        return {
            "booking_state": booking_state,
            "checkpoints": checkpoints,
            "agent_summary": agent_summary,
        }

    async def run_plan(self, request: TripPlanRequest) -> tuple[TripPlanData | None, TripPlanMeta, str | None, int | None]:
        initial_state: TripAgentState = {
            "mode": "plan",
            "request": request,
            "edit_request": None,
            "checkpoints": [],
            "meta": TripPlanMeta(),
            "error_message": None,
            "error_status": None,
        }
        final_state = await self._compiled_graph.ainvoke(initial_state)
        if final_state.get("error_message"):
            return (
                None,
                final_state["meta"],
                final_state["error_message"],
                final_state.get("error_status") or 502,
            )

        data = TripPlanData(
            itinerary=final_state["itinerary_days"],
            flights=final_state.get("flights") or [],
            stays=final_state.get("stays") or [],
            transport_options=final_state.get("transport_options") or [],
            cost_breakdown=final_state.get("cost_breakdown"),
            validation_report=final_state.get("validation_report"),
            booking_state=final_state.get("booking_state"),
            checkpoints=final_state.get("checkpoints") or [],
            agent_summary=final_state.get("agent_summary"),
        )
        return data, final_state["meta"], None, None

    async def run_edit(self, edit_request: TripEditRequest) -> tuple[TripPlanData | None, TripPlanMeta, str | None, int | None]:
        existing_booking = edit_request.current_itinerary.booking_state
        initial_state: TripAgentState = {
            "mode": "edit",
            "request": edit_request.trip_request,
            "edit_request": edit_request,
            "selected_flight_id": existing_booking.selected_flight_id if existing_booking else None,
            "selected_stay_id": existing_booking.selected_stay_id if existing_booking else None,
            "selected_transport_id": existing_booking.selected_transport_id if existing_booking else None,
            "checkpoints": [],
            "meta": TripPlanMeta(),
            "error_message": None,
            "error_status": None,
        }
        final_state = await self._compiled_graph.ainvoke(initial_state)
        if final_state.get("error_message"):
            return (
                None,
                final_state["meta"],
                final_state["error_message"],
                final_state.get("error_status") or 502,
            )

        data = TripPlanData(
            itinerary=final_state["itinerary_days"],
            flights=final_state.get("flights") or [],
            stays=final_state.get("stays") or [],
            transport_options=final_state.get("transport_options") or [],
            cost_breakdown=final_state.get("cost_breakdown"),
            validation_report=final_state.get("validation_report"),
            booking_state=final_state.get("booking_state"),
            checkpoints=final_state.get("checkpoints") or [],
            agent_summary=final_state.get("agent_summary"),
        )
        return data, final_state["meta"], None, None

    async def select_options(self, payload: TripOptionSelectionRequest) -> PlannedTripResult:
        request = payload.trip_request
        current = payload.current_itinerary

        flights = current.flights or await discover_flights(request)
        stays = current.stays or await discover_stays(request)
        transport_options = current.transport_options or await discover_transport(request)

        existing_booking = current.booking_state
        flight_id = payload.selected_flight_id or (
            existing_booking.selected_flight_id if existing_booking else None
        )
        stay_id = payload.selected_stay_id or (
            existing_booking.selected_stay_id if existing_booking else None
        )
        transport_id = payload.selected_transport_id or (
            existing_booking.selected_transport_id if existing_booking else None
        )

        flights, stays, transport_options, flight_id, stay_id, transport_id = (
            evaluate_and_rank_options(
                request=request,
                flights=flights,
                stays=stays,
                transport_options=transport_options,
                selected_flight_id=flight_id,
                selected_stay_id=stay_id,
                selected_transport_id=transport_id,
            )
        )

        cost_breakdown = compute_cost_breakdown(
            request=request,
            itinerary_days=current.itinerary,
            flights=flights,
            stays=stays,
            transport_options=transport_options,
            selected_flight_id=flight_id,
            selected_stay_id=stay_id,
            selected_transport_id=transport_id,
        )

        validation_report = validate_trip_options(
            request=request,
            flights=flights,
            stays=stays,
            transport_options=transport_options,
            cost_breakdown=cost_breakdown,
            weather_available=request.trip_start is not None,
        )

        booking_state = build_booking_state(
            request=request,
            flights=flights,
            stays=stays,
            transport_options=transport_options,
            selected_flight_id=flight_id,
            selected_stay_id=stay_id,
            selected_transport_id=transport_id,
            approved=False,
        )

        checkpoints = [
            WorkflowCheckpoint(
                step="planning",
                label="1. Planning & Spec",
                status="completed",
                summary=f"{request.number_of_days}-day itinerary active.",
            ),
            WorkflowCheckpoint(
                step="research",
                label="2. Multi-Source Research",
                status="completed",
                summary=f"Compared {len(flights)} flights, {len(stays)} stays, {len(transport_options)} transit options.",
            ),
            WorkflowCheckpoint(
                step="evaluation",
                label="3. Option Comparison",
                status="completed",
                summary=f"Updated selection: ${cost_breakdown.estimated_total:,} total (${cost_breakdown.per_person_total:,}/person).",
            ),
            WorkflowCheckpoint(
                step="validation",
                label="4. Price & Policy Validation",
                status="completed" if validation_report.unverified_count == 0 else "warning",
                summary=f"Re-validated selected options ({validation_report.verified_count} verified, {validation_report.unverified_count} estimated).",
            ),
            WorkflowCheckpoint(
                step="review",
                label="5. Review & Approval Gate",
                status="active",
                summary="Selection changed — review updated cost & policies and approve to unlock booking links.",
            ),
            WorkflowCheckpoint(
                step="booking",
                label="6. Guided Booking Handoff",
                status="pending",
                summary="Awaiting explicit approval of updated selections.",
            ),
        ]

        updated = current.model_copy(
            update={
                "flights": flights,
                "stays": stays,
                "transport_options": transport_options,
                "cost_breakdown": cost_breakdown,
                "validation_report": validation_report,
                "booking_state": booking_state,
                "checkpoints": checkpoints,
            }
        )
        return PlannedTripResult(data=updated, meta=TripPlanMeta())

    async def approve_booking(self, payload: TripBookingApprovalRequest) -> PlannedTripResult:
        request = payload.trip_request
        current = payload.current_itinerary

        flights = current.flights or await discover_flights(request)
        stays = current.stays or await discover_stays(request)
        transport_options = current.transport_options or await discover_transport(request)
        existing_booking = current.booking_state

        flight_id = (
            existing_booking.selected_flight_id
            if existing_booking and existing_booking.selected_flight_id
            else (flights[0].id if flights else None)
        )
        stay_id = (
            existing_booking.selected_stay_id
            if existing_booking and existing_booking.selected_stay_id
            else (stays[0].id if stays else None)
        )
        transport_id = (
            existing_booking.selected_transport_id
            if existing_booking and existing_booking.selected_transport_id
            else (transport_options[0].id if transport_options else None)
        )

        cost_breakdown = current.cost_breakdown or compute_cost_breakdown(
            request=request,
            itinerary_days=current.itinerary,
            flights=flights,
            stays=stays,
            transport_options=transport_options,
            selected_flight_id=flight_id,
            selected_stay_id=stay_id,
            selected_transport_id=transport_id,
        )
        validation_report = current.validation_report or validate_trip_options(
            request=request,
            flights=flights,
            stays=stays,
            transport_options=transport_options,
            cost_breakdown=cost_breakdown,
            weather_available=request.trip_start is not None,
        )

        booking_state = build_booking_state(
            request=request,
            flights=flights,
            stays=stays,
            transport_options=transport_options,
            selected_flight_id=flight_id,
            selected_stay_id=stay_id,
            selected_transport_id=transport_id,
            approved=payload.approved,
            approval_notes=payload.approval_notes,
        )

        checkpoints = [
            WorkflowCheckpoint(
                step="planning",
                label="1. Planning & Spec",
                status="completed",
                summary=f"{request.number_of_days}-day itinerary finalized.",
            ),
            WorkflowCheckpoint(
                step="research",
                label="2. Multi-Source Research",
                status="completed",
                summary="Flights, stays, and local transit options sourced.",
            ),
            WorkflowCheckpoint(
                step="evaluation",
                label="3. Option Comparison",
                status="completed",
                summary=f"Final estimated total: ${cost_breakdown.estimated_total:,}.",
            ),
            WorkflowCheckpoint(
                step="validation",
                label="4. Price & Policy Validation",
                status="completed" if validation_report.unverified_count == 0 else "warning",
                summary="Exclusions and cancellation terms reviewed.",
            ),
            WorkflowCheckpoint(
                step="review",
                label="5. Review & Approval Gate",
                status="completed" if payload.approved else "active",
                summary=(
                    "Explicit user approval recorded."
                    if payload.approved
                    else "Approval revoked or pending; booking links locked."
                ),
            ),
            WorkflowCheckpoint(
                step="booking",
                label="6. Guided Booking Handoff",
                status="active" if payload.approved else "pending",
                summary=(
                    "Guided provider checkout links unlocked. Complete payment on each provider site."
                    if payload.approved
                    else "Locked until explicit approval is granted."
                ),
            ),
        ]

        updated = current.model_copy(
            update={
                "flights": flights,
                "stays": stays,
                "transport_options": transport_options,
                "cost_breakdown": cost_breakdown,
                "validation_report": validation_report,
                "booking_state": booking_state,
                "checkpoints": checkpoints,
            }
        )
        return PlannedTripResult(data=updated, meta=TripPlanMeta())


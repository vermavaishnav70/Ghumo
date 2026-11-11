from dataclasses import dataclass

from app.schemas.trips import (
    PlannedTripResult,
    TripBookingApprovalRequest,
    TripEditRequest,
    TripIntakeData,
    TripIntakeRequest,
    TripOptionSelectionRequest,
    TripPlanMeta,
    TripPlanRequest,
)
from app.services.agent_graph import TripAgentWorkflow
from app.services.providers.base import AIProvider
from app.services.travel_tools import parse_trip_intake
from app.services.weather import WeatherService


@dataclass(frozen=True)
class TripPlanningError(Exception):
    user_message: str
    status_code: int
    meta: TripPlanMeta


class TripPlanningOrchestrator:
    def __init__(self, providers: list[AIProvider], weather_service: WeatherService | None = None):
        self._providers = providers
        self._weather_service = weather_service
        self._workflow = TripAgentWorkflow(
            providers=providers,
            weather_service=weather_service,
        )

    @property
    def provider_names(self) -> list[str]:
        return [provider.name for provider in self._providers]

    async def analyze_intake(self, payload: TripIntakeRequest) -> TripIntakeData:
        return parse_trip_intake(payload)

    async def plan_trip(self, request: TripPlanRequest) -> PlannedTripResult:
        data, meta, error_message, error_status = await self._workflow.run_plan(request)
        if error_message or data is None:
            raise TripPlanningError(
                user_message=error_message or "We couldn't generate an itinerary right now. Please try again.",
                status_code=error_status or 502,
                meta=meta,
            )
        return PlannedTripResult(data=data, meta=meta)

    async def edit_trip(self, request: TripEditRequest) -> PlannedTripResult:
        data, meta, error_message, error_status = await self._workflow.run_edit(request)
        if error_message or data is None:
            raise TripPlanningError(
                user_message=error_message or "We couldn't update the itinerary right now. Please try again.",
                status_code=error_status or 502,
                meta=meta,
            )
        return PlannedTripResult(data=data, meta=meta)

    async def select_options(self, payload: TripOptionSelectionRequest) -> PlannedTripResult:
        return await self._workflow.select_options(payload)

    async def approve_booking(self, payload: TripBookingApprovalRequest) -> PlannedTripResult:
        return await self._workflow.approve_booking(payload)

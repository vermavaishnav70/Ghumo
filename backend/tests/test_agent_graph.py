import asyncio
from fastapi.testclient import TestClient

from app.dependencies import get_orchestrator
from app.main import create_app
from app.schemas.trips import (
    TripBookingApprovalRequest,
    TripIntakeRequest,
    TripOptionSelectionRequest,
    TripPlanRequest,
)
from app.services.orchestrator import TripPlanningOrchestrator
from app.services.providers.base import AIProvider


class StubAIProvider(AIProvider):
    def __init__(self) -> None:
        super().__init__(name="gemini", model_name="gemini-2.5-flash")

    async def generate_itinerary(self, *, system_instruction: str, prompt: str) -> dict:
        return {
            "itinerary": [
                {
                    "day": "Day 1",
                    "activities": [
                        {
                            "time": "09:00 AM",
                            "name": "Sensoji Temple",
                            "location": "Asakusa, Tokyo",
                            "price": 15,
                            "duration": "2 hours",
                            "description": "Explore Tokyo's oldest Buddhist temple.",
                        },
                        {
                            "time": "01:00 PM",
                            "name": "Tsukiji Outer Market",
                            "location": "Chuo City, Tokyo",
                            "price": 30,
                            "duration": "2 hours",
                            "description": "Sample fresh sushi and street food.",
                        },
                    ],
                },
                {
                    "day": "Day 2",
                    "activities": [
                        {
                            "time": "10:00 AM",
                            "name": "Meiji Jingu Shrine",
                            "location": "Shibuya, Tokyo",
                            "price": 10,
                            "duration": "2 hours",
                            "description": "Walk through the forested shrine grounds.",
                        }
                    ],
                },
            ]
        }


def test_intake_asks_follow_up_questions_when_details_missing() -> None:
    orchestrator = TripPlanningOrchestrator(providers=[StubAIProvider()])
    result = asyncio.run(
        orchestrator.analyze_intake(
            TripIntakeRequest(prompt="I want a foodie trip to Tokyo")
        )
    )

    assert result.ready_to_plan is False
    assert result.extracted_spec.destination == "Tokyo"
    assert "origin" in result.missing_fields
    assert "number_of_days" in result.missing_fields
    assert "budget" in result.missing_fields
    assert len(result.follow_up_questions) >= 3


def test_intake_completes_when_all_essential_details_present_or_answered() -> None:
    orchestrator = TripPlanningOrchestrator(providers=[StubAIProvider()])
    result = asyncio.run(
        orchestrator.analyze_intake(
            TripIntakeRequest(
                prompt="Plan a 5-day couple foodie trip from Mumbai to Tokyo under $2400",
            )
        )
    )

    assert result.ready_to_plan is True
    assert result.trip_request is not None
    assert result.trip_request.destination == "Tokyo"
    assert result.trip_request.origin == "Mumbai"
    assert result.trip_request.number_of_days == 5
    assert result.trip_request.travelers == 2
    assert result.trip_request.budget_amount == 2400


def test_langgraph_workflow_populates_candidates_validation_and_checkpoints() -> None:
    orchestrator = TripPlanningOrchestrator(providers=[StubAIProvider()])
    request = TripPlanRequest(
        destination="Tokyo",
        origin="Mumbai",
        number_of_days=3,
        travelers=2,
        itinerary_type="Foodie",
        budget="Medium",
    )

    result = asyncio.run(orchestrator.plan_trip(request))
    data = result.data

    assert len(data.itinerary) == 2
    assert len(data.flights) == 3
    assert len(data.stays) == 3
    assert len(data.transport_options) == 3
    assert data.cost_breakdown is not None
    assert data.cost_breakdown.estimated_total > 0
    assert data.cost_breakdown.travelers == 2
    assert data.validation_report is not None
    assert len(data.validation_report.items) >= 3
    assert len(data.validation_report.exclusions) >= 3
    assert data.booking_state is not None
    assert data.booking_state.status == "awaiting_approval"
    assert data.booking_state.approved_by_user is False
    assert len(data.checkpoints) == 6


def test_select_options_and_approve_booking_endpoints() -> None:
    app = create_app()
    app.dependency_overrides[get_orchestrator] = lambda: TripPlanningOrchestrator(
        providers=[StubAIProvider()]
    )
    client = TestClient(app)

    plan_res = client.post(
        "/api/trips/plan",
        json={
            "destination": "Tokyo",
            "origin": "Mumbai",
            "number_of_days": 3,
            "travelers": 2,
            "itinerary_type": "Foodie",
            "budget": "Medium",
        },
    )
    assert plan_res.status_code == 200
    planned_data = plan_res.json()["data"]

    # Switch to value flight and luxury stay
    select_res = client.post(
        "/api/trips/select-options",
        json={
            "trip_request": {
                "destination": "Tokyo",
                "origin": "Mumbai",
                "number_of_days": 3,
                "travelers": 2,
                "itinerary_type": "Foodie",
                "budget": "Medium",
            },
            "current_itinerary": planned_data,
            "selected_flight_id": "flight-value-saver",
            "selected_stay_id": "stay-signature-retreat",
        },
    )
    assert select_res.status_code == 200
    updated_data = select_res.json()["data"]
    assert updated_data["booking_state"]["selected_flight_id"] == "flight-value-saver"
    assert updated_data["booking_state"]["selected_stay_id"] == "stay-signature-retreat"
    assert updated_data["booking_state"]["approved_by_user"] is False

    # Approve booking
    approve_res = client.post(
        "/api/trips/approve-booking",
        json={
            "trip_request": {
                "destination": "Tokyo",
                "origin": "Mumbai",
                "number_of_days": 3,
                "travelers": 2,
                "itinerary_type": "Foodie",
                "budget": "Medium",
            },
            "current_itinerary": updated_data,
            "approved": True,
            "approval_notes": "Reviewed exclusions and cancellation terms.",
        },
    )
    assert approve_res.status_code == 200
    approved_data = approve_res.json()["data"]
    assert approved_data["booking_state"]["status"] == "approved_ready_to_book"
    assert approved_data["booking_state"]["approved_by_user"] is True
    assert "NOT charged" in approved_data["booking_state"]["limitation_notice"]
    assert len(approved_data["booking_state"]["booking_links"]) == 3


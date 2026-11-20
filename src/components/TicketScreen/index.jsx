import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import BrandHeader from "../Common/BrandHeader/index.jsx";
import { AlertIcon, ArrowRightIcon, CheckIcon, CompassIcon } from "../Common/Icons.jsx";
import { analyzeTripIntake } from "../../utils/apiService.js";
import "./style.css";

const STYLE_OPTIONS = [
  "City Experiences",
  "Foodie",
  "Adventure",
  "Couple friendly",
  "Relaxation",
  "Luxury",
  "Solo travel",
  "Nature",
  "Family friendly",
  "Road Trip",
  "Low budget",
  "Partying",
];

const BUDGET_TIERS = [
  { id: "Low", label: "Low", hint: "Value flights, guesthouses & rail passes" },
  { id: "Medium", label: "Medium", hint: "Direct flights & curated boutique stays" },
  { id: "High", label: "High", hint: "Flexible cabins & signature retreats" },
];

const QUICK_BRIEFS = [
  "I want a foodie trip to Tokyo",
  "Plan a 5-day couple trip from Mumbai to Tokyo under $2600",
  "4-day luxury getaway from London to Paris for 2 adults",
  "6-day adventure trip from New Delhi to Bali for 3 friends with Medium budget",
];

const TicketScreen = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const initialPromptFromState = location.state?.initialPrompt || "";
  const initialIntakeFromState = location.state?.initialIntake || null;

  const [prompt, setPrompt] = useState(initialPromptFromState);
  const [analyzing, setAnalyzing] = useState(false);
  const [intakeResult, setIntakeResult] = useState(initialIntakeFromState);
  const [clarificationAnswers, setClarificationAnswers] = useState({});
  const [error, setError] = useState("");

  const [destination, setDestination] = useState("");
  const [origin, setOrigin] = useState("");
  const [numberOfDays, setNumberOfDays] = useState(4);
  const [tripStart, setTripStart] = useState("");
  const [travelers, setTravelers] = useState(2);
  const [itineraryType, setItineraryType] = useState("City Experiences");
  const [budget, setBudget] = useState("Medium");
  const [budgetAmount, setBudgetAmount] = useState("");
  const [preferences, setPreferences] = useState(["City Experiences"]);

  const syncSpecToForm = (spec) => {
    if (!spec) return;
    if (spec.destination) setDestination(spec.destination);
    if (spec.origin) setOrigin(spec.origin);
    if (spec.number_of_days) setNumberOfDays(spec.number_of_days);
    if (spec.trip_start) setTripStart(spec.trip_start);
    if (spec.travelers) setTravelers(spec.travelers);
    if (spec.itinerary_type) setItineraryType(spec.itinerary_type);
    if (spec.budget) setBudget(spec.budget);
    if (spec.budget_amount) setBudgetAmount(String(spec.budget_amount));
    if (spec.preferences?.length) setPreferences(spec.preferences);
  };

  const runIntakeAnalysis = async (promptText, extraAnswers = {}) => {
    const trimmed = (promptText ?? prompt).trim();
    if (!trimmed) {
      setError("Describe your trip first or complete the specification fields on the right.");
      return;
    }

    setAnalyzing(true);
    setError("");
    try {
      const result = await analyzeTripIntake({
        prompt: trimmed,
        current_spec: intakeResult?.extracted_spec || null,
        answers: extraAnswers,
      });
      setIntakeResult(result);
      syncSpecToForm(result.extracted_spec);
    } catch (err) {
      setError(err.message || "Could not analyze travel brief.");
    } finally {
      setAnalyzing(false);
    }
  };

  useEffect(() => {
    if (initialIntakeFromState?.extracted_spec) {
      syncSpecToForm(initialIntakeFromState.extracted_spec);
      return;
    }
    if (initialPromptFromState) {
      runIntakeAnalysis(initialPromptFromState);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialPromptFromState]);

  const handleClarificationChange = (field, value) => {
    setClarificationAnswers((prev) => ({ ...prev, [field]: value }));
    if (field === "destination") setDestination(String(value));
    if (field === "origin") setOrigin(String(value));
    if (field === "number_of_days") setNumberOfDays(Number(value) || 3);
    if (field === "travelers") setTravelers(Number(value) || 1);
    if (field === "budget") setBudget(String(value));
  };

  const handleApplyClarifications = async () => {
    await runIntakeAnalysis(prompt, clarificationAnswers);
  };

  const togglePreference = (style) => {
    setItineraryType(style);
    setPreferences((prev) =>
      prev.includes(style)
        ? prev.length > 1
          ? prev.filter((item) => item !== style)
          : prev
        : [...prev, style]
    );
  };

  const handleLaunchPlanner = (event) => {
    event?.preventDefault?.();
    const cleanDestination = destination.trim();
    if (!cleanDestination) {
      setError("Enter a destination or analyze a travel brief before building your timetable.");
      return;
    }

    const days = Math.max(1, Math.min(Number(numberOfDays) || 3, 10));
    const pax = Math.max(1, Math.min(Number(travelers) || 1, 20));
    const parsedBudgetAmount = budgetAmount ? Number(budgetAmount) : null;

    const tripRequest = {
      destination: cleanDestination,
      origin: origin.trim() || "New Delhi",
      number_of_days: days,
      trip_start: tripStart || null,
      travelers: pax,
      itinerary_type: itineraryType || "City Experiences",
      budget: budget || "Medium",
      budget_amount:
        parsedBudgetAmount && parsedBudgetAmount >= 50 ? parsedBudgetAmount : null,
      preferences,
      natural_language_query: prompt.trim() || null,
    };

    navigate("/your-itinerary", {
      state: {
        tripRequest,
        inputValues: {
          1: tripRequest.destination,
          2: tripRequest.number_of_days,
          3: tripRequest.trip_start,
          4: tripRequest.itinerary_type,
          5: tripRequest.budget,
        },
      },
    });
  };

  return (
    <div className="studio-shell">
      <BrandHeader />

      <main className="studio-main">
        <div className="studio-header">
          <h1 className="studio-title">Trip Intake Studio</h1>
          <p className="studio-subtitle">
            Describe your trip in plain words—Ghumo will capture every detail and ask
            short follow-ups if anything essential is missing—or edit the dispatch spec directly.
          </p>
        </div>

        {error ? (
          <div className="studio-error-banner" role="alert">
            <AlertIcon size={16} />
            <span>{error}</span>
          </div>
        ) : null}

        <div className="studio-grid">
          <section className="studio-card studio-ai-pane">
            <div className="studio-card-head">
              <h2 className="studio-card-title">Describe Your Trip</h2>
              <span className="studio-badge-pine">Conversational Intake</span>
            </div>

            <p className="studio-card-desc">
              Include where you want to go, departure city, days, travelers, and target
              budget. Try an incomplete line to see how Ghumo clarifies missing essentials.
            </p>

            <textarea
              className="studio-prompt-textarea"
              rows={4}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g., Plan a 5-day couple foodie trip from Mumbai to Tokyo in November under $2500..."
            />

            <div className="studio-quick-briefs">
              <span className="studio-quick-label">Sample trip briefs</span>
              <div className="studio-quick-chips">
                {QUICK_BRIEFS.map((sample) => (
                  <button
                    key={sample}
                    type="button"
                    className="studio-quick-chip"
                    onClick={() => {
                      setPrompt(sample);
                      runIntakeAnalysis(sample);
                    }}
                  >
                    {sample}
                  </button>
                ))}
              </div>
            </div>

            <div className="studio-ai-actions">
              <button
                type="button"
                className="studio-btn-analyze"
                disabled={analyzing}
                onClick={() => runIntakeAnalysis(prompt, clarificationAnswers)}
              >
                <CompassIcon size={16} />
                <span>
                  {analyzing
                    ? "Checking travel brief..."
                    : "Check Brief & Missing Details"}
                </span>
              </button>
            </div>

            {intakeResult ? (
              <div
                className={`studio-intake-feedback ${
                  intakeResult.ready_to_plan ? "ready" : "needs-info"
                }`}
              >
                <div className="studio-intake-status-row">
                  <span
                    className={`studio-status-pill ${
                      intakeResult.ready_to_plan ? "pine" : "saffron"
                    }`}
                  >
                    {intakeResult.ready_to_plan ? (
                      <>
                        <CheckIcon size={13} />
                        <span>Specification Complete</span>
                      </>
                    ) : (
                      <>
                        <AlertIcon size={13} />
                        <span>
                          {intakeResult.missing_fields.length} Follow-Up Question(s)
                        </span>
                      </>
                    )}
                  </span>
                </div>
                <p className="studio-intake-message">{intakeResult.assistant_message}</p>

                {intakeResult.follow_up_questions?.length > 0 ? (
                  <div className="studio-clarification-list">
                    {intakeResult.follow_up_questions.map((q) => (
                      <div className="studio-clarification-item" key={q.field}>
                        <label className="studio-clarification-question">
                          {q.question}
                        </label>
                        {q.options?.length > 0 ? (
                          <div className="studio-clarification-options">
                            {q.options.map((opt) => (
                              <button
                                key={opt}
                                type="button"
                                className={`studio-option-pill ${
                                  String(clarificationAnswers[q.field] || "") === String(opt)
                                    ? "selected"
                                    : ""
                                }`}
                                onClick={() => handleClarificationChange(q.field, opt)}
                              >
                                {opt}
                              </button>
                            ))}
                          </div>
                        ) : null}
                        <input
                          type="text"
                          className="studio-input compact"
                          placeholder={q.placeholder || "Type your answer..."}
                          value={clarificationAnswers[q.field] ?? ""}
                          onChange={(e) =>
                            handleClarificationChange(q.field, e.target.value)
                          }
                        />
                      </div>
                    ))}
                    <button
                      type="button"
                      className="studio-btn-secondary"
                      disabled={analyzing}
                      onClick={handleApplyClarifications}
                    >
                      Apply Answers & Re-Check Spec
                    </button>
                  </div>
                ) : null}
              </div>
            ) : null}
          </section>

          <form className="studio-card studio-form-pane" onSubmit={handleLaunchPlanner}>
            <div className="studio-card-head">
              <h2 className="studio-card-title">Route & Budget Specification</h2>
              <span className="studio-badge-saffron">Dispatch Ledger</span>
            </div>

            <div className="studio-form-grid-2">
              <div className="studio-field">
                <label className="studio-label" htmlFor="studio-origin">
                  Departure City / Airport
                </label>
                <input
                  id="studio-origin"
                  type="text"
                  className="studio-input"
                  placeholder="e.g., Mumbai, New York, London"
                  value={origin}
                  onChange={(e) => setOrigin(e.target.value)}
                />
              </div>

              <div className="studio-field">
                <label className="studio-label" htmlFor="studio-destination">
                  Destination *
                </label>
                <input
                  id="studio-destination"
                  type="text"
                  className="studio-input"
                  placeholder="e.g., Tokyo, Bangkok, Paris"
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="studio-form-grid-3">
              <div className="studio-field">
                <label className="studio-label" htmlFor="studio-days">
                  Duration (1–10 Days)
                </label>
                <input
                  id="studio-days"
                  type="number"
                  min={1}
                  max={10}
                  className="studio-input tabular"
                  value={numberOfDays}
                  onChange={(e) =>
                    setNumberOfDays(Math.max(1, Math.min(Number(e.target.value) || 1, 10)))
                  }
                />
              </div>

              <div className="studio-field">
                <label className="studio-label" htmlFor="studio-travelers">
                  Travelers
                </label>
                <input
                  id="studio-travelers"
                  type="number"
                  min={1}
                  max={20}
                  className="studio-input tabular"
                  value={travelers}
                  onChange={(e) =>
                    setTravelers(Math.max(1, Math.min(Number(e.target.value) || 1, 20)))
                  }
                />
              </div>

              <div className="studio-field">
                <label className="studio-label" htmlFor="studio-date">
                  Start Date (Optional)
                </label>
                <input
                  id="studio-date"
                  type="date"
                  className="studio-input tabular"
                  value={tripStart}
                  onChange={(e) => setTripStart(e.target.value)}
                />
              </div>
            </div>

            <div className="studio-field">
              <label className="studio-label">Budget Tier</label>
              <div className="studio-budget-cards">
                {BUDGET_TIERS.map((tier) => (
                  <button
                    key={tier.id}
                    type="button"
                    className={`studio-budget-card ${
                      budget === tier.id ? "active" : ""
                    }`}
                    onClick={() => setBudget(tier.id)}
                  >
                    <div className="studio-budget-card-title">{tier.label}</div>
                    <div className="studio-budget-card-hint">{tier.hint}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="studio-field">
              <label className="studio-label" htmlFor="studio-budget-amount">
                Optional Total Budget Cap (USD $)
              </label>
              <input
                id="studio-budget-amount"
                type="number"
                min={100}
                step={50}
                className="studio-input tabular"
                placeholder="Leave blank for tier default (e.g., 2500)"
                value={budgetAmount}
                onChange={(e) => setBudgetAmount(e.target.value)}
              />
            </div>

            <div className="studio-field">
              <label className="studio-label">
                Travel Style & Interests
              </label>
              <div className="studio-style-chips">
                {STYLE_OPTIONS.map((style) => {
                  const isSelected =
                    itineraryType === style || preferences.includes(style);
                  return (
                    <button
                      key={style}
                      type="button"
                      className={`studio-style-chip ${isSelected ? "active" : ""}`}
                      onClick={() => togglePreference(style)}
                    >
                      {style}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="studio-submit-bar">
              <div className="studio-spec-summary">
                <span className="studio-spec-summary-label">Active Route</span>
                <span className="studio-spec-summary-value tabular">
                  {origin.trim() || "New Delhi"} →{" "}
                  <strong>{destination.trim() || "Select Destination"}</strong> ·{" "}
                  {numberOfDays}d · {travelers} pax · {budget}
                  {budgetAmount ? ` ($${budgetAmount})` : ""}
                </span>
              </div>

              <button type="submit" className="studio-btn-launch">
                <span>Build Timetable & Compare Options</span>
                <ArrowRightIcon size={16} />
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};

export default TicketScreen;

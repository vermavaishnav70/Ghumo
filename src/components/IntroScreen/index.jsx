import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import BrandHeader from "../Common/BrandHeader/index.jsx";
import FlightArc from "../Common/FlightArc.jsx";
import {
  ArrowRightIcon,
  CheckIcon,
  HotelIcon,
  PinIcon,
  PlaneIcon,
  SparkIcon,
  TrainIcon,
} from "../Common/Icons.jsx";
import { analyzeTripIntake } from "../../utils/apiService.js";
import "./style.css";

const SAMPLE_TRIPS = [
  {
    id: "tokyo",
    label: "Mumbai to Tokyo · 5 Days",
    prompt:
      "5-day couple trip from Mumbai to Tokyo in November under $2,600, love ramen and quiet shrines",
    chips: ["BOM → TYO", "5 Days · 2 Pax", "Cap $2,600"],
    originCode: "BOM",
    destinationCode: "TYO",
    flightCaption: "Nonstop Air Corridor · 7h 25m",
    routeTitle: "Mumbai → Tokyo · 5 Days",
    subtitle: "Sample Verified Dispatch · 2 Travelers",
    total: "$1,975",
    budgetNote: "within $2,600 budget",
    legs: [
      {
        code: "08:15 DEP",
        kind: "flight",
        title: "Nonstop Air · WL-104",
        detail: "23kg checked bag · 24h free cancel",
        price: "$1,040",
      },
      {
        code: "DAY 1–5",
        kind: "stay",
        title: "Asakusa Atelier Hotel",
        detail: "4.7 rating · Free cancel 48h prior",
        price: "$725",
      },
      {
        code: "PASS",
        kind: "transit",
        title: "Suica + Narita Express",
        detail: "Illustrative municipal rail fare",
        price: "$120",
        verified: true,
      },
      {
        code: "DAY 01",
        kind: "activity",
        title: "Sensoji & Tsukiji Market",
        detail: "Quiet shrines & morning ramen route",
        price: "$90",
      },
    ],
  },
  {
    id: "bali",
    label: "Singapore to Bali · 6 Days",
    prompt:
      "6-day relaxation trip from Singapore to Bali for 2 adults with a Medium budget",
    chips: ["SIN → DPS", "6 Days · 2 Pax", "Medium Tier"],
    originCode: "SIN",
    destinationCode: "DPS",
    flightCaption: "Direct Morning Jet · 2h 45m",
    routeTitle: "Singapore → Bali · 6 Days",
    subtitle: "Sample Verified Dispatch · 2 Travelers",
    total: "$1,480",
    budgetNote: "within $2,200 target",
    legs: [
      {
        code: "09:40 DEP",
        kind: "flight",
        title: "Direct Morning Jet · WL-208",
        detail: "Carry-on + 20kg bag · 24h free cancel",
        price: "$460",
      },
      {
        code: "DAY 1–6",
        kind: "stay",
        title: "Ubud Rice Terrace Retreat",
        detail: "4.8 rating · Breakfast & 48h cancel",
        price: "$780",
      },
      {
        code: "TRANSFER",
        kind: "transit",
        title: "Private Driver + Airport Pickup",
        detail: "Fixed daily island charter estimate",
        price: "$140",
        verified: true,
      },
      {
        code: "DAY 01",
        kind: "activity",
        title: "Campuhan Ridge & Tirta Empul",
        detail: "Unhurried arrival afternoon",
        price: "$100",
      },
    ],
  },
  {
    id: "paris",
    label: "London to Paris · 4 Days",
    prompt:
      "4-day luxury city experience from London to Paris for 2 travelers under $4,800",
    chips: ["LON → PAR", "4 Days · 2 Pax", "Cap $4,800"],
    originCode: "LON",
    destinationCode: "PAR",
    flightCaption: "Channel Express Corridor · 1h 20m",
    routeTitle: "London → Paris · 4 Days",
    subtitle: "Sample Verified Dispatch · 2 Travelers",
    total: "$2,890",
    budgetNote: "within $4,800 budget",
    legs: [
      {
        code: "08:31 DEP",
        kind: "flight",
        title: "Express Air / Rail · WL-412",
        detail: "Flexible ticket · Free date changes",
        price: "$680",
      },
      {
        code: "DAY 1–4",
        kind: "stay",
        title: "Saint-Germain Boutique Folio",
        detail: "4.9 rating · Free cancel 24h prior",
        price: "$1,840",
      },
      {
        code: "PASS",
        kind: "transit",
        title: "Navigo 4-Day Zone 1–5 Pass",
        detail: "Published Paris metro & RER tariff",
        price: "$110",
        verified: true,
      },
      {
        code: "DAY 01",
        kind: "activity",
        title: "Orsay Morning & Seine Walk",
        detail: "Timed entry + bistro supper",
        price: "$260",
      },
    ],
  },
];

const DISPATCH_RULES = [
  {
    stage: "Clarify essentials first",
    detail:
      "Describe a trip in your own words. If departure city, traveler count, dates, or budget are missing, Ghumo asks short follow-up questions before planning.",
    outcome: "Structured trip specification",
  },
  {
    stage: "Compare flights, stays, and transit together",
    detail:
      "Instead of juggling fourteen browser tabs, review nonstop vs. saver flights, vetted stays, and local transit side by side with cancellation rules and fit scores.",
    outcome: "One unified Bookings ledger",
  },
  {
    stage: "Label live prices vs. market estimates honestly",
    detail:
      "When direct provider APIs are not connected, Ghumo flags estimated fares and surfaces exclusions such as local tourist taxes or checked baggage upfront.",
    outcome: "Zero hidden surprises",
  },
  {
    stage: "Require explicit approval before booking",
    detail:
      "Ghumo never treats a payment or reservation as completed on its own. Review your itemized total, check the confirmation box, and open verified provider links.",
    outcome: "Traveler stays in control",
  },
];

const renderLegIcon = (kind) => {
  if (kind === "flight") return <PlaneIcon size={14} />;
  if (kind === "stay") return <HotelIcon size={14} />;
  if (kind === "transit") return <TrainIcon size={14} />;
  return <PinIcon size={14} />;
};

const IntroScreen = () => {
  const navigate = useNavigate();
  const [selectedSampleId, setSelectedSampleId] = useState(SAMPLE_TRIPS[0].id);
  const [promptText, setPromptText] = useState(SAMPLE_TRIPS[0].prompt);
  const [submitting, setSubmitting] = useState(false);

  const activeSample =
    SAMPLE_TRIPS.find((item) => item.id === selectedSampleId) || SAMPLE_TRIPS[0];

  const handleSelectSample = (sample) => {
    setSelectedSampleId(sample.id);
    setPromptText(sample.prompt);
  };

  const handleBuildTimetable = async (event) => {
    event.preventDefault();
    const trimmed = promptText.trim();
    if (!trimmed) {
      navigate("/fill-details");
      return;
    }

    setSubmitting(true);
    try {
      const intake = await analyzeTripIntake({ prompt: trimmed });
      if (intake?.ready_to_plan && intake?.trip_request) {
        navigate("/your-itinerary", {
          state: {
            tripRequest: intake.trip_request,
            inputValues: {
              1: intake.trip_request.destination,
              2: intake.trip_request.number_of_days,
              3: intake.trip_request.trip_start,
              4: intake.trip_request.itinerary_type,
              5: intake.trip_request.budget,
            },
          },
        });
        return;
      }
      navigate("/fill-details", {
        state: {
          initialPrompt: trimmed,
          initialIntake: intake,
        },
      });
    } catch {
      navigate("/fill-details", {
        state: { initialPrompt: trimmed },
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="intro-shell">
      <div className="intro-scenic-top" aria-hidden="true">
        <img
          src="/assets/hero-coastal.jpg"
          alt=""
          className="intro-coastal-photo"
          loading="eager"
          decoding="async"
        />
        <div className="intro-coastal-fade" />
      </div>

      <div className="intro-scenic-bottom" aria-hidden="true">
        <img
          src="/assets/footer-clouds-wing.jpg"
          alt=""
          className="intro-wing-photo"
          loading="lazy"
          decoding="async"
        />
        <div className="intro-wing-fade" />
      </div>

      <BrandHeader />

      <main className="intro-main">
        <section className="intro-hero-band">
          <div className="intro-hero-copy">
            <h1 className="intro-hero-title">
              One{" "}
              <span className="intro-hero-warm">
                warm
                <svg
                  className="intro-warm-stroke"
                  viewBox="0 0 132 14"
                  fill="none"
                  aria-hidden="true"
                >
                  <path
                    d="M3 10.5C38 3.5 92 2.5 129 7.5"
                    stroke="currentColor"
                    strokeWidth="4"
                    strokeLinecap="round"
                  />
                </svg>
              </span>{" "}
              timetable from prompt to booking.
            </h1>
            <p className="intro-hero-subtitle">
              Describe your trip in plain words. Ghumo asks only for missing
              details, compares flights, stays, and transit side by side, flags
              estimates honestly, and waits for your approval before booking.
            </p>

            <form className="intro-composer-card" onSubmit={handleBuildTimetable}>
              <label htmlFor="home-trip-prompt" className="intro-composer-label">
                <span className="intro-composer-spark" aria-hidden="true">
                  <SparkIcon size={12} />
                </span>
                <span>Describe your trip</span>
              </label>
              <textarea
                id="home-trip-prompt"
                className="intro-composer-textarea"
                rows={3}
                value={promptText}
                onChange={(e) => setPromptText(e.target.value)}
                placeholder="e.g., 5-day couple trip from Mumbai to Tokyo in November under $2,600..."
              />

              <div className="intro-sample-switcher">
                {SAMPLE_TRIPS.map((sample) => (
                  <button
                    key={sample.id}
                    type="button"
                    className={`intro-sample-tab ${
                      sample.id === activeSample.id ? "active" : ""
                    }`}
                    onClick={() => handleSelectSample(sample)}
                  >
                    {sample.label}
                  </button>
                ))}
              </div>

              <div className="intro-composer-footer">
                <div className="intro-chip-group">
                  {activeSample.chips.map((chip) => (
                    <span className="intro-spec-chip tabular" key={chip}>
                      {chip}
                    </span>
                  ))}
                </div>

                <div className="intro-composer-actions">
                  <Link to="/fill-details" className="intro-studio-link">
                    Open full studio
                  </Link>
                  <button
                    type="submit"
                    className="intro-build-btn"
                    disabled={submitting}
                  >
                    <span>{submitting ? "Checking brief..." : "Build Timetable"}</span>
                    <ArrowRightIcon size={16} />
                  </button>
                </div>
              </div>
            </form>
          </div>

          <aside
            className="intro-timetable-card"
            aria-label="Sample trip timetable preview"
          >
            <div className="intro-timetable-head" key={`head-${activeSample.id}`}>
              <div>
                <h2 className="intro-timetable-route">{activeSample.routeTitle}</h2>
                <p className="intro-timetable-sub">{activeSample.subtitle}</p>
              </div>
              <span className="intro-verified-seal">
                <CheckIcon size={13} />
                <span>SAMPLE TIMETABLE</span>
              </span>
            </div>

            <FlightArc
              key={`arc-${activeSample.id}`}
              originCode={activeSample.originCode}
              destinationCode={activeSample.destinationCode}
              caption={activeSample.flightCaption}
              compact
            />

            <div className="intro-timetable-divider">
              <span className="intro-notch left" aria-hidden="true" />
              <span className="intro-dashed-rule" aria-hidden="true" />
              <span className="intro-notch right" aria-hidden="true" />
            </div>

            <div className="intro-leg-list" key={`legs-${activeSample.id}`}>
              {activeSample.legs.map((leg, idx) => (
                <div
                  className="intro-leg-row"
                  key={leg.code + idx}
                  style={{ "--row-delay": `${idx * 45}ms` }}
                >
                  <div className="intro-leg-marker-col">
                    <span className="intro-leg-dot">
                      {renderLegIcon(leg.kind)}
                    </span>
                    {idx < activeSample.legs.length - 1 ? (
                      <span className="intro-leg-track" aria-hidden="true" />
                    ) : null}
                  </div>
                  <div className="intro-leg-code tabular">{leg.code}</div>
                  <div className="intro-leg-info">
                    <div className="intro-leg-title-line">
                      <strong>{leg.title}</strong>
                      {leg.verified ? (
                        <span className="intro-inline-seal">Sample Tariff</span>
                      ) : null}
                    </div>
                    <div className="intro-leg-detail">{leg.detail}</div>
                  </div>
                  <div className="intro-leg-price tabular">{leg.price}</div>
                </div>
              ))}
            </div>

            <div className="intro-timetable-divider">
              <span className="intro-notch left" aria-hidden="true" />
              <span className="intro-dashed-rule" aria-hidden="true" />
              <span className="intro-notch right" aria-hidden="true" />
            </div>

            <div className="intro-timetable-foot">
              <div>
                <div className="intro-total-label">Estimated total</div>
                <div className="intro-total-note">{activeSample.budgetNote}</div>
              </div>
              <div className="intro-total-amount tabular">{activeSample.total}</div>
            </div>
          </aside>
        </section>

        <section id="booking-guide" className="intro-ledger-section">
          <div className="intro-postmark-watermark" aria-hidden="true">
            <svg width="260" height="86" viewBox="0 0 260 86" fill="none">
              <circle cx="38" cy="44" r="24" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 2" />
              <circle cx="38" cy="44" r="16" stroke="currentColor" strokeWidth="1" />
              <ellipse cx="38" cy="44" rx="8" ry="16" stroke="currentColor" strokeWidth="1" />
              <path d="M22 44h32M25 36h26M25 52h26" stroke="currentColor" strokeWidth="0.9" />
              <path d="M62 34c18-5 24 6 42 1M62 44c18-5 24 6 42 1M62 54c18-5 24 6 42 1" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round" />
              <path d="M114 48 Q 185 18 254 38" stroke="currentColor" strokeWidth="1.2" strokeDasharray="5 5" />
            </svg>
          </div>

          <div className="intro-ledger-head">
            <h2 className="intro-ledger-title">
              How Ghumo prepares a trip before you commit to booking
            </h2>
            <p className="intro-ledger-sub">
              Every recommendation separates confirmed facts from estimates and keeps
              final booking approval in your hands.
            </p>
          </div>

          <div className="intro-ledger-table">
            {DISPATCH_RULES.map((row) => (
              <div className="intro-ledger-row" key={row.stage}>
                <div className="intro-ledger-stage">{row.stage}</div>
                <div className="intro-ledger-detail">{row.detail}</div>
                <div className="intro-ledger-outcome">{row.outcome}</div>
              </div>
            ))}
          </div>

          <div className="intro-ledger-cta-bar">
            <span>Ready to plan your own route with flights, stays, and daily stops?</span>
            <Link to="/fill-details" className="intro-secondary-cta">
              <span>Configure in Trip Studio</span>
              <ArrowRightIcon size={15} />
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
};

export default IntroScreen;

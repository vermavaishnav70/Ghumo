import { useState } from "react";
import {
  AlertIcon,
  CheckIcon,
  ExternalLinkIcon,
  FlightJetIcon,
  HotelIcon,
  LockIcon,
  PinIcon,
  PlaneIcon,
  StarIcon,
  TrainIcon,
} from "../Common/Icons.jsx";
import "./style.css";

const WORKSPACE_TABS = [
  { id: "timeline", label: "Timeline" },
  { id: "bookings", label: "Bookings" },
  { id: "review", label: "Review & Book" },
];

const BOOKING_FILTERS = [
  { id: "all", label: "All Options" },
  { id: "flights", label: "Flights" },
  { id: "stays", label: "Stays & Hotels" },
  { id: "transit", label: "Local Transit" },
];

const AgenticBookingHub = ({
  data,
  activeTab,
  onTabChange,
  onSelectOptions,
  onApproveBooking,
  updatingOptions = false,
  approvingBooking = false,
  children,
}) => {
  const [bookingFilter, setBookingFilter] = useState("all");
  const [confirmChecked, setConfirmChecked] = useState(false);
  const [approvalNotes, setApprovalNotes] = useState("");

  const flights = data?.flights || [];
  const stays = data?.stays || [];
  const transportOptions = data?.transport_options || [];
  const costBreakdown = data?.cost_breakdown;
  const validationReport = data?.validation_report;
  const bookingState = data?.booking_state;
  const checkpoints = data?.checkpoints || [];

  const selectedFlightId =
    bookingState?.selected_flight_id ||
    flights.find((f) => f.recommended)?.id ||
    flights[0]?.id;
  const selectedStayId =
    bookingState?.selected_stay_id ||
    stays.find((s) => s.recommended)?.id ||
    stays[0]?.id;
  const selectedTransportId =
    bookingState?.selected_transport_id ||
    transportOptions.find((t) => t.recommended)?.id ||
    transportOptions[0]?.id;

  const isApproved = Boolean(bookingState?.approved_by_user);

  const handleStepClick = (stepName) => {
    if (stepName === "planning") onTabChange("timeline");
    if (stepName === "research" || stepName === "evaluation") onTabChange("bookings");
    if (stepName === "validation" || stepName === "review" || stepName === "booking") {
      onTabChange("review");
    }
  };

  const showFlights = bookingFilter === "all" || bookingFilter === "flights";
  const showStays = bookingFilter === "all" || bookingFilter === "stays";
  const showTransit = bookingFilter === "all" || bookingFilter === "transit";

  return (
    <div className="agentic-hub">
      {/* Unified Dispatch Progress & Cost Summary Folio */}
      <div className="dispatch-folio-bar">
        {data?.agent_summary ? (
          <p className="dispatch-summary-copy">{data.agent_summary}</p>
        ) : null}

        {checkpoints.length > 0 ? (
          <div className="dispatch-checkpoint-rail" role="list" aria-label="Trip planning progress">
            {checkpoints.map((cp, idx) => (
              <button
                key={cp.step}
                type="button"
                role="listitem"
                className={`dispatch-checkpoint-step status-${cp.status}`}
                onClick={() => handleStepClick(cp.step)}
                title={cp.summary}
              >
                <span className={`dispatch-step-marker status-${cp.status}`}>
                  {cp.status === "completed" ? (
                    <CheckIcon size={11} />
                  ) : cp.status === "warning" ? (
                    <AlertIcon size={11} />
                  ) : (
                    <span className="tabular">{idx + 1}</span>
                  )}
                </span>
                <span className="dispatch-step-label">{cp.label.replace(/^\d+\.\s*/, "")}</span>
              </button>
            ))}
          </div>
        ) : null}

        {costBreakdown ? (
          <div className="dispatch-ledger-strip">
            <div className="dispatch-ledger-cell">
              <span className="dispatch-cell-key">Estimated Total</span>
              <span className="dispatch-cell-val tabular">
                ${costBreakdown.estimated_total.toLocaleString()}
                <small> (${costBreakdown.per_person_total.toLocaleString()}/pax)</small>
              </span>
            </div>
            <div className="dispatch-ledger-cell">
              <span className="dispatch-cell-key">Budget Target</span>
              <span
                className={`dispatch-inline-tag ${
                  costBreakdown.within_budget ? "pine" : "terracotta"
                } tabular`}
              >
                ${costBreakdown.budget_target.toLocaleString()} ·{" "}
                {costBreakdown.within_budget ? "Within Budget" : "Over Target"}
              </span>
            </div>
            <div className="dispatch-ledger-cell">
              <span className="dispatch-cell-key">Price Validation</span>
              <span
                className={`dispatch-inline-tag ${
                  validationReport?.unverified_count === 0 ? "pine" : "saffron"
                } tabular`}
              >
                {validationReport?.verified_count ?? 0} Verified ·{" "}
                {validationReport?.unverified_count ?? 0} Estimated
              </span>
            </div>
            <div className="dispatch-ledger-cell">
              <span className="dispatch-cell-key">Booking Status</span>
              <span
                className={`dispatch-inline-tag ${
                  isApproved ? "pine" : "saffron"
                }`}
              >
                {isApproved ? "Approved for Handoff" : "Awaiting Approval"}
              </span>
            </div>
          </div>
        ) : null}
      </div>

      {/* 3 Streamlined Workspace Tabs */}
      <div className="agentic-tabs-bar" role="tablist" aria-label="Trip workspace views">
        {WORKSPACE_TABS.map((tab) => {
          const bookingsCount =
            tab.id === "bookings"
              ? flights.length + stays.length + transportOptions.length
              : 0;
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={activeTab === tab.id}
              className={`agentic-tab-btn ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => onTabChange(tab.id)}
            >
              <span>{tab.label}</span>
              {bookingsCount > 0 ? (
                <span className="agentic-tab-count tabular">{bookingsCount}</span>
              ) : null}
              {tab.id === "review" ? (
                <span
                  className={`agentic-tab-dot ${isApproved ? "pine" : "saffron"}`}
                  aria-hidden="true"
                />
              ) : null}
            </button>
          );
        })}
      </div>

      {/* Tab 1: Timeline */}
      {activeTab === "timeline" ? (
        <div className="agentic-tab-panel" key="tab-timeline">{children}</div>
      ) : null}

      {/* Tab 2: Unified Bookings (Flights + Stays + Local Transit) */}
      {activeTab === "bookings" ? (
        <div className="agentic-tab-panel" key="tab-bookings">
          <div className="bookings-filter-row">
            {BOOKING_FILTERS.map((filter) => (
              <button
                key={filter.id}
                type="button"
                className={`bookings-filter-pill ${
                  bookingFilter === filter.id ? "active" : ""
                }`}
                onClick={() => setBookingFilter(filter.id)}
              >
                {filter.label}
              </button>
            ))}
          </div>

          {showFlights ? (
            <section className="agentic-section-block">
              <div className="agentic-section-head">
                <div className="agentic-section-title-row">
                  <PlaneIcon size={18} />
                  <h2 className="agentic-section-title">Flights</h2>
                </div>
                <p className="agentic-section-sub">
                  Ranked by total fare, travel time, baggage rules, cancellation terms, and schedule fit.
                </p>
              </div>

              <div className="agentic-options-list">
                {flights.map((flight) => {
                  const isSelected = flight.id === selectedFlightId;
                  return (
                    <div
                      key={flight.id}
                      className={`agentic-option-card ${isSelected ? "selected" : ""}`}
                    >
                      <div className="agentic-option-top">
                        <div className="agentic-option-badges">
                          <span className="agentic-fit-pill tabular">
                            {flight.fit_score}% Fit
                          </span>
                          <span
                            className={`agentic-verify-pill ${
                              flight.verified ? "verified" : "estimated"
                            }`}
                          >
                            {flight.verified ? (
                              <>
                                <CheckIcon size={12} />
                                <span>Live Verified</span>
                              </>
                            ) : (
                              <>
                                <AlertIcon size={12} />
                                <span>Fare Estimate</span>
                              </>
                            )}
                          </span>
                          {isSelected ? (
                            <span className="agentic-selected-pill">Selected</span>
                          ) : null}
                        </div>

                        <div className="agentic-option-price-box">
                          <div className="agentic-option-total tabular">
                            ${flight.total_price.toLocaleString()}
                          </div>
                          <div className="agentic-option-unit tabular">
                            ${flight.price_per_person.toLocaleString()} / person
                          </div>
                        </div>
                      </div>

                      <div className="agentic-option-title">
                        {flight.airline}{" "}
                        <span className="agentic-option-code tabular">
                          · {flight.flight_number} ({flight.cabin_class})
                        </span>
                      </div>

                      <div className="agentic-route-strip">
                        <div>
                          <div className="agentic-route-city">{flight.origin}</div>
                          <div className="agentic-route-time tabular">
                            {flight.departure_time}
                          </div>
                        </div>
                        <div className="agentic-route-mid">
                          <span className="agentic-route-duration tabular">
                            {flight.duration}
                          </span>
                          <div className="agentic-route-track-wrap">
                            <div className="agentic-route-line" />
                            <span
                              className={`agentic-route-jet ${
                                isSelected ? "cruising" : ""
                              }`}
                              aria-hidden="true"
                            >
                              <FlightJetIcon size={14} />
                            </span>
                          </div>
                          <span className="agentic-route-stops">
                            {flight.stops === 0
                              ? "Nonstop"
                              : `${flight.stops} Stop(s)`}
                          </span>
                        </div>
                        <div className="agentic-route-dest">
                          <div className="agentic-route-city">{flight.destination}</div>
                          <div className="agentic-route-time tabular">
                            {flight.arrival_time}
                          </div>
                        </div>
                      </div>

                      <p className="agentic-option-reason">{flight.fit_reason}</p>

                      <div className="agentic-option-meta-list">
                        <div>
                          <strong>Baggage:</strong> {flight.baggage_policy}
                        </div>
                        <div>
                          <strong>Cancellation:</strong> {flight.cancellation_terms}
                        </div>
                        <div className="agentic-rating-line">
                          <strong>Source:</strong> {flight.source_name} ·{" "}
                          <span className="agentic-inline-rating tabular">
                            {flight.rating} <StarIcon size={12} />
                          </span>
                        </div>
                      </div>

                      <div className="agentic-option-actions">
                        <button
                          type="button"
                          className={`agentic-select-btn ${
                            isSelected ? "active" : ""
                          }`}
                          disabled={updatingOptions || isSelected}
                          onClick={() =>
                            onSelectOptions({ selected_flight_id: flight.id })
                          }
                        >
                          {isSelected ? (
                            <>
                              <CheckIcon size={14} />
                              <span>Included in Plan</span>
                            </>
                          ) : updatingOptions ? (
                            "Updating..."
                          ) : (
                            "Select This Flight"
                          )}
                        </button>
                        <a
                          href={flight.booking_url}
                          target="_blank"
                          rel="noreferrer"
                          className="agentic-ext-link"
                        >
                          <span>Inspect on Provider</span>
                          <ExternalLinkIcon size={13} />
                        </a>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>
          ) : null}

          {showStays ? (
            <section className="agentic-section-block">
              <div className="agentic-section-head">
                <div className="agentic-section-title-row">
                  <HotelIcon size={18} />
                  <h2 className="agentic-section-title">Stays & Hotels</h2>
                </div>
                <p className="agentic-section-sub">
                  Evaluated for neighborhood access to your daily itinerary, guest ratings, nightly rates, and cancellation rules.
                </p>
              </div>

              <div className="agentic-options-list">
                {stays.map((stay) => {
                  const isSelected = stay.id === selectedStayId;
                  return (
                    <div
                      key={stay.id}
                      className={`agentic-option-card ${isSelected ? "selected" : ""}`}
                    >
                      <div className="agentic-option-top">
                        <div className="agentic-option-badges">
                          <span className="agentic-fit-pill tabular">
                            {stay.fit_score}% Fit
                          </span>
                          <span
                            className={`agentic-verify-pill ${
                              stay.verified ? "verified" : "estimated"
                            }`}
                          >
                            {stay.verified ? (
                              <>
                                <CheckIcon size={12} />
                                <span>Rate Verified</span>
                              </>
                            ) : (
                              <>
                                <AlertIcon size={12} />
                                <span>Seasonal Estimate</span>
                              </>
                            )}
                          </span>
                          {isSelected ? (
                            <span className="agentic-selected-pill">Selected</span>
                          ) : null}
                        </div>

                        <div className="agentic-option-price-box">
                          <div className="agentic-option-total tabular">
                            ${stay.total_price.toLocaleString()}
                          </div>
                          <div className="agentic-option-unit tabular">
                            ${stay.price_per_night.toLocaleString()}/night ·{" "}
                            {stay.nights} nights
                          </div>
                        </div>
                      </div>

                      <div className="agentic-option-title">
                        {stay.name}{" "}
                        <span className="agentic-option-code tabular">
                          · {stay.rating} <StarIcon size={12} /> · {stay.property_type}
                        </span>
                      </div>

                      <div className="agentic-stay-neighborhood">
                        <PinIcon size={13} />
                        <span>{stay.neighborhood}</span>
                      </div>

                      <p className="agentic-option-reason">{stay.fit_reason}</p>

                      <div className="agentic-amenity-chips">
                        {(stay.amenities || []).map((amenity) => (
                          <span className="agentic-amenity-chip" key={amenity}>
                            {amenity}
                          </span>
                        ))}
                      </div>

                      <div className="agentic-option-meta-list">
                        <div>
                          <strong>Cancellation Terms:</strong>{" "}
                          {stay.cancellation_terms}
                        </div>
                        <div>
                          <strong>Source:</strong> {stay.source_name}
                        </div>
                      </div>

                      <div className="agentic-option-actions">
                        <button
                          type="button"
                          className={`agentic-select-btn ${
                            isSelected ? "active" : ""
                          }`}
                          disabled={updatingOptions || isSelected}
                          onClick={() =>
                            onSelectOptions({ selected_stay_id: stay.id })
                          }
                        >
                          {isSelected ? (
                            <>
                              <CheckIcon size={14} />
                              <span>Included in Plan</span>
                            </>
                          ) : updatingOptions ? (
                            "Updating..."
                          ) : (
                            "Select This Stay"
                          )}
                        </button>
                        <a
                          href={stay.booking_url}
                          target="_blank"
                          rel="noreferrer"
                          className="agentic-ext-link"
                        >
                          <span>Inspect Property</span>
                          <ExternalLinkIcon size={13} />
                        </a>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>
          ) : null}

          {showTransit ? (
            <section className="agentic-section-block">
              <div className="agentic-section-head">
                <div className="agentic-section-title-row">
                  <TrainIcon size={18} />
                  <h2 className="agentic-section-title">Local Transit & Transfers</h2>
                </div>
                <p className="agentic-section-sub">
                  Compare airport express passes, metro cards, and private transfers matched to your daily stops.
                </p>
              </div>

              <div className="agentic-options-list">
                {transportOptions.map((trans) => {
                  const isSelected = trans.id === selectedTransportId;
                  return (
                    <div
                      key={trans.id}
                      className={`agentic-option-card ${isSelected ? "selected" : ""}`}
                    >
                      <div className="agentic-option-top">
                        <div className="agentic-option-badges">
                          <span className="agentic-fit-pill tabular">
                            {trans.fit_score}% Fit
                          </span>
                          <span
                            className={`agentic-verify-pill ${
                              trans.verified ? "verified" : "estimated"
                            }`}
                          >
                            {trans.verified ? (
                              <>
                                <CheckIcon size={12} />
                                <span>Tariff Verified</span>
                              </>
                            ) : (
                              <>
                                <AlertIcon size={12} />
                                <span>Mobility Estimate</span>
                              </>
                            )}
                          </span>
                          {isSelected ? (
                            <span className="agentic-selected-pill">Selected</span>
                          ) : null}
                        </div>

                        <div className="agentic-option-price-box">
                          <div className="agentic-option-total tabular">
                            ${trans.estimated_cost.toLocaleString()}
                          </div>
                          <div className="agentic-option-unit">Total trip transit</div>
                        </div>
                      </div>

                      <div className="agentic-option-title">{trans.mode}</div>
                      <p className="agentic-option-reason">{trans.route_summary}</p>

                      <div className="agentic-option-meta-list">
                        <div>
                          <strong>Provider:</strong> {trans.provider}
                        </div>
                        <div>
                          <strong>Typical Transit Time:</strong> {trans.duration}
                        </div>
                        <div>
                          <strong>Terms:</strong> {trans.cancellation_terms}
                        </div>
                      </div>

                      <div className="agentic-option-actions">
                        <button
                          type="button"
                          className={`agentic-select-btn ${
                            isSelected ? "active" : ""
                          }`}
                          disabled={updatingOptions || isSelected}
                          onClick={() =>
                            onSelectOptions({ selected_transport_id: trans.id })
                          }
                        >
                          {isSelected ? (
                            <>
                              <CheckIcon size={14} />
                              <span>Included in Plan</span>
                            </>
                          ) : updatingOptions ? (
                            "Updating..."
                          ) : (
                            "Select Transit Option"
                          )}
                        </button>
                        <a
                          href={trans.booking_url}
                          target="_blank"
                          rel="noreferrer"
                          className="agentic-ext-link"
                        >
                          <span>Route Details</span>
                          <ExternalLinkIcon size={13} />
                        </a>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>
          ) : null}
        </div>
      ) : null}

      {/* Tab 3: Review, Validation & Explicit Booking Approval */}
      {activeTab === "review" ? (
        <div className="agentic-tab-panel" key="tab-review">
          <section className="agentic-section-block">
            <div className="agentic-section-head">
              <div className="agentic-section-title-row">
                <LockIcon size={18} />
                <h2 className="agentic-section-title">
                  Final Cost Ledger, Validation & Booking Approval
                </h2>
              </div>
              <p className="agentic-section-sub">
                Inspect verified vs. estimated fares, exclusions, and cancellation terms before unlocking provider booking links.
              </p>
            </div>

            {costBreakdown ? (
              <div className="agentic-cost-table">
                <div className="agentic-cost-row">
                  <span>Selected Flight ({costBreakdown.travelers} traveler(s))</span>
                  <strong className="tabular">
                    ${costBreakdown.flights_total.toLocaleString()}
                  </strong>
                </div>
                <div className="agentic-cost-row">
                  <span>Selected Accommodation</span>
                  <strong className="tabular">
                    ${costBreakdown.stays_total.toLocaleString()}
                  </strong>
                </div>
                <div className="agentic-cost-row">
                  <span>Local Transit & Transfers</span>
                  <strong className="tabular">
                    ${costBreakdown.transport_total.toLocaleString()}
                  </strong>
                </div>
                <div className="agentic-cost-row">
                  <span>Itinerary Activities ({costBreakdown.travelers} traveler(s))</span>
                  <strong className="tabular">
                    ${costBreakdown.activities_total.toLocaleString()}
                  </strong>
                </div>
                <div className="agentic-cost-row total">
                  <div>
                    <div>Total Estimated Trip Cost (USD)</div>
                    <small className="tabular">
                      ${costBreakdown.per_person_total.toLocaleString()} per traveler ·
                      Target budget: ${costBreakdown.budget_target.toLocaleString()}
                    </small>
                  </div>
                  <div className="agentic-cost-grand tabular">
                    ${costBreakdown.estimated_total.toLocaleString()}
                  </div>
                </div>
              </div>
            ) : null}

            {/* Validation Flags & Itemized Verification */}
            {validationReport?.flags?.length ? (
              <div className="agentic-flags-box">
                <div className="agentic-flags-title">
                  <AlertIcon size={15} />
                  <span>Items Requiring Live Confirmation Before Payment</span>
                </div>
                <ul className="agentic-flags-list">
                  {validationReport.flags.map((flag, idx) => (
                    <li key={idx}>{flag}</li>
                  ))}
                </ul>
              </div>
            ) : null}

            <div className="agentic-validation-items">
              {(validationReport?.items || []).map((item, idx) => (
                <div className="agentic-validation-row" key={idx}>
                  <div className="agentic-validation-row-top">
                    <div className="agentic-validation-name-group">
                      <span className="agentic-validation-cat">{item.category}</span>
                      <span className="agentic-validation-name">
                        {item.item_name}
                      </span>
                    </div>
                    <span
                      className={`agentic-verify-pill ${
                        item.verified ? "verified" : "estimated"
                      }`}
                    >
                      {item.status_label}
                    </span>
                  </div>
                  <p className="agentic-validation-detail">{item.detail}</p>
                  <div className="agentic-validation-source">
                    Source: {item.source}
                  </div>
                </div>
              ))}
            </div>

            <div className="agentic-two-col-cards">
              <div className="agentic-info-box">
                <h3>Exclusions (Not Included in Estimate)</h3>
                <ul>
                  {(validationReport?.exclusions || []).map((exc, i) => (
                    <li key={i}>{exc}</li>
                  ))}
                </ul>
              </div>
              <div className="agentic-info-box">
                <h3>Data Sources & Cancellation Terms</h3>
                <p>{validationReport?.cancellation_summary}</p>
                <div className="agentic-source-tags">
                  {(validationReport?.live_sources_used || []).map((src) => (
                    <span key={src} className="agentic-amenity-chip">
                      {src}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="agentic-limitation-banner">
              <strong>Provider & Payment Disclosure:</strong>{" "}
              {bookingState?.limitation_notice}
            </div>

            {!isApproved ? (
              <div className="agentic-approval-gate">
                <h3 className="agentic-approval-title">
                  Traveler Approval Checkpoint
                </h3>
                <label className="agentic-checkbox-row">
                  <input
                    type="checkbox"
                    checked={confirmChecked}
                    onChange={(e) => setConfirmChecked(e.target.checked)}
                  />
                  <span>
                    I have reviewed the selected flight, stay, local transit, price
                    estimates, exclusions, and cancellation policies, and I authorize
                    preparing the guided booking links.
                  </span>
                </label>

                <input
                  type="text"
                  className="agentic-notes-input"
                  placeholder="Optional booking notes (e.g., aisle seat preference, late check-in)..."
                  value={approvalNotes}
                  onChange={(e) => setApprovalNotes(e.target.value)}
                />

                <button
                  type="button"
                  className="agentic-approve-btn"
                  disabled={!confirmChecked || approvingBooking}
                  onClick={() =>
                    onApproveBooking({
                      approved: true,
                      approval_notes: approvalNotes,
                    })
                  }
                >
                  <CheckIcon size={16} />
                  <span>
                    {approvingBooking
                      ? "Recording Approval..."
                      : "Approve Trip Plan & Unlock Booking Links"}
                  </span>
                </button>
              </div>
            ) : (
              <div className="agentic-approved-panel">
                <div className="agentic-approved-header">
                  <div>
                    <span className="agentic-verify-pill verified">
                      <CheckIcon size={12} />
                      <span>Explicitly Approved</span>
                    </span>
                    <h3 className="agentic-approval-title" style={{ marginTop: "8px" }}>
                      Guided Booking Checklist & Provider Handoff
                    </h3>
                  </div>
                  <button
                    type="button"
                    className="agentic-revoke-btn"
                    disabled={approvingBooking}
                    onClick={() =>
                      onApproveBooking({ approved: false, approval_notes: null })
                    }
                  >
                    Revoke Approval
                  </button>
                </div>

                <div className="agentic-booking-links-grid">
                  {(bookingState?.booking_links || []).map((link, idx) => (
                    <div className="agentic-booking-link-card" key={idx}>
                      <div className="agentic-booking-link-top">
                        <span className="agentic-validation-cat">
                          {link.category}
                        </span>
                        <strong className="agentic-booking-link-amt tabular">
                          ${link.amount.toLocaleString()} {link.currency}
                        </strong>
                      </div>
                      <div className="agentic-booking-link-title">
                        {link.title}
                      </div>
                      <div className="agentic-booking-link-meta">
                        Provider: {link.provider} · {link.cancellation_note}
                      </div>
                      <a
                        href={link.url}
                        target="_blank"
                        rel="noreferrer"
                        className="agentic-checkout-link"
                      >
                        <span>Continue to {link.provider}</span>
                        <ExternalLinkIcon size={13} />
                      </a>
                    </div>
                  ))}
                </div>

                <div className="agentic-steps-box">
                  <h4>Recommended Booking Sequence</h4>
                  <ul className="agentic-steps-list">
                    {(bookingState?.booking_steps || []).map((step, i) => (
                      <li key={i}>{step}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </section>
        </div>
      ) : null}
    </div>
  );
};

export default AgenticBookingHub;

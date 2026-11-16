import { FlightJetIcon } from "./Icons.jsx";
import "./FlightArc.css";

const FlightArc = ({
  originCode = "BOM",
  destinationCode = "TYO",
  caption = "Direct Air Corridor",
  compact = false,
}) => {
  return (
    <div className={`flight-arc-banner ${compact ? "compact" : ""}`}>
      <span className="flight-arc-airport tabular">{originCode}</span>

      <div className="flight-arc-stage" aria-hidden="true">
        <svg
          className="flight-arc-svg"
          viewBox="0 0 240 42"
          fill="none"
          preserveAspectRatio="xMidYMid meet"
        >
          <path
            className="flight-arc-track"
            d="M 12 32 Q 120 2 228 32"
          />
          <circle cx="12" cy="32" r="4" fill="#1D262B" />
          <path
            d="M228 24.5L229.8 29.2L234.5 31L229.8 32.8L228 37.5L226.2 32.8L221.5 31L226.2 29.2L228 24.5Z"
            fill="#2E5E54"
          />
        </svg>
        <div className="flight-arc-plane">
          <FlightJetIcon size={17} />
        </div>
      </div>

      <span className="flight-arc-airport tabular">{destinationCode}</span>

      {caption ? <span className="flight-arc-caption">{caption}</span> : null}
    </div>
  );
};

export default FlightArc;

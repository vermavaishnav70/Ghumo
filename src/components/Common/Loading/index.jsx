import FlightArc from "../FlightArc.jsx";
import { GhumoMark } from "../Icons.jsx";
import "./style.css";

const Loading = () => {
  return (
    <div className="ghumo-loading-shell">
      <div className="ghumo-loading-card" role="status" aria-live="polite">
        <div className="ghumo-loading-head">
          <GhumoMark size={38} />
          <div className="ghumo-loading-title">Preparing your Ghumo timetable</div>
        </div>
        <FlightArc
          originCode="ORIGIN"
          destinationCode="DEST"
          caption="Assembling route legs, stays & validation checks"
        />
      </div>
    </div>
  );
};

export default Loading;

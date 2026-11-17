import { Link } from "react-router-dom";
import BrandHeader from "../Common/BrandHeader/index.jsx";
import { AlertIcon, ArrowRightIcon } from "../Common/Icons.jsx";
import "./style.css";

const ErrorScreen = ({ errorMessage }) => {
  return (
    <div className="error-shell">
      <BrandHeader />
      <main className="error-main">
        <div className="error-card">
          <div className="error-icon-badge">
            <AlertIcon size={24} />
          </div>
          <h1 className="error-title">Could not prepare this timetable</h1>
          <p className="error-message">
            {errorMessage || "Something unexpected interrupted your trip request."}
          </p>
          <div className="error-actions">
            <Link to="/fill-details" className="error-btn-primary">
              <span>Return to Trip Studio</span>
              <ArrowRightIcon size={15} />
            </Link>
            <Link to="/" className="error-btn-secondary">
              Back to Home
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ErrorScreen;

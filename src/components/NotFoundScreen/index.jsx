import { Link } from "react-router-dom";
import BrandHeader from "../Common/BrandHeader/index.jsx";
import { ArrowRightIcon, CompassIcon } from "../Common/Icons.jsx";
import "./style.css";

const NotFoundScreen = () => {
  return (
    <div className="not-found-screen">
      <BrandHeader />
      <main className="not-found-overlay">
        <div className="not-found-content">
          <div className="not-found-icon">
            <CompassIcon size={28} />
          </div>
          <h1 className="not-found-title">Page not found</h1>
          <p className="not-found-description">
            The route or saved trip folio you are looking for does not exist or may have been removed.
          </p>
          <div className="not-found-actions">
            <Link className="not-found-btn primary" to="/fill-details">
              <span>Plan a Trip</span>
              <ArrowRightIcon size={15} />
            </Link>
            <Link className="not-found-btn secondary" to="/">
              Back to Home
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
};

export default NotFoundScreen;

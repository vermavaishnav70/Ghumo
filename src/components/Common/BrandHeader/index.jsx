import { Link, useLocation } from "react-router-dom";

import { useAuth } from "../../../context/AuthContext.jsx";
import { GhumoMark } from "../Icons.jsx";
import "./style.css";

const getAvatarLabel = (user) => {
  const email = user?.email?.trim();
  if (email) {
    return email[0].toUpperCase();
  }
  return "U";
};

const BrandHeader = () => {
  const { user } = useAuth();
  const location = useLocation();

  return (
    <header className="brand-header">
      <div className="brand-header-container">
        <Link to="/" className="brand-header-inner">
          <GhumoMark size={36} />
          <div className="brand-name-wrapper">
            <span className="brand-name">Ghumo</span>
            <span className="brand-tag">Trip Dispatch</span>
          </div>
        </Link>

        <nav className="brand-nav" aria-label="Primary navigation">
          <Link
            to="/fill-details"
            className={`brand-nav-link ${
              location.pathname === "/fill-details" ? "active" : ""
            }`}
          >
            Trip Studio
          </Link>
          <Link
            to="/saved-trips"
            className={`brand-nav-link ${
              location.pathname.startsWith("/saved-trips") ? "active" : ""
            }`}
          >
            Saved Trips
          </Link>
          {location.pathname === "/" ? (
            <a href="#booking-guide" className="brand-nav-link">
              Booking Guide
            </a>
          ) : null}
          {user ? (
            <Link
              aria-label="Open saved trips"
              className="brand-avatar-link"
              to="/saved-trips"
              title={user.email || "Saved trips"}
            >
              {getAvatarLabel(user)}
            </Link>
          ) : (
            <Link to="/saved-trips" className="brand-signin-pill">
              Sign in
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
};

export default BrandHeader;

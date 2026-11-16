import { ClockIcon, PinIcon } from "../Icons.jsx";
import "./style.css";

const ActivityCard = ({ activity, activityNumber, isLast = false }) => {
  const price = Number(activity?.price) || 0;

  return (
    <div className="activity-timeline-item">
      <div className="activity-step-col">
        <div className="activity-step-circle tabular">{activityNumber}</div>
        {!isLast ? <div className="activity-step-track" aria-hidden="true" /> : null}
      </div>

      <div className="activity-body-col">
        <div className="activity-top-row">
          <div className="activity-title-group">
            <span className="activity-time-pill tabular">{activity?.time}</span>
            <h4 className="activity-name">{activity?.name}</h4>
          </div>

          <div className="activity-meta-pills">
            <span className="activity-duration-pill">
              <ClockIcon size={12} />
              <span>{activity?.duration}</span>
            </span>
            <span className="activity-price-pill tabular">
              {price === 0 ? "Free" : `$${price}`}
            </span>
          </div>
        </div>

        <div className="activity-location">
          <PinIcon size={13} />
          <span>{activity?.location}</span>
        </div>
        <p className="activity-description">{activity?.description}</p>
      </div>
    </div>
  );
};

export default ActivityCard;

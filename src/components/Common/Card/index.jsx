import ActivityCard from "../ActivityCard";
import "./style.css";

const Card = ({ itinerary }) => {
  const activities = itinerary?.activities || [];
  const dayTotal = activities.reduce(
    (sum, item) => sum + (Number(item?.price) || 0),
    0
  );

  return (
    <article className="timeline-day-card">
      <div className="timeline-day-header">
        <div className="timeline-day-title-row">
          <h3 className="timeline-day-badge">{itinerary.day}</h3>
          <span className="timeline-day-count tabular">
            {activities.length} scheduled stops
          </span>
        </div>
        <div className="timeline-day-subtotal tabular">
          Est. activities: <strong>${dayTotal.toLocaleString()}</strong> / person
        </div>
      </div>

      <div className="timeline-activities-list">
        {activities.map((activity, index) => (
          <ActivityCard
            key={index}
            activity={activity}
            activityNumber={index + 1}
            isLast={index === activities.length - 1}
          />
        ))}
      </div>
    </article>
  );
};

export default Card;

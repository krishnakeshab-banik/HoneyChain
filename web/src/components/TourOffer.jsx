import { useState } from "react";
import { useAuth } from "../auth";
import { useTour } from "./GuidedTour";
import { TOURS, TOUR_OFFER, tourStorageKey } from "../tourScripts";

export default function TourOffer() {
  const { user, role } = useAuth();
  const { startTour } = useTour();
  const [hidden, setHidden] = useState(false);
  if (hidden || !user || !TOURS[role]) {
    return null;
  }
  if (window.localStorage.getItem(tourStorageKey(user.username))) {
    return null;
  }
  const offer = TOUR_OFFER[role];
  return (
    <div className="card tour-offer">
      <strong>{offer?.title || "Take a short walkthrough?"}</strong>
      <p className="muted">
        {offer?.body} Each step highlights the control on that screen and can be read aloud. Skip any time.
      </p>
      <div className="row">
        <button className="primary" type="button" onClick={() => startTour(role)}>
          Start tour
        </button>
        <button
          className="ghost"
          type="button"
          onClick={() => {
            window.localStorage.setItem(tourStorageKey(user.username), "1");
            setHidden(true);
          }}
        >
          Not now
        </button>
      </div>
    </div>
  );
}

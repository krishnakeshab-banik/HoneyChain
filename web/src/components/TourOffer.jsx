import { useState } from "react";
import { useAuth } from "../auth";
import { useTour } from "./GuidedTour";
import { TOURS, tourStorageKey } from "../tourScripts";

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
  return (
    <div className="card tour-offer">
      <strong>Take a short walkthrough?</strong>
      <p className="muted">We will highlight the real buttons on your own screens and read each step aloud in the language you selected. You can skip at any time.</p>
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

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { TOURS, tourStorageKey } from "../tourScripts";
import { useAuth } from "../auth";
import { speak, stopSpeaking } from "../speech";

const TourContext = createContext({ startTour() {}, stopTour() {}, active: false });

export function TourProvider({ children }) {
  const { user, role } = useAuth();
  const { i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const [script, setScript] = useState([]);
  const [index, setIndex] = useState(-1);
  const [box, setBox] = useState(null);
  const step = index >= 0 ? script[index] : null;

  function stopTour(markDone = false) {
    if (markDone && user) {
      window.localStorage.setItem(tourStorageKey(user.username), "1");
    }
    setIndex(-1);
    setScript([]);
    setBox(null);
    stopSpeaking();
  }

  function startTour(persona) {
    const next = TOURS[persona] || TOURS.beekeeper;
    setScript(next);
    setIndex(0);
    navigate(next[0].path);
  }

  useEffect(() => {
    if (!step) {
      return undefined;
    }
    if (location.pathname !== step.path) {
      navigate(step.path);
      return undefined;
    }
    let tries = 0;
    const timer = setInterval(() => {
      const el = document.querySelector(step.target);
      tries += 1;
      if (el) {
        const rect = el.getBoundingClientRect();
        setBox({ top: rect.top, left: rect.left, width: rect.width, height: rect.height });
        el.scrollIntoView({ block: "center", behavior: "smooth" });
        clearInterval(timer);
      } else if (tries > 20) {
        setBox({ top: 80, left: 280, width: 320, height: 80 });
        clearInterval(timer);
      }
    }, 150);
    if (step.title) {
      speak(`${step.title}. ${step.body}`, (i18n.resolvedLanguage || i18n.language || "en").slice(0, 2));
    }
    return () => clearInterval(timer);
  }, [step, location.pathname, navigate, i18n.language, i18n.resolvedLanguage]);

  const value = useMemo(() => ({ startTour, stopTour, active: index >= 0 }), [index]);

  return (
    <TourContext.Provider value={value}>
      {children}
      {step && (
        <div className="tour-layer" role="dialog" aria-label="Product tour">
          <div className="tour-dim" onClick={() => stopTour(false)} />
          {box && (
            <div
              className="tour-spot"
              style={{ top: box.top - 8, left: box.left - 8, width: box.width + 16, height: box.height + 16 }}
            />
          )}
          <div className="tour-card card" style={{ top: (box?.top || 80) + (box?.height || 0) + 16, left: box?.left || 280 }}>
            <p className="page-kicker">
              Step {index + 1} of {script.length}
            </p>
            <h3>{step.title}</h3>
            <p>{step.body}</p>
            <div className="row">
              <button className="ghost" type="button" disabled={index === 0} onClick={() => setIndex((i) => i - 1)}>
                Back
              </button>
              {index < script.length - 1 ? (
                <button className="primary" type="button" onClick={() => setIndex((i) => i + 1)}>
                  Next
                </button>
              ) : (
                <button className="primary" type="button" onClick={() => stopTour(true)}>
                  Finish
                </button>
              )}
              <button className="ghost" type="button" onClick={() => stopTour(true)}>
                Skip
              </button>
            </div>
          </div>
        </div>
      )}
    </TourContext.Provider>
  );
}

export function useTour() {
  return useContext(TourContext);
}

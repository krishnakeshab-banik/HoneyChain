import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { TOURS, tourCopy, tourStorageKey } from "../tourScripts";
import { useAuth } from "../auth";
import { canSpeak, speak, stopSpeaking } from "../speech";

const TourContext = createContext({ startTour() {}, stopTour() {}, active: false });

export function TourProvider({ children }) {
  const { user, role } = useAuth();
  const { i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const [script, setScript] = useState([]);
  const [index, setIndex] = useState(-1);
  const [box, setBox] = useState(null);
  const [speechNote, setSpeechNote] = useState("");
  const step = index >= 0 ? script[index] : null;
  const lang = (i18n.resolvedLanguage || i18n.language || "en").slice(0, 2);
  const copy = step ? tourCopy(step, lang) : null;

  const narrate = useCallback(
    (nextStep) => {
      if (!nextStep) {
        return;
      }
      const nextCopy = tourCopy(nextStep, lang);
      if (!canSpeak()) {
        setSpeechNote("This browser cannot speak — read the captions.");
        return;
      }
      setSpeechNote(lang === "en" ? "Reading this step aloud" : `Reading this step aloud (${lang})`);
      speak(`${nextCopy.title}. ${nextCopy.body}`, lang).then((ok) => {
        if (!ok) {
          setSpeechNote("Voice did not start — captions are still on screen.");
        }
      });
    },
    [lang],
  );

  const stopTour = useCallback(
    (markDone = false) => {
      if (markDone && user) {
        window.localStorage.setItem(tourStorageKey(user.username), "1");
      }
      setIndex(-1);
      setScript([]);
      setBox(null);
      setSpeechNote("");
      stopSpeaking();
    },
    [user],
  );

  const startTour = useCallback(
    (persona) => {
      const next = TOURS[persona] || TOURS[role];
      if (!next?.length) {
        return;
      }
      setScript(next);
      setIndex(0);
      setBox(null);
      navigate(next[0].path);
      narrate(next[0]);
    },
    [navigate, narrate, role],
  );

  useEffect(() => {
    if (!step) {
      return undefined;
    }
    if (location.pathname !== step.path) {
      navigate(step.path);
      return undefined;
    }
    let tries = 0;
    const place = () => {
      const el = document.querySelector(step.target);
      if (el) {
        const rect = el.getBoundingClientRect();
        setBox({ top: rect.top, left: rect.left, width: rect.width, height: rect.height });
        el.scrollIntoView({ block: "nearest", inline: "nearest", behavior: "smooth" });
        return true;
      }
      return false;
    };
    if (place()) {
      return undefined;
    }
    const timer = setInterval(() => {
      tries += 1;
      if (place() || tries > 40) {
        if (!place()) {
          setBox({ top: 80, left: 24, width: 320, height: 80 });
        }
        clearInterval(timer);
      }
    }, 150);
    const onMove = () => place();
    window.addEventListener("resize", onMove);
    window.addEventListener("scroll", onMove, true);
    return () => {
      clearInterval(timer);
      window.removeEventListener("resize", onMove);
      window.removeEventListener("scroll", onMove, true);
    };
  }, [step, location.pathname, navigate]);

  const value = useMemo(() => ({ startTour, stopTour, active: index >= 0 }), [index, startTour, stopTour]);

  return (
    <TourContext.Provider value={value}>
      {children}
      {step && copy && (
        <div className="tour-layer" role="dialog" aria-label="Product tour" data-testid="tour-layer">
          <div className="tour-dim" />
          {box && (
            <div
              className="tour-spot"
              style={{ top: box.top - 8, left: box.left - 8, width: box.width + 16, height: box.height + 16 }}
            />
          )}
          <div className="tour-card card" data-testid="tour-card">
            <p className="page-kicker">
              Step {index + 1} of {script.length}
            </p>
            <h3 data-testid="tour-title">{copy.title}</h3>
            <p data-testid="tour-body">{copy.body}</p>
            <p className="muted" data-testid="tour-speech" data-speech-lang={lang}>
              {speechNote}
            </p>
            <div className="row">
              <button
                className="ghost"
                type="button"
                data-testid="tour-back"
                disabled={index === 0}
                onClick={() => {
                  const nextIndex = Math.max(0, index - 1);
                  setIndex(nextIndex);
                  narrate(script[nextIndex]);
                }}
              >
                Back
              </button>
              {index < script.length - 1 ? (
                <button
                  className="primary"
                  type="button"
                  data-testid="tour-next"
                  onClick={() => {
                    const nextIndex = index + 1;
                    setIndex(nextIndex);
                    narrate(script[nextIndex]);
                  }}
                >
                  Next
                </button>
              ) : (
                <button className="primary" type="button" data-testid="tour-finish" onClick={() => stopTour(true)}>
                  Finish
                </button>
              )}
              <button
                className="ghost"
                type="button"
                data-testid="tour-repeat"
                onClick={() => narrate(step)}
              >
                Read aloud
              </button>
              <button className="ghost" type="button" data-testid="tour-skip" onClick={() => stopTour(true)}>
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

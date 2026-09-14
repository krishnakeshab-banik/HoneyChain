import { useEffect, useState } from "react";

export default function OfflineBanner() {
  const [online, setOnline] = useState(typeof navigator === "undefined" ? true : navigator.onLine);
  const [queued, setQueued] = useState(0);

  useEffect(() => {
    function sync() {
      setOnline(navigator.onLine);
      try {
        const items = JSON.parse(window.localStorage.getItem("honeychain_offline_queue") || "[]");
        setQueued(items.length);
      } catch {
        setQueued(0);
      }
    }
    sync();
    window.addEventListener("online", sync);
    window.addEventListener("offline", sync);
    const timer = setInterval(sync, 4000);
    return () => {
      window.removeEventListener("online", sync);
      window.removeEventListener("offline", sync);
      clearInterval(timer);
    };
  }, []);

  if (online && queued === 0) {
    return null;
  }
  return (
    <div className={`offline-banner ${online ? "syncing" : "offline"}`} role="status">
      {online ? `Online — syncing ${queued} saved action${queued === 1 ? "" : "s"}…` : "You are offline. Harvests you save will wait here until the phone has a signal."}
    </div>
  );
}

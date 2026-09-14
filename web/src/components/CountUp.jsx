import { useEffect, useState } from "react";

export default function CountUp({ value, duration = 700, statKey }) {
  const target = Number(value) || 0;
  const storageKey = statKey ? `honeychain_stat_${statKey}` : "";
  const stored = storageKey ? Number(window.localStorage.getItem(storageKey)) : Number.NaN;
  const from = Number.isFinite(stored) ? stored : target;
  const [shown, setShown] = useState(from);

  useEffect(() => {
    const startValue = Number.isFinite(stored) ? stored : target;
    const start = performance.now();
    let frame = 0;
    function tick(now) {
      const progress = Math.min(1, (now - start) / duration);
      setShown(Math.round(startValue + (target - startValue) * progress));
      if (progress < 1) {
        frame = requestAnimationFrame(tick);
      } else if (storageKey) {
        window.localStorage.setItem(storageKey, String(target));
      }
    }
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, duration, storageKey]);

  return <span data-final={target}>{shown}</span>;
}

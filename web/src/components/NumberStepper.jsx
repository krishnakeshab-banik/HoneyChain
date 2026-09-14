export default function NumberStepper({ id, label, value, onChange, step = 0.1, min = 0.1, max = 200 }) {
  const current = Number(value) || 0;
  return (
    <div>
      <label htmlFor={id}>{label}</label>
      <div className="stepper">
        <button type="button" className="ghost" onClick={() => onChange(Math.max(min, +(current - step).toFixed(1)))}>
          −
        </button>
        <input
          id={id}
          type="number"
          step={step}
          min={min}
          max={max}
          value={value}
          onChange={(event) => onChange(event.target.value)}
        />
        <button type="button" className="ghost" onClick={() => onChange(Math.min(max, +(current + step).toFixed(1)))}>
          +
        </button>
      </div>
    </div>
  );
}

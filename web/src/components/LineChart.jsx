export default function LineChart({ rows, xKey, yKeys, labels }) {
  if (!rows || rows.length < 1) {
    return <p className="muted">No points yet.</p>;
  }
  const plot = rows.length === 1 ? [rows[0], rows[0]] : rows;
  const width = 640;
  const height = 180;
  const pad = 28;
  const xs = plot.map((_, index) => index);
  const series = yKeys.map((key) => plot.map((row) => Number(row[key])));
  const all = series.flat();
  const min = Math.min(...all);
  const max = Math.max(...all);
  const span = max - min || 1;

  const point = (index, value) => {
    const x = pad + (index / (plot.length - 1)) * (width - pad * 2);
    const y = height - pad - ((value - min) / span) * (height - pad * 2);
    return `${x},${y}`;
  };

  const colors = ["#9a6a16", "#2f6b45", "#3d4f7c"];

  return (
    <svg className="chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Telemetry chart">
      {series.map((values, seriesIndex) => (
        <polyline
          key={yKeys[seriesIndex]}
          fill="none"
          stroke={colors[seriesIndex]}
          strokeWidth="2"
          points={values.map((value, index) => point(xs[index], value)).join(" ")}
        />
      ))}
      <text x={pad} y={16} fontSize="11" fill="#6d6458">
        {(labels || yKeys).join(" · ")} · {rows[0][xKey]} → {rows[rows.length - 1][xKey]}
      </text>
    </svg>
  );
}

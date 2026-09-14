export function Banner({ tone = "info", children }) {
  return <div className={`banner ${tone}`}>{children}</div>;
}

export function Loading({ label }) {
  return (
    <Banner tone="info">
      <span className="spinner" aria-hidden="true" />
      {label}
    </Banner>
  );
}

export function Card({ children, className = "" }) {
  return <div className={`card ${className}`.trim()}>{children}</div>;
}

export function StatCard({ label, value }) {
  return (
    <div className="metric">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
    </div>
  );
}

export const Metric = StatCard;

export function SectionHeading({ kicker, title, purpose }) {
  return (
    <header>
      {kicker && <p className="page-kicker">{kicker}</p>}
      <h1>{title}</h1>
      {purpose && <p className="purpose">{purpose}</p>}
    </header>
  );
}

export const PageHeader = SectionHeading;

export function PrimaryButton({ children, type = "button", ...props }) {
  return (
    <button className="primary" type={type} {...props}>
      {children}
    </button>
  );
}

export function SecondaryButton({ children, type = "button", ...props }) {
  return (
    <button className="ghost" type={type} {...props}>
      {children}
    </button>
  );
}

export function DataTable({ rows, columns }) {
  if (!rows.length) {
    return null;
  }
  return (
    <div className="card" style={{ overflowX: "auto" }}>
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={row.id || row.harvest_id || row.batch_id || row.package_id || row.username || index}>
              {columns.map((column) => (
                <td key={column.key}>{column.render ? column.render(row) : String(row[column.key] ?? "")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function HiveSelect({ hives, value, onChange, id = "hive" }) {
  return (
    <div>
      <label htmlFor={id}>Hive</label>
      <select id={id} value={value} onChange={(event) => onChange(event.target.value)}>
        {hives.map((hive) => (
          <option key={hive.hive_id} value={hive.hive_id}>
            {hive.hive_id} · {hive.name}
          </option>
        ))}
      </select>
    </div>
  );
}

import { useEffect, useState } from "react";
import { apiGet } from "../api";
import { Banner, DataTable, Loading, Metric, PageHeader } from "../components/Ui";

export default function CloneWatch() {
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    apiGet("/api/clonewatch")
      .then(setReport)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
  }, []);

  const rows = (report?.flagged_items || []).map((item) => ({
    ...item,
    ...item.extra,
  }));

  return (
    <div data-tour="clonewatch">
      <PageHeader
        kicker="CLONEWATCH"
        title="CloneWatch"
        purpose="Every oracle rejection and flagged consumer scan, each with its specific reason. This list is empty only when nothing has been flagged."
      />
      {loading && <Loading label="Loading CloneWatch flags…" />}
      {error && (
        <Banner tone="bad">
          Couldn't load CloneWatch — {error}{" "}
          <button className="ghost" type="button" onClick={load}>
            Retry
          </button>
        </Banner>
      )}
      {report && (
        <>
          <div className="grid-3">
            <Metric label="Flagged items" value={report.flagged_items.length} />
            <Metric label="Oracle failures" value={report.oracle_failures} />
            <Metric label="Anomalous scans" value={report.flagged_scans} />
          </div>
          {rows.length === 0 ? (
            <Banner tone="info">
              Nothing flagged yet. Commit a batch whose declared weight is more than 10% off
              the harvest sum, or verify the same package from Kolkata and Bremen within two hours.
            </Banner>
          ) : (
            <DataTable
              rows={rows}
              columns={[
                { key: "kind", label: "Kind" },
                { key: "reference_id", label: "Reference" },
                { key: "reason", label: "Reason" },
                { key: "recorded_at", label: "Recorded" },
              ]}
            />
          )}
        </>
      )}
    </div>
  );
}

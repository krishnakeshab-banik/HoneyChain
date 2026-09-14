import { useEffect, useState } from "react";
import { apiGet } from "../api";
import LineChart from "../components/LineChart";
import { Banner, DataTable, Loading, Metric, PageHeader } from "../components/Ui";

export default function ModelTransparency() {
  const [body, setBody] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiGet("/api/ml/transparency")
      .then(setBody)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div data-tour="model">
      <PageHeader
        kicker="MODEL TRANSPARENCY"
        title="Held-out MSPB evaluation"
        purpose="These scores come from a 25% test split the served models never trained on. MSPB is an international field proxy until an Indian labelled set exists."
      />
      {error && <Banner tone="bad">{error}</Banner>}
      {!body && !error && <Loading label="Loading held-out metrics…" />}
      {body && (
        <>
          <Banner tone="info">{body.note}</Banner>
          <p className="muted">{body.split}</p>
          <p className="muted">{body.provenance}</p>
          {body.health && (
            <div className="grid-3">
              <Metric label="Health accuracy" value={`${(body.health.accuracy * 100).toFixed(1)}%`} />
              <Metric label="Precision (macro)" value={body.health.precision_macro.toFixed(3)} />
              <Metric label="Recall (macro)" value={body.health.recall_macro.toFixed(3)} />
            </div>
          )}
          {body.yield_metrics && (
            <div className="grid-3">
              <Metric label="Honey RMSE" value={`${body.yield_metrics.rmse.toFixed(2)} kg`} />
              <Metric label="Honey MAE" value={`${body.yield_metrics.mae.toFixed(2)} kg`} />
              <Metric label="Yield test rows" value={body.yield_metrics.n_test} />
            </div>
          )}
          <h2>Health feature importance</h2>
          <LineChart
            rows={body.health_feature_importance}
            xKey="feature"
            yKeys={["importance"]}
            labels={["Importance"]}
          />
          <DataTable
            rows={body.health_feature_importance}
            columns={[
              { key: "feature", label: "Feature" },
              { key: "importance", label: "Importance", render: (row) => row.importance.toFixed(4) },
            ]}
          />
          {body.yield_feature_importance?.length > 0 && (
            <>
              <h2>Yield |coefficient| share</h2>
              <LineChart
                rows={body.yield_feature_importance}
                xKey="feature"
                yKeys={["importance"]}
                labels={["|coef| share"]}
              />
            </>
          )}
        </>
      )}
    </div>
  );
}

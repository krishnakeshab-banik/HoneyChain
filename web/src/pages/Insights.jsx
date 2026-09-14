import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { apiGet, apiPost } from "../api";
import LineChart from "../components/LineChart";
import { Banner, HiveSelect, Loading, Metric, PageHeader } from "../components/Ui";

export default function Insights() {
  const [hives, setHives] = useState(null);
  const [hiveId, setHiveId] = useState("");
  const [insights, setInsights] = useState(null);
  const { t, i18n } = useTranslation();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [photoNote, setPhotoNote] = useState("");
  const [photoBusy, setPhotoBusy] = useState(false);

  useEffect(() => {
    apiGet("/api/auth/me/hives").catch(() => apiGet("/api/hives"))
      .then((list) => {
        setHives(list);
        setHiveId((current) => current || list.find((item) => item.hive_id === "IN-WB-001")?.hive_id || list[0]?.hive_id || "");
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!hiveId) {
      return;
    }
    setInsights(null);
    setError("");
    apiGet(`/api/insights/${hiveId}`)
      .then(setInsights)
      .catch((err) => setError(err.message));
  }, [hiveId]);

  const featureRows = insights
    ? Object.entries(insights.health.features).map(([feature, value]) => ({ feature, value }))
    : [];

  return (
    <div data-tour="insights">
      <PageHeader
        kicker={t("insights.kicker")}
        title={t("insights.title")}
        purpose={t("insights.purpose")}
      />
      {loading && <Loading label="Loading hives…" />}
      {hives && hives.length === 0 && <Banner tone="warn">No hives registered yet.</Banner>}
      {hives && hives.length > 0 && <HiveSelect hives={hives} value={hiveId} onChange={setHiveId} id="insights-hive" />}
      {!insights && !error && hiveId && <Loading label="Running models on this hive's sensor history…" />}
      {error && (
        <Banner tone="bad">
          Couldn't load insights — {error}
        </Banner>
      )}
      {insights && (
        <>
          <div className="grid-3">
            <Metric label="Colony status" value={insights.health.status} />
            <Metric label="Model confidence" value={`${(insights.health.confidence * 100).toFixed(1)}%`} />
            <Metric label="Forecast hive weight" value={`${insights.forecast.predicted_weight_kg.toFixed(2)} kg`} />
          </div>
          {insights.forecast.predicted_honey_kg != null && (
            <div className="grid-3">
              <Metric
                label="MSPB honey yield"
                value={`${insights.forecast.predicted_honey_kg.toFixed(2)} kg`}
              />
            </div>
          )}
          <p className="muted">{insights.health.model_name}. {insights.health.trained_on}</p>
          <p className="muted">{insights.forecast.model_name}. {insights.forecast.trained_on}</p>
          <div className="card">
            <p className="page-kicker">WHAT THIS STATUS MEANS</p>
            <p>{insights.health.status_meaning || insights.computed_explanation}</p>
            {insights.health.reasons?.length > 0 && (
              <ul>
                {insights.health.reasons.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
            )}
          </div>
          {insights.health.class_probabilities && Object.keys(insights.health.class_probabilities).length > 0 && (
            <div className="card">
              <p className="page-kicker">CLASS PROBABILITIES</p>
              <p className="muted">How the RandomForest split probability across inspection-risk classes for this hive.</p>
              <div className="grid-3">
                {Object.entries(insights.health.class_probabilities).map(([label, value]) => (
                  <Metric key={label} label={label} value={`${(Number(value) * 100).toFixed(1)}%`} />
                ))}
              </div>
            </div>
          )}
          {insights.health.drivers?.length > 0 && (
            <div className="card">
              <p className="page-kicker">WHY THE MODEL LEANED THIS WAY</p>
              <p className="muted">Top live features by model importance, compared with a typical brood-nest band. Weight is shown in the live-reading note; it is not an MSPB training feature.</p>
              <table>
                <thead>
                  <tr>
                    <th>Feature</th>
                    <th>This hive</th>
                    <th>Importance</th>
                    <th>Vs typical</th>
                  </tr>
                </thead>
                <tbody>
                  {insights.health.drivers.map((row) => (
                    <tr key={row.feature}>
                      <td>{row.feature}</td>
                      <td>{Number(row.value).toFixed(3)}</td>
                      <td>{(Number(row.importance) * 100).toFixed(1)}%</td>
                      <td>{row.note}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <div className="card">
            <p className="page-kicker">FROM THE LIVE READINGS</p>
            <p>{insights.computed_explanation || "Awaiting enough sensor history to explain this hive."}</p>
          </div>
          <div className="card ai-card">
            <p className="page-kicker">AI EXPLANATION</p>
            <p>{insights.ai_explanation || "AI narrative is optional. The status, probabilities, and reasons above are still from the live sensor history and the MSPB health model."}</p>
            <p className="ai-tag">{insights.ai_label}</p>
          </div>
          <label htmlFor="comb-photo">Optional comb photo (preliminary observation only)</label>
          <input
            id="comb-photo"
            type="file"
            accept="image/*"
            onChange={async (event) => {
              const file = event.target.files?.[0];
              if (!file) {
                return;
              }
              setPhotoBusy(true);
              const reader = new FileReader();
              reader.onload = async () => {
                try {
                  const raw = String(reader.result || "");
                  const image_base64 = raw.split(",")[1] || "";
                  const result = await apiPost("/api/assistant/observe", {
                    image_base64,
                    mime_type: file.type || "image/jpeg",
                    language: (i18n.resolvedLanguage || "en").slice(0, 2),
                  });
                  setPhotoNote(`${result.observation} ${result.ai_label}`);
                } catch (err) {
                  setPhotoNote(err.message);
                } finally {
                  setPhotoBusy(false);
                }
              };
              reader.readAsDataURL(file);
            }}
          />
          {photoBusy && <Loading label="Looking at the photo…" />}
          {photoNote && <Banner tone="info">{photoNote}</Banner>}
          <h2>Input feature vector</h2>
          <p className="muted">Exact values sent into the live models for this hive. Nothing in the inference step is hidden.</p>
          <table>
            <thead>
              <tr>
                <th>Feature</th>
                <th>Value</th>
              </tr>
            </thead>
            <tbody>
              {featureRows.map((row) => (
                <tr key={row.feature}>
                  <td>{row.feature}</td>
                  <td>{Number(row.value).toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <h2>Features fed to the models</h2>
          <LineChart rows={featureRows} xKey="feature" yKeys={["value"]} labels={["Feature value"]} />
          <h2>Measured vs forecast hive weight</h2>
          <LineChart
            rows={[
              { label: "Latest measured", kg: insights.forecast.recent_weight_kg },
              { label: "Forecast", kg: insights.forecast.predicted_weight_kg },
            ]}
            xKey="label"
            yKeys={["kg"]}
            labels={["kg"]}
          />
        </>
      )}
    </div>
  );
}

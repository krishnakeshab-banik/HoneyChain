import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { apiGet } from "../api";
import { Banner, Loading, Metric, PageHeader } from "../components/Ui";

export default function PublicModel() {
  const { t } = useTranslation();
  const [body, setBody] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiGet("/api/public/model")
      .then(setBody)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div>
      <PageHeader kicker={t("model.kicker")} title={t("model.title")} purpose={t("model.purpose")} />
      {error && <Banner tone="bad">{error}</Banner>}
      {!body && !error && <Loading label={t("model.loading")} />}
      {body && (
        <>
          <div className="grid-3">
            <Metric
              label={t("model.accuracy")}
              value={body.health_accuracy != null ? `${(body.health_accuracy * 100).toFixed(1)}%` : "—"}
            />
            <Metric
              label={t("model.precision")}
              value={body.health_precision_macro != null ? body.health_precision_macro.toFixed(3) : "—"}
            />
            <Metric
              label={t("model.rmse")}
              value={body.yield_rmse != null ? `${body.yield_rmse.toFixed(1)} kg` : "—"}
            />
          </div>
          <p className="muted">{body.split}</p>
          <p>{body.provenance}</p>
        </>
      )}
    </div>
  );
}

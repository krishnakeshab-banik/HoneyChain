import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { apiGet } from "../api";
import LineChart from "../components/LineChart";
import { Banner, DataTable, Loading, Metric, PageHeader } from "../components/Ui";

function pinStyle(lat, lng) {
  if (lat > 45) {
    return { left: "84%", top: "14%" };
  }
  const x = ((lng - 68) / 30) * 68 + 10;
  const y = ((36 - lat) / 28) * 68 + 16;
  return { left: `${Math.max(6, Math.min(90, x))}%`, top: `${Math.max(8, Math.min(88, y))}%` };
}

export default function AdminAnalytics() {
  const { t } = useTranslation();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiGet("/api/analytics/admin")
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div>
      <PageHeader kicker={t("analytics.kicker")} title={t("analytics.title")} purpose={t("analytics.purpose")} />
      {error && <Banner tone="bad">{error}</Banner>}
      {!data && !error && <Loading label={t("analytics.loading")} />}
      {data && (
        <>
          <div className="grid-3">
            <Metric label={t("analytics.hives")} value={data.hive_count} />
            <Metric label={t("analytics.saleKg")} value={`${data.sale_kg.toFixed(1)} kg`} />
            <Metric label={t("analytics.saleValue")} value={`₹${data.sale_value_inr.toFixed(0)}`} />
          </div>
          <h2>{t("analytics.mapTitle")}</h2>
          <p className="muted">{t("analytics.mapHint")}</p>
          <div className="seller-map" aria-label={t("analytics.mapTitle")}>
            <div className="seller-map-land" />
            {data.pins.map((pin) => (
              <button
                key={pin.beekeeper_id}
                type="button"
                className="seller-pin"
                style={pinStyle(pin.latitude, pin.longitude)}
                title={`${pin.name} · ${pin.region} · ${pin.sale_kg} kg`}
              >
                <span>{pin.name.split(" ")[0]}</span>
              </button>
            ))}
          </div>
          <DataTable
            rows={data.pins}
            columns={[
              { key: "name", label: t("analytics.seller") },
              { key: "region", label: t("analytics.region") },
              { key: "hive_count", label: t("analytics.hives") },
              { key: "sale_kg", label: t("analytics.saleKg") },
              { key: "sale_value_inr", label: t("analytics.saleValue") },
            ]}
          />
          <h2>{t("analytics.regionChart")}</h2>
          <LineChart rows={data.sales_by_region} xKey="label" yKeys={["value"]} labels={[t("analytics.saleKg")]} />
          <h2>{t("analytics.volumeChart")}</h2>
          <LineChart rows={data.volume_by_day} xKey="label" yKeys={["value"]} labels={[t("analytics.saleKg")]} />
          <h2>{t("analytics.reportTitle")}</h2>
          <div className="card">
            <p>{data.report}</p>
          </div>
        </>
      )}
    </div>
  );
}

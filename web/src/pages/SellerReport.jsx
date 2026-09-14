import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { apiGet } from "../api";
import LineChart from "../components/LineChart";
import { Banner, Loading, Metric, PageHeader } from "../components/Ui";

export default function SellerReport() {
  const { t } = useTranslation();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiGet("/api/analytics/seller")
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div>
      <PageHeader kicker={t("seller.kicker")} title={t("seller.title")} purpose={t("seller.purpose")} />
      {error && <Banner tone="bad">{error}</Banner>}
      {!data && !error && <Loading label={t("seller.loading")} />}
      {data && (
        <>
          <div className="grid-3">
            <Metric label={t("analytics.hives")} value={data.hive_count} />
            <Metric label={t("seller.harvestKg")} value={`${data.harvest_kg.toFixed(1)} kg`} />
            <Metric label={t("analytics.saleValue")} value={`₹${data.sale_value_inr.toFixed(0)}`} />
          </div>
          <h2>{t("seller.volume")}</h2>
          <LineChart rows={data.volume_by_day} xKey="label" yKeys={["value"]} labels={[t("seller.harvestKg")]} />
          <h2>{t("analytics.reportTitle")}</h2>
          <div className="card">
            <p>{data.report}</p>
          </div>
        </>
      )}
    </div>
  );
}

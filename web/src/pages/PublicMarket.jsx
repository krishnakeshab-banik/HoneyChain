import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { apiGet } from "../api";
import EmptyState from "../components/EmptyState";
import { Banner, Loading } from "../components/Ui";
import { isSeedDemand, isSeedSale, splitSeed } from "../marketSeed";

export default function PublicMarket() {
  const { t } = useTranslation();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet("/api/public/market")
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const demands = data?.demands || [];
  const prices = data?.prices || [];
  const { live: liveDemands, seed: seedDemands } = splitSeed(demands, isSeedDemand);
  const { live: livePrices, seed: seedPrices } = splitSeed(prices, isSeedSale);

  return (
    <div>
      <p className="page-kicker">{t("publicMarket.kicker")}</p>
      <h1>{t("publicMarket.title")}</h1>
      <p className="purpose">{t("publicMarket.purpose")}</p>
      {loading && <Loading label={t("publicMarket.loading")} />}
      {error && <Banner tone="bad">{t("publicMarket.error")} — {error}</Banner>}
      {data && (
        <>
          <h2>{t("publicMarket.demand")}</h2>
          {liveDemands.length === 0 && <EmptyState title={t("publicMarket.emptyDemand")}>{t("publicMarket.emptyDemand")}</EmptyState>}
          {liveDemands.length > 0 && (
            <div className="card">
              <table>
                <thead>
                  <tr>
                    <th>{t("publicMarket.buyer")}</th>
                    <th>{t("publicMarket.region")}</th>
                    <th>{t("publicMarket.qty")}</th>
                    <th>{t("publicMarket.price")}</th>
                  </tr>
                </thead>
                <tbody>
                  {liveDemands.map((row) => (
                    <tr key={row.demand_id}>
                      <td>{row.buyer_name}</td>
                      <td>{row.region}</td>
                      <td>{row.quantity_kg}</td>
                      <td>
                        {row.price_min_inr}–{row.price_max_inr}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {seedDemands.length > 0 && (
            <div className="seed-panel" data-testid="seed-demand">
              <p className="page-kicker">EXAMPLE LISTINGS</p>
              <h3>One-time seed demand — not a live buyer post</h3>
              <div className="card">
                <table>
                  <thead>
                    <tr>
                      <th>{t("publicMarket.buyer")}</th>
                      <th>{t("publicMarket.region")}</th>
                      <th>{t("publicMarket.qty")}</th>
                      <th>{t("publicMarket.price")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {seedDemands.map((row) => (
                      <tr key={row.demand_id}>
                        <td>{row.buyer_name}</td>
                        <td>{row.region}</td>
                        <td>{row.quantity_kg}</td>
                        <td>
                          {row.price_min_inr}–{row.price_max_inr}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
          <h2>{t("publicMarket.sales")}</h2>
          {livePrices.length === 0 && <EmptyState title={t("publicMarket.emptySales")}>{t("publicMarket.emptySales")}</EmptyState>}
          {livePrices.length > 0 && (
            <div className="card">
              <table>
                <thead>
                  <tr>
                    <th>{t("publicMarket.when")}</th>
                    <th>{t("publicMarket.price")}</th>
                    <th>{t("publicMarket.qty")}</th>
                  </tr>
                </thead>
                <tbody>
                  {livePrices.map((row) => (
                    <tr key={row.sale_id}>
                      <td>{row.recorded_at ? new Date(row.recorded_at).toLocaleString() : "—"}</td>
                      <td>₹{row.price_per_kg_inr}/kg</td>
                      <td>{row.quantity_kg} kg</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {seedPrices.length > 0 && (
            <div className="seed-panel" data-testid="seed-sales">
              <p className="page-kicker">EXAMPLE SALES</p>
              <h3>One-time seed sale — not a new live trade</h3>
              <div className="card">
                <table>
                  <thead>
                    <tr>
                      <th>{t("publicMarket.when")}</th>
                      <th>{t("publicMarket.price")}</th>
                      <th>{t("publicMarket.qty")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {seedPrices.map((row) => (
                      <tr key={row.sale_id}>
                        <td>{row.recorded_at ? new Date(row.recorded_at).toLocaleString() : "—"}</td>
                        <td>₹{row.price_per_kg_inr}/kg</td>
                        <td>{row.quantity_kg} kg</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
          <p>
            <Link className="primary" to="/login">
              {t("publicMarket.trade")}
            </Link>
          </p>
        </>
      )}
    </div>
  );
}

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiGet } from "../api";
import EmptyState from "../components/EmptyState";
import { Banner, Loading } from "../components/Ui";

export default function PublicMarket() {
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

  return (
    <div>
      <p className="page-kicker">PUBLIC</p>
      <h1>Honey market preview</h1>
      <p className="purpose">Standing demand and recent verified sale prices. Sign in to post a listing or bid.</p>
      {loading && <Loading label="Loading market…" />}
      {error && <Banner tone="bad">Couldn't load the market — {error}</Banner>}
      {data && (
        <>
          <h2>Standing demand</h2>
          {demands.length === 0 && (
            <EmptyState title="No demand posts yet">Buyers have not posted standing demand.</EmptyState>
          )}
          {demands.length > 0 && (
            <div className="card">
              <table>
                <thead>
                  <tr>
                    <th>Buyer</th>
                    <th>Region</th>
                    <th>Qty</th>
                    <th>₹/kg</th>
                  </tr>
                </thead>
                <tbody>
                  {demands.map((row) => (
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
          <h2>Recent sales</h2>
          {prices.length === 0 && <EmptyState title="No sales yet">Verified sales will show here.</EmptyState>}
          {prices.length > 0 && (
            <div className="card">
              <table>
                <thead>
                  <tr>
                    <th>When</th>
                    <th>Price</th>
                    <th>Qty</th>
                  </tr>
                </thead>
                <tbody>
                  {prices.map((row) => (
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
          <p>
            <Link className="primary" to="/login">
              Sign in to trade
            </Link>
          </p>
        </>
      )}
    </div>
  );
}

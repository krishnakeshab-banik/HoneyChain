import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { apiGet, apiSend } from "../api";
import { useAuth } from "../auth";
import { Banner, DataTable, Loading, PageHeader } from "../components/Ui";
import { isSeedDemand, isSeedSale, splitSeed } from "../marketSeed";

export default function Market() {
  const { t } = useTranslation();
  const { role } = useAuth();
  const [demands, setDemands] = useState([]);
  const [prices, setPrices] = useState([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);
  const [offerKg, setOfferKg] = useState({});
  const [busyId, setBusyId] = useState("");
  const [demandForm, setDemandForm] = useState({
    demand_id: "DEM-NEW-01",
    buyer_name: "Regional buyer",
    region: "West Bengal",
    quantity_kg: 40,
    price_min_inr: 260,
    price_max_inr: 320,
    notes: "",
  });
  const [saleForm, setSaleForm] = useState({
    sale_id: "SALE-NEW-01",
    batch_id: "",
    demand_id: "",
    region: "West Bengal",
    season: "Mustard 2026",
    price_per_kg_inr: 300,
    quantity_kg: 12,
    buyer_name: "Cluster buyer",
  });

  async function refresh() {
    const [nextDemands, nextPrices] = await Promise.all([apiGet("/api/market/demands"), apiGet("/api/market/prices")]);
    setDemands(nextDemands);
    setPrices(nextPrices);
  }

  useEffect(() => {
    refresh()
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function run(action) {
    setError("");
    setNotice("");
    try {
      const message = await action();
      await refresh();
      if (message) {
        setNotice(message);
      }
    } catch (err) {
      setError(err.message);
    }
  }

  const { live: liveDemands, seed: seedDemands } = splitSeed(demands, isSeedDemand);
  const { live: livePrices, seed: seedPrices } = splitSeed(prices, isSeedSale);

  return (
    <div data-tour="market-board">
      <PageHeader kicker={t("market.kicker")} title={t("market.title")} purpose={t("market.purpose")} />
      {loading && <Loading label={t("market.loading")} />}
      {error && (
        <div data-testid="page-error">
          <Banner tone="bad">
            {t("market.error")} — {error}
          </Banner>
        </div>
      )}
      {notice && (
        <div data-testid="page-notice">
          <Banner tone="good">{notice}</Banner>
        </div>
      )}

      <h2>{t("market.demandTitle")}</h2>
      {liveDemands.length === 0 && !loading && <Banner tone="info">{t("market.emptyDemand")}</Banner>}
      {liveDemands.map((demand) => (
        <div className="card" key={demand.demand_id} style={{ marginBottom: 12 }}>
          <strong>{demand.buyer_name}</strong>
          <p className="muted">
            {demand.demand_id} · {demand.region} · {demand.status}
          </p>
          <p>
            {demand.quantity_kg} kg · ₹{demand.price_min_inr}–{demand.price_max_inr} / kg · {t("market.interest")}:{" "}
            {demand.interest_count}
          </p>
          {demand.notes && <p className="muted">{demand.notes}</p>}
          {role === "admin" && (
            <div className="row" style={{ marginTop: 8 }}>
              <button
                className="ghost"
                type="button"
                onClick={() =>
                  run(async () => {
                    await apiSend("PATCH", `/api/market/demands/${demand.demand_id}`, { status: "approved" });
                    return "Demand approved.";
                  })
                }
              >
                Approve listing
              </button>
              <button
                className="ghost"
                type="button"
                onClick={() =>
                  run(async () => {
                    await apiSend("PATCH", `/api/market/demands/${demand.demand_id}`, { status: "closed" });
                    return "Demand closed.";
                  })
                }
              >
                Close listing
              </button>
            </div>
          )}
          {role === "beekeeper" && demand.status === "open" && (
            <div className="row" style={{ marginTop: 8 }}>
              <input
                type="number"
                min="0.1"
                step="0.1"
                placeholder={t("market.offer")}
                value={offerKg[demand.demand_id] || ""}
                onChange={(event) => setOfferKg((prev) => ({ ...prev, [demand.demand_id]: event.target.value }))}
                style={{ maxWidth: 140 }}
              />
              <button
                className="primary"
                type="button"
                disabled={busyId === demand.demand_id || !offerKg[demand.demand_id]}
                onClick={() =>
                  run(async () => {
                    setBusyId(demand.demand_id);
                    try {
                      await apiSend("POST", `/api/market/demands/${demand.demand_id}/interest`, {
                        offered_kg: Number(offerKg[demand.demand_id]),
                      });
                      return "Interest recorded.";
                    } finally {
                      setBusyId("");
                    }
                  })
                }
              >
                {busyId === demand.demand_id ? t("market.expressing") : t("market.express")}
              </button>
            </div>
          )}
        </div>
      ))}

      {seedDemands.length > 0 && (
        <div className="seed-panel" data-testid="seed-demand">
          <p className="page-kicker">EXAMPLE LISTINGS</p>
          <h3>One-time seed demand — not a live buyer post</h3>
          <p className="muted">Kept apart from the live board so a new listing is not mistaken for demo data.</p>
          {seedDemands.map((demand) => (
            <div className="card" key={demand.demand_id} style={{ marginBottom: 12 }}>
              <strong>{demand.buyer_name}</strong>
              <p className="muted">
                {demand.demand_id} · {demand.region} · {demand.status}
              </p>
              <p>
                {demand.quantity_kg} kg · ₹{demand.price_min_inr}–{demand.price_max_inr} / kg
              </p>
              {demand.notes && <p className="muted">{demand.notes}</p>}
            </div>
          ))}
        </div>
      )}

      {["officer", "admin"].includes(role) && (
        <form
          className="card"
          onSubmit={(event) => {
            event.preventDefault();
            run(async () => {
              await apiSend("POST", "/api/market/demands", {
                ...demandForm,
                quantity_kg: Number(demandForm.quantity_kg),
                price_min_inr: Number(demandForm.price_min_inr),
                price_max_inr: Number(demandForm.price_max_inr),
              });
              return t("market.posted");
            });
          }}
        >
          <h3>{t("market.postDemand")}</h3>
          <div className="grid-2">
            {["demand_id", "buyer_name", "region", "quantity_kg", "price_min_inr", "price_max_inr", "notes"].map((key) => (
              <div key={key}>
                <label htmlFor={key}>{key.replaceAll("_", " ")}</label>
                <input
                  id={key}
                  value={demandForm[key]}
                  onChange={(event) => setDemandForm((prev) => ({ ...prev, [key]: event.target.value }))}
                />
              </div>
            ))}
          </div>
          <div className="row" style={{ marginTop: 12 }}>
            <button className="primary" type="submit">
              {t("market.postDemand")}
            </button>
          </div>
        </form>
      )}

      <h2>{t("market.pricesTitle")}</h2>
      {livePrices.length === 0 && !loading ? (
        <Banner tone="info">{t("market.emptyPrices")}</Banner>
      ) : (
        <DataTable
          rows={livePrices}
          columns={[
            { key: "sale_id", label: t("market.saleId") },
            { key: "batch_id", label: t("market.batchId") },
            { key: "region", label: t("market.region") },
            { key: "season", label: t("market.season") },
            { key: "price_per_kg_inr", label: t("market.pricePerKg") },
            { key: "quantity_kg", label: t("market.quantity") },
            { key: "buyer_name", label: t("market.buyer") },
          ]}
        />
      )}
      {seedPrices.length > 0 && (
        <div className="seed-panel" data-testid="seed-sales">
          <p className="page-kicker">EXAMPLE SALES</p>
          <h3>One-time seed sale — not a new live trade</h3>
          <DataTable
            rows={seedPrices}
            columns={[
              { key: "sale_id", label: t("market.saleId") },
              { key: "batch_id", label: t("market.batchId") },
              { key: "region", label: t("market.region") },
              { key: "price_per_kg_inr", label: t("market.pricePerKg") },
              { key: "quantity_kg", label: t("market.quantity") },
            ]}
          />
        </div>
      )}

      {role === "admin" && (
        <form
          className="card"
          style={{ marginTop: 16 }}
          onSubmit={(event) => {
            event.preventDefault();
            run(async () => {
              await apiSend("POST", "/api/market/sales", {
                ...saleForm,
                demand_id: saleForm.demand_id || null,
                price_per_kg_inr: Number(saleForm.price_per_kg_inr),
                quantity_kg: Number(saleForm.quantity_kg),
              });
              return t("market.saleLinked");
            });
          }}
        >
          <h3>{t("market.linkSale")}</h3>
          <div className="grid-2">
            {Object.keys(saleForm).map((key) => (
              <div key={key}>
                <label htmlFor={`sale_${key}`}>{key.replaceAll("_", " ")}</label>
                <input
                  id={`sale_${key}`}
                  value={saleForm[key]}
                  onChange={(event) => setSaleForm((prev) => ({ ...prev, [key]: event.target.value }))}
                />
              </div>
            ))}
          </div>
          <div className="row" style={{ marginTop: 12 }}>
            <button className="primary" type="submit" disabled={!saleForm.batch_id}>
              {t("market.linkSale")}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

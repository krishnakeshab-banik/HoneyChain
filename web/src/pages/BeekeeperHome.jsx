import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiGet } from "../api";
import { useAuth } from "../auth";
import TourOffer from "../components/TourOffer";
import { Banner, Loading, StatCard } from "../components/Ui";
import { welcomeLine } from "../greeting";

export default function BeekeeperHome() {
  const { user } = useAuth();
  const [hives, setHives] = useState([]);
  const [summary, setSummary] = useState(null);
  const [harvests, setHarvests] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([apiGet("/api/auth/me/hives"), apiGet("/api/auth/me/harvests")])
      .then(async ([nextHives, nextHarvests]) => {
        setHives(nextHives);
        setHarvests(nextHarvests);
        if (nextHives[0]) {
          setSummary(await apiGet(`/api/hives/${nextHives[0].hive_id}/summary`));
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const latest = summary?.latest;
  const pending = harvests.filter((row) => row.status === "pending").length;

  return (
    <div className="role-home">
      <p className="page-kicker">YOUR HIVES</p>
      <h1 data-tour="dash-welcome">{welcomeLine(user?.display_name, "here's your hive status today")}</h1>
      <p className="purpose">Only your assigned colonies. Numbers below refresh from the live hive feed.</p>
      <TourOffer />
      {loading && <Loading label="Loading your hives…" />}
      {error && <Banner tone="bad">Couldn't load your home — {error}</Banner>}
      <div className="grid-3">
        <StatCard label="Your hives" value={hives.length} />
        <StatCard label="Harvests still pending" value={pending} />
        <StatCard label="Latest hive weight" value={latest ? `${Number(latest.weight_kg).toFixed(2)} kg` : "Awaiting data"} />
      </div>
      {latest ? (
        <div className="card lift-card">
          <p className="page-kicker">{hives[0]?.hive_id}</p>
          <strong>Live colony reading</strong>
          <p>
            {Number(latest.inside_temperature_c).toFixed(1)} °C · {Number(latest.humidity_pct).toFixed(1)}% humidity ·{" "}
            {Number(latest.weight_kg).toFixed(2)} kg
          </p>
        </div>
      ) : (
        !loading && <Banner tone="info">Awaiting hive scale data. Start the simulator or wait for the next reading.</Banner>
      )}
      <div className="row" style={{ marginTop: 16 }}>
        <Link className="primary" to="/app/harvests">
          Log a harvest
        </Link>
        <Link className="ghost" to="/app/monitor">
          See hive status
        </Link>
        <Link className="ghost" to="/app/market">
          Open market board
        </Link>
      </div>
    </div>
  );
}

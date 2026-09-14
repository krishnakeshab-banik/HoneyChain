import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiGet } from "../api";
import TourOffer from "../components/TourOffer";
import { useAuth } from "../auth";
import { Banner, DataTable, Loading, SectionHeading, StatCard } from "../components/Ui";
import { welcomeLine } from "../greeting";

export default function OfficerCluster() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet("/api/auth/me/cluster")
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div data-tour="cluster">
        <SectionHeading
          kicker="CLUSTER OVERVIEW"
          title={welcomeLine(user?.display_name, "here's your cluster today")}
          purpose="Hives and beekeepers in your region. You will not see hives from other regions."
        />
      </div>
      <TourOffer />
      <div className="row" style={{ marginBottom: 12 }}>
        <Link className="primary" to="/app/batches">
          Review pending harvests
        </Link>
        <Link className="ghost" to="/app/alerts">
          Cluster alerts
        </Link>
      </div>
      {loading && <Loading label="Loading cluster…" />}
      {error && <Banner tone="bad">Couldn't load cluster — {error}</Banner>}
      {data && (
        <>
          <div className="grid-3">
            <StatCard label="Region" value={data.region || "—"} />
            <StatCard label="Hives" value={data.hives.length} />
            <StatCard label="Beekeepers" value={data.beekeepers.length} />
          </div>
          <h2>Beekeepers</h2>
          {data.beekeepers.length === 0 ? (
            <Banner tone="info">No beekeepers in this region yet.</Banner>
          ) : (
            <DataTable
              rows={data.beekeepers}
              columns={[
                { key: "beekeeper_id", label: "ID" },
                { key: "name", label: "Name" },
                { key: "cluster", label: "Cluster" },
                { key: "region", label: "Region" },
              ]}
            />
          )}
          <h2>Hives</h2>
          {data.hives.length === 0 ? (
            <Banner tone="info">No hives assigned to this cluster.</Banner>
          ) : (
            <DataTable
              rows={data.hives}
              columns={[
                { key: "hive_id", label: "Hive" },
                { key: "name", label: "Name" },
                { key: "region", label: "Region" },
                { key: "bee_species", label: "Species" },
              ]}
            />
          )}
        </>
      )}
    </div>
  );
}

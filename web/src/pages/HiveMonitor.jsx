import { useEffect, useState } from "react";
import { apiGet, apiSend } from "../api";
import LineChart from "../components/LineChart";
import { Banner, HiveSelect, Loading, Metric, PageHeader } from "../components/Ui";

export default function HiveMonitor() {
  const [hives, setHives] = useState(null);
  const [hiveId, setHiveId] = useState("");
  const [readings, setReadings] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [probe, setProbe] = useState("");

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
      return undefined;
    }
    setReadings(null);
    const tick = () => {
      apiGet(`/api/hives/${hiveId}/sensor-readings`)
        .then(setReadings)
        .catch((err) => setError(err.message));
    };
    tick();
    const timer = setInterval(tick, 5000);
    return () => clearInterval(timer);
  }, [hiveId]);

  const latest = readings && readings.length ? readings[readings.length - 1] : null;

  return (
    <div>
      <PageHeader
        kicker="HIVE MONITOR"
        title="Hive Monitor"
        purpose="Watch the full sensor history for one hive. Charts are drawn from GET /api/hives/{id}/sensor-readings and refresh every five seconds."
      />
      {loading && <Loading label="Loading hives…" />}
      {error && (
        <Banner tone="bad">
          Couldn't load hive telemetry — {error}{" "}
          <button className="ghost" type="button" onClick={() => window.location.reload()}>
            Retry
          </button>
        </Banner>
      )}
      {hives && hives.length === 0 && <Banner tone="warn">No hives registered yet. Register one on Overview.</Banner>}
      {hives && hives.length > 0 && (
        <div data-tour="hive-select">
          <HiveSelect hives={hives} value={hiveId} onChange={setHiveId} id="monitor-hive" />
        </div>
      )}
      {hiveId && readings === null && !error && <Loading label="Loading telemetry…" />}

      {readings && readings.length === 0 && (
        <Banner tone="warn">Nothing here yet. Start the hive simulator so readings can arrive.</Banner>
      )}

      {latest && (
        <>
          <div className="grid-3">
            <Metric label="Latest inside temperature" value={`${Number(latest.inside_temperature_c).toFixed(1)} °C`} />
            <Metric label="Latest humidity" value={`${Number(latest.humidity_pct).toFixed(1)} %`} />
            <Metric label="Telemetry points" value={readings.length} />
          </div>
          <h2>Temperature</h2>
          <LineChart
            rows={readings}
            xKey="timestamp"
            yKeys={["inside_temperature_c", "outside_temperature_c"]}
            labels={["Inside °C", "Outside °C"]}
          />
          <h2>Humidity</h2>
          <LineChart rows={readings} xKey="timestamp" yKeys={["humidity_pct"]} labels={["Humidity %"]} />
          <h2>Hive weight</h2>
          <LineChart rows={readings} xKey="timestamp" yKeys={["weight_kg"]} labels={["Weight kg"]} />
        </>
      )}

      <h2>Probe an invalid reading</h2>
      <p className="muted">Sends humidity 140% to POST /api/sensor-readings. The API must reject it with a readable validation error.</p>
      <button
        className="ghost"
        type="button"
        onClick={async () => {
          setProbe("");
          try {
            await apiSend("POST", "/api/sensor-readings", {
              hive_id: hiveId || "IN-WB-001",
              timestamp: new Date().toISOString(),
              inside_temperature_c: 34.2,
              outside_temperature_c: 31,
              humidity_pct: 140,
              weight_kg: 42.8,
              source: "manual",
            });
            setProbe("Unexpected success — the API accepted an impossible humidity.");
          } catch (err) {
            setProbe(err.message);
          }
        }}
      >
        Send invalid humidity reading
      </button>
      {probe && <Banner tone="warn">{probe}</Banner>}
    </div>
  );
}

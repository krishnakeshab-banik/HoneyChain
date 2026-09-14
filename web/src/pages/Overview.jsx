import { useEffect, useState } from "react";
import { apiGet, apiPost, apiSend } from "../api";
import { useAuth } from "../auth";
import { Banner, HiveSelect, Loading, Metric, PageHeader } from "../components/Ui";
import { welcomeLine } from "../greeting";

export default function Overview({ canRegister = true }) {
  const { user } = useAuth();
  const [hives, setHives] = useState(null);
  const [hiveId, setHiveId] = useState("");
  const [summary, setSummary] = useState(null);
  const [hive, setHive] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [registering, setRegistering] = useState(false);
  const [demo, setDemo] = useState(null);
  const [form, setForm] = useState({
    hive_id: "IN-KL-002",
    name: "Kerala Field Hive",
    country: "India",
    region: "Kerala",
    bee_species: "Apis cerana",
    climate_zone: "tropical",
    data_source: "manual",
    source_reference: "operator entry",
  });

  async function loadHives() {
    const list = await apiGet("/api/auth/me/hives").catch(() => apiGet("/api/hives"));
    setHives(list);
    setHiveId((current) => current || list.find((item) => item.hive_id === "IN-WB-001")?.hive_id || list[0]?.hive_id || "");
  }

  async function loadLive(id) {
    if (!id) {
      return;
    }
    const [nextSummary, nextHive] = await Promise.all([
      apiGet(`/api/hives/${id}/summary`),
      apiGet(`/api/hives/${id}`),
    ]);
    setSummary(nextSummary);
    setHive(nextHive);
  }

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    loadHives()
      .catch((err) => {
        if (!cancelled) {
          setError(err.message);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!hiveId) {
      return undefined;
    }
    setSummary(null);
    setHive(null);
    let cancelled = false;
    const tick = () => {
      loadLive(hiveId).catch((err) => {
        if (!cancelled) {
          setError(err.message);
        }
      });
    };
    tick();
    const timer = setInterval(tick, 5000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [hiveId]);

  async function registerHive(event) {
    event.preventDefault();
    setRegistering(true);
    setError("");
    try {
      await apiSend("POST", "/api/hives", { ...form, active: true });
      await loadHives();
      setHiveId(form.hive_id);
    } catch (err) {
      setError(err.message);
    } finally {
      setRegistering(false);
    }
  }

  const latest = summary?.latest;

  useEffect(() => {
    if (!canRegister) {
      return undefined;
    }
    let cancelled = false;
    const tick = () => {
      apiGet("/api/demo/status")
        .then((row) => {
          if (!cancelled) {
            setDemo(row);
          }
        })
        .catch(() => {});
    };
    tick();
    const timer = setInterval(tick, 4000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [canRegister]);

  return (
    <div>
      <PageHeader
        kicker="OVERVIEW"
        title={welcomeLine(user?.display_name, "here's the live hive picture")}
        purpose="See the latest hive telemetry. Numbers refresh from the API every five seconds."
      />
      <h2 className="sr-only">From hive signals to trusted honey.</h2>

      {loading && <Loading label="Loading hive list…" />}
      {error && (
        <Banner tone="bad">
          Couldn't load hive data — {error}{" "}
          <button className="ghost" type="button" onClick={() => window.location.reload()}>
            Retry
          </button>
        </Banner>
      )}
      {hives && hives.length === 0 && (
        <Banner tone="warn">No hives are registered yet. Use the form below to add one.</Banner>
      )}

      {hives && hives.length > 0 && (
        <HiveSelect hives={hives} value={hiveId} onChange={setHiveId} />
      )}
      {hiveId && !summary && !error && <Loading label="Loading current hive state…" />}

      {hiveId && summary && !latest && (
        <Banner tone="warn">
          Nothing here yet — hive {hiveId} has no sensor readings. Start the simulator
          (`python simulator/hive_simulator.py`) or wait for queued readings to sync.
        </Banner>
      )}

      {latest && (
        <>
          <p className="muted">Live simulation · last reading {latest.timestamp}</p>
          <div className="grid-4">
            <Metric label="Inside temperature" value={`${Number(latest.inside_temperature_c).toFixed(1)} °C`} />
            <Metric label="Humidity" value={`${Number(latest.humidity_pct).toFixed(1)} %`} />
            <Metric label="Hive weight" value={`${Number(latest.weight_kg).toFixed(2)} kg`} />
            <Metric label="Readings received" value={summary.reading_count} />
          </div>
          {hive && (
            <div className="card">
              <strong>{hive.name}</strong>
              <p className="muted">
                {hive.hive_id} · {hive.bee_species} · {hive.climate_zone} · {hive.data_source}
              </p>
              <p>{hive.source_reference}</p>
            </div>
          )}
        </>
      )}

      {canRegister && demo && (
        <div className="card">
          <p className="page-kicker">SIMULATOR LINK</p>
          <p>Mode {demo.mode}. Offline queue {demo.queue_length} reading(s). {demo.note}</p>
          <div className="row">
            {["offline", "online", "auto"].map((mode) => (
              <button
                key={mode}
                className="ghost"
                type="button"
                onClick={() => apiPost("/api/demo/link", { mode }).then(setDemo).catch((err) => setError(err.message))}
              >
                Force {mode}
              </button>
            ))}
          </div>
        </div>
      )}
      {canRegister && <h2>Register a hive</h2>}
      {canRegister && <p className="purpose">Creates a real hive record via POST /api/hives. The new hive appears in this list immediately.</p>}
      {canRegister && (
      <form className="card" onSubmit={registerHive}>
        <div className="grid-2">
          {Object.entries(form).map(([key, value]) => (
            <div key={key}>
              <label htmlFor={key}>{key.replaceAll("_", " ")}</label>
              {key === "data_source" ? (
                <select
                  id={key}
                  value={value}
                  onChange={(event) => setForm((prev) => ({ ...prev, [key]: event.target.value }))}
                >
                  <option value="manual">manual</option>
                  <option value="simulated">simulated</option>
                  <option value="real_dataset">real_dataset</option>
                </select>
              ) : (
                <input
                  id={key}
                  value={value}
                  onChange={(event) => setForm((prev) => ({ ...prev, [key]: event.target.value }))}
                />
              )}
            </div>
          ))}
        </div>
        <div className="row" style={{ marginTop: 12 }}>
          <button className="primary" type="submit" disabled={registering}>
            {registering ? "Registering…" : "Register hive"}
          </button>
        </div>
      </form>
      )}
    </div>
  );
}

import { useCallback, useEffect, useState } from "react";
import { apiGet, apiSend, qrImageUrl } from "../api";
import { Banner, DataTable, Loading, PageHeader } from "../components/Ui";

function nowIso() {
  return new Date().toISOString();
}

export default function Traceability({ role = "admin" }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [hives, setHives] = useState([]);
  const [keepers, setKeepers] = useState([]);
  const [harvests, setHarvests] = useState([]);
  const [batches, setBatches] = useState([]);
  const [packages, setPackages] = useState([]);
  const [chain, setChain] = useState([]);
  const [integrity, setIntegrity] = useState(null);
  const [harvestForm, setHarvestForm] = useState({
    harvest_id: "HV-WEB-001",
    hive_id: "IN-WB-001",
    beekeeper_id: "BK-WB-01",
    raw_weight_kg: 6.5,
    moisture_pct: 17.2,
  });
  const [batchForm, setBatchForm] = useState({
    batch_id: "BT-WEB-001",
    harvest_ids: [],
    declared_weight_kg: 6.5,
    lab_test_result: "pass",
    lab_notes: "Moisture and HMF within spec.",
  });
  const [commitId, setCommitId] = useState("");
  const [packageForm, setPackageForm] = useState({
    package_id: "PK-WEB-001",
    batch_id: "",
  });

  const refresh = useCallback(async () => {
    const [nextHives, nextKeepers, nextHarvests, nextBatches, nextPackages, nextChain, nextIntegrity] =
      await Promise.all([
        apiGet("/api/hives"),
        apiGet("/api/beekeepers"),
        apiGet("/api/harvests"),
        apiGet("/api/batches"),
        apiGet("/api/packages"),
        apiGet("/api/ledger/chain"),
        apiGet("/api/ledger/integrity"),
      ]);
    setHives(nextHives);
    setKeepers(nextKeepers);
    setHarvests(nextHarvests);
    setBatches(nextBatches);
    setPackages(nextPackages);
    setChain(nextChain);
    setIntegrity(nextIntegrity);
    setHarvestForm((prev) => ({
      ...prev,
      hive_id: prev.hive_id || nextHives[0]?.hive_id || "",
      beekeeper_id: prev.beekeeper_id || nextKeepers[0]?.beekeeper_id || "",
    }));
    setPackageForm((prev) => ({
      ...prev,
      batch_id: prev.batch_id || nextBatches.find((item) => item.status === "committed")?.batch_id || "",
    }));
  }, []);

  useEffect(() => {
    refresh()
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [refresh]);

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

  const committed = batches.filter((item) => item.status === "committed");
  const committable = batches.filter((item) => item.status !== "committed");
  const canBatch = role !== "beekeeper";

  return (
    <div>
      <PageHeader
        kicker="TRACEABILITY"
        title="Traceability"
        purpose="Register a harvest, assemble a batch, run the weight oracle, commit a passing batch to the hash-chain, and issue a package QR."
      />
      {loading && <Loading label="Loading harvests, batches, and ledger…" />}
      {error && (
        <div data-testid="page-error">
          <Banner tone="bad">Couldn't update traceability data — {error}</Banner>
        </div>
      )}
      {notice && (
        <div data-testid="page-notice">
          <Banner tone="good">{notice}</Banner>
        </div>
      )}

      <h2>1. Register a harvest</h2>
      <p className="muted">Needs at least one sensor reading. Harvest weight cannot exceed the latest hive scale reading.</p>
      <form
        className="card"
        onSubmit={(event) => {
          event.preventDefault();
          run(async () => {
            const created = await apiSend("POST", "/api/harvests", {
              ...harvestForm,
              harvested_at: nowIso(),
              raw_weight_kg: Number(harvestForm.raw_weight_kg),
              moisture_pct: Number(harvestForm.moisture_pct),
            });
            return `Harvest ${created.harvest_id} stored. Sensor-logged weight ${created.sensor_logged_weight_kg} kg.`;
          });
        }}
      >
        <div className="grid-2">
          <div>
            <label htmlFor="harvest_id">Harvest ID</label>
            <input
              id="harvest_id"
              value={harvestForm.harvest_id}
              onChange={(event) => setHarvestForm((prev) => ({ ...prev, harvest_id: event.target.value }))}
            />
          </div>
          <div>
            <label htmlFor="harvest_hive">Hive</label>
            <select
              id="harvest_hive"
              value={harvestForm.hive_id}
              onChange={(event) => setHarvestForm((prev) => ({ ...prev, hive_id: event.target.value }))}
            >
              {hives.map((hive) => (
                <option key={hive.hive_id} value={hive.hive_id}>
                  {hive.hive_id} · {hive.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="beekeeper">Beekeeper</label>
            <select
              id="beekeeper"
              value={harvestForm.beekeeper_id}
              onChange={(event) => setHarvestForm((prev) => ({ ...prev, beekeeper_id: event.target.value }))}
            >
              {keepers.map((keeper) => (
                <option key={keeper.beekeeper_id} value={keeper.beekeeper_id}>
                  {keeper.beekeeper_id} · {keeper.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="raw_weight">Raw harvest weight (kg)</label>
            <input
              id="raw_weight"
              type="number"
              step="0.1"
              value={harvestForm.raw_weight_kg}
              onChange={(event) => setHarvestForm((prev) => ({ ...prev, raw_weight_kg: event.target.value }))}
            />
          </div>
          <div>
            <label htmlFor="moisture">Moisture %</label>
            <input
              id="moisture"
              type="number"
              step="0.1"
              value={harvestForm.moisture_pct}
              onChange={(event) => setHarvestForm((prev) => ({ ...prev, moisture_pct: event.target.value }))}
            />
          </div>
        </div>
        <div className="row" style={{ marginTop: 12 }}>
          <button className="primary" type="submit">Create harvest</button>
        </div>
      </form>
      {harvests.length === 0 ? (
        <Banner tone="info">No harvests yet. Create one after the simulator has sent readings.</Banner>
      ) : (
        <DataTable
          rows={harvests}
          columns={[
            { key: "harvest_id", label: "Harvest" },
            { key: "hive_id", label: "Hive" },
            { key: "raw_weight_kg", label: "Raw kg" },
            { key: "sensor_logged_weight_kg", label: "Sensor-logged kg" },
            { key: "moisture_pct", label: "Moisture %" },
          ]}
        />
      )}

      {canBatch && <h2>2. Create and commit a batch</h2>}
      {canBatch && (<>
      <form
        className="card"
        data-tour="batch-form"
        onSubmit={(event) => {
          event.preventDefault();
          run(async () => {
            const created = await apiSend("POST", "/api/batches", {
              batch_id: batchForm.batch_id,
              harvest_ids: batchForm.harvest_ids,
              processing_date: nowIso(),
              declared_weight_kg: Number(batchForm.declared_weight_kg),
              lab_test_result: batchForm.lab_test_result,
              lab_notes: batchForm.lab_notes,
            });
            setCommitId(created.batch_id);
            return `Draft batch ${created.batch_id} created.`;
          });
        }}
      >
        <div className="grid-2">
          <div>
            <label htmlFor="batch_id">Batch ID</label>
            <input
              id="batch_id"
              value={batchForm.batch_id}
              onChange={(event) => setBatchForm((prev) => ({ ...prev, batch_id: event.target.value }))}
            />
          </div>
          <div>
            <label htmlFor="declared">Declared batch weight (kg)</label>
            <input
              id="declared"
              type="number"
              step="0.1"
              value={batchForm.declared_weight_kg}
              onChange={(event) => setBatchForm((prev) => ({ ...prev, declared_weight_kg: event.target.value }))}
            />
          </div>
          <div>
            <label htmlFor="lab">Lab test result</label>
            <select
              id="lab"
              value={batchForm.lab_test_result}
              onChange={(event) => setBatchForm((prev) => ({ ...prev, lab_test_result: event.target.value }))}
            >
              <option value="pass">pass</option>
              <option value="fail">fail</option>
              <option value="pending">pending</option>
            </select>
          </div>
          <div>
            <label htmlFor="notes">Lab notes</label>
            <input
              id="notes"
              value={batchForm.lab_notes}
              onChange={(event) => setBatchForm((prev) => ({ ...prev, lab_notes: event.target.value }))}
            />
          </div>
        </div>
        <div style={{ marginTop: 10 }}>
          <label>Linked harvests</label>
          {harvests.length === 0 && <p className="muted">No harvests available to link.</p>}
          {harvests.map((harvest) => (
            <label key={harvest.harvest_id} style={{ display: "block", margin: "6px 0" }} data-testid={`harvest-link-${harvest.harvest_id}`}>
              <input
                type="checkbox"
                checked={batchForm.harvest_ids.includes(harvest.harvest_id)}
                onChange={(event) => {
                  setBatchForm((prev) => ({
                    ...prev,
                    harvest_ids: event.target.checked
                      ? [...prev.harvest_ids, harvest.harvest_id]
                      : prev.harvest_ids.filter((id) => id !== harvest.harvest_id),
                  }));
                }}
              />{" "}
              {harvest.harvest_id} ({harvest.sensor_logged_weight_kg} kg sensor-logged)
            </label>
          ))}
        </div>
        <div className="row" style={{ marginTop: 12 }}>
          <button className="primary" type="submit">Create draft batch</button>
        </div>
      </form>

      {batches.length === 0 ? (
        <Banner tone="info">No batches yet. Create a draft after you have a harvest.</Banner>
      ) : (
        <DataTable
          rows={batches}
          columns={[
            { key: "batch_id", label: "Batch" },
            { key: "status", label: "Status" },
            { key: "oracle_status", label: "Oracle" },
            { key: "declared_weight_kg", label: "Declared kg" },
            { key: "oracle_reason", label: "Oracle reason" },
          ]}
        />
      )}

      <div className="card" style={{ marginTop: 12 }} data-tour="commit">
        <label htmlFor="commit">Commit batch</label>
        <select id="commit" value={commitId} onChange={(event) => setCommitId(event.target.value)}>
          <option value="">Select a draft or rejected batch</option>
          {committable.map((batch) => (
            <option key={batch.batch_id} value={batch.batch_id}>
              {batch.batch_id} · {batch.status}
            </option>
          ))}
        </select>
        <div className="row" style={{ marginTop: 12 }}>
          <button
            className="primary"
            type="button"
            disabled={!commitId}
            onClick={() =>
              run(async () => {
                const result = await apiSend("POST", `/api/batches/${commitId}/commit`);
                return `Batch ${result.batch_id} committed. ${result.oracle_reason}`;
              })
            }
          >
            Run oracle and commit
          </button>
        </div>
      </div>

      </>)}
      {canBatch && <h2>3. Issue a package QR</h2>}
      {canBatch && (<>
      <form
        className="card"
        onSubmit={(event) => {
          event.preventDefault();
          run(async () => {
            const created = await apiSend("POST", "/api/packages", {
              package_id: packageForm.package_id,
              batch_id: packageForm.batch_id,
              verify_base_url: `${window.location.origin}/verify`,
            });
            return `Package ${created.package_id} ready. Scan URL: ${created.qr_reference}`;
          });
        }}
      >
        <div className="grid-2">
          <div>
            <label htmlFor="package_id">Package ID</label>
            <input
              id="package_id"
              value={packageForm.package_id}
              onChange={(event) => setPackageForm((prev) => ({ ...prev, package_id: event.target.value }))}
            />
          </div>
          <div>
            <label htmlFor="pkg_batch">Committed batch</label>
            <select
              id="pkg_batch"
              value={packageForm.batch_id}
              onChange={(event) => setPackageForm((prev) => ({ ...prev, batch_id: event.target.value }))}
            >
              <option value="">Select a committed batch</option>
              {committed.map((batch) => (
                <option key={batch.batch_id} value={batch.batch_id}>
                  {batch.batch_id}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="row" style={{ marginTop: 12 }}>
          <button className="primary" type="submit" disabled={!packageForm.batch_id}>
            Generate package + QR
          </button>
        </div>
      </form>
      {packages.length === 0 ? (
        <Banner tone="info">No packages yet. Commit a passing batch first.</Banner>
      ) : (
        <div className="grid-2">
          {packages.map((item) => (
            <div className="card" key={item.package_id}>
              <strong>{item.package_id}</strong>
              <p className="muted">{item.qr_reference}</p>
              <img className="qr" alt={`QR for ${item.package_id}`} src={qrImageUrl(item.package_id)} />
            </div>
          ))}
        </div>
      )}

      <h2>Ledger</h2>
      {integrity && (
        <Banner tone={integrity.valid ? "good" : "bad"}>{integrity.detail}</Banner>
      )}
      {chain.length === 0 ? (
        <Banner tone="info">Ledger is empty until a batch passes the oracle and is committed.</Banner>
      ) : (
        <DataTable
          rows={chain}
          columns={[
            { key: "index", label: "Index" },
            { key: "batch_id", label: "Batch" },
            { key: "block_hash", label: "Block hash" },
          ]}
        />
      )}
      </>)}
    </div>
  );
}

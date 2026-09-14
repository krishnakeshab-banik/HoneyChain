import { useEffect, useState } from "react";
import { apiGet } from "../api";
import { Banner, DataTable, Loading, SectionHeading } from "../components/Ui";

export default function LedgerIntegrity() {
  const [chain, setChain] = useState([]);
  const [integrity, setIntegrity] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    Promise.all([apiGet("/api/ledger/chain"), apiGet("/api/ledger/integrity")])
      .then(([nextChain, nextIntegrity]) => {
        setChain(nextChain);
        setIntegrity(nextIntegrity);
        setError("");
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div data-tour="ledger">
      <SectionHeading
        kicker="LEDGER INTEGRITY"
        title="Live hash-chain verification"
        purpose="Integrity is recomputed from the stored blocks every time this page loads. It is never a stored tick."
      />
      {loading && <Loading label="Recomputing ledger…" />}
      {error && (
        <Banner tone="bad">
          Couldn't load ledger — {error}{" "}
          <button className="ghost" type="button" onClick={load}>
            Retry
          </button>
        </Banner>
      )}
      {integrity && <Banner tone={integrity.valid ? "good" : "bad"}>{integrity.detail}</Banner>}
      {chain.length === 0 && !loading ? (
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
    </div>
  );
}

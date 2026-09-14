import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { apiGet, apiSend, qrImageUrl } from "../api";
import { Banner, DataTable, Loading, Metric, PageHeader } from "../components/Ui";

const LOCATIONS = {
  "Kolkata shop": { latitude: 22.5726, longitude: 88.3639, location_label: "Kolkata shop" },
  "Mumbai market": { latitude: 19.076, longitude: 72.8777, location_label: "Mumbai market" },
  "Bremen store": { latitude: 53.0793, longitude: 8.8017, location_label: "Bremen store" },
};

export default function ConsumerVerify() {
  const { t } = useTranslation();
  const [params, setParams] = useSearchParams();
  const initialPackageId = params.get("package_id") || "";
  const [packageId, setPackageId] = useState(initialPackageId);
  const [locationName, setLocationName] = useState("Kolkata shop");
  const [packages, setPackages] = useState([]);
  const [passport, setPassport] = useState(null);
  const [error, setError] = useState("");
  const [loadingList, setLoadingList] = useState(true);
  const [verifying, setVerifying] = useState(false);

  useEffect(() => {
    apiGet("/api/packages")
      .then((list) => {
        setPackages(list);
        if (!packageId && list[0]) {
          setPackageId(list[0].package_id);
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoadingList(false));
  }, []);

  useEffect(() => {
    if (initialPackageId) {
      setPackageId(initialPackageId);
    }
  }, [initialPackageId]);

  useEffect(() => {
    if (!initialPackageId) {
      return;
    }
    setVerifying(true);
    apiSend("POST", `/api/verify/${initialPackageId}`, LOCATIONS["Kolkata shop"])
      .then((result) => {
        setPassport(result);
        if (initialPackageId) {
          const next = new URLSearchParams(params);
          next.delete("package_id");
          setParams(next, { replace: true });
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setVerifying(false));
  }, [initialPackageId]);

  function resolvePackageId(raw) {
    const value = (raw || "").trim();
    if (!value) {
      return "";
    }
    const exact = packages.find((item) => item.package_id === value);
    if (exact) {
      return exact.package_id;
    }
    const byBatch = packages.find((item) => item.batch_id === value);
    if (byBatch) {
      return byBatch.package_id;
    }
    return value;
  }

  async function verify(event) {
    event.preventDefault();
    setVerifying(true);
    setError("");
    try {
      const target = resolvePackageId(packageId);
      const result = await apiSend("POST", `/api/verify/${target}`, LOCATIONS[locationName]);
      setPassport(result);
    } catch (err) {
      setPassport(null);
      setError(err.message);
    } finally {
      setVerifying(false);
    }
  }

  return (
    <div className="verify-page">
      <PageHeader kicker={t("verify.kicker")} title={t("verify.title")} purpose={t("verify.purpose")} />
      {loadingList && <Loading label={t("verify.loading")} />}
      {error && (
        <div data-testid="page-error">
          <Banner tone="bad">
            {t("verify.error")} — {error}
          </Banner>
        </div>
      )}

      <form className="card verify-card" onSubmit={verify}>
        <div className="grid-2">
          <div>
            <label htmlFor="verify_id">{t("verify.packageId")}</label>
            <input
              id="verify_id"
              value={packageId}
              onChange={(event) => setPackageId(event.target.value)}
              placeholder="PK-… or BT-…"
            />
            <p className="muted">{t("verify.batchHint")}</p>
          </div>
          <div>
            <label htmlFor="scan_location">{t("verify.location")}</label>
            <select id="scan_location" value={locationName} onChange={(event) => setLocationName(event.target.value)}>
              {Object.keys(LOCATIONS).map((name) => (
                <option key={name} value={name}>
                  {name}
                </option>
              ))}
            </select>
          </div>
        </div>
        {packages.length === 0 && <Banner tone="info">{t("verify.empty")}</Banner>}
        <div className="row" style={{ marginTop: 12 }}>
          <button className="primary verify-cta" type="submit" disabled={!packageId || verifying}>
            {verifying ? t("verify.verifying") : t("verify.submit")}
          </button>
        </div>
      </form>

      {!passport && !verifying && !error && <Banner tone="info">{t("verify.idle")}</Banner>}
      {verifying && <Loading label={t("verify.recomputing")} />}

      {passport && (
        <>
          <Banner tone={passport.ledger_verified ? "good" : "bad"}>
            {passport.ledger_verified ? `${t("verify.verified")} ` : `${t("verify.failed")} `}
            {passport.ledger_detail}
          </Banner>
          {passport.scan_flagged && (
            <Banner tone="bad">
              {t("verify.flagged")} {passport.scan_flag_reason}
            </Banner>
          )}
          <div className="grid-3 verify-metrics">
            <Metric label={t("verify.beekeeper")} value={passport.beekeeper_name} />
            <Metric label={t("verify.cluster")} value={passport.cluster} />
            <Metric label={t("verify.lab")} value={passport.lab_test_result} />
          </div>
          <h2>{t("verify.harvests")}</h2>
          <p>{passport.harvest_dates.map((item) => new Date(item).toLocaleString()).join(" · ") || "None"}</p>
          <h2>{t("verify.health")}</h2>
          <DataTable
            rows={passport.hive_health_at_harvest}
            columns={[
              { key: "hive_id", label: t("verify.hive") },
              { key: "inside_temperature_c", label: t("verify.temp") },
              { key: "humidity_pct", label: t("verify.humidity") },
              { key: "weight_kg", label: t("verify.weight") },
              { key: "status_label", label: t("verify.status") },
            ]}
          />
          <p className="muted">
            {t("verify.qr")}: {passport.qr_reference}
          </p>
          <img className="qr" alt={`QR for ${passport.package_id}`} src={qrImageUrl(passport.package_id)} />
        </>
      )}
    </div>
  );
}

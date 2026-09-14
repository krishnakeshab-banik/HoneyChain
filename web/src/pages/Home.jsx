import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { apiGet } from "../api";
import CountUp from "../components/CountUp";
import { BeeDoodle, Sprig } from "../components/Decor";
import { HeroHive, HexIcon, IconChain, IconHive, IconLang, IconMarket, IconQr, IconSensor, IconYield } from "../components/Icons";
import { Banner, Loading } from "../components/Ui";

const FEATURES = [
  ["Blockchain Traceability", "Every passing batch is sealed on a hash-chain so a jar can be checked later.", IconChain],
  ["IoT Hive Monitoring", "Weight, heat, and humidity from the colony — used to corroborate harvests.", IconSensor],
  ["AI Disease & Yield Prediction", "Health and honey-yield models trained on inspected MSPB hive-season rows; live weight stays on this hive's scale.", IconYield],
  ["QR Consumer Verification", "Scan a jar. No account. The page recomputes ledger status live.", IconQr],
  ["Market Linkage", "Standing demand and recent verified sale prices, not only a middleman’s word.", IconMarket],
  ["Multilingual Access", "English plus six Indian languages. IDs and hashes stay untranslated.", IconLang],
];

export default function Home() {
  const { t } = useTranslation();
  const [stats, setStats] = useState(null);
  const [impact, setImpact] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([apiGet("/api/public/stats"), apiGet("/api/public/impact")])
      .then(([nextStats, nextImpact]) => {
        setStats(nextStats);
        setImpact(nextImpact);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="landing honeycomb-bg">
      <section className="hero-editorial">
        <div className="hero-copy">
          <p className="page-kicker">{t("home.kicker")}</p>
          <h1>{t("home.title")}</h1>
          <p className="purpose">{t("home.lead")}</p>
          <div className="row" style={{ marginBottom: 8 }}>
            <Link className="primary" to="/verify">
              {t("home.ctaVerify")}
            </Link>
            <Link className="ghost" to="/login?intent=beekeeper">
              {t("home.ctaBeekeeper")}
            </Link>
            <Link className="ghost" to="/login?intent=officer">
              {t("home.ctaOfficer")}
            </Link>
          </div>
        </div>
        <div className="hero-media">
          <img
            className="photo-frame photo-back"
            src="/media/hero-honeycomb.jpg"
            alt=""
            width="480"
            height="360"
            decoding="async"
          />
          <div className="photo-frame photo-front">
            <HeroHive />
          </div>
          <BeeDoodle className="hero-bee" />
        </div>
      </section>

      <section className="card problem-card">
        <p className="page-kicker">THE PROBLEM</p>
        <h2>Counterfeit jars, thin trust, and weak market access</h2>
        <p>
          Buyers cannot tell honest honey from adulterated product. Beekeepers rarely see a fair price. Field officers
          cannot prove a batch’s path from hive to shop.
        </p>
        <p>
          HoneyChain answers each gap: hive sensors corroborate harvests, a hash-chain seals a passing batch, a QR
          lets anyone verify a jar, and a demand board shows real prices.
        </p>
      </section>

      <section className="mission-split">
        <div className="photo-stack">
          <img
            className="photo-frame photo-mission"
            src="/media/mission-beekeeper.jpg"
            alt="A beekeeper tending wooden hives in a rural field"
            width="440"
            height="330"
            loading="lazy"
            decoding="async"
          />
          <Sprig className="mission-sprig" />
        </div>
        <div>
          <p className="page-kicker">{t("home.missionKicker")}</p>
          <h2>{t("home.missionTitle")}</h2>
          <p>{t("home.missionBody")}</p>
        </div>
      </section>

      <p className="page-kicker">CAPABILITIES</p>
      <h2>What HoneyChain does</h2>
      <div className="grid-3 feature-grid">
        {FEATURES.map(([title, body, Icon]) => (
          <div className="card lift-card" key={title}>
            <HexIcon>
              <Icon />
            </HexIcon>
            <strong>{title}</strong>
            <p className="muted">{body}</p>
          </div>
        ))}
      </div>

      <p className="page-kicker">PROCESS</p>
      <h2>{t("home.howTitle")}</h2>
      <div className="grid-4 how-grid">
        {[
          ["step1Title", "step1"],
          ["step2Title", "step2"],
          ["step3Title", "step3"],
          ["step4Title", "step4"],
        ].map(([titleKey, bodyKey], index) => (
          <div className="card how-card lift-card" key={titleKey}>
            <div className="how-num">{index + 1}</div>
            <strong>{t(`home.${titleKey}`)}</strong>
            <p className="muted">{t(`home.${bodyKey}`)}</p>
          </div>
        ))}
      </div>

      <p className="page-kicker">LIVE</p>
      <h2>{t("home.trustTitle")}</h2>
      {loading && <Loading label={t("home.loadingStats")} />}
      {error && (
        <Banner tone="bad">
          {t("home.statsError")} — {error}{" "}
          <button className="ghost" type="button" onClick={() => window.location.reload()}>
            {t("common.retry")}
          </button>
        </Banner>
      )}
      {stats && (
        <div className="grid-3" data-testid="trust-strip">
          <div className="metric hex-stat">
            <div className="label">{t("home.hives")}</div>
            <div className="value">
              <CountUp statKey="hives" value={stats.hives_connected} />
            </div>
          </div>
          <div className="metric hex-stat">
            <div className="label">{t("home.batches")}</div>
            <div className="value">
              <CountUp statKey="batches" value={stats.batches_verified} />
            </div>
          </div>
          <div className="metric hex-stat">
            <div className="label">{t("home.flagged")}</div>
            <div className="value">
              <CountUp statKey="flagged" value={stats.flagged_attempts} />
            </div>
          </div>
        </div>
      )}

      {impact?.points && (
        <>
          <p className="page-kicker">IMPACT</p>
          <h2>{t("home.impactTitle")}</h2>
          <div className="card">
            <table>
              <thead>
                <tr>
                  <th />
                  <th>{t("home.hives")}</th>
                  <th>{t("home.batches")}</th>
                  <th>{t("home.flagged")}</th>
                </tr>
              </thead>
              <tbody>
                {impact.points.map((point) => (
                  <tr key={point.label}>
                    <td>{point.label}</td>
                    <td>{point.hives_connected}</td>
                    <td>{point.batches_verified}</td>
                    <td>{point.flagged_attempts}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      <section className="persona-cta">
        <Link className="card lift-card" to="/register">
          <HexIcon>
            <IconHive />
          </HexIcon>
          <h3>I'm a beekeeper</h3>
          <p className="muted">Create an account, see your own hives, and log a harvest in plain language.</p>
        </Link>
        <Link className="card lift-card" to="/login?intent=officer">
          <HexIcon>
            <IconChain />
          </HexIcon>
          <h3>I'm a KVIC officer</h3>
          <p className="muted">Sign in with the account an admin created for your cluster.</p>
        </Link>
        <Link className="card lift-card" to="/verify">
          <HexIcon>
            <IconQr />
          </HexIcon>
          <h3>I'm checking a jar</h3>
          <p className="muted">No login. Scan the QR or type a package or batch ID.</p>
        </Link>
      </section>
    </div>
  );
}

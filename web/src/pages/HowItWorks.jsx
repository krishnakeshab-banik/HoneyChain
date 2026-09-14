import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Card, SectionHeading } from "../components/Ui";

export default function HowItWorks() {
  const { t } = useTranslation();
  const steps = [
    ["step1Title", "step1", "Sensors stream weight, temperature, and humidity from each colony. Those readings corroborate harvests later."],
    ["step2Title", "step2", "A beekeeper logs a harvest. An officer groups harvests into a batch. A lab inspector records moisture and purity before commit."],
    ["step3Title", "step3", "The weight oracle checks the declared batch against sensor-logged harvests. A passing batch is sealed on the local hash-chain."],
    ["step4Title", "step4", "Each package gets a QR. Anyone can open /verify with no account. The page recomputes ledger status live."],
  ];

  return (
    <div>
      <SectionHeading kicker={t("home.howTitle")} title={t("home.howTitle")} purpose={t("home.lead")} />
      <div className="grid-2">
        {steps.map(([titleKey, bodyKey, extra], index) => (
          <Card key={titleKey} className="how-card">
            <div className="how-num">{index + 1}</div>
            <strong>{t(`home.${titleKey}`)}</strong>
            <p>{t(`home.${bodyKey}`)}</p>
            <p className="muted">{extra}</p>
          </Card>
        ))}
      </div>
      <div className="row" style={{ marginTop: 24 }}>
        <Link className="primary" to="/verify">
          {t("home.ctaVerify")}
        </Link>
      </div>
    </div>
  );
}

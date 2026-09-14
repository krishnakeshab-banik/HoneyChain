import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Card, SectionHeading } from "../components/Ui";

export default function HowItWorks() {
  const { t } = useTranslation();
  const steps = [
    ["step1Title", "step1", "howExtra1"],
    ["step2Title", "step2", "howExtra2"],
    ["step3Title", "step3", "howExtra3"],
    ["step4Title", "step4", "howExtra4"],
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
            <p className="muted">{t(`home.${extra}`)}</p>
          </Card>
        ))}
      </div>
      <div className="row" style={{ marginTop: 24 }}>
        <Link className="primary" to="/verify">
          {t("home.ctaVerify")}
        </Link>
        <Link className="ghost" to="/model">
          {t("home.modelCard")}
        </Link>
      </div>
    </div>
  );
}

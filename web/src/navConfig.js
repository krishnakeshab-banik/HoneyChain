export const ROLE_NAV = {
  consumer: [
    { to: "/", key: "nav.home" },
    { to: "/how-it-works", key: "nav.how" },
    { to: "/model", key: "nav.model" },
    { to: "/verify", key: "nav.verify" },
  ],
  beekeeper: [
    { to: "/app/dashboard", key: "nav.dashboard" },
    { to: "/app/harvests", key: "nav.harvests" },
    { to: "/app/monitor", key: "nav.monitor" },
    { to: "/app/insights", key: "nav.insights" },
    { to: "/app/market", key: "nav.market" },
    { to: "/app/report", key: "nav.report" },
    { to: "/verify", key: "nav.verify" },
  ],
  officer: [
    { to: "/app/cluster", key: "nav.cluster" },
    { to: "/app/batches", key: "nav.batches" },
    { to: "/app/alerts", key: "nav.alerts" },
    { to: "/app/ledger", key: "nav.ledger" },
    { to: "/app/clonewatch", key: "nav.clonewatch" },
    { to: "/app/market", key: "nav.market" },
    { to: "/verify", key: "nav.verify" },
  ],
  lab: [
    { to: "/app/lab", key: "nav.lab" },
    { to: "/verify", key: "nav.verify" },
  ],
  admin: [
    { to: "/app/dashboard", key: "nav.dashboard" },
    { to: "/app/monitor", key: "nav.monitor" },
    { to: "/app/batches", key: "nav.batches" },
    { to: "/app/lab", key: "nav.lab" },
    { to: "/app/ledger", key: "nav.ledger" },
    { to: "/app/clonewatch", key: "nav.clonewatch" },
    { to: "/app/insights", key: "nav.insights" },
    { to: "/app/market", key: "nav.market" },
    { to: "/app/alerts", key: "nav.alerts" },
    { to: "/app/users", key: "nav.users" },
    { to: "/app/model", key: "nav.model" },
    { to: "/app/analytics", key: "nav.analytics" },
    { to: "/verify", key: "nav.verify" },
  ],
};

export const ROLE_HOME = {
  beekeeper: "/app/dashboard",
  officer: "/app/cluster",
  lab: "/app/lab",
  admin: "/app/dashboard",
};

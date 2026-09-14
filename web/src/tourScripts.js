export const TOURS = {
  beekeeper: [
    {
      path: "/app/dashboard",
      target: "[data-tour=dash-welcome]",
      title: "Your hive home",
      body: "This page is only your hives and the next jobs that matter today — not the public marketing site.",
    },
    {
      path: "/app/monitor",
      target: "[data-tour=hive-select]",
      title: "Watch the colony",
      body: "Weight, heat, and humidity update from the live hive feed. Use this before you log a harvest.",
    },
    {
      path: "/app/harvests",
      target: "[data-tour=harvest-form]",
      title: "Log a harvest",
      body: "Write the harvest weight here. HoneyChain checks it against the hive scale so the later batch can be trusted.",
    },
    {
      path: "/app/harvests",
      target: "[data-tour=harvest-status]",
      title: "From harvest to batch",
      body: "Status stays pending until an officer groups the harvest into a batch and the ledger accepts it.",
    },
    {
      path: "/app/insights",
      target: "[data-tour=insights]",
      title: "Colony health and yield",
      body: "These models estimate health and the next weight forecast from your own hive readings.",
    },
    {
      path: "/app/market",
      target: "[data-tour=market-board]",
      title: "See real demand",
      body: "Open listings and recent sale prices — so you are not guessing what buyers will pay.",
    },
  ],
  officer: [
    {
      path: "/app/cluster",
      target: "[data-tour=cluster]",
      title: "Your cluster",
      body: "Every hive and beekeeper in your assigned region. Other regions stay out of this list.",
    },
    {
      path: "/app/batches",
      target: "[data-tour=batch-form]",
      title: "Review a harvest into a batch",
      body: "Link pending harvests, set the declared weight, and create a draft batch for inspection.",
    },
    {
      path: "/app/batches",
      target: "[data-tour=commit]",
      title: "Oracle check",
      body: "Commit runs the weight oracle against sensor-logged harvests before anything is sealed on the chain.",
    },
    {
      path: "/app/ledger",
      target: "[data-tour=ledger]",
      title: "Ledger integrity",
      body: "This page recomputes the hash-chain live. A green result is not a stored tick.",
    },
    {
      path: "/app/clonewatch",
      target: "[data-tour=clonewatch]",
      title: "Flagged batches",
      body: "CloneWatch lists oracle rejections and implausible scans so a cluster officer can follow up.",
    },
  ],
};

export function tourStorageKey(username) {
  return `honeychain_tour_done_${username || "anon"}`;
}

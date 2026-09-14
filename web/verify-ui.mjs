import { chromium } from "playwright";

const BASE = "http://127.0.0.1:5173";
const API = "http://127.0.0.1:8000";
const stamp = Date.now().toString().slice(-6);
const issues = [];

function note(pageName, message) {
  issues.push(`${pageName}: ${message}`);
  console.log(`ISSUE ${pageName}: ${message}`);
}

async function loginAs(page, username, password) {
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle" });
  await page.fill("#username", username);
  await page.fill("#password", password);
  await page.locator("form.card").first().getByRole("button", { name: "Sign in" }).click();
  await page.waitForTimeout(1000);
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  page.on("pageerror", (error) => note("runtime", error.message));

  await page.goto(BASE, { waitUntil: "networkidle" });
  for (const width of [390, 768, 1280]) {
    await page.setViewportSize({ width, height: 800 });
    await page.waitForTimeout(200);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 12);
    if (overflow) {
      note("Responsive", `Home overflows horizontally at ${width}px`);
    }
  }
  await page.setViewportSize({ width: 1280, height: 800 });
  const homeTitle = await page.locator("h1").innerText();
  if (!/hive signals|trusted honey/i.test(homeTitle)) {
    note("Home", `Unexpected heading: ${homeTitle}`);
  }
  await page.waitForSelector("[data-testid=trust-strip] .metric .value [data-final]");
  await page.waitForFunction(() => {
    const el = document.querySelector("[data-testid=trust-strip] .metric .value [data-final]");
    return el && el.textContent === el.getAttribute("data-final");
  });
  const uiHives = Number(await page.locator("[data-testid=trust-strip] .metric .value [data-final]").nth(0).getAttribute("data-final"));
  const stats = await (await page.request.get(`${API}/api/public/stats`)).json();
  if (Number.isNaN(uiHives) || uiHives !== stats.hives_connected) {
    note("Home", `Trust hives UI ${uiHives} != API ${stats.hives_connected}`);
  }
  if (!(await page.getByRole("link", { name: "Verify your honey" }).count())) {
    note("Home", "Verify CTA missing");
  }

  await page.getByRole("link", { name: "How it works" }).first().click();
  await page.waitForTimeout(400);
  if (!page.url().includes("/how-it-works")) {
    note("How it works", `Did not navigate: ${page.url()}`);
  }

  await page.getByRole("link", { name: "Verify your honey" }).first().click();
  await page.waitForTimeout(600);
  if (!(await page.getByText("Consumer honey passport").count())) {
    note("Consumer Verify", "Public verify page did not open without login");
  }

  await loginAs(page, "admin", "Admin123!");
  if (!page.url().includes("/app/")) {
    note("Login", `Admin did not land on a dashboard: ${page.url()}`);
  }
  if (!(await page.locator("[data-testid=voice-fab]").count())) {
    note("Voice", "Ask HoneyChain button missing after login");
  } else {
    await page.locator("[data-testid=voice-fab]").click();
    await page.waitForTimeout(300);
    if (!(await page.locator("[data-testid=voice-panel]").count())) {
      note("Voice", "Voice panel did not open");
    } else {
      await page.fill("#voice-q", "How many hives can I see?");
      await page.locator("[data-testid=voice-panel]").getByRole("button", { name: "Ask" }).click();
      await page.waitForTimeout(1200);
      const panel = await page.locator("[data-testid=voice-panel]").innerText();
      if (!/HoneyChain|live record|IN-WB|hive/i.test(panel)) {
        note("Voice", `Assistant reply missing live context: ${panel.slice(0, 180)}`);
      }
    }
  }

  await page.getByRole("link", { name: "Dashboard" }).click();
  await page.waitForTimeout(1500);
  if (!(await page.getByText("Inside temperature").count())) {
    note("Overview", "Temperature metric missing after load");
  }
  await page.fill("#hive_id", `IN-UI-${stamp}`);
  await page.fill("#name", `Walkthrough hive ${stamp}`);
  await page.getByRole("button", { name: "Register hive" }).click();
  await page.waitForTimeout(800);
  const hiveOptions = await page.locator("#hive option").allTextContents();
  if (!hiveOptions.some((item) => item.includes(`IN-UI-${stamp}`))) {
    const registerError = await page.locator(".banner.bad").innerText().catch(() => "");
    note("Overview", `Registered hive did not appear. ${registerError}`);
  }

  await page.getByRole("link", { name: "Hive Monitor" }).click();
  await page.waitForTimeout(1200);
  if (!(await page.getByRole("heading", { name: "Hive Monitor" }).count())) {
    note("Hive Monitor", "Title missing");
  }
  await page.getByRole("button", { name: "Send invalid humidity reading" }).click();
  await page.waitForTimeout(800);
  const probe = await page.locator(".banner.warn, .banner.bad").last().innerText();
  if (!/humidity|less than or equal|422|le=100/i.test(probe)) {
    note("Hive Monitor", `Invalid reading did not surface a validation reason: ${probe}`);
  }

  await page.getByRole("link", { name: "Batch Review" }).click();
  await page.waitForTimeout(800);
  await page.fill("#harvest_id", `HV-UI-${stamp}`);
  await page.fill("#raw_weight", "6.2");
  await page.getByRole("button", { name: "Create harvest" }).click();
  await page.waitForTimeout(1000);
  const harvestNotice = await page.locator("[data-testid=page-notice], [data-testid=page-error]").first().innerText();
  if (!/HV-UI-|Couldn't|sensor/i.test(harvestNotice)) {
    note("Traceability", `Harvest action produced unclear feedback: ${harvestNotice}`);
  }
  const harvestBox = page.locator(`[data-testid=harvest-link-HV-UI-${stamp}] input`);
  if (await harvestBox.count()) {
    await harvestBox.check();
  } else {
    note("Traceability", `Harvest checkbox missing for HV-UI-${stamp}`);
  }
  await page.fill("#batch_id", `BT-UI-${stamp}`);
  await page.fill("#declared", "6.2");
  await page.getByRole("button", { name: "Create draft batch" }).click();
  await page.waitForTimeout(800);
  await page.selectOption("#commit", `BT-UI-${stamp}`).catch(() => {});
  await page.getByRole("button", { name: "Run oracle and commit" }).click();
  await page.waitForTimeout(1000);
  await page.fill("#package_id", `PK-UI-${stamp}`);
  await page.selectOption("#pkg_batch", `BT-UI-${stamp}`).catch(() => {});
  await page.getByRole("button", { name: "Generate package + QR" }).click();
  await page.waitForTimeout(1000);

  await page.getByRole("link", { name: "Consumer Verify" }).click();
  await page.waitForTimeout(600);
  await page.fill("#verify_id", "PK-DOES-NOT-EXIST");
  await page.getByRole("button", { name: "Verify package" }).click();
  await page.waitForTimeout(800);
  const missing = await page.locator("[data-testid=page-error], .banner.bad").first().innerText();
  if (!/does not exist|Couldn't verify/i.test(missing)) {
    note("Consumer Verify", `Missing package error unclear: ${missing}`);
  }
  await page.fill("#verify_id", `PK-UI-${stamp}`);
  await page.getByRole("button", { name: "Verify package" }).click();
  await page.waitForTimeout(1000);
  if (!(await page.getByText("Chain verified").count()) && !(await page.getByText("Chain check failed").count())) {
    note("Consumer Verify", "No live ledger status after verify");
  }

  await page.getByRole("link", { name: "CloneWatch" }).click();
  await page.waitForTimeout(800);
  const flags = await page.locator("body").innerText();
  if (!/anomalous_scan|oracle_rejection|Nothing flagged|PK-UI|km/i.test(flags)) {
    note("CloneWatch", "Expected flag list or empty-state hint missing");
  }

  await page.getByRole("link", { name: "Insights" }).click();
  await page.waitForTimeout(1200);
  if (!(await page.getByText("Colony status").count()) && !(await page.getByText("Couldn't load insights").count())) {
    note("Insights", "Neither model output nor error shown");
  }

  await page.getByRole("link", { name: "Market Linkage" }).click();
  await page.waitForTimeout(800);
  if (!(await page.getByText("Demand board").count())) {
    note("Market", "Demand board heading missing");
  }

  await page.getByRole("link", { name: "Lab desk" }).click();
  await page.waitForTimeout(600);
  if (!(await page.getByText("Moisture and purity").count())) {
    note("Lab", "Lab desk title missing");
  }

  await page.getByRole("link", { name: "Ledger Integrity" }).click();
  await page.waitForTimeout(600);
  if (!(await page.getByText("hash-chain").count()) && !(await page.getByText("Ledger").count())) {
    note("Ledger", "Ledger page missing");
  }

  await page.getByRole("link", { name: "User management" }).click();
  await page.waitForTimeout(600);
  if (!(await page.getByText("Create and deactivate").count())) {
    note("Users", "User management page missing");
  }

  await page.goto(`${BASE}/app/lab`, { waitUntil: "networkidle" });
  await page.waitForTimeout(400);

  await page.goto(`${BASE}/?package_id=PK-NOPE-FRESH`, { waitUntil: "networkidle" });
  await page.waitForTimeout(1000);
  const fresh = await page.locator("body").innerText();
  if (!/Consumer honey passport|Couldn't verify|does not exist/i.test(fresh)) {
    note("Consumer Verify", "Fresh QR URL did not open verify page with a clear error");
  }

  await loginAs(page, "beekeeper", "Beekeeper123!");
  if (await page.getByRole("link", { name: "CloneWatch" }).count()) {
    note("Roles", "Beekeeper can see CloneWatch in the nav");
  }
  if (await page.getByRole("link", { name: "Lab desk" }).count()) {
    note("Roles", "Beekeeper can see Lab desk in the nav");
  }
  await page.goto(`${BASE}/app/clonewatch`, { waitUntil: "networkidle" });
  await page.waitForTimeout(400);
  if (!(await page.getByText("don't have access").count()) && !page.url().includes("/403")) {
    note("Roles", "Beekeeper was not blocked from admin CloneWatch");
  }

  await page.goto(`${BASE}/this-page-does-not-exist`, { waitUntil: "networkidle" });
  if (!(await page.getByText("not on HoneyChain").count())) {
    note("404", "Missing 404 page");
  }

  await browser.close();
  if (issues.length) {
    console.log(`\nFOUND ${issues.length} ISSUES`);
    process.exit(1);
  }
  console.log("\nCLEAN PASS");
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});

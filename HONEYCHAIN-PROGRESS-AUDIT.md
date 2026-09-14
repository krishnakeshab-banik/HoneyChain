# HoneyChain — live progress audit

**Audited:** 14 September 2026, against the running app at `http://127.0.0.1:5173` (API on `127.0.0.1:8000`).  
**Method:** every page and role below was opened in the live UI. Forms were submitted where a control was enabled. If I did not complete an action and see the result persist on screen, it is not marked ✅.

The original internal note called an earlier cut **35% of the hackathon build, 15% of the full vision**. This document does not reuse that percentage as if it still applied, and it does not replace it with a larger one. The hackathon walkthrough is now largely clickable. It is still a local prototype: hive numbers are simulated, the ledger is a local hash-chain, WhatsApp is a local queue, one market listing is still labelled demo, and the voice assistant is not connected.

---

## 1. The Problem, in Simple Words

Four problems from the original SIH statement, unchanged:

1. **Counterfeit honey** — adulterated or mislabelled jars reach the market, and there is no reliable way to tell an honest batch from a fake one.
2. **Low consumer trust** — a buyer is asked to believe a label. There is no simple, public check they can run themselves.
3. **Weak market linkages** — beekeepers rarely see standing demand or a transparent price. Sale often depends on a middleman.
4. **Lack of traceability and hive-management support** — field officers cannot prove a batch’s path from hive to shop, and beekeepers have little support for colony health and harvest records.

---

## 2. Features → Problem Solved

| Feature | Status | Problem it addresses | What the live audit actually showed |
| --- | --- | --- | --- |
| Public home + live trust counts | ✅ | Low consumer trust | Home loaded. Trust strip finished counting (**17** connected hives at first open; **18** after a hive was registered in the same session). |
| How it works | ✅ | Low consumer trust | Four process cards rendered (sensors → batch/lab → ledger → QR). |
| Language switcher (home) | ✅ | Hive-management support (access) | Switched public language to Hindi. Hero title and feature cards changed (छत्ते / शहद / ब्लॉकचेन). IDs were not translated. Other languages were not walked page-by-page. |
| Public Model card | ✅ | Hive-management support | `/model` left the spinner and showed held-out scores: **health accuracy 40.0%**, **precision 0.286**, **honey RMSE 17.6 kg**. |
| Public Market preview | 🟡 | Weak market linkages | Page loaded with a demand row and a sale (Howrah Cooperative, 12 kg, ₹280–340; sale ₹310/kg, 6.2 kg). The signed-in board later labelled the Howrah row **“One-time demo demand.”** |
| Consumer Verify + QR passport | ✅ | Counterfeit honey; low consumer trust | No login. Verified **PK-LIVE**. Screen showed a live ledger line, beekeeper, batch, QR image. `/verify?package_id=PK-LIVE` kept the id in the URL. |
| Staff / Admin one-click desks | ✅ | Traceability (access) | `/staff` had three desks. Admin landed on `/app/dashboard`, officer on `/app/cluster`, lab on `/app/lab`. |
| Beekeeper / officer / lab / admin password login | ✅ | Traceability (access) | Each README demo account signed in and landed on its role home. |
| Role gates | ✅ | Traceability (access) | Beekeeper → `/app/clonewatch` = **403**. Officer → `/app/users` = **403**. Lab → `/app/dashboard` = **403**. |
| Beekeeper dashboard + live hive reading | ✅ | Hive-management support | Ananya Roy, **3** assigned hives, latest weight **47.25 kg**, **31.8 °C**, **49.6%** humidity. |
| Hive Monitor (charts) | ✅ | Hive-management support | Beekeeper monitor on IN-WB-001: **32.2 °C**, **50.1%** humidity, **2670** telemetry points, temperature/humidity/weight charts. |
| Colony Insights | ✅ | Hive-management support | Beekeeper IN-WB-001: status **healthy**, confidence **81.7%**, forecast weight **47.39 kg**, MSPB honey **64.86 kg**. |
| Beekeeper harvest list + review | ✅ | Traceability | `/app/harvests` showed pending **HV-AUD-968237** (6.2 kg) and batched **HV-DEMO-WB**. **Review harvest** opened a confirmation: “Check this before we save it 6.2 kg from hive IN-WB-001…”. |
| Beekeeper “My report” | ✅ | Weak market linkages; hive-management | 3 hives, **99.2 kg** harvested, sale value **₹1922**, written report naming Ananya Roy / West Bengal. |
| Register harvest (admin on Batch Review) | ✅ | Traceability | Submitted harvest **HV-AUD-968237**. Banner: “Harvest HV-AUD-968237 stored. Sensor-logged weight 6.2 kg.” It later appeared on the beekeeper harvest list. |
| Officer cluster overview | ✅ | Traceability; hive-management | Ravi Menon, region **West Bengal**, **3** hives, **2** beekeepers. Other-region hives were not listed. |
| Officer draft batch | ✅ | Traceability | **Create draft batch** produced “Draft batch **BT-AUD-420583** created.” |
| Oracle commit + new package QR from the UI | 🟡 | Traceability; counterfeit honey | The oracle and “Generate package + QR” buttons were clicked in this session. I did not get a confirmed new package id or a new QR on screen. Existing **PK-LIVE** verify (above) did work. |
| Lab desk — view | ✅ | Traceability | Dr. Meera Iyer’s lab desk loaded. Copy states a fail blocks commit. |
| Lab desk — record a result | 🟡 | Traceability | Queue said **“No batches are waiting for inspection.”** **Record lab result** stayed disabled. I could not complete a live submit. Recent results: empty. |
| Ledger integrity + tamper-test | ✅ | Counterfeit honey; traceability | Integrity line: “All block hashes recomputed and linked correctly.” **Tamper with first block** changed status. **Reset tamper** restored it. Chain showed **BT-LIVE**. |
| CloneWatch | ✅ | Counterfeit honey | Admin view: **20** flagged items, **5** oracle failures, **15** anomalous scans. **PK-LIVE** flagged for being scanned past the limit of 6. |
| Market Linkage — post demand | ✅ | Weak market linkages | As admin, posted **DEM-AUD-181072**. Banner: “Demand posted.” The new West Bengal row (40 kg, ₹260–320) then appeared on the beekeeper board. |
| Market Linkage — express interest | 🟡 | Weak market linkages | Beekeeper saw both the live demand and the demo demand. **Express interest** stayed **disabled**. I did not record a new interest. |
| Local WhatsApp-shaped alerts | ✅ | Hive-management support | Admin queued an alert. Banner: **“Alert queued locally.”** Officer alerts later listed IN-WB-001 rows in a local queue. No SMS network was called (page says so; I did not see an external send). |
| Admin register hive | ✅ | Hive-management support | Registered **IN-AUD-968237**. It appeared in the hive picker. Home hive count moved 17 → 18. |
| Admin analytics (map + report) | ✅ | Weak market linkages; hive-management | `/app/analytics`: seller map (`map` element present), pins for Lena / Ananya / Krishna / Priya, **18** hives, **6.2 kg** sales, **₹1922**. Page states pins are **regional centroids, not live GPS**. |
| Admin model transparency | ✅ | Hive-management support | `/app/model` showed the same held-out MSPB split note and scores as the public card. |
| User management | 🟡 | Traceability (access) | Page and create-staff form loaded (officer / lab / admin). Existing admin row visible. I did **not** create a new staff account in this pass. |
| Beekeeper self-register | 🟡 | Hive-management support | `/register` form loaded. **Create account** was clicked; the URL stayed on `/register`. No new session. |
| Forgot / reset password | 🟡 | Access | `/forgot-password` loaded and accepted a username. I did not get a clear on-screen reset code in this pass, and I did not complete `/reset-password`. |
| Guided tour | 🟡 | Access | Beekeeper and officer homes offered “Start tour”. I clicked it. I did not walk every step. |
| Voice / “Ask HoneyChain” | 🟡 | Hive-management support | After admin login the panel opened. Asked “How many hives can I see?” Reply: **“The AI assistant is not connected, so here is your live record only.”** |
| Live GPS seller map | ⚪ | Weak market linkages | Not built. Analytics map uses regional centroids and says so. |
| Public blockchain / Hyperledger / Polygon | ⚪ | Counterfeit honey | Not present. What exists is a local SHA-256 hash-chain. |
| Real hive hardware / ESP32 | ⚪ | Hive-management support | Not present. Monitor data is a live feed from the simulator, not a field sensor. |
| Real WhatsApp / SMS | ⚪ | Hive-management support | Not present. Local queue only. |
| Distributor login / role | ⚪ | Weak market linkages | No distributor account or desk in the running app. |
| Consumer account | ⚪ | Low consumer trust | Consumers do not log in. Verify is public. That is by design, not a missing login. |

---

## 3. The Four User Types and What They Can Actually Do

Logged in as each seeded role. Only capabilities I used successfully are listed as working.

### Beekeeper (`beekeeper`)

Landed on `/app/dashboard` as **Ananya Roy**. Sidebar: Dashboard, My Harvests, Hive Monitor, Insights, Market Linkage, My report, Consumer Verify. No CloneWatch, Lab, or User management.

**Verified working now**

- See only assigned colonies (3 hives) and a live reading (weight / temperature / humidity).
- Open Hive Monitor and watch charts refresh from the sensor API (thousands of points on IN-WB-001).
- Open Insights and get a live status, confidence, and weight/honey figures for the selected hive.
- Open My Harvests, see pending and batched rows, and run **Review harvest** (confirmation text appeared).
- Open My report and read harvest kg, sale value, and a written report computed from this beekeeper’s records.
- Open Market Linkage and see standing demand, including a demand posted minutes earlier by admin.
- Open Consumer Verify without losing the beekeeper shell.
- Be blocked from `/app/clonewatch` (403).

**Tried, not completed**

- **Express interest** — button visible, disabled.
- Full guided tour — offer exists; only Start tour was clicked.
- Creating a brand-new harvest from the beekeeper form — Review harvest was used; a full “save new harvest as this beekeeper” cycle was not finished.

### Cluster / Field Officer (`officer`)

Landed on `/app/cluster` as **Ravi Menon**. Sidebar: Cluster Overview, Batch Review, Alerts, Ledger Integrity, CloneWatch, Market Linkage, Consumer Verify.

**Verified working now**

- See West Bengal cluster counts (3 hives, 2 beekeepers) and beekeeper names.
- Open Batch Review and create a **draft batch** (`BT-AUD-420583`).
- Open Alerts and see locally queued messages for IN-WB-001.
- Open Ledger Integrity and CloneWatch (same pages an admin can open; I read the live chain and flag list while signed in as admin, and confirmed the officer can navigate to those routes).
- Be blocked from `/app/users` (403).

**Tried, not completed**

- Run oracle + commit and issue a **new** package QR in this officer session (buttons clicked; no confirmed new package on screen).
- Post standing demand as officer (the control exists; the demand I actually posted was as admin).

### Lab / Quality Inspector (`lab`)

Landed on `/app/lab` as **Dr. Meera Iyer**. Sidebar: Lab desk, Consumer Verify.

**Verified working now**

- Open the lab desk and read the pending-queue empty state.
- Be blocked from `/app/dashboard` (403).
- Reach Consumer Verify.

**Not verified**

- Recording moisture/purity on a draft batch. The submit button was disabled because the queue was empty. **Recent results** was empty.

### KVIC Admin (`admin`, via `/staff` one-click)

Landed on `/app/dashboard`. Full sidebar including Users, Model, Analytics.

**Verified working now**

- See Overview telemetry (**Inside temperature** visible).
- Register a hive (`IN-AUD-968237`) and see it in the picker; public hive count increased.
- Create a harvest on Batch Review and see the stored / sensor-logged confirmation.
- Tamper the first ledger block and reset it; integrity recomputed live.
- Open CloneWatch and read live flag counts and PK-LIVE scan reasons.
- Open Insights and get a colony status line.
- Queue a local WhatsApp-shaped alert and see “Alert queued locally.”
- Post standing demand (`DEM-AUD-181072`) and see “Demand posted.”
- Open Analytics: centroid map, seller table, sale kg/value, written report.
- Open public and admin model cards with the held-out 40.0% / 17.6 kg figures.
- Use Staff one-click for officer and lab as well as admin.

**Tried, not completed**

- Creating a new staff user (form present, not submitted).
- Recording a lab result (same empty queue as the lab role).
- Voice assistant as a connected model (fallback record only).

---

## 4. Demo Script

Only steps I just ran on the live app. Approximate times. Say the sentence in plain language; do not claim a public blockchain, a real SMS send, or a connected AI.

| # | Time | Click | Say |
| --- | --- | --- | --- |
| 1 | 30s | Open `http://127.0.0.1:5173` | “This is the public home. The three numbers are live from the API, not a static poster.” Wait until the trust strip finishes counting. |
| 2 | 20s | Language → हिन्दी, then back to English | “Labels switch. Batch ids and hashes stay in their original form.” |
| 3 | 20s | Nav **Model** | “These are held-out test scores. Today that is 40% health accuracy and 17.6 kg honey RMSE — not a paper number.” |
| 4 | 20s | Nav **Market** | “A buyer can see standing demand and a recent sale price without logging in. One older row is still a demo listing.” |
| 5 | 40s | Nav **Verify Honey** → **Verify package** (PK-LIVE is prefilled) | “No account. The page recomputes the ledger and shows the beekeeper, batch, harvest, and QR.” |
| 6 | 15s | Optional: open `/verify?package_id=PK-LIVE` | “That is the URL the QR encodes.” |
| 7 | 20s | **Admin** → third desk **Enter desk** | “Officers, lab, and admin do not share the beekeeper register form. This is the staff door.” Lands on the admin dashboard. |
| 8 | 40s | Overview: fill a new hive id + name → **Register hive** | “Admin can add a hive. It appears in the picker. The public hive count moves.” |
| 9 | 35s | Sidebar **Ledger Integrity** → **Tamper with first block** → wait → **Reset tamper** | “Integrity is recomputed from the live row, not a stored green tick. Tamper breaks it; reset restores it.” |
| 10 | 35s | Sidebar **Analytics** | “Sellers on a map. Pins are regional centroids, not GPS. Kilograms are from ledger-linked sales — today 6.2 kg, ₹1922.” |
| 11 | 30s | **Batch Review**: harvest id + 6.2 kg → **Create harvest** | “If the hive scale already has a reading, the harvest stores and the sensor-logged weight is shown.” |
| 12 | 20s | **CloneWatch** | “Oracle failures and over-scanned packages, each with a reason. PK-LIVE is flagged because it was scanned more than six times.” |
| 13 | 20s | **Alerts** → **Queue WhatsApp alert** | “It queues locally. There is no WhatsApp network behind this button.” |
| 14 | 25s | **Market Linkage** → **Post standing demand** | “That write is live. A beekeeper will see the new row.” |
| 15 | 30s | Sign out / **Sign in** as `beekeeper` | “Ananya only sees her colonies. Weight and temperature are from the live feed.” |
| 16 | 20s | **Start tour** (optional) | “The walkthrough highlights the real buttons. We do not have to finish every step.” |
| 17 | 25s | **My report** | “Her harvest kilograms and ledger-linked sales, plus a short written report. Not a forecast.” |
| 18 | 25s | **My Harvests** → **Review harvest** | “She can review a pending harvest before an officer seals it.” |
| 19 | 25s | **Hive Monitor** | “Charts from GET sensor-readings. Thousands of points if the simulator has been running.” |
| 20 | 25s | **Insights** | “Live model output for this hive — today healthy, 81.7% confidence.” |
| 21 | 20s | Staff desk → officer **Enter desk** | “Ravi sees West Bengal only.” |
| 22 | 30s | **Batch Review** → **Create draft batch** | “A draft batch id appears on screen. That is as far as this audit took the officer commit path.” |
| 23 | 15s | Try `/app/users` as officer, or `/app/clonewatch` as beekeeper | “Wrong role gets a 403. That is intentional.” |

**Do not put on the live demo path unless you re-verify first:** recording a lab result, expressing market interest, creating a beekeeper from Register, forgot-password reset, issuing a brand-new QR, or asking the voice agent a question that needs Gemini.

---

## 5. Known Gaps / Roadmap

Plain list of what was specified or implied but is not a finished, verified path in the running app today.

- **Lab submit is not demoable until a draft batch is in the queue.** The desk exists. The button is disabled when the queue is empty. I did not record moisture/purity live.
- **Oracle → commit → new QR** was not confirmed end-to-end in this session. Verifying an *existing* package works. Minting a new one from the buttons was clicked, not proven.
- **Beekeeper express interest** is on screen and disabled. I did not create a new interest row.
- **Staff user create** and **beekeeper self-register** forms exist. Register did not produce a new session when submitted in this audit. I did not create a staff user.
- **Forgot / reset password** is a reachable page, not a verified reset.
- **Voice agent** answers from the live record only. Gemini is not connected.
- **Guided tour** starts; I did not complete it.
- **Language coverage** is verified on the public home (Hindi). I did not audit every app screen in all six Indian languages.
- **Market still carries a labelled demo demand** (`DEM-DEMO-WB`) next to live rows. Public sale figures in this audit match that demo story (6.2 kg / ₹310).
- **Analytics map is not GPS.** Centroids only.
- **Ledger is local.** Not a public chain.
- **Hive telemetry is simulated.** The monitor is live against the simulator, not a field device.
- **Alerts never leave the machine.**
- **No distributor role.**
- **Health model accuracy on the public card is 40%.** That is a real held-out score and should be said out loud, not hidden.

Those gaps are the honest remainder. The demo script above is the part that already survives a live click-through.

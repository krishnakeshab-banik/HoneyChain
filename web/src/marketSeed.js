export function isSeedDemand(row) {
  const id = String(row?.demand_id || "");
  const notes = String(row?.notes || "");
  return id.startsWith("DEM-DEMO") || /one-time demo/i.test(notes);
}

export function isSeedSale(row) {
  return String(row?.sale_id || "").startsWith("SALE-DEMO");
}

export function splitSeed(rows, predicate) {
  const live = [];
  const seed = [];
  for (const row of rows || []) {
    (predicate(row) ? seed : live).push(row);
  }
  return { live, seed };
}

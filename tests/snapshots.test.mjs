// Data checks for snapshots.js (the dashboard's only data file).
// Run: node --test tests/*.test.mjs   (no dependencies)
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const src = readFileSync(new URL("../snapshots.js", import.meta.url), "utf8");
const ctx = { window: {} };
vm.runInNewContext(src, ctx);
const SNAPS = ctx.window.SNAPS_DATA;
const DAY = /^\d{4}-\d{2}-\d{2}$/;
const validDay = s => DAY.test(s) && !Number.isNaN(Date.parse(s + "T00:00:00Z"));

test("snapshots.js defines a non-empty window.SNAPS_DATA array", () => {
  assert.ok(Array.isArray(SNAPS));
  assert.ok(SNAPS.length > 0);
});

test("snapshot ids are unique and dates are valid", () => {
  const ids = SNAPS.map(s => s.id);
  assert.equal(new Set(ids).size, ids.length, "duplicate snapshot id");
  for (const s of SNAPS) {
    assert.ok(validDay(s.searched_at), `${s.id}: searched_at ${s.searched_at}`);
    assert.ok(validDay(s.window.from) && validDay(s.window.to), `${s.id}: window`);
    assert.ok(s.window.from <= s.window.to, `${s.id}: window from > to`);
    if (s.cabin) assert.ok(["economy", "business"].includes(s.cabin), `${s.id}: cabin ${s.cabin}`);
  }
});

test("each route has an IATA code and no duplicate code within a snapshot", () => {
  for (const s of SNAPS) {
    const codes = s.routes.map(r => r.code);
    for (const c of codes) assert.match(c, /^[A-Z]{3}$/, `${s.id}: code ${c}`);
    assert.equal(new Set(codes).size, codes.length, `${s.id}: duplicate route code`);
    for (const r of s.routes) assert.ok(r.city && r.region, `${s.id}/${r.code}: city/region`);
  }
});

test("monthly cheapest prices are positive THB and dates fall in their month", () => {
  for (const s of SNAPS)
    for (const r of s.routes)
      for (const [month, v] of Object.entries(r.monthly_cheapest || {})) {
        if (!v) continue;
        const where = `${s.id}/${r.code}/${month}`;
        assert.match(month, /^\d{4}-\d{2}$/, where);
        assert.ok(Number.isFinite(v.price) && v.price > 0, `${where}: price ${v.price}`);
        assert.ok(v.price < 500_000, `${where}: price looks wrong ${v.price}`);
        if (v.dep) {
          assert.ok(validDay(v.dep), `${where}: dep ${v.dep}`);
          assert.equal(v.dep.slice(0, 7), month, `${where}: dep outside month`);
        }
        if (v.dep && v.ret) assert.ok(v.dep <= v.ret, `${where}: dep after ret`);
      }
});

test("trips have valid dates, a price, and a Google Flights link", () => {
  for (const s of SNAPS)
    for (const t of s.trips || []) {
      const where = `${s.id}/${t.code}/${t.dep}`;
      assert.ok(validDay(t.dep) && validDay(t.ret), `${where}: dates`);
      assert.ok(t.dep <= t.ret, `${where}: dep after ret`);
      assert.ok(Number.isFinite(t.price) && t.price > 0, `${where}: price`);
      if (t.url) assert.match(t.url, /^https:\/\/www\.google\.com\/travel\/flights/, `${where}: url`);
    }
});

test("every page that loads data points at snapshots.js", () => {
  const html = readFileSync(new URL("../index.html", import.meta.url), "utf8");
  assert.match(html, /snapshots\.js/);
});

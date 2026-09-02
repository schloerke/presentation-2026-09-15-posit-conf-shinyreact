// `node check.mjs` — the one check behind www/data.js. The expected counts are
// R's, from:
//   x <- faithful$waiting
//   hist(x, breaks = seq(min(x), max(x), length.out = b + 1), plot = FALSE)$counts
import { readFileSync } from "node:fs";
import { createContext, runInContext } from "node:vm";
import assert from "node:assert";

const ctx = {};
createContext(ctx);
runInContext(
  readFileSync(new URL("www/data.js", import.meta.url), "utf8") +
    ";this.m = { waiting, bin_data };",
  ctx,
);
const { waiting, bin_data } = ctx.m;

const expected = {
  1: "272",
  7: "26 44 27 23 68 69 15",
  30: "1 8 7 10 6 12 15 7 4 13 4 7 3 3 3 9 8 6 17 27 18 13 26 16 8 6 9 2 3 1",
};

assert.equal(waiting.length, 272);
for (const [bins, counts] of Object.entries(expected)) {
  const got = bin_data(waiting, Number(bins));
  assert.equal(got.breaks.length, Number(bins) + 1);
  assert.equal(got.counts.join(" "), counts, `bins = ${bins}`);
}
console.log("ok");

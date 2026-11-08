// Known-answer parity gate, run by "npm run build" before vite.
// The browser port in engine.js must reproduce the committed Python results exactly:
// every Learn and Build extraction, every table row, all 16 QA answers, the Deep
// band table, ECE, Brier, Wilson intervals, the threshold sweep, and the stress set.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  FIELDS, learnExtract, buildRecord, answerQuestion, deepEqual, bandTable, ece, brier,
  queueAtThreshold, wilson, PERTURB, scoreFields, scoreTables,
} from './engine.js';

const load = (p) => JSON.parse(readFileSync(new URL(`../../${p}`, import.meta.url), 'utf8'));
const docs = load('results/documents_export.json');
const learn = load('results/results_learn.json');
const build = load('results/results_build.json');
const deep = load('results/results_deep.json');
const stress = load('results/results_stress.json');

// Learn: 8 documents x 5 fields, extracted value and confidence.
assert.equal(docs.learn.length, learn.per_document.length);
docs.learn.forEach((d, j) => {
  const want = learn.per_document[j];
  assert.equal(d.id, want.doc_id);
  for (const f of FIELDS) {
    const got = learnExtract(f, d.text);
    assert.equal(got.value, want.fields[f].extracted, `learn ${d.id} ${f}`);
    assert.equal(got.confidence, want.fields[f].confidence, `learn ${d.id} ${f} confidence`);
  }
});

// Build: 32 records (fields, confidences, line items).
const records = docs.build.map((d) => buildRecord(d));
assert.equal(records.length, build.records.length);
records.forEach((r, j) => {
  const { rules, ...rec } = r;
  assert.ok(deepEqual(rec, build.records[j]), `build record ${r.doc_id}`);
});
const fs = scoreFields(docs.build, records), ts = scoreTables(docs.build, records);
assert.equal(fs.correct, build.field_summary.total_correct);
assert.deepEqual(fs.per.map((p) => p.correct), build.per_field.map((p) => p.correct));
assert.equal(ts.rowsCorrect, build.table.rows_correct);
assert.equal(ts.cellsCorrect, build.table.cells_correct);

// QA: answers and cited ids, and the correct flag against gold.
let qaCorrect = 0;
for (const pq of build.per_question) {
  const got = answerQuestion(records, pq);
  assert.ok(deepEqual(got, pq.answer), `qa ${pq.id}`);
  const ok = deepEqual(got.value, pq.gold.value) && deepEqual(got.doc_ids, pq.gold.doc_ids);
  assert.equal(ok, pq.correct, `qa ${pq.id} correct flag`);
  qaCorrect += ok;
}
assert.equal(qaCorrect, build.qa_summary.correct);

// Deep: bands, ECE, Brier, intervals, sweep over the 160 recorded items.
const items = deep.items;
const bands = bandTable(items);
assert.ok(deepEqual(bands, deep.bands), 'band table');
assert.equal(ece(items, bands), deep.ece);
assert.equal(brier(items), deep.brier);
for (const s of deep.threshold_sweep) assert.ok(deepEqual(queueAtThreshold(items, s.threshold), s), `sweep ${s.threshold}`);
for (const f of deep.per_field) assert.deepEqual(wilson(f.correct, f.count), f.wilson95, `wilson ${f.field}`);
assert.deepEqual(wilson(2, 2), [0.3424, 1.0]);
assert.deepEqual(wilson(deep.total_correct, deep.total_fields), deep.overall_wilson95, 'wilson overall');

// Stress: each perturbation re-run through the browser pipeline.
for (const p of stress.perturbations) {
  const pd = docs.build.map((d) => ({ ...d, text: PERTURB[p.name](d.text) }));
  const pr = pd.map((d) => buildRecord(d));
  const sf = scoreFields(pd, pr), st = scoreTables(pd, pr);
  assert.equal(sf.correct, p.total_correct, `stress ${p.name} fields`);
  assert.deepEqual(sf.per.map((x) => x.correct), p.per_field.map((x) => x.correct), `stress ${p.name} per field`);
  assert.equal(st.rowsCorrect, p.rows_correct, `stress ${p.name} rows`);
}

console.log('parity ok', { learn: docs.learn.length, build: records.length, qa: `${qaCorrect}/${build.per_question.length}`, ece: deep.ece, brier: deep.brier, stress: stress.perturbations.length });

// Browser port of the repo's extraction, QA and calibration code.
// src/extractor.py (EXTRACTORS), src/pipeline.py (BUILD_FIRST,
// extract_table), src/qa.py (answer_question), src/eval_build.py
// (field and table scoring), src/calibration.py and src/stress.py.
// parity.check.mjs runs this file over every document and fails the build on any
// difference from the committed results_*.json files.

export const FIELDS = ['invoice_number', 'date', 'vendor', 'total', 'due_date'];

// Python str.splitlines() boundaries.
export const splitlines = (text) => {
  const parts = text.split(/\r\n|[\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029]/);
  if (parts.length && parts[parts.length - 1] === '') parts.pop();
  return parts;
};
const pyStrip = (s) => s.replace(/^[\s\x1c-\x1f\x85]+|[\s\x1c-\x1f\x85]+$/g, '');

const ISO = '(\\d{4}-\\d{2}-\\d{2})';
const MONEY = '\\$([\\d,]+\\.\\d{2})';
const ID = '([A-Z]+-\\d+|\\d+)';
const m1 = (re, text) => text.match(new RegExp(re, 'm'));
const stripCommas = (s) => s.replace(/,/g, '');

// Each rule: [regex, confidence, rule name, value transform]
const LEARN_RULES = {
  invoice_number: [[`^Invoice Number:\\s*${ID}\\s*$`, 1.0, 'Invoice Number:'], [`^Invoice No:\\s*${ID}\\s*$`, 0.8, 'Invoice No:'], [`^Invoice #\\s*${ID}\\s*$`, 0.8, 'Invoice #']],
  date: [[`^(?:Invoice Date|Date):\\s*${ISO}\\s*$`, 1.0, 'Date: (ISO)']],
  vendor: [['^Vendor:\\s*(.+?)\\s*$', 1.0, 'Vendor:'], ['^Supplier:\\s*(.+?)\\s*$', 0.8, 'Supplier:']],
  total: [[`^Total:\\s*${MONEY}\\s*$`, 1.0, 'Total:', stripCommas], [`^Amount Due:\\s*${MONEY}\\s*$`, 0.8, 'Amount Due:', stripCommas]],
  due_date: [[`^Due Date:\\s*${ISO}\\s*$`, 1.0, 'Due Date:'], [`^Due:\\s*${ISO}\\s*$`, 0.8, 'Due:']],
};
const BUILD_RULES = {
  invoice_number: [[`^Receipt Number:\\s*${ID}\\s*$`, 1.0, 'Receipt Number:'], [`^Receipt No:\\s*${ID}\\s*$`, 0.8, 'Receipt No:']],
  vendor: [['^Store:\\s*(.+?)\\s*$', 1.0, 'Store:']],
  total: [['^Paid:\\s*\\$([\\d,]+\\.\\d{2})\\s*$', 0.8, 'Paid:', stripCommas]],
};

const runRules = (rules, text) => {
  for (const [re, conf, rule, fx] of rules) {
    const m = m1(re, text);
    if (m) return { value: fx ? fx(m[1]) : m[1], confidence: conf, rule };
  }
  return null;
};

const FALLBACKS = {
  date: (text) => {
    for (const line of splitlines(text)) {
      if (line.startsWith('Due')) continue;
      const m = line.match(new RegExp(ISO));
      if (m) return { value: m[1], confidence: 0.6, rule: 'unlabelled ISO date' };
    }
    return null;
  },
  vendor: (text) => {
    for (let line of splitlines(text)) {
      line = pyStrip(line);
      if (line && !line.includes(':') && line !== 'INVOICE' && line !== 'PURCHASE FORM') return { value: line, confidence: 0.6, rule: 'first unlabelled line' };
    }
    return null;
  },
};
const NONE = { value: null, confidence: 0.0, rule: 'nothing matched' };

export function learnExtract(field, text) {
  return runRules(LEARN_RULES[field], text) || (FALLBACKS[field] && FALLBACKS[field](text)) || NONE;
}

// pipeline.extract_fields: Build receipt patterns first, then the Learn extractor.
export function extractFields(text, level = 'build') {
  const out = {};
  for (const f of FIELDS) out[f] = (level === 'build' && BUILD_RULES[f] && runRules(BUILD_RULES[f], text)) || learnExtract(f, text);
  return out;
}

const MONEY_CELL = /^\$([\d,]+\.\d{2})$/;
export function extractTable(text) {
  const lines = splitlines(text);
  for (let i = 0; i < lines.length; i++) {
    const low = lines[i].toLowerCase();
    if (!low.includes('item') || !low.includes('qty')) continue;
    const delim = lines[i].includes('|') ? '|' : lines[i].includes(';') ? ';' : null;
    if (delim === null) continue;
    const rows = [];
    for (const rowLine of lines.slice(i + 1)) {
      if (!rowLine.includes(delim)) break;
      const cells = rowLine.split(delim).map(pyStrip);
      if (cells.length !== 4) break;
      const unit = cells[2].match(MONEY_CELL), lineTotal = cells[3].match(MONEY_CELL);
      if (!(/^\d+$/.test(cells[1]) && unit && lineTotal)) break;
      rows.push({ item: cells[0], quantity: parseInt(cells[1], 10), unit_price: stripCommas(unit[1]), line_total: stripCommas(lineTotal[1]) });
    }
    return rows;
  }
  return [];
}

export function buildRecord(doc, text = doc.text) {
  const f = extractFields(text);
  return {
    doc_id: doc.id, kind: doc.kind, variant: doc.variant,
    fields: Object.fromEntries(FIELDS.map((k) => [k, f[k].value])),
    confidence: Object.fromEntries(FIELDS.map((k) => [k, f[k].confidence])),
    rules: Object.fromEntries(FIELDS.map((k) => [k, f[k].rule])),
    line_items: extractTable(text),
  };
}

// ---- money in integer cents, matching Decimal for two-place amounts ----
export const toCents = (s) => { const [w, f = ''] = s.split('.'); return parseInt(w, 10) * 100 + parseInt((f + '00').slice(0, 2), 10); };
export const fromCents = (c) => `${Math.floor(c / 100)}.${String(c % 100).padStart(2, '0')}`;

const spend = (records) => {
  let total = 0; const cited = [];
  for (const r of records) if (r.fields.total !== null) { total += toCents(r.fields.total); cited.push(r.doc_id); }
  return { value: fromCents(total), doc_ids: cited };
};
const byInvoice = (records, n) => records.find((r) => r.fields.invoice_number === n) || null;

export function answerQuestion(records, q) {
  const p = q.params;
  switch (q.type) {
    case 'total_spend_per_vendor': return spend(records.filter((r) => r.fields.vendor === p.vendor));
    case 'total_spend_all': return spend(records);
    case 'total_spend_for_kind': return spend(records.filter((r) => r.kind === p.kind));
    case 'largest_document': {
      let best = null;
      for (const r of records) if (r.fields.total !== null && (best === null || toCents(r.fields.total) > toCents(best.fields.total))) best = r;
      if (!best) return { value: null, doc_ids: [] };
      return { value: { doc_id: best.doc_id, total: best.fields.total }, doc_ids: [best.doc_id] };
    }
    case 'count_by_vendor': { const s = records.filter((r) => r.fields.vendor === p.vendor); return { value: s.length, doc_ids: s.map((r) => r.doc_id) }; }
    case 'count_by_kind': { const s = records.filter((r) => r.kind === p.kind); return { value: s.length, doc_ids: s.map((r) => r.doc_id) }; }
    case 'line_items_for_invoice': { const r = byInvoice(records, p.invoice_number); return r ? { value: r.line_items, doc_ids: [r.doc_id] } : { value: [], doc_ids: [] }; }
    case 'vendor_of_invoice': { const r = byInvoice(records, p.invoice_number); return r ? { value: r.fields.vendor, doc_ids: [r.doc_id] } : { value: null, doc_ids: [] }; }
    case 'documents_over_amount': {
      const t = toCents(p.amount);
      const s = records.filter((r) => r.fields.total !== null && toCents(r.fields.total) > t).map((r) => r.doc_id);
      return { value: s, doc_ids: [...s] };
    }
    default: throw new Error(`unknown question type: ${q.type}`);
  }
}

// Key-order-independent equality (results files are written with sort_keys).
export function deepEqual(a, b) {
  if (a === b) return true;
  if (a === null || b === null || typeof a !== 'object' || typeof b !== 'object') return false;
  if (Array.isArray(a) !== Array.isArray(b)) return false;
  const ka = Object.keys(a), kb = Object.keys(b);
  return ka.length === kb.length && ka.every((k) => deepEqual(a[k], b[k]));
}

// ---- scoring (eval_build.evaluate_fields / evaluate_tables) ----
const CELLS = ['item', 'quantity', 'unit_price', 'line_total'];
export function scoreTables(docs, records) {
  let rowsCorrect = 0, rowsTotal = 0, cellsCorrect = 0, cellsTotal = 0;
  docs.forEach((d, j) => {
    const gold = d.table_ground_truth, got = records[j].line_items;
    rowsTotal += gold.length; cellsTotal += gold.length * CELLS.length;
    gold.forEach((g, i) => {
      if (i >= got.length) return;
      if (CELLS.every((c) => got[i][c] === g[c])) rowsCorrect++;
      cellsCorrect += CELLS.filter((c) => got[i][c] === g[c]).length;
    });
  });
  return { rowsCorrect, rowsTotal, cellsCorrect, cellsTotal };
}
export function scoreFields(docs, records) {
  const per = FIELDS.map((f) => ({ field: f, correct: docs.filter((d, j) => records[j].fields[f] === d.ground_truth[f]).length, total: docs.length }));
  return { per, correct: per.reduce((s, p) => s + p.correct, 0), total: docs.length * FIELDS.length };
}

// ---- calibration (src/calibration.py) ----
// CPython 3.12 sum() over floats uses Neumaier compensated summation; match it.
export function pysum(xs) {
  let s = 0, c = 0;
  for (const x of xs) { const t = s + x; c += Math.abs(s) >= Math.abs(x) ? (s - t) + x : (x - t) + s; s = t; }
  return s + c;
}
// Python round(x, 4): nearest by exact binary value, exact ties to even.
export function pyRound4(x) {
  const [w, f] = Math.abs(x).toFixed(30).split('.');
  if (/^50+$/.test(f.slice(4))) { // exact decimal tie: round half to even
    const down = Number(`${w}.${f.slice(0, 4)}`), even = +f[3] % 2 === 0;
    return Math.sign(x) * Number((even ? down : down + 1e-4).toFixed(4));
  }
  return Number(x.toFixed(4));
}
export function wilson(k, n, z = 1.959964) {
  if (n === 0) return [0.0, 1.0];
  const p = k / n, denom = 1 + z * z / n;
  const centre = (p + z * z / (2 * n)) / denom;
  const half = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom;
  return [pyRound4(Math.max(0.0, centre - half)), pyRound4(Math.min(1.0, centre + half))];
}
export function bandTable(items) {
  return [...new Set(items.map((i) => i.confidence))].sort((a, b) => a - b).map((conf) => {
    const sel = items.filter((i) => i.confidence === conf);
    const correct = sel.filter((i) => i.correct).length, acc = correct / sel.length;
    return { confidence: conf, count: sel.length, correct, accuracy: pyRound4(acc), gap: pyRound4(Math.abs(acc - conf)), wilson95: wilson(correct, sel.length) };
  });
}
export const ece = (items, bands) => pyRound4(pysum(bands.map((b) => (b.count / items.length) * Math.abs(b.accuracy - b.confidence))));
export const brier = (items) => pyRound4(pysum(items.map((i) => (i.confidence - (i.correct ? 1 : 0)) ** 2)) / items.length);

export function queueAtThreshold(items, threshold) {
  const flagged = items.filter((i) => i.confidence < threshold);
  const totalErrors = items.filter((i) => !i.correct).length;
  const captured = flagged.filter((i) => !i.correct).length;
  const docs = [...new Set(flagged.map((i) => i.doc_id))].sort();
  return {
    threshold, rule: `confidence < ${threshold.toFixed(2)}`,
    fields_flagged: flagged.length, review_burden: pyRound4(flagged.length / items.length),
    documents_flagged: docs.length, document_ids: docs,
    errors_captured: captured, total_errors: totalErrors,
    error_capture_rate: totalErrors ? pyRound4(captured / totalErrors) : 0.0,
    capture_wilson95: wilson(captured, totalErrors),
    flagged_correct: flagged.length - captured,
    queue: flagged.map((i) => ({ doc_id: i.doc_id, field: i.field, confidence: i.confidence, extracted: i.extracted, correct: i.correct })),
  };
}

// ---- perturbation stress set (src/stress.py) ----
export const PERTURB = {
  none: (t) => t,
  lowercase_labels: (t) => t.split('\n').map((l) => { const k = l.indexOf(':'); return k < 0 ? l : l.slice(0, k).toLowerCase() + l.slice(k); }).join('\n'),
  indented_lines: (t) => t.split('\n').map((l) => (l ? `  ${l}` : l)).join('\n'),
  dmy_dates: (t) => t.replace(/(\d{4})-(\d{2})-(\d{2})/g, '$3/$2/$1'),
  no_currency_symbol: (t) => t.replaceAll('$', ''),
};

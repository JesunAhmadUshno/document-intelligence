import { useMemo, useState, useEffect, useId } from 'react';
import exported from '../../results/documents_export.json';
import learn from '../../results/results_learn.json';
import build from '../../results/results_build.json';
import deep from '../../results/results_deep.json';
import stress from '../../results/results_stress.json';
import report from '../../REPORT.md?raw';
import proposal from '../../PROPOSAL.md?raw';
import readme from '../../README.md?raw';
import {
  FIELDS, extractFields, extractTable, buildRecord, answerQuestion, deepEqual,
  queueAtThreshold, wilson, PERTURB, scoreFields, scoreTables,
} from './engine.js';

const REPO = 'https://github.com/JesunAhmadUshno/document-intelligence';
const blob = (p) => `${REPO}/blob/main/${p}`;
const pct = (x, d = 1) => `${(x * 100).toFixed(d)}%`;
const f4 = (x) => x.toFixed(4);
// Provenance label parsed from the Deep README results heading, never typed here.
const [, RECORDED_ON, RECORDED_WHERE] = report.match(/## Results \(measured (\d{4}-\d{2}-\d{2}), ([^,]+),/);
const RECORDED = `recorded ${RECORDED_ON}, ${RECORDED_WHERE}`;
// The verdict sentence from the README abstract, e.g. "Functional, not pre-registered".
const [, VERDICT] = readme.match(/\*\*Verdict\.\*\* ([^.]+)\./);
// The backlog is the numbered list in PROPOSAL.md's "## Next cycle" section.
const roadmap = proposal.split(/^## Next cycle\n/m)[1];
const BACKLOG = [...roadmap.matchAll(/^(\d+)\. ([^.]+)\./gm)].map((m) => [m[1], m[2].replace(/\bLLM\b/g, 'Language-model')]);

const BUILD_DOCS = exported.build;
const LEARN_DOCS = exported.learn;
const ALL_DOCS = Object.fromEntries([...BUILD_DOCS, ...LEARN_DOCS].map((d) => [d.id, d]));
const QUESTIONS = build.per_question;
const ERRORS = deep.items.filter((i) => !i.correct);
const bandOf = (c) => deep.bands.find((b) => b.confidence === c);
const recQueue = deep.recommended_queue;

const SECTIONS = [['top', 'Overview', '◎'], ['extract', 'Extract', '⌕'], ['fields', 'Fields', '▥'], ['tables', 'Tables', '▦'], ['qa', 'QA', '?'], ['calibration', 'Calibration', '◢'], ['queue', 'Review queue', '⚑'], ['stress', 'Stress', '≋'], ['limits', 'Limits', '!'], ['reproduce', 'Reproduce', '❯_']];

function useReveal() {
  useEffect(() => {
    const els = document.querySelectorAll('.reveal');
    if (!('IntersectionObserver' in window)) { els.forEach((e) => e.classList.add('in')); return; }
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: 0.08 });
    els.forEach((e) => io.observe(e));
    return () => io.disconnect();
  }, []);
}

function MenuBar() {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => { const t = setInterval(() => setNow(new Date()), 30000); return () => clearInterval(t); }, []);
  return (
    <div className="menubar" role="banner">
      <span className="apple" aria-hidden="true">◆</span>
      <a className="app" href="#top">Document Intelligence</a>
      <a className="m" href={blob('README.md')}>Abstract</a>
      <a className="m" href={blob('PROPOSAL.md')}>Proposal</a>
      <a className="m" href={blob('REPORT.md')}>Report</a>
      <a className="m" href={blob('CHANGELOG.md')}>Changelog</a>
      <span className="spacer" />
      <span className="status"><i /> Browser port matches Python</span>
      <a href={REPO}>GitHub ↗</a>
      <span className="clock">{now.toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' })}</span>
    </div>
  );
}

function Dock() {
  const [active, setActive] = useState('top');
  useEffect(() => {
    const io = new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting && setActive(e.target.id)), { rootMargin: '-45% 0px -50% 0px' });
    SECTIONS.forEach(([id]) => { const el = document.getElementById(id); if (el) io.observe(el); });
    return () => io.disconnect();
  }, []);
  return (
    <nav className="dock" aria-label="Sections">
      {SECTIONS.map(([id, label, icon]) => (
        <a key={id} href={`#${id}`} className={active === id ? 'on' : ''} aria-current={active === id ? 'true' : undefined}>
          <span className="ico" aria-hidden="true">{icon}</span><span className="lbl">{label}</span>
        </a>
      ))}
    </nav>
  );
}

function Range({ label, value, min, max, step, onChange, show }) {
  const id = useId();
  return (
    <div className="field">
      <label htmlFor={id}>{label} <span>{show}</span></label>
      <input id={id} type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(+e.target.value)} />
    </div>
  );
}

const Conf = ({ c }) => <span className={`pill ${c >= 0.8 ? 'good' : c > 0 ? 'warn' : 'bad'}`}>{c.toFixed(2)}</span>;
const Mark = ({ ok }) => <span className={ok ? 'ok' : 'no'}>{ok ? '✓ match' : '✗ miss'}</span>;
const show = (v) => (v === null ? <span className="hint">None</span> : String(v));

export default function App() {
  useReveal();
  const [edits, setEdits] = useState({});
  const [sel, setSel] = useState('B16');
  const textOf = (id) => edits[id] ?? ALL_DOCS[id].text;
  // Live Build records: QA, tables and the playground all read these, so an edit flows everywhere.
  const records = useMemo(() => BUILD_DOCS.map((d) => buildRecord(d, textOf(d.id))), [edits]); // eslint-disable-line react-hooks/exhaustive-deps
  const setText = (id, t) => setEdits((e) => ({ ...e, [id]: t }));
  const reset = (id) => setEdits((e) => { const n = { ...e }; delete n[id]; return n; });
  return (
    <div className="wrap">
      <MenuBar />
      <div className="glow" aria-hidden="true" />
      <Hero />
      <Extract sel={sel} setSel={setSel} text={textOf(sel)} setText={setText} reset={reset} edited={sel in edits} />
      <Fields />
      <Tables sel={sel} setSel={setSel} records={records} />
      <QA records={records} edits={edits} setText={setText} reset={reset} />
      <Calibration />
      <Queue />
      <Stress />
      <Limits />
      <Reproduce />
      <Dock />
      <footer>
        Every number on this page is read at build time from <code>results/*.json</code> or computed in your browser by a port of the Python extractor that a build-time parity check holds to the committed results.
        <br />Documents are synthetic and every vendor name is invented. Code: Apache-2.0.
      </footer>
    </div>
  );
}

function Hero() {
  const fs = build.field_summary, t = build.table, q = build.qa_summary;
  return (
    <header className="card hero window" id="top" data-title="document-intelligence — README.md">
      <div className="head">
        <p className="eyebrow">Learn · Build · Deep · rule-based document extraction</p>
        <span className="pill warn">● Synthetic text, no OCR</span>
        <span className="pill">Verdict: {VERDICT}</span>
      </div>
      <h1>Hand-written rules get {fs.total_correct} of {fs.total_fields} fields right. Their confidence scores are <em>route labels</em>, not probabilities.</h1>
      <p className="sub">
        Regular-expression rules pull five fields, a line-item table and cross-document answers out of {BUILD_DOCS.length} synthetic invoices, forms and receipts.
        A calibration audit then asks whether the {deep.bands.map((b) => b.confidence.toFixed(2)).join(' / ')} confidence values mean what they say. They sort fields for review well; read as probabilities, every non-zero value understates accuracy.
      </p>
      <p className="banner" role="note">
        <b>Scope, stated plainly:</b> the input is synthetic plain text in the layout an OCR step would produce. There is no OCR and no language model in the shipped code. All levels ran on CPU ({RECORDED}).
      </p>
      <div className="actions">
        <a className="btn primary" href="#extract">Open the live extractor</a>
        <a className="btn ghost" href="#calibration">See the calibration audit</a>
        <span className="hint">Reproduce with three <code>python</code> runners and <code>unittest</code></span>
      </div>
      <div className="tiles">
        <div className="tile"><div className="num">{fs.total_correct}/{fs.total_fields}</div><div className="cap">Build fields correct (accuracy {f4(fs.overall_accuracy)})</div></div>
        <div className="tile"><div className="num">{t.rows_correct}/{t.rows_total}</div><div className="cap">Table rows exact, {t.cells_correct}/{t.cells_total} cells</div></div>
        <div className="tile"><div className="num">{q.correct}/{q.questions}</div><div className="cap">Cross-document questions answered correctly</div></div>
        <div className="tile"><div className="num">{f4(deep.ece)}</div><div className="cap">Expected calibration error; Brier {f4(deep.brier)}</div></div>
        <div className="tile"><div className="num">{learn.summary.total_correct}/{learn.summary.total_fields}</div><div className="cap">Learn fields correct on {learn.summary.documents} smaller documents</div></div>
        <div className="tile"><div className="num">{recQueue.errors_captured}/{recQueue.total_errors}</div><div className="cap">Errors caught by flagging {recQueue.rule}</div></div>
        <div className="tile"><div className="num">{pct(recQueue.review_burden, 2)}</div><div className="cap">Review burden at that rule ({recQueue.fields_flagged} of {deep.total_fields} fields)</div></div>
        <div className="tile"><div className="num">{deep.total_errors}</div><div className="cap">Errors in the whole eval, so every rate here is small-n</div></div>
      </div>
    </header>
  );
}

function Extract({ sel, setSel, text, setText, reset, edited }) {
  const [shift, setShift] = useState('none');
  const doc = ALL_DOCS[sel];
  const isBuild = sel.startsWith('B');
  const input = PERTURB[shift](text);
  const fields = useMemo(() => extractFields(input, isBuild ? 'build' : 'learn'), [input, isBuild]);
  const rows = useMemo(() => (isBuild ? extractTable(input) : []), [input, isBuild]);
  const matches = FIELDS.filter((f) => fields[f].value === doc.ground_truth[f]).length;
  const taId = useId();
  return (
    <section id="extract" className="card window reveal" data-title="extract.app — live in your browser">
      <div className="head">
        <div>
          <p className="eyebrow">Live extractor playground</p>
          <h2>Edit any document and watch the rules <em>re-fire</em>.</h2>
          <p className="sub">
            A JavaScript port of <a href={blob('src/extractor.py')}>extractor.py</a> and <a href={blob('src/pipeline.py')}>pipeline.py</a> runs on the exact texts the Python code reads.
            Before every build, a parity check runs the port over all {BUILD_DOCS.length + LEARN_DOCS.length} documents and stops the build if any value, confidence or table row differs from the committed results.
          </p>
        </div>
        <span className={`pill ${matches === FIELDS.length ? 'good' : 'warn'}`}>{matches}/{FIELDS.length} fields match the labels</span>
      </div>
      <div className="controls">
        <div className="field"><label htmlFor="doc">Document</label>
          <select id="doc" value={sel} onChange={(e) => setSel(e.target.value)}>
            <optgroup label={`Build corpus (${BUILD_DOCS.length})`}>{BUILD_DOCS.map((d) => <option key={d.id} value={d.id}>{d.id} · {d.kind} {d.variant} · {d.ground_truth.vendor}</option>)}</optgroup>
            <optgroup label={`Learn fixtures (${LEARN_DOCS.length})`}>{LEARN_DOCS.map((d) => <option key={d.id} value={d.id}>{d.id} · {d.kind} · {d.ground_truth.vendor}</option>)}</optgroup>
          </select>
        </div>
        <div className="field"><label htmlFor="shift">Format shift (stress set)</label>
          <select id="shift" value={shift} onChange={(e) => setShift(e.target.value)}>
            <option value="none">None, text as written</option>
            {stress.perturbations.map((p) => <option key={p.name} value={p.name}>{p.description}</option>)}
          </select>
        </div>
      </div>
      <div className="play">
        <div>
          <label className="ta-label" htmlFor={taId}>Document text {edited && <span className="pill info">edited</span>}</label>
          <textarea id={taId} value={text} spellCheck="false" onChange={(e) => setText(sel, e.target.value)} rows={11} />
          <div className="actions" style={{ marginTop: 10 }}>
            <button className="btn ghost" onClick={() => reset(sel)} disabled={!edited}>Reset to original</button>
            <span className="hint">{isBuild ? 'Build rules: receipt labels first, then the Learn rules.' : 'Learn rules only (Level 1).'}{shift !== 'none' && ' The shift is applied before extraction.'}</span>
          </div>
        </div>
        <div>
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead><tr><th>Field</th><th>Extracted · rule that fired</th><th>Conf.</th><th>Label</th></tr></thead>
              <tbody>
                {FIELDS.map((f) => (
                  <tr key={f}>
                    <td className="mono">{f}</td><td>{show(fields[f].value)}<div className="hint" style={{ fontSize: 11.5 }}>{fields[f].rule}</div></td><td><Conf c={fields[f].confidence} /></td>
                    <td><Mark ok={fields[f].value === doc.ground_truth[f]} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {isBuild && (
            <>
              <h3 style={{ marginTop: 16 }}>Parsed line items ({rows.length} of {doc.table_ground_truth.length} labelled rows)</h3>
              <div style={{ overflowX: 'auto' }}>
                <table>
                  <thead><tr><th>Item</th><th>Qty</th><th>Unit</th><th>Line total</th></tr></thead>
                  <tbody>{rows.length ? rows.map((r, i) => <tr key={i}><td>{r.item}</td><td>{r.quantity}</td><td>{r.unit_price}</td><td>{r.line_total}</td></tr>) : <tr><td colSpan="4" className="hint">No table matched the stated format.</td></tr>}</tbody>
                </table>
              </div>
            </>
          )}
          <p className="hint" style={{ marginTop: 10 }}>Confidence is the route the rule took: 1.00 primary label, 0.80 alternate label, 0.60 unlabelled fallback, 0.00 nothing matched.</p>
        </div>
      </div>
    </section>
  );
}

function Fields() {
  const [pick, setPick] = useState('total');
  const lf = Object.fromEntries(learn.per_field.map((p) => [p.field, p]));
  const bf = Object.fromEntries(build.per_field.map((p) => [p.field, p]));
  const W = 640, rowH = 56, H = FIELDS.length * rowH + 30, l = 118, r = 86;
  const lo = 0.5, x = (v) => l + ((Math.max(lo, v) - lo) / (1 - lo)) * (W - l - r);
  const errs = [
    ...learn.per_document.filter((d) => !d.fields[pick].correct).map((d) => ({ level: 'Learn', id: d.doc_id, got: d.fields[pick].extracted, want: d.fields[pick].ground_truth })),
    ...ERRORS.filter((e) => e.field === pick).map((e) => ({ level: 'Build', id: e.doc_id, got: e.extracted, want: e.ground_truth })),
  ];
  return (
    <section id="fields" className="card window reveal" data-title={`fields.csv — Learn ${learn.summary.documents} docs vs Build ${BUILD_DOCS.length} docs`}>
      <p className="eyebrow">Per-field accuracy · {RECORDED}</p>
      <h2>Three fields are perfect at both levels. <em>Date and total</em> each miss once.</h2>
      <p className="sub">
        Bars are accuracy per field; whiskers are Wilson 95% intervals computed in your browser from the counts, wide because each level has few documents. Click a field to see its errors.
      </p>
      <div className="seg" role="group" aria-label="Choose a field" style={{ marginTop: 14, flexWrap: 'wrap' }}>
        {FIELDS.map((f) => <button key={f} aria-pressed={pick === f} onClick={() => setPick(f)}>{f}</button>)}
      </div>
      <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Per-field accuracy, Learn against Build, with Wilson 95% intervals" style={{ marginTop: 12 }}>
        {[0.5, 0.75, 1].map((t) => <g key={t}><line className="axis" x1={x(t)} x2={x(t)} y1={0} y2={H - 22} /><text x={x(t)} y={H - 6} textAnchor="middle">{t.toFixed(2)}</text></g>)}
        {FIELDS.map((f, i) => (
          <g key={f} transform={`translate(0 ${i * rowH + 10})`} onClick={() => setPick(f)} style={{ cursor: 'pointer' }} opacity={pick === f ? 1 : 0.55}>
            <text x={0} y={22} style={{ fill: 'var(--text)', fontSize: 14, fontWeight: pick === f ? 700 : 400 }}>{f}</text>
            {[[lf[f], 'var(--warn)', 4, 'Learn'], [bf[f], 'var(--primary)', 24, 'Build']].map(([p, c, dy, lab]) => {
              const [wl, wh] = wilson(p.correct, p.total);
              return (
                <g key={lab}>
                  <rect x={l} y={dy} width={x(p.accuracy) - l} height={14} rx={4} fill={c} opacity={0.85} />
                  <line x1={x(wl)} x2={x(wh)} y1={dy + 7} y2={dy + 7} stroke="var(--text)" strokeWidth="1.5" opacity="0.6" />
                  <text x={W - r + 8} y={dy + 12} style={{ fill: 'var(--text)' }}>{lab} {p.correct}/{p.total}</text>
                </g>
              );
            })}
          </g>
        ))}
      </svg>
      <div className="legend"><span><i style={{ background: 'var(--warn)' }} />Learn ({learn.summary.documents} documents)</span><span><i style={{ background: 'var(--primary)' }} />Build ({BUILD_DOCS.length} documents)</span><span>Axis starts at 0.50</span></div>
      <div className="tip" aria-live="polite">
        {errs.length ? errs.map((e) => <div key={e.level + e.id}><b>{e.level} {e.id}</b>: extracted {e.got === null ? 'None' : e.got}, label {e.want}. Source line: <span className="mono">{srcLine(e.id, pick)}</span></div>)
          : <>No errors on <span className="mono">{pick}</span> at either level.</>}
      </div>
    </section>
  );
}

const SRC = { date: /^Date:.*$/m, total: /^(Total|Amount Due|Paid):.*$/m };
const srcLine = (id, field) => (ALL_DOCS[id].text.match(SRC[field] || new RegExp(`^.*${field}.*$`, 'mi')) || ['(no labelled line)'])[0];

function Tables({ sel, setSel, records }) {
  const id = sel.startsWith('B') ? sel : 'B01';
  const j = BUILD_DOCS.findIndex((d) => d.id === id);
  const doc = BUILD_DOCS[j], got = records[j].line_items;
  const live = scoreTables(BUILD_DOCS, records);
  return (
    <section id="tables" className="card window reveal" data-title="tables.view — line items">
      <div className="head">
        <div>
          <p className="eyebrow">Table extraction</p>
          <h2>Every labelled row comes back exact, in both <em>pipe and semicolon</em> layouts.</h2>
          <p className="sub">Recorded: {build.table.rows_correct}/{build.table.rows_total} rows and {build.table.cells_correct}/{build.table.cells_total} cells, {build.table.extra_rows} extra rows. Live, with your edits: {live.rowsCorrect}/{live.rowsTotal} rows, {live.cellsCorrect}/{live.cellsTotal} cells. Pick a document.</p>
        </div>
      </div>
      <div className="chips" role="group" aria-label="Choose a document">
        {BUILD_DOCS.map((d, k) => {
          const ok = records[k].line_items.length === d.table_ground_truth.length && d.table_ground_truth.every((g, i) => deepEqual(g, records[k].line_items[i]));
          return <button key={d.id} className={`chip ${d.id === id ? 'on' : ''} ${ok ? '' : 'bad'}`} aria-pressed={d.id === id} onClick={() => setSel(d.id)}>{d.id}<small>{records[k].line_items.length}/{d.table_ground_truth.length}</small></button>;
        })}
      </div>
      <div style={{ overflowX: 'auto', marginTop: 14 }}>
        <table>
          <thead><tr><th>#</th><th>Item</th><th>Qty</th><th>Unit price</th><th>Line total</th><th>Against label</th></tr></thead>
          <tbody>
            {doc.table_ground_truth.map((g, i) => {
              const r = got[i];
              return <tr key={i}><td>{i + 1}</td><td>{r ? r.item : '–'}</td><td>{r ? r.quantity : '–'}</td><td>{r ? r.unit_price : '–'}</td><td>{r ? r.line_total : '–'}</td><td><Mark ok={!!r && deepEqual(r, g)} /></td></tr>;
            })}
          </tbody>
        </table>
      </div>
      <p className="hint" style={{ marginTop: 8 }}>{doc.id}: {doc.kind}, layout {doc.variant} ({doc.variant === 'A' ? 'pipe' : 'semicolon'}-delimited), {doc.ground_truth.vendor}.</p>
    </section>
  );
}

function describe(q) {
  const p = q.params;
  return {
    total_spend_per_vendor: `Total spend with ${p.vendor}?`, total_spend_all: 'Total spend across all documents?',
    total_spend_for_kind: `Total spend on ${p.kind}s?`, largest_document: 'Which document has the largest total?',
    count_by_vendor: `How many documents from ${p.vendor}?`, count_by_kind: `How many ${p.kind}s?`,
    line_items_for_invoice: `Line items on ${p.invoice_number}?`, vendor_of_invoice: `Who issued ${p.invoice_number}?`,
    documents_over_amount: `Which documents total more than ${p.amount}?`,
  }[q.type];
}
const fmtVal = (v) => (v === null ? 'None' : Array.isArray(v) ? (v.length && typeof v[0] === 'object' ? v.map((r) => `${r.item} ×${r.quantity}`).join(', ') : v.join(', ') || '(none)') : typeof v === 'object' ? `${v.doc_id} (${v.total})` : String(v));

function QA({ records, edits, setText, reset }) {
  const [qid, setQid] = useState(QUESTIONS.find((q) => !q.correct).id);
  const q = QUESTIONS.find((x) => x.id === qid);
  const answers = useMemo(() => QUESTIONS.map((x) => answerQuestion(records, x)), [records]);
  const okAll = QUESTIONS.map((x, i) => deepEqual(answers[i].value, x.gold.value) && deepEqual(answers[i].doc_ids, x.gold.doc_ids));
  const k = QUESTIONS.indexOf(q), got = answers[k];
  const missed = q.gold.doc_ids.filter((d) => !got.doc_ids.includes(d));
  const knownMiss = QUESTIONS.find((x) => !x.correct);
  const b16 = ERRORS.find((e) => e.field === 'total')?.doc_id;
  const fixB16 = () => setText(b16, ALL_DOCS[b16].text.replace(/^Amount Due: .*$/m, `Amount Due: $${ALL_DOCS[b16].ground_truth.total}`));
  return (
    <section id="qa" className="card window reveal" data-title={`qa.console — ${QUESTIONS.length} structured questions`}>
      <div className="head">
        <div>
          <p className="eyebrow">Cross-document question answering</p>
          <h2>One total written in words moves the <em>grand total</em>.</h2>
          <p className="sub">
            A port of <a href={blob('src/qa.py')}>qa.py</a> answers {QUESTIONS.length} structured questions from the records extracted live above, adding money in integer cents so it matches Python's Decimal exactly. Gold answers come from <a href={blob('results/results_build.json')}>results_build.json</a>. Questions are structured queries, not free text.
          </p>
        </div>
        <span className={`pill ${okAll.every(Boolean) ? 'good' : 'warn'}`}>{okAll.filter(Boolean).length}/{QUESTIONS.length} correct live</span>
      </div>
      <div className="controls" style={{ gridTemplateColumns: 'minmax(0, 1fr)' }}>
        <div className="field"><label htmlFor="q">Question</label>
          <select id="q" value={qid} onChange={(e) => setQid(e.target.value)}>
            {QUESTIONS.map((x, i) => <option key={x.id} value={x.id}>{x.id} · {describe(x)} {okAll[i] ? '' : '(wrong)'}</option>)}
          </select>
        </div>
      </div>
      <div className="grid2">
        <div className="tile">
          <div className="head" style={{ marginBottom: 6 }}><h3>Browser answer</h3><Mark ok={okAll[k]} /></div>
          <div className="answer">{fmtVal(got.value)}</div>
          <p className="hint" style={{ margin: '6px 0 0' }}>Cites {got.doc_ids.length} document{got.doc_ids.length === 1 ? '' : 's'}: {got.doc_ids.join(', ') || 'none'}</p>
        </div>
        <div className="tile">
          <div className="head" style={{ marginBottom: 6 }}><h3>Gold answer</h3><span className="pill info">from labels</span></div>
          <div className="answer">{fmtVal(q.gold.value)}</div>
          <p className="hint" style={{ margin: '6px 0 0' }}>{missed.length ? <>Not cited by the browser: <b>{missed.join(', ')}</b>, whose extracted total is None.</> : `Cites ${q.gold.doc_ids.length} document${q.gold.doc_ids.length === 1 ? '' : 's'}.`}</p>
        </div>
      </div>
      <div className="actions">
        <button className="btn primary" onClick={fixB16} disabled={b16 in edits}>Write {b16}'s total in digits</button>
        <button className="btn ghost" onClick={() => reset(b16)} disabled={!(b16 in edits)}>Undo</button>
        <span className="hint">The recorded run gets {knownMiss.id} wrong ({knownMiss.answer.value} against {knownMiss.gold.value}). Rewrite {b16}'s total and the live answer turns correct.</span>
      </div>
    </section>
  );
}

function Calibration() {
  const W = 460, H = 340, pad = { l: 52, r: 16, t: 44, b: 44 };
  const sx = (v) => pad.l + ((v + 0.06) / 1.12) * (W - pad.l - pad.r), sy = (v) => pad.t + ((1.04 - v) / 1.08) * (H - pad.t - pad.b);
  const diagDeg = (Math.atan2(sy(1) - sy(0), sx(1) - sx(0)) * 180) / Math.PI;
  const maxN = Math.max(...deep.bands.map((b) => b.count));
  const zero = bandOf(0), bl = deep.baselines;
  const dueZero = deep.per_field.find((f) => f.field === 'due_date').by_band.find((b) => b.confidence === 0);
  return (
    <section id="calibration" className="card window reveal" data-title="calibration.plot — reliability diagram">
      <p className="eyebrow">Calibration audit · {RECORDED}</p>
      <h2>The 0.60 and 0.80 bands are <em>underconfident</em>, 1.00 is exact; the 0.00 band mixes two meanings.</h2>
      <p className="sub">
        Bands are the four stated confidence values themselves, so no binning choice is hidden. Points sit on or above the diagonal: every field in a non-zero band was right.
        The 0.00 band pools {dueZero.correct} correct absences (receipts have no due date) with the {deep.total_errors} real misses, so its {f4(zero.accuracy)} describes neither.
      </p>
      <div className="grid2" style={{ marginTop: 16 }}>
        <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Reliability diagram: stated confidence against measured accuracy per band, with Wilson 95% intervals">
          {[0, 0.2, 0.4, 0.6, 0.8, 1].map((t) => <g key={t}><line className="axis" x1={pad.l} x2={W - pad.r} y1={sy(t)} y2={sy(t)} /><text x={pad.l - 8} y={sy(t) + 4} textAnchor="end">{t.toFixed(1)}</text><text x={sx(t)} y={H - pad.b + 18} textAnchor="middle">{t.toFixed(1)}</text></g>)}
          <line x1={sx(0)} y1={sy(0)} x2={sx(1)} y2={sy(1)} stroke="var(--muted)" strokeDasharray="5 4" />
          <text x={sx(0.3)} y={sy(0.3) - 8} transform={`rotate(${diagDeg} ${sx(0.3)} ${sy(0.3) - 8})`}>perfect calibration</text>
          {deep.bands.map((b) => {
            const [wl, wh] = wilson(b.correct, b.count);
            const r = 5 + 13 * Math.sqrt(b.count / maxN);
            return (
              <g key={b.confidence}>
                <line x1={sx(b.confidence)} x2={sx(b.confidence)} y1={sy(wl)} y2={sy(wh)} stroke="var(--primary)" strokeWidth="2" opacity="0.5" />
                <line x1={sx(b.confidence)} x2={sx(b.confidence)} y1={sy(b.confidence)} y2={sy(b.accuracy)} stroke="var(--bad)" strokeWidth="1.5" strokeDasharray="2 3" />
                <circle cx={sx(b.confidence)} cy={sy(b.accuracy)} r={r} fill="var(--primary)" fillOpacity="0.25" stroke="var(--primary)" strokeWidth="2" />
                <text x={b.confidence === 0 ? sx(b.confidence) + r + 6 : sx(b.confidence)} y={b.confidence === 0 ? sy(b.accuracy) + 4 : sy(b.accuracy) - r - 6} textAnchor={b.confidence === 0 ? 'start' : 'middle'} style={{ fill: 'var(--text)' }}>{b.correct}/{b.count}</text>
              </g>
            );
          })}
          <text x={(pad.l + W - pad.r) / 2} y={H - 6} textAnchor="middle">stated confidence (band)</text>
          <text x={14} y={(pad.t + H - pad.b) / 2} textAnchor="middle" transform={`rotate(-90 14 ${(pad.t + H - pad.b) / 2})`}>measured accuracy</text>
        </svg>
        <div>
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead><tr><th>Band</th><th>Fields</th><th>Accuracy</th><th>Wilson 95%</th><th>Gap</th></tr></thead>
              <tbody>{deep.bands.map((b) => <tr key={b.confidence}><td>{b.confidence.toFixed(2)}</td><td>{b.count}</td><td>{f4(b.accuracy)}</td><td>{b.wilson95[0].toFixed(2)}–{b.wilson95[1].toFixed(2)}</td><td>{f4(b.gap)}</td></tr>)}</tbody>
            </table>
          </div>
          <p className="formula">ECE = Σ<sub>b</sub> (n<sub>b</sub>/N)·|acc<sub>b</sub> − conf<sub>b</sub>| = <b>{f4(deep.ece)}</b><br />Brier = mean (conf − outcome)² = <b>{f4(deep.brier)}</b></p>
          <h3 style={{ marginTop: 14 }}>Against in-sample baselines</h3>
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead><tr><th>Scorer</th><th>ECE</th><th>Brier</th></tr></thead>
              <tbody>
                <tr><td>Stated route labels</td><td>{f4(bl.stated_route_labels.ece)}</td><td>{f4(bl.stated_route_labels.brier)}</td></tr>
                <tr><td>Constant {f4(bl.constant_overall_accuracy.confidence)} (overall accuracy)</td><td>{f4(bl.constant_overall_accuracy.ece)}</td><td>{f4(bl.constant_overall_accuracy.brier)}</td></tr>
                <tr><td>Band-accuracy map</td><td>{f4(bl.band_accuracy_map_in_sample.ece)}</td><td>{f4(bl.band_accuracy_map_in_sample.brier)}</td></tr>
              </tbody>
            </table>
          </div>
          <p className="hint">Both baselines are fitted on the same {deep.total_fields} fields they are scored on, so they flatter themselves. They show that most of the Brier score is label miscalibration, not ranking failure.</p>
        </div>
      </div>
      <h3 style={{ marginTop: 18 }}>Cuts by kind and layout variant (indicative only: {deep.total_errors} errors in total)</h3>
      <div style={{ overflowX: 'auto' }}>
        <table>
          <thead><tr><th>Group</th><th>Fields</th><th>Errors</th><th>Accuracy</th><th>Wilson 95%</th><th>Mean conf.</th><th>ECE</th></tr></thead>
          <tbody>{[...deep.breakdowns.by_kind, ...deep.breakdowns.by_variant.map((g) => ({ ...g, group: `variant ${g.group}` }))].map((g) => (
            <tr key={g.group}><td>{g.group}</td><td>{g.count}</td><td>{g.errors}</td><td>{f4(g.accuracy)}</td><td>{g.wilson95[0].toFixed(2)}–{g.wilson95[1].toFixed(2)}</td><td>{f4(g.mean_confidence)}</td><td>{f4(g.ece)}</td></tr>
          ))}</tbody>
        </table>
      </div>
    </section>
  );
}

function Queue() {
  const [t, setT] = useState(deep.recommended_threshold);
  const q = useMemo(() => queueAtThreshold(deep.items, t), [t]);
  const isRecorded = deep.threshold_sweep.some((s) => s.threshold === t);
  return (
    <section id="queue" className="card window reveal" data-title={`review.queue — ${deep.total_fields} recorded extractions`}>
      <div className="head">
        <div>
          <p className="eyebrow">Review-queue threshold explorer</p>
          <h2>Flag below {recQueue.threshold.toFixed(2)} and a reviewer sees <em>every error</em> in {recQueue.fields_flagged} fields.</h2>
          <p className="sub">
            Drag the threshold. The browser recomputes the queue over the {deep.total_fields} recorded extractions in <a href={blob('results/results_deep.json')}>results_deep.json</a> using a port of <span className="mono">queue_at_threshold</span>. The parity check holds it to the recorded sweep at {deep.threshold_sweep.map((x) => x.threshold.toFixed(2)).join(', ')}.
          </p>
        </div>
        <span className="pill info">{isRecorded ? 'matches recorded sweep' : 'computed live'}</span>
      </div>
      <div className="controls" style={{ gridTemplateColumns: 'minmax(0, 1fr)' }}>
        <Range label="Flag fields with confidence below" value={t} min={0} max={1.05} step={0.05} onChange={setT} show={t > 1 ? 'everything' : t.toFixed(2)} />
      </div>
      <div className="tiles" style={{ marginTop: 0 }}>
        <div className="tile"><div className="num">{q.fields_flagged}</div><div className="cap">fields flagged of {deep.total_fields}</div></div>
        <div className="tile"><div className="num">{pct(q.review_burden, 2)}</div><div className="cap">review burden</div></div>
        <div className="tile"><div className="num">{q.documents_flagged}</div><div className="cap">documents touched of {deep.total_documents}</div></div>
        <div className="tile"><div className="num">{q.errors_captured}/{q.total_errors}</div><div className="cap">errors captured, Wilson 95% {pct(q.capture_wilson95[0], 0)}–{pct(q.capture_wilson95[1], 0)}</div></div>
      </div>
      <div className="chips" style={{ marginTop: 14 }} aria-live="polite">
        {q.queue.length ? q.queue.slice(0, 80).map((i) => <span key={i.doc_id + i.field} className={`chip ${i.correct ? '' : 'bad'}`}>{i.doc_id}<small>{i.field} · {i.confidence.toFixed(2)}{i.correct ? '' : ' · wrong'}</small></span>) : <span className="hint">Nothing flagged at this threshold, so both errors pass unseen.</span>}
        {q.queue.length > 80 && <span className="hint">and {q.queue.length - 80} more</span>}
      </div>
      <p className="hint" style={{ marginTop: 10 }}>The interval on the capture rate spans {pct(recQueue.capture_wilson95[0], 0)} to {pct(recQueue.capture_wilson95[1], 0)} because it rests on {recQueue.total_errors} errors. The threshold was chosen on the same eval it is scored on.</p>
    </section>
  );
}

function Stress() {
  const live = useMemo(() => stress.perturbations.map((p) => {
    const docs = BUILD_DOCS.map((d) => ({ ...d, text: PERTURB[p.name](d.text) }));
    const recs = docs.map((d) => buildRecord(d));
    return { ...p, f: scoreFields(docs, recs), t: scoreTables(docs, recs) };
  }), []);
  const base = stress.baseline;
  return (
    <section id="stress" className="card window reveal" data-title="stress.run — four format shifts">
      <p className="eyebrow">Perturbation stress set · new experiment, reported separately</p>
      <h2>The rules are <em>format-bound</em>: small surface changes erase most of the accuracy.</h2>
      <p className="sub">
        Each shift is a fixed text edit applied to all {BUILD_DOCS.length} Build documents with labels unchanged (<a href={blob('src/stress.py')}>stress.py</a>). Your browser re-runs the whole pipeline for every shift; the numbers below are computed here and the build checks them against <span className="mono">results_stress.json</span>. Unperturbed: {base.total_correct}/{base.total_fields} fields, {base.rows_correct}/{base.rows_total} rows.
      </p>
      <div className="bars" style={{ marginTop: 16 }}>
        {live.map((p) => (
          <div className="bar-row" key={p.name}>
            <div className="lab"><span>{p.description}</span><b>{p.f.correct}/{p.f.total} fields · {p.t.rowsCorrect}/{p.t.rowsTotal} rows</b></div>
            <div className="track">
              <div className="fill" style={{ width: pct(p.f.correct / p.f.total), background: p.f.correct / p.f.total < 0.5 ? 'var(--bad)' : 'var(--warn)' }} />
              <div className="ref" style={{ left: pct(base.total_correct / base.total_fields) }} title="Unperturbed accuracy" />
            </div>
            <div className="hint">Per field: {p.f.per.map((x) => `${x.field} ${x.correct}/${x.total}`).join(' · ')}</div>
          </div>
        ))}
      </div>
      <p className="hint" style={{ marginTop: 12 }}>Black tick: unperturbed accuracy. Try any shift on a single document in the extractor above. These shifts were authored by the same person who wrote the rules, so they are a floor on brittleness, not a sample of real-world variation.</p>
    </section>
  );
}

function Limits() {
  const items = [
    ['Synthetic, self-authored corpus', `All ${BUILD_DOCS.length + LEARN_DOCS.length} documents and the rules were written by the same author, with planted hard cases. The ${f4(build.field_summary.overall_accuracy)} accuracy measures the rules against their own format spec, not generalisation.`],
    ['No OCR, no language model', 'Input is plain text in OCR layout and extraction is rule-based. The project target names OCR and model-based extraction; neither runs here, and no result for either is claimed.'],
    [`Only ${deep.total_errors} errors`, `Capture rate, band accuracies and the threshold rest on ${deep.total_errors} errors in ${deep.total_fields} fields. A Wilson 95% interval on ${recQueue.errors_captured}/${recQueue.total_errors} runs from ${f4(recQueue.capture_wilson95[0])} to ${f4(recQueue.capture_wilson95[1])}.`],
    ['Threshold chosen in-sample', `The ${recQueue.rule} review rule is selected and scored on the same eval. There is no held-out split; the selection bias is named, not fixed.`],
    ['Route labels, not a model', `${deep.bands.length} discrete confidence values cannot be recalibrated meaningfully on this data; the band-accuracy baseline is in-sample only.`],
    ['Run location', `All levels ran on the ${RECORDED_WHERE} CPU, not the assigned fleet node.`],
  ];
  return (
    <section id="limits" className="card window reveal" data-title="limits.md — threats to validity">
      <p className="eyebrow">Limits and threats to validity</p>
      <h2>What this project does <em>not</em> show.</h2>
      <div className="grid2" style={{ marginTop: 16 }}>
        {items.map(([t, d]) => <div className="tile" key={t}><h3>{t}</h3><p className="hint" style={{ margin: '6px 0 0', fontSize: 13 }}>{d}</p></div>)}
      </div>
      <h3 style={{ marginTop: 20 }}>Next cycle from <a href={blob('PROPOSAL.md')}>PROPOSAL.md</a> (named, not built, not claimed)</h3>
      <ol className="backlog">{BACKLOG.map(([n, t]) => <li key={n}><span className="n">{n}</span>{t}</li>)}</ol>
    </section>
  );
}

function Reproduce() {
  const docs = [
    ['README.md', 'Abstract', 'Question, headline, verdict, reproduce'],
    ['PROPOSAL.md', 'Proposal', 'Scope, Build and Deep plans, next cycle (not locked)'],
    ['REPORT.md', 'Report', 'Results with evidence, each stage, self-review'],
    ['docs/decisions/0001-named-substitutions.md', 'Decisions', 'Substitutions, eval reuse, absence scoring'],
    ['CHANGELOG.md', 'Changelog', 'What changed and when'],
  ];
  return (
    <section id="reproduce" className="card window reveal" data-title="Terminal — reproduce">
      <p className="eyebrow">Reproduce it</p>
      <h2>Standard-library Python, deterministic output, <em>git stays clean</em>.</h2>
      <ol className="steps" style={{ marginTop: 16 }}>
        <li><span className="n">1</span><div><b>Run every stage</b><div className="hint"><code>python3 src/run_learn.py && python3 src/run_build.py && python3 src/run_deep.py && python3 src/stress.py && python3 src/export_texts.py</code></div></div></li>
        <li><span className="n">2</span><div><b>Run the tests</b><div className="hint"><code>python3 -m unittest discover -s tests -p "test_*.py"</code></div></div></li>
        <li><span className="n">3</span><div><b>Check nothing moved</b><div className="hint"><code>git diff --exit-code -- results/</code></div></div></li>
      </ol>
      <div className="docs" style={{ marginTop: 20 }}>
        {docs.map(([p, t, d]) => <a key={p} href={blob(p)}><b>{t}</b><small>{d}</small></a>)}
        <a href={`${REPO}/releases`}><b>Releases</b><small>Tagged versions</small></a>
      </div>
    </section>
  );
}

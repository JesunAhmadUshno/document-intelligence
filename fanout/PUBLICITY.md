# PUBLICITY: document-intelligence (P16)

Publicity log under the documentation and publishing standard,
Section 7. Every finished level produced its written fan-out set.
Drafts are prepared by the loop. Actual social posting follows
the standing platform rules and gates. The loop itself never posts
to social.

Project state: v1.0, Learn, Build, and compressed Deep done
2026-11-05, 52 tests passing plus the scaffold smoke test.

Paths in this log and in the fan-out drafts predate the 2026-11-08
restructure to the portfolio standard v2: the level READMEs are now
REPORT.md, SPEC.md, the level specs, NOVELTY.md, DOSSIER.md and
ROADMAP.md are now PROPOSAL.md, the code is in src/ and the results
files are in results/. Self-assigned grades are kept off public pages.

## Fan-out (moved from the README, 2026-11-08)

Written fan-out set for v1.0 (2026-11-05), in fanout/. Every
piece states plainly that there is no OCR and no LLM in the
shipped project, that every document is synthetic plain text,
and that the confidence values are route labels, not
probabilities. Channel outcomes are logged below in this file.

- Blog post: fanout/blog-post.md
- Tutorial: fanout/tutorial.md
- Website page copy: fanout/website-page.md
- LinkedIn post draft (DRAFT NOT POSTED): fanout/linkedin-post.md
- Paper candidate: fanout/paper-candidate.md
- Release notes: fanout/release-notes.md

## Actions polish pack (2026-11-05)

Applied through a pull request on 2026-11-05, following the Actions
polish pack standard. The pack adds: CI on a Python 3.11 and 3.12
matrix with a ruff lint step (the pre-existing CI step preserved:
scaffold smoke test; plus per-level test and runner steps for Learn,
Build, and Deep, following the proven pack pattern), CodeQL
scanning, Dependabot for pip and GitHub Actions, a release workflow
that attaches a source tarball named
document-intelligence-<tag>.tar.gz to v* tag releases, Labeler,
Greetings (snake_case inputs for actions/first-interaction@v3:
repo_token, issue_message, pr_message), Stale in comment-only mode
(days-before-close: -1, never closes), and a docs summary page at
docs/index.md for GitHub Pages. Ruff scope is recorded in
ruff.toml (E, F, I, line-length 120). Ruff fixes in this pull
request were style only: 6 initial errors, all import order or
format (I001), fixed by ruff fix output with no change to behaviour,
any imported name, or any string value. All three results files
(results_learn.json, results_build.json, results_deep.json)
stayed byte-identical across the runners on Python 3.12. The new
3.11 matrix leg exposed a real cross-version float boundary in
the Deep tests: the exact ECE (0.11875) and exact mean confidence
(0.86875) sit on a 4-place rounding boundary, and Python 3.11
naive float summation rounds them one way while Python 3.12
Neumaier summation rounds them the other (0.1187 and 0.8688 are
the published 3.12 values). Two Deep test assertions were changed
from exact equality to a 3-place tolerance for those two values
only; no production code and no published result changed.
requirements.txt records
the standard-library-only fact so Dependabot pip has a manifest
to watch.

| Channel | Outcome on 2026-11-05 |
| --- | --- |
| GitHub Pages | Docs page added at docs/index.md in this pull request. Pages enablement and live build status are verified after merge and recorded in the batch ledger; no live claim is made in this file before that check. |
| PyPI publishing | Held: needs a PyPI token, a new credential. Jesun's tap only. Not set up. |
| Social channels (LinkedIn, X, Facebook, Instagram, Threads) | Held: no posts made. The loop never posts to social; Threads waits for Jesun's tap per post under the standing gates. |

## v1.0 fan-out set (2026-11-05)

Written fan-out set prepared in this cycle, in fanout/. Every
piece states plainly that there is no OCR and no LLM in the
shipped project, that every document is synthetic plain text,
and that the confidence values are route labels, not
probabilities. Every number is sourced from the repo files
(README.md, DOSSIER.md, the three level READMEs, and the three
results files). Tutorial commands were verified by running them;
the full suite (52 tests plus the scaffold smoke test) passes
and all three results files stayed byte-identical across the
runners on Python 3.12.

Jev claim_check on the blog main results claim (extracted byte
exact from fanout/blog-post.md by script): model jev-1.13.0,
1,340 input tokens, question id supported, noul 0.83, route
REVIEW (claim_check bands: clear at 0.85 or above, block at
0.10 or below, review between). Not blocked, so the claim ships
in its gated form. Spec and results are in the goal
hidden_files (jev-p16-fanout-claim-spec-2026-11-05.json and
jev-p16-fanout-claim-results-2026-11-05.json).

| Channel | Piece | Outcome on 2026-11-05 |
| --- | --- | --- |
| GitHub release v0.1 | Learn release | Live: https://github.com/JesunAhmadUshno/document-intelligence/releases/tag/v0.1 |
| GitHub release v0.5 | Build release | Live: https://github.com/JesunAhmadUshno/document-intelligence/releases/tag/v0.5 |
| GitHub release v1.0 | Learn, Build, compressed Deep release | Live: https://github.com/JesunAhmadUshno/document-intelligence/releases/tag/v1.0 |
| GitHub Pages | Docs page | Live and built: https://jesunahmadushno.github.io/document-intelligence/ (enabled after the polish pack merge, legacy build from main /docs, build status verified built on 2026-11-05). |
| Repo (blog) | Blog post draft | fanout/blog-post.md, repo draft. Not posted to any blog platform. |
| Repo (tutorial) | Tutorial draft | fanout/tutorial.md, repo draft. Every command verified by running it in this cycle. |
| Repo (website) | Website page copy draft | fanout/website-page.md, copy only. No website was changed by this file. |
| LinkedIn | Post draft | fanout/linkedin-post.md, DRAFT NOT POSTED. Held: posting follows the standing platform rules; the link is carried as the first-comment line in the draft, per the LinkedIn rule. |
| Paper | Candidate brief | fanout/paper-candidate.md, a confidence calibration note. Submission is Jesun's tap; nothing submitted, no venue contacted. |
| Repo (release notes) | Release notes | fanout/release-notes.md, covering v0.1, v0.5, and v1.0 with measured results and release links verified with gh release list. |
| X | Social post | Held: no post made. The loop never posts to social; drafts only under the standing platform rules. |
| Facebook | Social post | Held: no post made. Standing Facebook rule applies (no link in body or comments, keyword call to action by DM) and the loop never posts to social. |
| Instagram | Social post | Held: no post made. Standing Instagram rule applies (link in bio) and the loop never posts to social. |
| Threads | Social post | Held: awaiting Jesun's tap. Every Threads post needs his one-tap pre-approval, hash-locked on exact text and media. |
| Video | 3D playbook video | Held: flagship video production runs through the January engine queue. No video produced in this cycle. |
| Book | Book chapter | Held: chapter drafted from finished projects under the journey publishing plan; no chapter file is claimed in this cycle. |

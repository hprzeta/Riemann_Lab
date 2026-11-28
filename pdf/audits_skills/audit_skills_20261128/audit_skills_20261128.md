# Skills audit report — 2026-11-28

Project: SKILLS ZETA · executor: Claude Code on PC1 · branch: Riemann_Lab_IA (head 4830738).
Nothing was committed or pushed.

## 1. Starting state

- `.claude/skills/` is tracked (rule `!.claude/skills/**`, `.gitignore` line 30).
- Repo had 15 skills: 13 `riemann-*` + `grilling` + `grill-me`. Account (inventory 28/11): same 13 + grilling; `grill-me` disabled.
- `skills_export/` did not exist (only an old export in `pdf/archive/skills_export_202611141924/`).
  Decision: derived export, if needed, is generated under the audit folder, never edited by hand.
- `grill-me` stays in the repo (decision of hprzeta) although disabled in the account.
- superpowers is not in `installed_plugins.json`: it comes from the account-synced plugin folder, v7.0.2, MIT.

## 2. Five new skills (v1.0, 2026-11-28)

| Skill | Lines | Description chars | Trigger test (by reading) |
|---|---|---|---|
| zeta-token-hygiene | 66 | 590 | 3/3 yes, 2/2 no |
| skill-install-audit | 47 | 565 | 3/3, 2/2 |
| zeta-video-digest | 47 | 582 | 3/3, 2/2 |
| riemann-explicit-formula | 49 | 522 | 3/3, 2/2 |
| riemann-viz | 42 | 559 | 3/3, 2/2 |

Limit: judged by reading, no automated eval. Details: `tests_declenchement_20261128.md`.
Approved by hprzeta ("go", phase 3).

## 3. superpowers decision

- **Mode (a)**: plugin already present, nothing copied. Version 7.0.2 recorded in the manifest with SHA-256 of 4 retained skills (systematic-debugging, test-driven-development, verification-before-completion, writing-skills).
- `using-superpowers` excluded by **option A**: one rule added to project `CLAUDE.md` (backup `CLAUDE.md.bak-20261128`, local, ignored by git). The hook text is still injected; the rule says user stops take precedence. Plugin files untouched.
- `brainstorming`, `writing-plans`: only on explicit request.

## 4. Audit result (skill-install-audit on superpowers)

Nothing malicious found in what was read (hooks, wrapper, package.json, 4 skills, no invisible characters, no network/exec/secret access). Open: no pinnable commit (no `.git`); 3 helper scripts not read line by line (`find-polluter.sh`, `condition-based-waiting-example.ts`, `render-graphs.js`); `tests/`, `scripts/` and other skills not audited. Full report: `audit_superpowers_20261128.md`.

## 5. Alignment check

`.claude/skills/MANIFEST.md` (20 repo skills + 4 plugin skills) and `scripts/skills_manifest_check.sh`
(read-only, no network, non-zero exit on drift). Real run: 20 repo skills, 4 plugin skills, **0 drift**, exit 0.
Drift test on a throw-away copy: a modified skill → DÉRIVE, a removed skill → MANQUANT, exit 1;
a whitespace-only change is correctly ignored. The "account" column is still "à renseigner" for every skill
(only hprzeta can fill it after the claude.ai import).

## 6. Secrets check

Value-based check (project's sensitive-values file, positive control passed) on all files to commit:
no match. Generic patterns (IPv4, MAC, token prefixes, home path, e-mail): no match.

## 7. Open points

1. Account column of the manifest: to fill by hand after import into claude.ai.
2. Account names `wireguard-diagnostic` / `zeta-diagnostic` (no prefix) vs repo `riemann-*`: confirm.
3. `grill-me`: kept in repo, disabled in account: confirm intended.
4. Explicit-formula skill: which zero file is the reference (V16 5M run lost 18/08; reference described as V13+97): confirm in Handoff before first run. Davenport ch. 17 error behaviour to verify in the text.
5. Idea-box last number not found by the skill; to give when first used.
6. 3 superpowers helper scripts to read before use; no commit pin.
7. `CLAUDE.md` is modified (tracked): its change invalidates the prompt cache once; also check the 4-branch exception rule (CLAUDE.md propagates to the 4 branches).
8. Token-hygiene skill proposes (does not run) the 50 % / 70 % commits of CLAUDE.md, to respect "no commit without go".

---
Mis à jour le 2026-11-28 · 52 lignes

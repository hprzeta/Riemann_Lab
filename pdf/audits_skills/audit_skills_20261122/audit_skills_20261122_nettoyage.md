# Skills audit — D22 and cleanup of the leftovers of the grill-me adoption (22/11/2026, evening)

> Project: SKILLS ZETA · Machine: PC1 · Prompt: `PROMPT_D22_NETTOYAGE_20261122` · Decisions D22, R25; R18 dropped (option B followed, fresh upstream clone = reference).
> Status: steps 0 to 6 done. Commit `ebdc57a` pushed. 14 files and 1 folder deleted after « go suppression »; codeburn moved, not deleted.

## 1. Summary

| Item | Result |
|---|---|
| D22 | rule « non vérifié » added to § 4 of `claude/MODELE_INSTRUCTIONS_PROJET.md` (95 lines), commit `ebdc57a` on `Riemann_Lab_IA`, pushed (`69332e7..ebdc57a`) |
| codeburn | **moved** (option a, as TEL-D16 planned) from the sandbox to `~/outils/codeburn` (229 MB, commit `c08d761`, built); `--help` works offline |
| Deleted | 13 `.bak-20261122*` files, 1 stale git lock file (14 files, 452,900 bytes), then the sandbox folder (44 MB, 734 files) and its empty parent folder |
| Kept | `claude/MODELE_INSTRUCTIONS_PROJET.md.bak-202611221802` and `HANDOFF_SKILLS_20261122.md.bak-202611221805` (both made in this step, next cleanup) and 4 `.bak` of the site session (out of scope) |

## 2. Validation table

| Check | Result | State |
|---|---|---|
| Before: branch `Riemann_Lab_IA`, target file clean, diff of the model = exactly 1 line + footer | as expected | 🟢 |
| None of the files to delete is tracked by git (`ls-files --error-unmatch`) | 13 of 13 untracked | 🟢 |
| Recoverability of the backups before deletion | `CLAUDE.md`, `AGENTS.md`, `ETAT_SKILLS_ZETA.md` identical to commit `43b6b48`; `STACK.md`, `JOURNAL.md` identical to the wiki commit `e4701ef`; model v3.1 identical to the copy in `cloture_skills_20261114/` | 🟢 |
| Pre-push audit of the added line | empty; positive control 1/1 | 🟢 |
| Push without `--force`, simple fast-forward | `69332e7..ebdc57a` | 🟢 |
| Deletion limited to the listed paths (each re-checked: regular file, expected name, outside `.claude/skills`, `pdf/site`, `scripts`) | 14 deleted, 0 refused | 🟢 |
| After: old paths all gone; inventory re-run | 0 left; only the expected `.bak` remain (5 at that time, plus the handoff backup made afterwards) | 🟢 |
| `~/outils/codeburn --help` offline under `strace` | rc 0, 0 IP `connect`, `~/.config/codeburn` and `~/.cache/codeburn` still absent | 🟢 |
| Online page of `claude/MODELE_INSTRUCTIONS_PROJET.md` on `Riemann_Lab_IA` | line 30 (D22) visible, 95 lines, commit `ebdc57a` | 🟢 |
| Four `.bak` of the site session (3 in `pdf/site/maj_site_20261122/`, 1 in `scripts/`) | excluded from the deletion list, kept | 🟡 |
| Five intermediate drafts of the adoption report/handoff and the raw `openat` strace trace | deleted, no copy (final report committed; short `connect` trace kept in `captures/`) | 🟡 |

No 🔴.

## 3. Deviations from the prompt

1. **`~/outils/` and `~/outils/codeburn/` did not exist** (already noted in the adoption report): codeburn only existed in the sandbox. Option (a) was chosen by hprzeta: `mkdir -p ~/outils && mv`, same disk, nothing copied or removed.
2. **Two locations outside the prompt's perimeter** held `.bak-20261122` files: `pdf/site/maj_site_20261122/` and `scripts/` (from the site session, 11:50 to 13:30). They were excluded from the list; 4 paths kept.
3. The sandbox had a symbolic link (`AGENTS.md -> CLAUDE.md` inside the upstream clone, target inside the sandbox); `rm -rf` removes links, not targets.
4. The npm cache was inside the sandbox folder (33 MB), not outside, so it was removed with it.

## 4. What was deleted or moved

| Item | Size | Action |
|---|---|---|
| `AGENTS.md.bak-202611221641`, `CLAUDE.md.bak-202611221641` (repository root) | 20 KB | deleted |
| `JOURNAL.md.bak-202611221642`, `STACK.md.bak-202611221642` (`pdf/archive/`) | 375 KB | deleted |
| 6 files in `pdf/audits_skills/` (ETAT backup, 3 report drafts, 2 handoff drafts) | 40 KB | deleted |
| 3 files in `src/ia/prompts/` (model v3.1 backup, 2 adoption backups) | 17 KB | deleted |
| `.git/index.lock.perime-20261122-1749` (stale, empty) | 0 | deleted |
| Sandbox folder (npm cache 33 MB, cache 5.2 MB, upstream clone 2.2 MB, raw strace trace 3.1 MB, test copy, 2 JSON reports, small witnesses) | 44 MB, 734 files | deleted, then the empty parent folder |
| codeburn clone (built, `node_modules` included) | 229 MB | **moved** to `~/outils/codeburn` |

Total freed: about 44.4 MB (the 229 MB of codeburn were moved, not freed). The disk shows 20 GB available.

## 5. Timestamped changes (22/11/2026)

| Time | Change |
|---|---|
| before 18:02 | zip unpacked; before-state; inventory; codeburn moved to `~/outils/codeburn`; D22 file replaced (backup `.bak-202611221802`) |
| 18:02:45 | commit `ebdc57a` (after « go commit »), pushed after « go push » |
| 18:03:36 | exact deletion list written and shown |
| about 18:04 | 14 files deleted, sandbox folder and its parent removed (after « go suppression »); after-state, offline `--help`, capture |

## 6. Remaining and next

- To clean at the next cleanup: `claude/MODELE_INSTRUCTIONS_PROJET.md.bak-202611221802`, `HANDOFF_SKILLS_20261122.md.bak-202611221805` (identical to the handoff committed in `69332e7`), and the 4 `.bak` of the site session (decision for the SITE project).
- `~/outils/codeburn`: only `report` and `--help`, offline, with `CODEBURN_PRICING_SNAPSHOT_ONLY=1`, `CODEBURN_FX_NO_FETCH=1`, a dedicated `HOME`. Never `quota`, `sync`, `share`, `web`, `mcp`, `menubar`, `guard`, `optimize`, `update`.
- Still open for hprzeta (from the adoption report): `/skills` check in a new session, `/grill-me` test in the account (R21). R18 is dropped.
- Not committed: this report and the handoff change (decision of hprzeta).

---
<sub>audit_skills_20261122_nettoyage.md · SKILLS ZETA · Updated 2026-11-22 · 71 lines</sub>

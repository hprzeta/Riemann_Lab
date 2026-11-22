# Skills audit — adoption of `grill-me` + `grilling` (22/11/2026)

> Project: SKILLS ZETA · Machine: PC1 · Prompt: `PROMPT_ADOPTION_GRILL_ME_20261122` (based on `PROMPT_INSTALL_SKILL_MODELE.md` v3.2) · Decisions D17 to D20, audit TEL-D10 / TEL-D15.
> Status: steps 0 to 8 done. The 3 new skills and the 4 re-imported skills are **confirmed in the account** (sync of 17:43:33). **R9 is closed for content**: 8 skills byte-identical, 7 differ only by the front-matter layout, 0 outdated. Left for hprzeta: `/skills` check and the `/grill-me` test (section 8).

## 1. Summary

| Item | Result |
|---|---|
| Third-party skills added to the repository | `grilling`, `grill-me` (MIT, © 2026 Matt Pocock), byte-identical to upstream, with `LICENSE` and `SOURCE.md` |
| Skills in `.claude/skills/` | 13 → **15**, on the 4 branches |
| Rule D20 | one bullet added to `CLAUDE.md` and `AGENTS.md` |
| Wiki | `STACK.md` (2 rows + note) and `JOURNAL.md` (entry at the top) updated; site (`docs/`) untouched (D18) |
| Account zips | 3 zips ready in `A_DEPOSER/zips_compte/` |
| Not yet done | test in the account (R21), check in a new Claude Code session (`/skills`) |

## 2. Validation table

| Check | Result | State |
|---|---|---|
| Before: branch, clean target files, 13 skills, no stray copy in `~/.claude/skills/` | as expected | 🟢 |
| Before: files not ignored by `.gitignore` on the 4 branches (only `.bak` ignored) | as expected | 🟢 |
| Before: `CLAUDE.md`, `AGENTS.md`, `.claude/skills/` identical on the 3 other branches | 0 line of diff | 🟢 |
| SHA-256 of the 5 expected files vs sandbox copy vs fresh upstream clone | 0 mismatch (after the prompt typo fix, see 3) | 🟢 |
| `diff -r` sandbox copy / upstream (both skills) | empty | 🟢 |
| Secrets scan by values (v3.2 regex), 3 folders, with positive control | 0 hit; control 4/4 | 🟢 |
| Descriptions ≤ 1 024 characters | 51, 152, 530 | 🟢 |
| Repository `SKILL.md` and `openai.yaml` SHA-256 = expected values | 6/6 identical | 🟢 |
| Pre-push audit on the added lines of C1, C2, C3, W1 | empty; no forbidden path committed | 🟢 |
| Pushes without `--force`, cherry-picks without conflict | 4/4 branches + wiki | 🟢 |
| After: 0 diff between `Riemann_Lab_IA` and the 3 other branches; 15 skills on each | confirmed on `origin` | 🟢 |
| Zipped `SKILL.md` SHA-256 = repository = commit (3 zips, 0 `.bak` inside) | identical | 🟢 |
| `POUR_SKILLS_ZETA_grill_me_20261122.md` and `~/outils/skills_tiers/` | absent: procedure deviation (see 3) | 🟡 |
| Fresh Claude Code session, `/skills`: 15 « project » | not done in this session | 🟡 |
| Account import (R19): visible in `~/.claude/skills/synced/` | **confirmed** at the 17:33:32 sync (28 skills): the 3 new skills present, SHA-256 identical to the repository, `grill-me` not refused (first sync, 17:23:31, predated the import) | 🟢 |
| Account vs repository SHA-256 (R9), 15 skills, sync of 17:43:33 | 8 byte-identical, 7 format-only (body, name, other keys and normalized description identical), 0 outdated, 0 absent | 🟢 |
| No standalone `grill-me`, `grilling` or `riemann-*` in `~/.claude/skills/` | none (only `claude-statusbar` and `synced`) | 🟢 |
| Test `/grill-me` in the account (R21) | pending | 🟡 |

No 🔴.

## 3. Deviations from the procedure

1. **`POUR_SKILLS_ZETA_grill_me_20261122.md` absent** (searched in the three folders of step 3a) and **`~/outils/skills_tiers/` absent**. With hprzeta's agreement (option B), the sandbox copy of the TELANDROID audit (`essai_grill_me`, the copy hprzeta tested) replaced it. The step-3d table therefore has 3 real columns instead of 4. R18 stays open.
2. **Typo in the prompt**: the expected SHA-256 of `grilling/SKILL.md` had 63 characters (one `3` missing). The real value, 64 characters, was confirmed by hprzeta and by two independent measures. Fixed in the prompt and in `grilling_SOURCE.md` (backups `.bak-202611221640`). claude.ai should fix its own source.
3. Foreign uncommitted changes: 69 instead of ~217 (no impact: no `git add -A`, every file indexed by path).
4. `riemann-wireguard-diagnostic` description: 530 characters, not 532.
5. A stale, empty `.git/index.lock` (created 11:49, no git process) blocked the first commit. It was **moved**, not deleted, to `.git/index.lock.perime-20261122-1749`.
6. `JOURNAL.md`: the entry was inserted **at the top**, following the file's own rule (« le plus récent est en haut »), not at the end as the prompt said. Two sentences of the provided text were reworded (hash cross-check wording; imports marked « à importer »).
7. `AGENTS.md` had no date/line-count footer: one was added.

## 4. SHA-256 table (step 3, first 16 characters)

| File | Expected | `POUR_SKILLS_ZETA` | Sandbox copy | Fresh clone | Repository (IA) |
|---|---|---|---|---|---|
| `grill-me/SKILL.md` | `caaf8b8de1684f96` | absent | `caaf8b8de1684f96` | `caaf8b8de1684f96` | `caaf8b8de1684f96` |
| `grill-me/agents/openai.yaml` | `c061e39c3e0f9d86` | absent | `c061e39c3e0f9d86` | `c061e39c3e0f9d86` | `c061e39c3e0f9d86` |
| `grilling/SKILL.md` | `a146842ed93ca43d` | absent | `a146842ed93ca43d` | `a146842ed93ca43d` | `a146842ed93ca43d` |
| `grilling/agents/openai.yaml` | `1411d7df7d99b7e6` | absent | `1411d7df7d99b7e6` | `1411d7df7d99b7e6` | `1411d7df7d99b7e6` |
| `LICENSE` | `0e7ac423bf2c6e22` | absent | n/a | `0e7ac423bf2c6e22` | `0e7ac423bf2c6e22` |
| `riemann-wireguard-diagnostic/SKILL.md` | n/a | n/a | n/a | n/a | `5ec31d93ad0de7af` (= zip) |

Upstream: `mattpocock/skills`, commit `abeeaf95660ba9e8b7c753eb38f441ca707a8823` (19/11/2026), MIT.

## 5. Commits per branch

| Branch | C1 (skills) | C2 (rule D20) | C3 (ETAT) | Head |
|---|---|---|---|---|
| `Riemann_Lab_IA` | `c25f109` | `5129e36` | `cf24144` | `cf24144` |
| `main` | `cd7ac88` | `f6d8eae` | not applied (IA only) | `f6d8eae` |
| `Riemann_Lab_C` | `6558ef8` | `8580522` | not applied (IA only) | `8580522` |
| `Riemann_Lab_Test` | `7b975ab` | `a37e8bb` | not applied (IA only) | `a37e8bb` |
| Wiki `master` | W1 `2e82ee0` (`STACK.md`, `JOURNAL.md`) | | | `2e82ee0` |

Cherry-picks done with `-x` in temporary worktrees (removed). This report itself is not committed.

## 6. Timestamped changes (22/11/2026)

| Time | Change |
|---|---|
| 16:29 | Prompt zip unpacked; model v3.2 installed in `src/ia/prompts/` (v3.1 backed up) |
| 16:29 to 16:40 | Steps 1 to 3: audit folder, before-state, captures, SHA-256 comparison; typo fixed (16:40) |
| 16:41 | Copy of the two skills into `.claude/skills/`; D20 bullet; ETAT replaced (backups `.bak-202611221641`) |
| 16:42 | Wiki: `STACK.md` and `JOURNAL.md` edited (backups in `pdf/archive/`) |
| 17:14:00 to 17:14:07 | Commits C1, C2, C3 and W1, after « go commit » |
| 17:15 to 17:16 (approx.) | Pushes: IA and wiki, then `main`, `Riemann_Lab_C`, `Riemann_Lab_Test` after « go push » |
| 17:16 | 3 zips created, checked, after-state and captures; temporary clone removed |

## 7. Step 8 results (after the imports)

**Sync history of the local copy of the account** (`~/.claude/skills/synced/`): 17:23:31 (25 skills, import not yet visible), 17:33:32 (28 skills, the 3 new skills present), **17:43:33 (28 skills, after the re-import of the 4 outdated skills)**. The final comparison below uses the last one.

| Group (15 skills) | Skills | Finding |
|---|---|---|
| Byte-identical (🟢), 8 | `grill-me`, `grilling`, `riemann-wireguard-diagnostic`, `riemann-bastion-hardening`, `riemann-proof-status`, `riemann-site-check`, `riemann-site-update`, `riemann-zeta-diagnostic` | same SHA-256 as the repository |
| Format only (🟡), 7 | `riemann-agent-bridge`, `riemann-code-review`, `riemann-lab`, `riemann-literature-scout`, `riemann-phase-c-illinois`, `riemann-security-review`, `riemann-statistics-gue` | body identical, `name` and other keys identical, description identical once whitespace is normalized; the account rewrites the multi-line description (9 to 12 front-matter lines) on one line, so the bytes differ |
| Outdated in the account, 0 | none | the 4 previously outdated copies (`riemann-bastion-hardening`, `riemann-agent-bridge`, `riemann-code-review`, `riemann-statistics-gue`) are now up to date: `riemann-bastion-hardening` byte-identical, the 3 others format only |
| Absent, 0 | none | |

`~/.claude/skills/` holds no standalone copy of `grill-me`, `grilling` or `riemann-*` (only `claude-statusbar` and `synced`).

**Reading of R9:** the content of the 15 skills is aligned between repository and account. Exact byte equality is only possible for 8: the account normalizes the front matter of the other 7 (this was already the case before this adoption). It is not a drift of content.

## 8. Next actions

1. hprzeta: open a new Claude Code session from the repository and check `/skills` (15 « project », including `grill-me` and `grilling`). I could not verify this from the current session.
2. Test `/grill-me` in a new claude.ai conversation (SKILLS ZETA): is `grilling` loaded, are sub-agents launched, how many questions per round (R21).
3. Open items: R18 (`POUR_SKILLS_ZETA_grill_me_20261122.md` absent), R21 (account test), `/skills` check. R19 and R9 (content) are closed.

---
<sub>audit_skills_20261122_adoption.md · SKILLS ZETA · Updated 2026-11-22 · 111 lines</sub>

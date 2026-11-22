# Source — `grill-me` (third-party skill)

| Field | Value |
|---|---|
| Upstream | https://github.com/mattpocock/skills — `skills/productivity/grill-me/` |
| Commit | `abeeaf95660ba9e8b7c753eb38f441ca707a8823` (2026-11-19) |
| Licence | MIT, © 2026 Matt Pocock — full text in `LICENSE` (this folder) |
| Copied into Riemann_Lab | 2026-11-22, unchanged (decisions D17, D20; audit TEL-D10, TEL-D15) |
| `SKILL.md` SHA-256 | `caaf8b8de1684f96e26b28f3c29189db5c89cce4b73e1c93d86164f66ef88637` |
| `agents/openai.yaml` SHA-256 | `c061e39c3e0f9d865fb1b97556d485704af2a8a58f4b8221a8917a5c2074a32b` |
| Depends on | `grilling` (must be installed alongside) |
| Invocation | manual only (`disable-model-invocation: true`) : `/grill-me` |

## Rules for this copy

- Never edit `SKILL.md` or `agents/openai.yaml`: the copy must stay byte-identical to upstream.
- Project adaptation lives outside the skill: `CLAUDE.md` / `AGENTS.md` rule D20 (any recommended answer with a figure is marked « non vérifiée »).
- Update = new sandbox audit, then replace the folder and update this file.

---
<sub>SOURCE.md · grill-me · Riemann_Lab · Updated 2026-11-22 · 21 lines</sub>

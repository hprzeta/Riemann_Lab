# Audit — superpowers v7.0.2 (read-only, 2026-11-28)

Skill used: `skill-install-audit` v1.0. Nothing was executed, installed or modified.

## Scope and method

- Object: plugin `superpowers` v7.0.2, MIT, author Jesse Vincent, source github.com/obra/superpowers
  (from `plugin.json`). It sits in the account-synced plugin folder of PC1, not in
  `installed_plugins.json`. It was read **in place** (already present), not cloned.
- No `.git` folder: **no commit can be pinned**. Only the version number identifies it.
- Files read in full: `hooks/hooks.json`, `hooks/run-hook.cmd`, `hooks/session-start`,
  `package.json`, `index.js`, `LICENSE` (head). Pattern search (network, exec, secrets,
  hidden instructions, zero-width characters) on the hooks and on the four candidate skills.
- Not audited: `tests/`, `scripts/`, `.opencode`, `.pi`, `.hermes-plugin`, other platforms'
  manifests (238 files total), and all skills other than the four candidates and `using-superpowers`.

## Verdicts

| Point | Verdict | Evidence |
|---|---|---|
| Hooks declared | ⚠️ one | `hooks/hooks.json`: `SessionStart`, matcher `startup\|clear\|compact`, runs `run-hook.cmd session-start`, `async: false`. No PreToolUse/PostToolUse. |
| Hook behaviour | ✅ | `hooks/session-start`: reads `skills/using-superpowers/SKILL.md`, escapes it, prints JSON `additionalContext`. No network, no write, no subprocess. |
| Wrapper `run-hook.cmd` | ✅ | Unix half: picks `bash`/`zsh`, then `exec "$shell" "${SCRIPT_DIR}/${SCRIPT_NAME}"`. Windows half only looks for `bash.exe`; irrelevant on PC1. |
| Network calls in hooks | ✅ | grep for curl/wget/npx/nc/eval/base64 in the two hook files: no match. |
| Secrets access | ✅ | No reference to `~/.ssh`, `.env`, TOKEN, API_KEY in the hooks. |
| Writes outside plugin folder | ✅ | None in the hooks. |
| MCP servers declared | ✅ | No `.mcp.json`, no `mcpServers` found. |
| Hidden instructions | ✅ | No zero-width/invisible characters in the 4 candidate skills, `using-superpowers`, hooks. No "ignore previous instructions" pattern. |
| Network/exec in the 4 candidate skills | ✅ | Only documentation links (agentskills.io, platform.claude.com). |
| Helper scripts in candidates | ⚠️ | `systematic-debugging/find-polluter.sh`, `condition-based-waiting-example.ts`, `writing-skills/render-graphs.js`: **not read line by line**. They are only run if an agent decides to; read them before first use. |
| License | ✅ | MIT, © 2025 Jesse Vincent. Kept upstream if copied. |
| Pinned source | ❌ | No commit hash available (no `.git`). |
| Size | ✅ | 238 files, no file over 100 kB, no binary found by `file`. |
| Behavioural risk (not a security one) | ⚠️ | The hook injects `using-superpowers` into **every** session start/clear/compact: it orders invoking a skill before ANY answer, "even 1 % chance". Costs tokens and can conflict with the project's STOP points. |

Conclusion: **nothing malicious found in what was read** (not a guarantee of safety:
unread files and obfuscation cannot be excluded). Recommendation: keep the 4 skills
(systematic-debugging, test-driven-development, verification-before-completion,
writing-skills); neutralise `using-superpowers`.

## Excluding `using-superpowers` — options (nothing modified)

| Option | Effect | Drawback |
|---|---|---|
| A. Leave the plugin, add a line to project `CLAUDE.md`: using-superpowers is disabled, user stops take precedence | Costs no change to the plugin. The skill itself says user instructions override skills. | The text is still injected (tokens). `CLAUDE.md` change = action for hprzeta; invalidates prompt cache once. |
| B. Edit `hooks/session-start` in the synced folder | Stops the injection. | Folder is managed by the account sync: edit likely overwritten; modifies third-party code. Not recommended. |
| C. Disable the plugin in the project, vendor the 4 skills in `.claude/skills/` (mode b) | Full control, no hook, 4 skills only. | Copy to maintain; pinned commit unavailable here: record version 7.0.2 + file SHA-256 in MANIFEST. Needs "go" after audit of the 3 helper scripts. |

Recommended: **A now** (cheapest, reversible), **C** if token cost of the injection matters.
Decision belongs to hprzeta; mode (a) vs (b) is not yet fixed.

## Open points

1. Read the 3 helper scripts before use.
2. No commit pin: record version + SHA-256 of the four SKILL.md in MANIFEST.
3. Account vs PC1: both v7.0.2 per metadata, but the account copy was not diffed here.

---
Mis à jour le 2026-11-28 · 62 lignes

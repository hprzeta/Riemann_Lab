# Trigger tests — 5 new skills (draft, 2026-11-28)

Method: 3 queries that must trigger, 2 that must not. Result = manual reading of each
`description` against the query (judgement, NOT a measured trigger rate). The 5 skills
do appear in the session skill list, which confirms the frontmatter is parsed.

## zeta-token-hygiene
- YES: "la session devient trop longue et coûte cher, que faire ?"
- YES: "on approche de 70 % de contexte, prépare une passation"
- YES: "comment lire ce gros log sans consommer trop de tokens ?"
- NO: "calcule les zéros de zêta entre T=1000 et T=1100"
- NO: "pourquoi Z_fast donne un faux positif à t=300 ?"
Result: 3/3 trigger, 2/2 do not (by reading).

## skill-install-audit
- YES: "je veux installer ce plugin trouvé sur GitHub, il est sûr ?"
- YES: "audite le hook SessionStart de superpowers avant qu'on le copie"
- YES: "ajoute ce serveur MCP tiers"
- NO: "relis illinois_mpfr.c pour des bugs"
- NO: "vérifie que mon .gitignore ne laisse pas passer de token"  (-> riemann-security-review)
Result: 3/3, 2/2 (by reading). Ambiguity: the last NO is close; the description says "tiers".

## zeta-video-digest
- YES: "voici une vidéo YouTube sur une preuve de RH, fais-en une fiche d'idée"
- YES: "classe ces 4 captures TikTok dans la boîte à idées"
- YES: "traduis ce transcript et donne les affirmations avec horodatage"
- NO: "résume cet article arXiv sur les zéros de zêta"
- NO: "trace Z(t) entre 0 et 50"
Result: 3/3, 2/2 (by reading).

## riemann-explicit-formula
- YES: "reconstruis psi(x) avec les zéros du fichier 5M"
- YES: "teste la formule de von Mangoldt, erreur en fonction de T"
- YES: "compare R(x) de Riemann à pi(x)"
- NO: "calcule les 1000 premiers zéros"
- NO: "la formule explicite prouve-t-elle HR ?"  (-> riemann-proof-status; the skill must say no conclusion)
Result: 3/3, 2/2 (by reading). The last NO may co-trigger: acceptable, the skill states "no conclusion on HR".

## riemann-viz
- YES: "trace Z(t) de Hardy avec les zéros marqués entre 100 et 200"
- YES: "fais la coloration de domaine de xi"
- YES: "histogramme des écarts normalisés en PNG et PDF"
- NO: "calcule les écarts GUE et le test de Kolmogorov-Smirnov" (-> riemann-statistics-gue, no figure asked)
- NO: "fais un graphique des ventes mensuelles"
Result: 3/3, 2/2 (by reading).

Limit: no automated eval (skill-creator run_eval) was run. To be tested for real after approval.

---
Mis à jour le 2026-11-28 · 47 lignes

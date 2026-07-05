# Archive — Fichiers supprimés du projet Claude
> Date : 29 mai 2026  
> Raison : libérer de la place pour les 9 PDF de cadrage  
> Tous ces fichiers restent sur GitHub et sur la machine Linux

---

## Scripts Python — Versions obsolètes

Ces fichiers sont **supersédés** par v3/v4/v5 ou étaient des prototypes de test.

| Fichier | Raison de suppression |
|---|---|
| `compute_zeros_v1.py` | Supersédé par v3/v4/v5 |
| `compute_zeros_v2.py` | Supersédé par v3/v4/v5 |
| `compute_zeros_test_error1.py` | Fichier de test d'erreur — résolu |
| `compute_zeros_test_error1_corr1.py` | Correction archivée — intégrée en v3 |
| `compute_zeros_test_error2.py` | Fichier de test d'erreur — résolu |
| `zeros_finder.py` | Prototype initial — remplacé |
| `calcul_zeta.py` | Prototype initial — remplacé |
| `demo_complete.py` | Démo — non utilisée en production |
| `verification.py` | Remplacé par `turing_validation.py` |
| `factorielle__gamma__zeta_.py` | Script éducatif — non nécessaire |
| `prng_zeta_aleatoire.py` | Expérimentation — non prioritaire |
| `ia_zeta.py` | Prototype IA — non utilisé |
| `config_loader.py` | Remplacé par config YAML directe |
| `config_loader1.py` | Doublon |
| `plots.py` | Remplacé par visualisations intégrées |
| `logger_config.py` | Remplacé par loguru dans v3 |
| `cpu_temp_monitor.py` | Monitoring ponctuel — non critique |

---

## Fichiers CSV — Anciennes données

Le fichier de référence est `zeros_zeta_T10000_20260424_205325.csv` (10 142 zéros).
Les fichiers ci-dessous sont des runs partiels ou de test.

| Fichier | Raison |
|---|---|
| `zeros_zeta_T40_20260421_190235.csv` | Run T=40 — ancien test |
| `riemann_zeros.csv` | 20 zéros — remplacé par LMFDB direct |
| `zeros_intermediaire.csv` | Run partiel — 200 zéros |
| `resultats_zeta.csv` | 10 résultats de demo |
| `zeros_partiels_206.csv` | Run partiel — 200 zéros |
| `zeros_zeta_final.csv` | Run partiel — 200 zéros |
| `gpu_info.csv` | Capture GPU ponctuelle |

---

## Scripts shell — Setup terminé

| Fichier | Raison |
|---|---|
| `install_zeta_complete.sh` | Installation terminée |
| `setup_ollama_final.sh` | Ollama installé |
| `run_computation.sh` | Remplacé par commandes directes |
| `monitor2.sh` | Monitoring ponctuel |

---

## Fichiers divers

| Fichier | Raison |
|---|---|
| `IA_tools.txt` | Notes texte — intégrées dans Handoff |
| `zeros_config1.yaml` | Ancienne config — remplacée par zeros_config.yaml |
| `zeros_zeta.log` | Ancien log |
| `zeros_zeta_T10000_20260424_205325.log` | Log de run — sur GitHub |
| `gpu_info.csv` | Capture ponctuelle |

---

## Fichiers MD — Déjà dans le wiki

Ces fichiers `.md` sont **déjà dans le wiki GitHub** (`Riemann_Lab.wiki/`).
Inutile de les avoir aussi dans le projet Claude.

| Fichier | Equivalent dans le wiki |
|---|---|
| `niveau-0-prerequis.md` | Wiki ✅ |
| `niveau-1-series.md` | Wiki ✅ |
| `niveau-2-analyse-complexe.md` | Wiki ✅ |
| `niveau-3-gamma-dirichlet.md` | Wiki ✅ |
| `niveau-4-zeta.md` | Wiki ✅ |
| `niveau-5-expert.md` | Wiki ✅ |
| `Animations.md` | Wiki ✅ |
| `Katex-cheatsheet.md` | Wiki ✅ |
| `Tableau-Symboles-Mathématiques.md` | Wiki ✅ |
| `Bibliotheques.md` | Wiki ✅ |
| `Guide-Git-GitHub.md` | Wiki ✅ |
| `Guide-VSCode-Bonnes-Pratiques.md` | Wiki ✅ |
| `Interprétation-des-résultats-de-tests.md` | Wiki ✅ |
| `Parcours-complet.md` | Wiki ✅ |
| `Partie-1-La-Théorie-Étape_1.md` | Wiki ✅ |
| `Etape-1-Calcul-des-zéros-non-triviaux.md` | Wiki ✅ |
| `Methode.md` | Wiki ✅ |
| `Home.md` | Wiki ✅ |
| `Formulaire-zeta.md` | Wiki ✅ (doublon de Formules_zeta.md) |
| `Arbre_dossiers_projet.md` | Outdated — remplacé par Handoff |

---

## Fichiers HTML — PROTÉGÉS (ne pas archiver sur Linux)

| Fichier | Raison |
|---|---|
| `animation_theta.html` | 🔒 Lié 3x dans index.html — NE PAS DÉPLACER |
| `index.html` | 🔒 Page principale du site — NE PAS DÉPLACER |

---

## Suppressions supplémentaires dans le projet Claude (29 mai)

| Fichier | Raison |
|---|---|
| `IA_tools.txt` | Notes brutes — intégrées dans Handoff |
| `CLAUDE_global_dot-claude.md` | Remplacé par CLAUDE.md (285L, 29 mai) |
| `CLAUDE_projet_zeta.md` | Doublon obsolète |
| `PROMPT_CLAUDE_CODE_PHASE_C.md` | Supersédé par voie B/v5 |
| `PROMPT_CLAUDE_CODE_Vers_VOIEB_V5_INTEGRATION.md` | Mission accomplie |
| `PROMPT_CLAUDE_CODE_Stopper_le_travail.md` | Utilitaire ponctuel |
| `README.md` | Sur GitHub — inutile dans Claude |
| `CLAUDE.md` doublon (210L) | Garder 285L uniquement |
| `Bonnes-Pratiques-Claude-Code.md` doublon | Garder un seul exemplaire |
| `Guide-Git-GitHub.md` | Dans le wiki |
| `Arbre_dossiers_projet.md` | Remplacé par Handoff |

---

## Ce qu'il faut GARDER — liste finale projet Claude

```
✅ Handoff.md (29 mai, 788L)               — état projet à jour
✅ CLAUDE.md (29 mai, 285L)                — instructions Claude Code
✅ Bonnes-Pratiques-Claude-Code.md         — guide vivant sessions
✅ SKILL.md                                — skill principal zêta
✅ SKILL_phase_c.md                        — skill Phase C libmpfr
✅ knowledge_base_obj2.md                  — Objectif 2
✅ Rapport_validation_T10000.md            — rapport officiel
✅ Phase-Optimisation-compute_zeros_v3.md  — référence Phase 0
✅ PROMPT_CLAUDE_CODE_V4_INTEGRATION.md   — actif pour v4.1
✅ prompt_claude_code_phase_c_voie_b_v5.md — référence voie B
✅ animation_theta.html                    — référence site web
✅ zeros_zeta_T10000_20260424_205325.csv  — 10 142 zéros validés
✅ Les 9 PDF de cadrage (à uploader)
```

---

## Archivage 2026-06-10

| Fichier | Raison | Destination |
|---|---|---|
| `src/calculs/optimisation/compute_zeros_v4_1.py.bak` | Sauvegarde automatique avant patch STEP adaptatif — supersédée par commit `50837f7` | `docs/archive/` — local uniquement (`.bak` ignoré par `.gitignore`) |

---

*Fichiers supprimés du projet Claude uniquement — présents sur GitHub et Linux*  
*10 juin 2026*

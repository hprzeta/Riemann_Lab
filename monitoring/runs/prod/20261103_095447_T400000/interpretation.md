Note de correction — 2026-11-03 (postérieure au run)

L'alerte « INCOMPLET — 3 zéros manquants » en tête de rapport est lue dans le journal d'exécution du run, qui n'a pas été modifié : elle décrit l'état du run à sa fin (640 523 zéros). Elle est corrigée par la présente note.

- [mesuré] Les 3 zéros manquants sont t = 286 692,10233507601 et 306 086,79828720580 (segment 5, worker 5), et t = 385 415,72427039186 (segment 7, worker 7). Chacun figurait dans le journal d'échecs (checkpoints/echecs_worker_005 et 007) : l'affinage n'avait pas convergé.
- [mesuré] Dans chacun des 3 brackets, Z (mpmath.siegelz, 30 chiffres) ne change pas de signe : le zéro se trouve à environ 2,5e-7 à l'extérieur du bracket. Il a été affiné avec mpmath.siegelz + Illinois, avec |Z(t)| de l'ordre de 1e-29.
- [mesuré] Les 3 zéros ont été ajoutés au CSV (methode_affinage = siegelz_manuel, colonne n renumérotée) : 640 526 zéros. Sauvegarde : zeros_v17_T400000_20261103_095511.csv.bak-20261103.
- [mesuré] Turing–Backlund relancé sur le CSV corrigé (valider_turing, dps=30) : COMPLET, 0 manquant aux 5 points de contrôle (T_max = 399 999,68 : 640 526 calculés pour 640 526 attendus). Les points intermédiaires diffèrent du run d'origine car ils sont choisis par rang dans la liste.
- [hypothèse] Le décalage commun (environ 2,5e-7) des bords de brackets pourrait venir de l'erreur float64 de la détection de signe à t proche de 3e5 ; non testé.
- Non corrigés : execution_v17_*.log et le CSV principal (avant rescan) restent ceux du run d'origine. Le verdict en tête de rapport (INCOMPLET) vient de ce journal. Le comptage de la section 3 (640 526) reflète en revanche le CSV corrigé.

Conséquence : le CSV corrigé est complet selon Turing ; le run d'origine, lui, ne l'était pas.

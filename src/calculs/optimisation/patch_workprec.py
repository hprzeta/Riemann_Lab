#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_workprec.py — applique workprec(50) sur le bloc mpmath_petit_t
de compute_zeros_v4_1.py (version post-Claude Code, avec bracket).

Usage :
    python patch_workprec.py

Le fichier est modifié sur place. Une sauvegarde .bak est créée.
Auteur : hprzeta — Riemann_Lab Phase C — 2026-06-03
"""
import shutil
from pathlib import Path

CIBLE = Path(__file__).parent / "compute_zeros_v4_1.py"

AVANT = """                    with chrono("mpmath_petit_t"):
                        zero = float(_mp.findroot(
                            _mp.siegelz, (a, b),
                            solver="illinois", tol=tol, maxsteps=80,
                        ))"""

APRES = """                    with chrono("mpmath_petit_t"):
                        with _mp.workprec(50):   # ~15 dps — suffit pour N<7 termes RS
                            zero = float(_mp.findroot(
                                _mp.siegelz, (a, b),
                                solver="illinois", tol=tol, maxsteps=80,
                            ))"""

def main():
    if not CIBLE.exists():
        print(f"ERREUR : fichier introuvable : {CIBLE}")
        print("Lance ce script depuis le dossier src/calculs/optimisation/")
        return

    texte = CIBLE.read_text(encoding="utf-8")

    if AVANT not in texte:
        if "workprec" in texte:
            print("✅ workprec déjà présent — patch déjà appliqué, rien à faire.")
        else:
            print("❌ Bloc cible introuvable — le fichier a peut-être une indentation différente.")
            print("   Cherche manuellement 'mpmath_petit_t' et ajoute :")
            print("       with _mp.workprec(50):  # ~15 dps")
            print("   autour du float(_mp.findroot(...))")
        return

    # Sauvegarde
    bak = CIBLE.with_suffix(".py.bak")
    shutil.copy(CIBLE, bak)
    print(f"Sauvegarde → {bak}")

    # Application
    nouveau = texte.replace(AVANT, APRES, 1)
    CIBLE.write_text(nouveau, encoding="utf-8")
    print(f"✅ Patch appliqué → {CIBLE}")

    # Vérification
    assert "workprec(50)" in CIBLE.read_text(encoding="utf-8"), "ERREUR post-write !"
    print("✅ Vérification OK — workprec(50) présent dans le fichier.")
    print()
    print("Prochaine étape :")
    print("  printf '1000\\nO\\n' | python compute_zeros_v4_1.py 2>&1 | tee /tmp/profil_workprec.log")
    print("  grep -A 8 'PROFIL PHASES' /tmp/profil_workprec.log")

if __name__ == "__main__":
    main()

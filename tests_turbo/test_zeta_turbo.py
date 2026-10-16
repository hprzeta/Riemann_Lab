# -*- coding: utf-8 -*-
"""
Tests du cycle de vie du turbo Zêta (scripts/zeta_turbo_on.sh, _off.sh, _status.sh, zeta_session_turbo.sh).

AUCUNE modification du système réel : chaque test construit un arbre sysfs/proc FACTICE dans un dossier
temporaire (ZETA_TURBO_SYSROOT, ZETA_TURBO_STATE_DIR — honorés par les scripts UNIQUEMENT hors root) et
un faux `systemctl` (dossier bin/ placé en tête du PATH). Aucun sudo, aucun appel à cpupower/sysctl réels.

Lancement :  zeta_env/bin/python3 -B -I tests_turbo/test_zeta_turbo.py

Couverture demandée : activation deux fois ; runs successifs ; restauration depuis état initial activé /
désactivé / mixte ; absence de privilèges ; interface CPU absente ; échec à mi-parcours ; échec d'une autre
étape avant le « bye bye » ; état manquant / invalide ; services ; dérive ; verrou concurrent.
"""
import os
import re
import stat
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
# ZETA_TURBO_TEST_SCRIPTS : permet de tester une COPIE modifiée (contrôle des mutations), jamais en production.
SCRIPTS = Path(os.environ.get("ZETA_TURBO_TEST_SCRIPTS", str(RACINE / "scripts")))
ON, OFF = SCRIPTS / "zeta_turbo_on.sh", SCRIPTS / "zeta_turbo_off.sh"
STATUT, SESSION = SCRIPTS / "zeta_turbo_status.sh", SCRIPTS / "zeta_session_turbo.sh"
EST_ROOT = os.geteuid() == 0

STUB_SYSTEMCTL = """#!/bin/bash
# faux systemctl : services « actifs » listés dans $FAKE_SVC (un par ligne)
cmd=$1; shift
[ "${1:-}" = "--" ] && shift
if [ "$cmd" = "is-active" ]; then [ "${1:-}" = "--quiet" ] && shift; grep -qx "$1" "$FAKE_SVC"; exit $?; fi
echo "$cmd $1" >> "$FAKE_SVC.calls"
case "$cmd" in
  stop)  [ "${FAKE_STOP_FAIL:-}" = "$1" ] && exit 1; grep -vx "$1" "$FAKE_SVC" > "$FAKE_SVC.t"; mv "$FAKE_SVC.t" "$FAKE_SVC" ;;
  start) [ "${FAKE_START_FAIL:-}" = "$1" ] && exit 1; grep -qx "$1" "$FAKE_SVC" || echo "$1" >> "$FAKE_SVC" ;;
esac
exit 0
"""


class Arbre:
    """Arbre factice : /sys/devices/system/cpu, /proc/sys/vm/swappiness, état, faux systemctl."""

    def __init__(self, base: Path, n_cpu=4, gov="powersave", epp="balance_performance", swap="10",
                 services=("cups", "bluetooth"), no_turbo="0", avec_cpufreq=True):
        self.base = base
        self.root = base / "root"
        self.etat = base / "etat"
        self.bin = base / "bin"
        self.svc = base / "services_actifs"
        self.cpu = self.root / "sys/devices/system/cpu"
        self.swap = self.root / "proc/sys/vm/swappiness"
        for d in (self.cpu, self.swap.parent, self.bin):
            d.mkdir(parents=True, exist_ok=True)
        if avec_cpufreq:
            for i in range(n_cpu):
                cf = self.cpu / f"cpu{i}/cpufreq"
                cf.mkdir(parents=True)
                (cf / "scaling_governor").write_text(gov + "\n")
                (cf / "scaling_available_governors").write_text("performance powersave schedutil\n")
                (cf / "energy_performance_preference").write_text(epp + "\n")
        (self.cpu / "intel_pstate").mkdir(parents=True, exist_ok=True)
        (self.cpu / "intel_pstate/no_turbo").write_text(no_turbo + "\n")
        self.swap.write_text(swap + "\n")
        self.svc.write_text("".join(s + "\n" for s in services))
        stub = self.bin / "systemctl"
        stub.write_text(STUB_SYSTEMCTL)
        stub.chmod(0o755)

    def env(self, **extra):
        e = dict(os.environ)
        e.update(ZETA_TURBO_SYSROOT=str(self.root), ZETA_TURBO_STATE_DIR=str(self.etat),
                 PATH=f"{self.bin}:{e['PATH']}", FAKE_SVC=str(self.svc))
        e.update(extra)
        return e

    def run(self, script, *args, env=None):
        return subprocess.run(["bash", str(script), *args], env=env or self.env(),
                              capture_output=True, text=True, timeout=60)

    def gov(self, i):
        return (self.cpu / f"cpu{i}/cpufreq/scaling_governor").read_text().strip()

    def set_gov(self, i, v):
        (self.cpu / f"cpu{i}/cpufreq/scaling_governor").write_text(v + "\n")

    def epp(self, i):
        return (self.cpu / f"cpu{i}/cpufreq/energy_performance_preference").read_text().strip()

    def swappiness(self):
        return self.swap.read_text().strip()

    def actifs(self):
        return sorted(self.svc.read_text().split())

    @property
    def etat_fichier(self):
        return self.etat / "state"


class Base(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.base = Path(self._t.name)

    def tearDown(self):
        # Les tests d'échec rendent des fichiers en lecture seule : on les rouvre avant nettoyage.
        for p in self.base.rglob("*"):
            try:
                p.chmod(p.stat().st_mode | stat.S_IWUSR)
            except OSError:
                pass
        self._t.cleanup()

    def arbre(self, **kw):
        return Arbre(self.base, **kw)

    def derniere_ligne(self, r):
        lignes = [l for l in r.stdout.splitlines() if l.startswith("TURBO")]
        return lignes[-1] if lignes else ""


class TestActivation(Base):
    def test_activation_deux_fois_idempotente(self):
        a = self.arbre()
        r1 = a.run(ON)
        self.assertEqual(r1.returncode, 0, r1.stdout + r1.stderr)
        self.assertIn("TURBO: ACTIF (vérifié", r1.stdout)
        self.assertEqual({a.gov(i) for i in range(4)}, {"performance"})
        etat1 = a.etat_fichier.read_bytes()
        self.assertIn(b"cpu_gov_0=powersave", etat1, "l'état INITIAL est enregistré")
        r2 = a.run(ON)
        self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
        self.assertIn("déjà géré", r2.stdout)
        self.assertEqual(a.etat_fichier.read_bytes(), etat1, "le 2e appel NE réécrit PAS l'état initial")
        self.assertEqual(stat.S_IMODE(a.etat_fichier.stat().st_mode), 0o640)

    def test_plusieurs_runs_successifs_meme_session(self):
        a = self.arbre()
        self.assertEqual(a.run(ON).returncode, 0)                      # début de session (hook)
        etat0 = a.etat_fichier.read_bytes()
        for _ in range(3):                                             # 3 gros runs successifs
            r = a.run(ON, "--services")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(a.actifs(), [], "services arrêtés pendant le run")
            r = a.run(OFF, "--services")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(a.actifs(), ["bluetooth", "cups"], "services redémarrés après le run")
            self.assertEqual({a.gov(i) for i in range(4)}, {"performance"}, "le turbo CPU RESTE actif")
        etat_fin = a.etat_fichier.read_text()
        self.assertIn("cpu_gov_0=powersave", etat_fin, "l'état initial n'a jamais été écrasé")
        self.assertEqual(etat0.decode().count("cpu_gov_"), etat_fin.count("cpu_gov_"))
        r = a.run(OFF)                                                 # « bye bye »
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual({a.gov(i) for i in range(4)}, {"powersave"})
        self.assertFalse(a.etat_fichier.exists())

    def test_swappiness_modifiee_puis_restauree(self):
        a = self.arbre(swap="60")
        self.assertEqual(a.run(ON).returncode, 0)
        self.assertEqual(a.swappiness(), "10")
        self.assertEqual(a.run(OFF).returncode, 0)
        self.assertEqual(a.swappiness(), "60")

    def test_swappiness_deja_a_10_inchangee(self):
        a = self.arbre(swap="10")
        a.run(ON)
        a.run(OFF)
        self.assertEqual(a.swappiness(), "10")


class TestRestauration(Base):
    def test_depuis_etat_initial_desactive_et_mixte(self):
        a = self.arbre()
        a.set_gov(1, "performance")                                    # mixte : cpu1 déjà performance
        a.run(ON)
        a.run(OFF)
        self.assertEqual([a.gov(i) for i in range(4)], ["powersave", "performance", "powersave", "powersave"])

    def test_depuis_etat_initial_deja_active_reste_active(self):
        a = self.arbre(gov="performance")
        r = a.run(ON)
        self.assertEqual(r.returncode, 0)
        self.assertIn("déjà « performance »", r.stdout)
        self.assertIn(b"cpu_gov_0=performance", a.etat_fichier.read_bytes(),
                      "un turbo déjà actif n'est PAS enregistré comme désactivé")
        r = a.run(OFF)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual({a.gov(i) for i in range(4)}, {"performance"}, "restauré TEL QUEL, pas forcé à powersave")

    def test_gouverneur_initial_autre_que_powersave_restaure_tel_quel(self):
        # Un 3e gouverneur (schedutil) : la restauration remet l'état enregistré, JAMAIS « powersave » par défaut.
        a = self.arbre(gov="schedutil")
        a.set_gov(2, "powersave")
        a.run(ON)
        self.assertEqual({a.gov(i) for i in range(4)}, {"performance"})
        r = a.run(OFF)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual([a.gov(i) for i in range(4)], ["schedutil", "schedutil", "powersave", "schedutil"])

    def test_epp_restauree_si_modifiee_par_effet_de_bord(self):
        a = self.arbre(epp="balance_performance")
        a.run(ON)
        (a.cpu / "cpu2/cpufreq/energy_performance_preference").write_text("performance\n")
        a.run(OFF)
        self.assertEqual(a.epp(2), "balance_performance")

    def test_off_sans_rien_actif_est_idempotent(self):
        a = self.arbre()
        r = a.run(OFF)
        self.assertEqual(r.returncode, 0)
        self.assertIn("RIEN À RESTAURER", r.stdout)
        self.assertEqual({a.gov(i) for i in range(4)}, {"powersave"})
        a.run(ON)
        self.assertEqual(a.run(OFF).returncode, 0)
        r = a.run(OFF)
        self.assertEqual(r.returncode, 0)
        self.assertIn("RIEN À RESTAURER", r.stdout)


class TestErreurs(Base):
    def test_absence_de_privileges(self):
        if EST_ROOT:
            self.skipTest("exécuté en root")
        a = self.arbre()
        env = dict(os.environ)                                         # sans variables de test, non root
        for var in ("ZETA_TURBO_SYSROOT", "ZETA_TURBO_STATE_DIR"):
            env.pop(var, None)
        for script in (ON, OFF):
            r = subprocess.run(["bash", str(script)], env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            self.assertIn("droits root requis", r.stderr)
        self.assertEqual({a.gov(i) for i in range(4)}, {"powersave"}, "rien n'a été modifié")
        self.assertFalse(a.etat.exists())

    def test_variables_de_test_ignorees_en_root_dans_le_code(self):
        src = ON.read_text() + OFF.read_text()
        self.assertEqual(len(re.findall(r"unset ZETA_TURBO_SYSROOT ZETA_TURBO_STATE_DIR", src)), 2)
        self.assertIn("PATH=/usr/sbin:/usr/bin:/sbin:/bin", ON.read_text())

    def test_interface_cpu_absente(self):
        a = self.arbre(avec_cpufreq=False)
        r = a.run(ON)
        self.assertEqual(r.returncode, 6, r.stdout + r.stderr)
        self.assertIn("TURBO: NON ACTIF (interface CPU absente)", r.stdout)
        self.assertFalse(a.etat_fichier.exists(), "aucun état créé quand rien n'est applicable")
        self.assertEqual(a.swappiness(), "10")

    @unittest.skipIf(EST_ROOT, "chmod ineffectif en root")
    def test_echec_a_mi_parcours_puis_restauration(self):
        a = self.arbre(swap="60")
        (a.cpu / "cpu2/cpufreq/scaling_governor").chmod(0o444)         # écriture refusée sur cpu2
        r = a.run(ON)
        self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
        self.assertIn("TURBO: PARTIEL", r.stdout)
        self.assertNotIn("ACTIF (vérifié", r.stdout)
        self.assertIn("cpu2", r.stderr)
        self.assertEqual(a.gov(0), "performance")
        self.assertEqual(a.gov(2), "powersave")
        self.assertTrue(a.etat_fichier.exists(), "l'état initial est conservé malgré l'échec")
        (a.cpu / "cpu2/cpufreq/scaling_governor").chmod(0o644)
        r = a.run(OFF)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual({a.gov(i) for i in range(4)}, {"powersave"})
        self.assertEqual(a.swappiness(), "60")

    @unittest.skipIf(EST_ROOT, "chmod ineffectif en root")
    def test_restauration_incomplete_conserve_l_etat_et_tente_le_reste(self):
        a = self.arbre(swap="60")
        a.run(ON)
        (a.cpu / "cpu1/cpufreq/scaling_governor").chmod(0o444)
        r = a.run(OFF)
        self.assertEqual(r.returncode, 5, r.stdout + r.stderr)
        self.assertIn("RESTAURATION INCOMPLÈTE", r.stdout)
        self.assertTrue(a.etat_fichier.exists(), "état CONSERVÉ pour une nouvelle tentative")
        self.assertEqual(a.gov(0), "powersave", "les autres éléments ont quand même été restaurés")
        self.assertEqual(a.swappiness(), "60")
        (a.cpu / "cpu1/cpufreq/scaling_governor").chmod(0o644)
        self.assertEqual(a.run(OFF).returncode, 0)
        self.assertFalse(a.etat_fichier.exists())

    def test_etat_manquant_alors_que_performance_actif(self):
        a = self.arbre(gov="performance")
        r = a.run(OFF)
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertEqual({a.gov(i) for i in range(4)}, {"performance"}, "rien modifié sans état")
        r = a.run(OFF, "--force-defaults")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual({a.gov(i) for i in range(4)}, {"powersave"})

    def test_etat_invalide(self):
        a = self.arbre()
        a.etat.mkdir()
        a.etat_fichier.write_text("version=1\nceci n'est pas valide ; rm -rf /\n")
        avant = a.etat_fichier.read_bytes()
        r = a.run(ON)
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertEqual(a.gov(0), "powersave", "rien modifié")
        self.assertEqual(a.etat_fichier.read_bytes(), avant, "fichier invalide conservé")
        r = a.run(OFF)
        self.assertEqual(r.returncode, 3)
        self.assertEqual(a.run(STATUT).returncode, 3)
        a.set_gov(0, "performance")
        r = a.run(OFF, "--force-defaults")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(a.gov(0), "powersave")
        self.assertEqual(len(list(a.etat.glob("state.invalid-*"))), 1, "invalide mis de côté, jamais supprimé")
        self.assertEqual(next(a.etat.glob("state.invalid-*")).read_bytes(), avant)

    def test_force_defaults_refuse_si_etat_valide(self):
        a = self.arbre()
        a.run(ON)
        r = a.run(OFF, "--force-defaults")
        self.assertEqual(r.returncode, 64)
        self.assertEqual({a.gov(i) for i in range(4)}, {"performance"})

    def test_arguments_inconnus(self):
        a = self.arbre()
        self.assertEqual(a.run(ON, "--bidon").returncode, 64)
        self.assertEqual(a.run(OFF, "--bidon").returncode, 64)
        self.assertEqual(a.run(OFF, "--services", "--force-defaults").returncode, 64)


class TestServices(Base):
    def test_services_arretes_et_redemarres_seulement_ceux_arretes(self):
        a = self.arbre(services=("cups", "bluetooth", "snapd"))
        r = a.run(ON, "--services")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(a.actifs(), [])
        a.run(OFF)
        self.assertEqual(a.actifs(), ["bluetooth", "cups", "snapd"])

    def test_service_deja_inactif_n_est_pas_demarre(self):
        a = self.arbre(services=("cups",))
        a.run(ON, "--services")
        a.run(OFF)
        self.assertEqual(a.actifs(), ["cups"])
        calls = Path(str(a.svc) + ".calls").read_text()
        self.assertNotIn("start avahi-daemon", calls)

    def test_echec_redemarrage_service_conserve_l_etat(self):
        a = self.arbre(services=("cups", "bluetooth"))
        a.run(ON, "--services")
        r = a.run(OFF, env=a.env(FAKE_START_FAIL="bluetooth"))
        self.assertEqual(r.returncode, 5, r.stdout + r.stderr)
        self.assertIn("service bluetooth", r.stderr)
        self.assertEqual(a.actifs(), ["cups"])
        self.assertEqual(a.gov(0), "powersave", "le CPU a quand même été restauré")
        self.assertIn("services=bluetooth", a.etat_fichier.read_text())
        self.assertEqual(a.run(OFF).returncode, 0)
        self.assertEqual(a.actifs(), ["bluetooth", "cups"])


class TestDurcissement(Base):
    def test_nom_de_service_hostile_dans_l_etat_n_est_jamais_execute(self):
        a = self.arbre(services=("cups",))
        a.run(ON, "--services")
        txt = a.etat_fichier.read_text().replace("services=cups", "services=--now,cups")
        a.etat_fichier.write_text(txt)
        r = a.run(OFF)
        self.assertEqual(r.returncode, 5, r.stdout + r.stderr)
        self.assertIn("nom invalide", r.stderr)
        calls = Path(str(a.svc) + ".calls").read_text()
        self.assertNotIn("start --now", calls, "un nom commençant par « - » ne doit jamais atteindre systemctl")
        self.assertIn("start cups", calls, "les autres services valides sont quand même traités")
        self.assertTrue(a.etat_fichier.exists(), "état conservé")


class TestStatut(Base):
    def test_statuts(self):
        a = self.arbre()
        r = a.run(STATUT)
        self.assertEqual((r.returncode, r.stdout.splitlines()[-1]), (1, "TURBO_STATUS=INACTIF"))
        a.run(ON)
        r = a.run(STATUT)
        self.assertEqual((r.returncode, r.stdout.splitlines()[-1]), (0, "TURBO_STATUS=ACTIF"))

    def test_derive_puis_reaffirmation_sans_toucher_a_l_etat_initial(self):
        a = self.arbre()
        a.run(ON)
        etat = a.etat_fichier.read_bytes()
        a.set_gov(1, "powersave")                                      # power-profiles-daemon a défait un CPU
        r = a.run(STATUT)
        self.assertEqual((r.returncode, r.stdout.splitlines()[-1]), (2, "TURBO_STATUS=DERIVE"))
        self.assertEqual(a.run(ON).returncode, 0)
        self.assertEqual(a.gov(1), "performance")
        self.assertEqual(a.etat_fichier.read_bytes(), etat, "état initial intact après ré-affirmation")
        self.assertEqual(a.run(STATUT).returncode, 0)

    def test_performance_sans_etat_signale(self):
        a = self.arbre(gov="performance")
        r = a.run(STATUT)
        self.assertEqual(r.returncode, 3)
        self.assertIn("SANS état", r.stdout)

    def test_boost_materiel_non_modifie_et_signale(self):
        a = self.arbre(no_turbo="1")
        r = a.run(ON)
        self.assertEqual(r.returncode, 0)
        self.assertIn("DÉSACTIVÉ (no_turbo=1)", r.stdout)
        self.assertEqual((a.cpu / "intel_pstate/no_turbo").read_text().strip(), "1")


class TestConcurrence(Base):
    def test_deux_activations_simultanees(self):
        a = self.arbre()
        res = []
        def go():
            res.append(a.run(ON))
        ths = [threading.Thread(target=go) for _ in range(4)]
        [t.start() for t in ths]
        [t.join() for t in ths]
        self.assertEqual([r.returncode for r in res], [0, 0, 0, 0], [r.stdout + r.stderr for r in res])
        self.assertEqual(a.etat_fichier.read_text().count("cpu_gov_0=powersave"), 1,
                         "un seul état initial, jamais écrasé par un concurrent")
        self.assertEqual(a.run(OFF).returncode, 0)
        self.assertEqual({a.gov(i) for i in range(4)}, {"powersave"})


class TestEnveloppeSession(Base):
    def env_session(self, a, sudo="env", **extra):
        return a.env(ZETA_SUDO=sudo, ZETA_TURBO_BIN_DIR=str(SCRIPTS),
                     ZETA_TURBO_LOG=str(self.base / "turbo_session.log"), **extra)

    def test_start_puis_end(self):
        a = self.arbre()
        env = self.env_session(a)
        r = a.run(SESSION, "start", env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Turbo Zêta : ACTIF (vérifié", r.stdout)
        self.assertEqual(len(r.stdout.strip().splitlines()), 1, "une seule ligne injectée dans le contexte")
        r = a.run(SESSION, "end", env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("RESTAURÉ (vérifié", r.stdout)
        self.assertEqual({a.gov(i) for i in range(4)}, {"powersave"})
        self.assertIn("zeta_turbo_on.sh", (self.base / "turbo_session.log").read_text())

    def test_start_sans_privileges_ne_bloque_pas_et_ne_pretend_rien(self):
        a = self.arbre()
        faux = self.base / "faux_sudo"
        faux.write_text("#!/bin/bash\necho 'sudo: un mot de passe est requis' >&2; exit 1\n")
        faux.chmod(0o755)
        r = a.run(SESSION, "start", env=self.env_session(a, sudo=str(faux)))
        self.assertEqual(r.returncode, 0, "le démarrage de session n'est jamais bloqué")
        self.assertIn("NON ACTIF", r.stdout)
        self.assertNotIn("ACTIF (vérifié", r.stdout)
        self.assertEqual({a.gov(i) for i in range(4)}, {"powersave"})

    def test_start_cause_lisible_sans_reinjecter_toute_la_sortie(self):
        a = self.arbre()
        faux = self.base / "faux_sudo2"
        faux.write_text("#!/bin/bash\necho 'ligne un'; echo 'derniere ligne'; exit 7\n")
        faux.chmod(0o755)
        r = a.run(SESSION, "start", env=self.env_session(a, sudo=str(faux)))
        self.assertEqual(r.returncode, 0)
        self.assertIn("derniere ligne (code 7)", r.stdout)
        self.assertNotIn("ligne un", r.stdout)
        r = a.run(SESSION, "start", env=self.env_session(a, sudo="false"))
        self.assertIn("aucune sortie (code 1)", r.stdout)

    def test_bye_bye_restaure_meme_apres_une_etape_en_echec(self):
        a = self.arbre()
        env = self.env_session(a)
        a.run(SESSION, "start", env=env)
        # étape de clôture qui échoue AVANT, puis « end » : la restauration ne dépend pas de l'étape précédente
        r = subprocess.run(["bash", "-c", f"false; bash {SESSION} end"], env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual({a.gov(i) for i in range(4)}, {"powersave"})

    @unittest.skipIf(EST_ROOT, "chmod ineffectif en root")
    def test_end_signale_une_restauration_incomplete(self):
        a = self.arbre()
        env = self.env_session(a)
        a.run(SESSION, "start", env=env)
        (a.cpu / "cpu3/cpufreq/scaling_governor").chmod(0o444)
        r = a.run(SESSION, "end", env=env)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ERREUR À LA RESTAURATION", r.stdout)
        self.assertTrue(a.etat_fichier.exists(), "état conservé")

    def test_end_sans_etat_est_idempotent(self):
        a = self.arbre()
        r = a.run(SESSION, "end", env=self.env_session(a))
        self.assertEqual(r.returncode, 0)
        self.assertIn("RIEN À RESTAURER", r.stdout)

    def test_usage(self):
        a = self.arbre()
        self.assertEqual(a.run(SESSION, "bidon", env=self.env_session(a)).returncode, 64)


if __name__ == "__main__":
    unittest.main(verbosity=2)

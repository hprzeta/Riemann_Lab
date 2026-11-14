# Archive de session — 18/10/2026

Projet Riemann_Lab — deux sessions Claude Code le 18/10/2026 (branche Riemann_Lab_IA), regroupées dans ce fichier : **Partie A** (sections 1 à 8, capture de 16h14) et **Partie B** (sections 9 à 14, capture de 18h53).

**Partie A — Turbo Zêta :** RESTAURÉ (vérifié : 4 CPU à leur gouverneur initial (cpu0=powersave), swappiness 10) — première étape du « bye bye ».

**Partie A — Capture brute du terminal :** active, fichier claude-traitement-journalier/session_20261018_1614.log ; le .md est généré à la fermeture (taper exit deux fois). Capture non commitée.

**Partie B — Turbo Zêta :** RESTAURÉ (vérifié : 4 CPU à leur gouverneur initial (cpu0=powersave), swappiness 10) — première étape du « bye bye ».

**Partie B — Capture brute du terminal :** active, fichier claude-traitement-journalier/session_20261018_1853.log ; le .md est généré à la fermeture (taper exit deux fois). Capture non commitée. La capture de 16h14 (partie A) tournait encore au moment du « bye bye » de la partie B.

Cette archive reprend la narration, les tableaux et les conclusions de la session ; aucun extrait de code n'y figure.

---

# Partie A — première session du jour (capture 16h14)

## 1. Point projet et actions 0, 1, 2 du Handoff

Sur la demande « point projet », le bloc de reprise du Handoff a été lu : session du 17/10 (runs prod T=10 000 et T=400 000), prochaine action en quatre points.

| Action | Résultat |
|---|---|
| 0 — cd dans zeta_run.sh | *cd "$PROJET_DIR"* ajouté : un run lancé depuis *~* n'écrit plus ses CSV dans *~/calculs/*. Validé en run réel depuis *~*. |
| 1 — verdict de Turing en tête du rapport | Le rapport lit le verdict dans le journal d'exécution voisin du CSV : alerte si INCOMPLET (cas T=400 000 : 5 zéros manquants), ligne neutre si COMPLET, « introuvable [non vérifié] » si absent. |
| 2 — débit instantané | Débit = croissance de la somme de tous les CSV de workers (maximum par worker, pas de double comptage avec les .partial.csv de la v17). Courbe en escalier avec la v16 (CSV écrit en fin de worker), lisse avec la v17. |

Commit des trois actions : 53d8f7f, propagé aux 4 branches.

## 2. Validation par runs réels

- **Run test T=100 000 depuis ~** : 138 069 zéros, 817 z/s, Turing complet, CSV bien rangé dans le dépôt. La fenêtre « machines » était vide : le logger de métriques n'avait pas été relancé après le redémarrage (zeta-mon-on nécessaire).
- **Second run test après zeta-mon-on** : 138 069 zéros, 908 z/s, Turing complet, PC1 max 80,0 °C (11 % du temps au-dessus de 75 °C), fréquence médiane 3 300 puis 3 200 MHz. Compteur de zéros 25 609 → 120 816 → 138 075 : la somme des workers fonctionne.
- Défaut relevé puis corrigé : la colonne t_max restait figée sur un seul fichier ; elle prend maintenant le maximum sur tous les workers (commit b1dda72).

## 3. Titres des fenêtres de graphiques

Demande de hprzeta : « modifie le titre de chaque fenêtre des graphiques avec un nom parlant et significatif au lieu de Figure 1 ». Trois titres explicites (zéros en direct, statistique GUE en direct, machines du cluster en direct) ; hprzeta a confirmé à l'écran que cela fonctionnait.

## 4. Commits et propagation du jour

| Étape | Commit | Contenu |
|---|---|---|
| Actions 0-1-2 | 53d8f7f | cd dans zeta_run.sh, verdict Turing, débit multi-workers |
| Titres + archives + données | 212715f | titres de fenêtres, archives des 10-17/10, runs du 17-18/10 |
| t_max | b1dda72 | maximum sur tous les workers |
| Rapports rattachés | 00230aa | 3 rapports T=100 000 du 17/10 rattachés à leur CSV |
| TUI progress + touche r | 3620eee, f148864 | code puis données (deux commits gardés par hprzeta) |

Chaque propagation s'est faite sur les 4 branches (C en fast-forward, main et Test en fusion sans fast-forward), sans --force, après audit sans résultat. Arrêt « tout commiter » : je n'ai pas inclus resultats_v17 (36 Mo, historique public difficilement réversible), les lignes du .gitignore concernant le projet téléphone, ni les fichiers de sauvegarde.

## 5. Nettoyage de ~/calculs et rattachement de trois rapports

Trois dossiers de run du 17/10 (27 Mo chacun) avaient été écrits dans *~/calculs/* à cause du piège de l'action 0 : déplacés vers le dossier calculs du dépôt (aucune donnée supprimée), le dossier vide a été supprimé. Les trois rapports (933, 939 et 1 008 z/s, 138 069 zéros, Turing complet) ont été rattachés à leur CSV puis régénérés.

## 6. TUI de suivi : diagnostic de l'id « 105 » et touche r

Instructions de hprzeta (extrait verbatim de l'énoncé en quatre tâches) :

> TÂCHE 1 — Diagnostic de l'id « 105 » (lecture seule) ... STOP : j'attends ma décision avant de modifier le moteur de calcul.
> TÂCHE 2 — Correctif d'affichage ... libellé normalisé = index d'ordre W0..W(n-1), id brut entre parenthèses si différent ... retour à la ligne par groupes selon la largeur du terminal.
> TÂCHE 3 — Touche r : rapport + capture ... un PDF ReportLab expliquant, pour CE run, en français ... un verdict simple (sain / à surveiller) avec les critères affichés ... un glossaire débutant → expert.
> TÂCHE 4 — Rangement ... déposer capture + PDF dans le dossier de CE run ... Ne pas écraser un rapport existant (suffixe horodaté).
> STOP avant chaque commit : j'attends mon feu vert.

**Tâche 1 — conclusion :** l'id 105 n'est pas un neuvième worker. Le moteur v16 numérote les workers du rescan ciblé « 100 + segment » ; 105 est le rescan (pas divisé par deux) du segment 5, qui avait un déficit de un zéro. Les 153 000 affichés étaient 9 fois 17 000 paliers additionnés ; le résultat final n'a aucun doublon (138 069 zéros, zéro net après déduplication). Décision de hprzeta : moteur intact, base de rapport zeta_rapport.py.

**Constat sur la base demandée :** le fichier rapport_run.py n'existe pas dans le dépôt, et zeta_rapport.py est un générateur Markdown d'inventaire sans PDF ni capture ; j'ai repris sa convention de pied de page et le moteur PDF du monitoring.

| Tâche | Résultat |
|---|---|
| 2 | Rescans affichés à part (R5), totaux et barre sur les workers principaux : 136 000 sur 138 069 (98,5 %) au lieu de 153 000 ; détail à retour à la ligne ; anciens logs inchangés. |
| 3 | Touche r : capture PNG rendue depuis les appels d'affichage enregistrés (indépendant de Wayland), rapport Markdown et PDF de trois pages : verdict avec critères, chiffres, tableau par worker, lecture de chaque élément de l'écran, signification exacte du jeton de détail, interprétation, glossaire. |
| 4 | Run actif détecté (statut en cours, pas de fichier de fin, superviseur vivant) ; sans run actif : message, rien d'écrit ; jamais d'écrasement ; chemin affiché dans la TUI. Testé sur deux runs prod réels. |

**Défaut trouvé au test réel :** le critère de déséquilibre entre workers donnait « à surveiller » à tort en cours de run (vitesses différentes, segments égaux en zéros) ; il est devenu une simple information.

## 7. Sortie du projet téléphone / médias du projet Zêta

Demande de hprzeta : compresser et déplacer le dossier du projet parenthèse dans un sous-dossier « autre_projet », mettre à jour le Handoff avec le sujet non traité, enlever toute référence dans le projet Zêta.

- **Constat :** le dossier du dépôt était un lien symbolique vers 26 Go de médias déjà sur le disque de données.
- **Décisions de hprzeta (questions posées) :** déplacement sans compression (médias déjà compressés) ; nettoyage des fichiers vivants seulement, archives datées et historique git conservés.
- **Fait :** contenu entier déplacé dans le sous-dossier autre_projet (8 714 fichiers, 79 dossiers, 27 237 302 489 octets identiques avant et après), 10 scripts et l'archive du 11/10 rangés avec ; lien, lignes du .gitignore et exclusions locales supprimés ; trois blocs du Handoff retirés et une section « sujet non traité » ajoutée ; mémoire nettoyée.
- **Conservé volontairement :** les mentions « téléphone » du wiki concernent le pair WireGuard du cluster, pas ce projet ; l'archive du 10/10 garde ses mentions (historique).
- **Point de sécurité resté ouvert :** les images conservées contiennent des captures avec un jeton DuckDNS et des chaînes ressemblant à des clés WireGuard ; la rotation du jeton figure parmi les points ouverts.

## 8. État de fin de session

| Branche | Commit |
|---|---|
| Riemann_Lab_IA / Riemann_Lab_C | f148864 |
| main | 47c5e25 |
| Riemann_Lab_Test | b1cdfa2 |

Non commités et laissés de côté : resultats_v17 (36 Mo), fichiers de sauvegarde, la présente archive. Le logger de métriques (zeta-mon-on) tourne encore et ne redémarre pas seul après un redémarrage de la machine.

**Prochaine action :** zéros manquants à grande hauteur (5 à T=400 000 en v16) ; décider v16 ou v17 pour le prochain gros run ; puis les points inchangés (sort de zeta_webmonitor, durcissement sudoers, V17 D4 et run T=5M, rotation du jeton DuckDNS).

---

# Partie B — seconde session du jour (capture 18h53) : publication de PDF du cluster

## 9. Enquête en lecture seule sur pdf/cluster/ et pdf/script/

Instruction de hprzeta (extrait verbatim) :

> MODE LECTURE SEULE — aucun add, commit, push, déplacement ni suppression. [...] Dis-moi s'il est : (a) ignoré par une règle (laquelle, quelle ligne de quel fichier), (b) simplement jamais ajouté, (c) présent sur une autre branche. [...] Termine par un tableau : fichier | statut git | décision proposée | raison. Puis écris STOP et attends ma validation avant toute action git.

**Constat (fait établi) :** les deux dossiers sont ignorés par le fichier d'exclusion local du clone (lignes 21 et 22), pas par le .gitignore versionné ; aucun commit ne les a jamais touchés, sur aucune des sept branches. Aucune règle écrite ne justifiait l'exclusion : le motif probable (adresses réseau) était une hypothèse, confirmée ensuite par hprzeta.

| Fichier | Taille | Motifs sensibles repérés dans le texte | Décision proposée |
|---|---|---|---|
| cluster / guide de distribution PC1+PC2 | 1,7 Mo | aucun | pousser, après contrôle visuel |
| cluster / document VPN enrichi (2 versions) | 100 Ko et 612 Ko | IP publique et privées, DuckDNS, e-mail | garder local |
| script / guide scripts du 17/10 | 193 Ko | 5 IP internes, 1 mention DuckDNS | version publiable à produire |
| script / guides du 04/10 et du 20/09 | 149 Ko et 21 Ko | idem, anciennes versions | garder local |
| script / deux copies de sauvegarde | – | doublons exacts (même empreinte) | garder local |

Les fichiers du dossier script sont des PDF, pas des scripts : il n'y avait donc aucun doublon à comparer avec les dossiers de scripts du dépôt.

## 10. Étape 1 — guide de distribution : publié

Feu vert de hprzeta pour ce seul fichier ; ligne 22 de l'exclusion à ne pas retirer (elle protège les deux documents VPN). Contrôle demandé : rasteriser toutes les pages et regarder chacune.

- **Contrôle visuel :** 12 pages, dont 5 captures de bureau regardées en pleine résolution. Aucune IP, adresse MAC, e-mail, clé, jeton, domaine DDNS ni QR code. Visibles : les noms de machines, le nom d'utilisateur dans la barre de titre du terminal, l'URL SSH du dépôt public, des noms de journaux, la jauge de quota de l'assistant.
- **Point de jugement :** ces noms de machines et ce nom d'utilisateur figurent déjà dans 88, 34 et 9 fichiers publics du dépôt ; ce n'est donc pas une nouvelle exposition. Le PDF est anonyme (auteur et titre vides), sans pièce jointe ni lien.
- **Revue de sécurité du projet :** checklist sur le texte vide ; verdict vert.
- **Ajout :** forcé pour ce seul fichier ; la règle d'exclusion est restée intacte. Une règle par fichier (exclure le dossier sauf ce guide) a été proposée, non appliquée.
- **Commit local :** be37a27.

## 11. Étape 2 — version publiable du guide scripts

Instruction : reprendre la méthode du skill de diagnostic et de son script de publication, ne pas modifier l'original, produire une variante avec placeholders, l'écrire dans un dossier versionné avec le suffixe _public, proposer l'emplacement avant d'écrire.

- **Méthode reprise :** masquage par motif puis contrôle résiduel bloquant, version publiable jamais éditée à la main, bandeau « version publiable ». Non applicable : le nommage et le gabarit des diagnostics, et leur dossier de destination (le guide n'est pas un diagnostic).
- **Résultat :** 5 adresses remplacées par des placeholders nommés (une par machine, deux pour le bastion), 1 mention DuckDNS par un placeholder de domaine DDNS. Contrôle du PDF final : 0 IPv4, 0 domaine, 0 adresse MAC, 0 e-mail, 0 clé ; 30 pages, mise en page identique ; seul le tableau de la page 1 est plus haut.
- **Points laissés tels quels sur décision de hprzeta :** le compte de sauvegarde de PC3 (16 occurrences, déjà présent dans 3 fichiers publics) et les chemins de sauvegarde Proton.
- **Emplacement validé par hprzeta :** un nouveau dossier distinct du dossier exclu, sur la branche Riemann_Lab_IA ; aucune modification de l'exclusion.

**Erreur de ma part, rattrapée avant publication :** au moment du « go push », l'audit des lignes ajoutées a montré que mon script de génération contenait **en clair les 5 IP et le mot DuckDNS** dans sa liste de remplacements, car il cherchait des valeurs exactes. Mon contrôle de l'étape 2 portait sur les PDF, pas sur le code. Rien n'était parti sur GitHub. Correction après accord de hprzeta : remplacement par position (colonne d'adresses du tableau des machines) et par motif, sans aucune valeur réelle dans le code, avec arrêt si les cinq lignes machines ne sont pas toutes trouvées (testé sur une source volontairement cassée) ; réécriture des deux commits locaux jamais poussés ; PDF régénéré, texte identique à celui déjà contrôlé. Commits : 41c6724 (script) et 6d95c4f (PDF). Les deux anciens commits n'existent plus que dans le journal local des références.

## 12. Étape 3 — convention documentée dans le wiki

Section 3b de ORGANISATION_FICHIERS.md : les deux dossiers sont locaux et hors git (lignes 21 et 22 de l'exclusion, adresses réseau) ; exceptions poussées (guide de distribution, version _public du guide scripts) ; règle « toute publication passe par la revue de sécurité et un contrôle visuel ». Pied de page mis à jour (18/10/2026, 169 lignes, comptage vérifié). Un lien vers une page non suivie du wiki a été remplacé par du texte pour éviter un lien cassé en ligne. Commit wiki : 9a4b5ee.

## 13. Push et vérification en ligne

Audit complet de tous les commits à pousser (texte et contenu des deux PDF) : seul résultat, le motif de détection de clés dans le script, pas une valeur. Push du dépôt de code (f148864 vers 6d95c4f) puis du wiki (2ff8060 vers 9a4b5ee), sans --force. Contrôle en ligne : le script publié ne contient aucune adresse ; seuls deux PDF sont présents dans les dossiers concernés (le guide de distribution et la version _public) ; les dossiers exclus ne sont pas partis.

| Fichier | Commit | Poussé |
|---|---|---|
| Guide de distribution PC1+PC2 | be37a27 | oui |
| Script de génération de la version publiable | 41c6724 | oui |
| Guide scripts du 17/10, version _public | 6d95c4f | oui |
| Section 3b du wiki | 9a4b5ee | oui |

## 14. État de fin de session (partie B)

| Branche | Commit |
|---|---|
| Riemann_Lab_IA | 6d95c4f (poussé) |
| Riemann_Lab_C | f148864 (non touchée) |
| main | 47c5e25 (non touchée) |
| Riemann_Lab_Test | b1cdfa2 (non touchée) |
| wiki (master) | 9a4b5ee (poussé) |

Les PDF et le script de cette partie ont été commités depuis Riemann_Lab_IA uniquement, conformément à la convention (PDF et scripts d'infrastructure sur cette branche) ; ils ne sont pas propagés aux autres branches.

**Restent ouverts :** la page Dossier-md du wiki n'est toujours pas suivie ; le commentaire d'en-tête du guide scripts privé affirme encore que le dossier script n'est pas exclu (devenu faux) ; le compte de sauvegarde, les chemins Proton et les noms de clés SSH restent dans la version publique (choix de hprzeta) ; les points de la partie A (zéros manquants à grande hauteur, v16 ou v17, sudoers, rotation du jeton DuckDNS) sont inchangés. Cette archive, ses copies de sauvegarde (.bak) et les captures brutes ne sont pas commitées.

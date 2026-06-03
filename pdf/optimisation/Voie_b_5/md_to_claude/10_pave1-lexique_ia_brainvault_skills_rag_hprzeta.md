## 10 Pilier1 **Lexique IA & Brain Vault — Manuel vivant hprzeta / Riemann_Lab** 

Version initiale — à enrichir au fil des discussions, des audits, des scripts et des phases Riemann_Lab. Ce PDF sert de guide lexical pour parler le même langage autour de Vault, Skills, RAG, agents, modèles locaux, recovery et Phase C. 

## **Principe** 

Ce document est un dictionnaire opérationnel, pas un glossaire abstrait. Chaque terme est relié au projet hprzeta : calcul expérimental des zéros, documentation, récupération système, IA locale, RAG, scripts, Git et migration. 

**Règle importante : ce lexique aide à structurer la mémoire et l’assistance IA. Il ne doit jamais transformer un résultat numérique ou une conjecture en preuve mathématique.** 

## **1. Organisation recommandée dans le Brain Vault** 

brain-vault/ ├── 00_index/ 

- │   └── index_general.md ├── 01_lexique/ 

- │   ├── lexique_ia_hprzeta.md 

- │   ├── lexique_riemann_lab.md 

- │   └── acronyms.md 

- ├── 02_math_zeta/ 

- │   ├── validation/ 

- │   ├── formules/ 

- │   └── limites_et_conjectures.md 

├── 03_code/ 

- │   ├── versions/ 

- │   ├── phase_c/ 

- │   └── runbooks/ 

- ├── 04_ia_locale/ 

- │   ├── ollama.md 

- │   ├── rag.md 

- │   ├── skills.md 

- │   └── prompts.md ├── 05_data_runs/ 

- │   ├── validated/ 

- │   ├── raw_benchmarks/ 

- │   └── manifests/ 

- └── 06_recovery/ 

- ├── audit_systeme.md 

- ├── restore_git.md 

└── bootstrap_ubuntu24.md 

But : séparer les notions générales, les preuves/limites mathématiques, les scripts, les runs numériques, l’IA locale et la récupération système. 

## **2. Familles lexicales** 

|Famille|Termes principaux|Usage dans hprzeta|
|---|---|---|
|Mémoire / Vault|Vault, Brain Vault, note atomique,<br>provenance, manifest|Organiser les connaissances, les scripts, les décisions<br>et les preuves de contexte.|
|IA / LLM|LLM, modèle local, Ollama, prompt,<br>hallucination, grounding|Assistance, explication, génération de scripts, aide à<br>la documentation.|
|RAG|Corpus, chunk, embeddings, vector store,<br>retrieval, reranking, citation|Faire répondre l’IA à partir du dépôt, des PDF, du wiki<br>et des logs.|
|Agents / Skills|Skill, agent, outil, MCP, runbook, workflow|Transformer des tâches répétables en procédures<br>fiables.|
|Recovery|Audit, archive, checksum, bundle, restore,<br>bootstrap|Recréer l’environnement Linux et protéger les<br>branches Git.|
|Riemann_Lab|Run, T_MAX, Z_batch, Phase C, Illinois C,<br>validation|Relier les mots IA au calcul numérique réel du projet.|



## **3. Lexique essentiel IA / Vault / RAG** 

## **Vault** 

Coffre de connaissances structuré. Dans hprzeta, le Vault regroupe les notes, décisions, scripts, rapports, preuves de contexte et runbooks. 

## **Brain Vault** 

Version orientée mémoire longue du Vault. C’est le cerveau documentaire : ce que le projet sait, pourquoi il le sait, et où retrouver la source. 

## **Note atomique** 

Petite note autonome décrivant une seule idée, une seule décision ou un seul terme. Elle facilite la recherche et le RAG. 

## **Provenance** 

Information sur l’origine d’un fait : fichier, log, commit, PDF, date, auteur ou contexte. Indispensable pour éviter les confusions. 

## **Manifest** 

Fichier d’inventaire qui décrit un lot : date, contenu, chemins, hash, objectif, limites. Exemple : manifest d’export ou d’audit. 

## **Corpus** 

Ensemble de documents utilisé pour l’analyse ou le RAG : PDF, Markdown, scripts, logs, CSV, wiki. 

## **RAG** 

Retrieval-Augmented Generation : méthode où l’IA cherche d’abord dans un corpus, puis répond avec les passages trouvés. 

## **Ingestion** 

Étape qui transforme des fichiers en documents indexables : lecture, nettoyage, découpage, métadonnées. 

## **Chunk** 

Morceau de document. Un fichier long est découpé en chunks pour être recherché plus efficacement. 

## **Embeddings** 

Vecteurs numériques représentant le sens d’un texte. Ils permettent la recherche sémantique. 

## **Vector store** 

Base où sont stockés les embeddings et les métadonnées. Sert à retrouver les chunks pertinents. 

## **Retrieval** 

Recherche des passages utiles dans le corpus avant génération de réponse. 

## **Reranking** 

Deuxième tri des résultats récupérés pour garder les passages les plus pertinents. 

## **Grounding** 

Ancrage de la réponse dans des documents vérifiables. Opposé à une réponse inventée. 

## **Citation** 

Lien ou référence vers la source utilisée. Dans hprzeta, une réponse sérieuse cite log, PDF, script ou commit. 

## **Hallucination** 

Réponse plausible mais non fondée. À combattre par provenance, citations, tests et logs. 

## **LLM** 

Large Language Model. Modèle de langage capable d’expliquer, résumer, coder, reformuler, mais pas de garantir seul la vérité. 

## **Modèle local** 

LLM exécuté sur la machine locale, par exemple via Ollama. Avantage : confidentialité et disponibilité hors cloud. 

## **Ollama** 

Service local qui sert des modèles comme phi3:mini, qwen3:4b, mathstral ou deepseek-coder. 

## **Prompt** 

Instruction envoyée à l’IA. Un bon prompt décrit rôle, contexte, objectif, contraintes et format attendu. 

## **Prompt de reprise** 

Prompt qui permet de reprendre une session longue avec état, objectifs et fichiers à considérer. 

## **Contexte** 

Informations disponibles pour répondre : conversation, fichiers, logs, PDF, mémoire projet. 

## **Fenêtre de contexte** 

Quantité maximale de texte qu’un modèle peut prendre en compte en une fois. 

## **Skill** 

Compétence formalisée : procédure, règles, outils et style pour une tâche répétable. 

## **Agent** 

Assistant qui suit un objectif, utilise des outils, lit des fichiers et produit des actions en plusieurs étapes. 

## **MCP** 

Model Context Protocol : approche permettant de connecter un assistant à des outils ou sources de contexte de manière standardisée. 

## **4. Lexique Recovery / Git / Scripts** 

## **Audit système** 

Inventaire d’une machine avant migration : OS, partitions, RAM, GPU, services, paquets, Python, Git, scripts, modèles IA. 

## **Archive complète** 

Sauvegarde volumineuse, par exemple hprzeta_system_audit_*.tar.gz. Elle reste locale et ne doit pas être commitée. 

## **Résumé d’archive** 

Fichier texte listant le contenu d’une archive sans l’extraire entièrement. Exemple : assistant_pack_audit_resume_global_v2.txt. 

## **Extraction ciblée** 

Extraction limitée aux fichiers utiles, par exemple hardware, configs, python, services, git, manifests. 

## **Checksum / SHA256** 

Empreinte de fichier. Sert à vérifier qu’une archive n’a pas changé. 

## **Git bundle** 

Fichier unique contenant un dépôt Git ou toutes ses branches. Très utile avant réinstallation. 

## **Branche** 

Ligne de développement Git. Dans Riemann_Lab : main, Riemann_Lab_IA, Riemann_Lab_C, Riemann_Lab_Test. 

## **Branche en avance** 

Branche locale avec des commits non poussés. Riemann_Lab_Test était en avance de 14 commits dans le mini-audit. 

## **Untracked files** 

Fichiers présents dans le dossier mais non suivis par Git. À trier avant commit. 

## **.gitignore** 

Fichier qui indique ce que Git ne doit pas suivre : archives, fichiers locaux, données temporaires. 

## **Bootstrap** 

Script qui prépare une machine neuve : paquets, dossiers, venv, Git, Ollama, dépendances C. 

## **Runbook** 

Procédure reproductible étape par étape. Exemple : tester Phase C ou restaurer la branche C. 

## **Artifact** 

Produit généré : PDF, log, CSV, PNG, .so, bundle, archive. 

## **Source of truth** 

Source de référence. Pour les zéros validés, source = CSV + log + hash + rapport. 

## **5. Lexique Riemann_Lab / Phase C** 

## **Run numérique** 

Exécution datée d’un calcul : paramètres, version, durée, nombre de zéros, logs, sorties. 

## **T_MAX** 

Borne supérieure de recherche des zéros. Exemples : T=1000 ou T=10000. 

## **Zéro non trivial** 

Zéro de la fonction zêta dans la bande critique. Les calculs du projet portent sur les parties imaginaires sur la droite critique. 

## **Hardy Z(t)** 

Fonction réelle utilisée pour repérer les changements de signe liés aux zéros sur la droite critique. 

## **Riemann-Siegel** 

Formule utilisée pour calculer efficacement Z(t) à grande hauteur. 

## **Z_batch** 

Version vectorisée de Z(t) via NumPy/CuPy pour accélérer la détection. 

## **theta_rapide** 

Module calculant rapidement la phase θ(t) via approximation asymptotique et fallback exact. 

## **Illinois** 

Méthode d’affinage de racine utilisée après détection d’un changement de signe. 

## **MPFR** 

Bibliothèque de précision multiple utilisée en C pour accélérer l’affinage Illinois. 

## **Phase C** 

Phase d’optimisation C/libmpfr. Elle porte notamment illinois_mpfr.c, z_function.c, Makefile, test_illinois.py et benchmark_illinois.py. 

## **illinois_mpfr.so** 

Bibliothèque partagée compilée depuis le C. Elle doit être reproductible par make. 

## **test_illinois.py** 

Script de validation du module C contre des références connues. 

## **benchmark_illinois.py** 

Script de comparaison de performance entre affinage C/libmpfr et Python/mpmath. 

## **Turing-Backlund** 

Critère/contrôle de complétude pour vérifier qu’aucun zéro n’a été oublié dans un intervalle. 

## **LMFDB check** 

Comparaison des premiers zéros calculés avec des valeurs de référence. 

## **Surplus Turing** 

Écart signalé dans certains logs : à documenter sans le cacher, possiblement lié à une convention de comptage ou correction S(T). 

## **6. Règles d’enrichissement du dictionnaire** 

- Chaque nouveau terme doit avoir une définition simple, une définition projet, un exemple et une source si possible. 

- Ne pas mélanger terme général et décision locale : par exemple RAG est général, mais rag_ingest_riemann_lab_c.py est local au projet. 

- Ajouter une date quand un terme dépend d’un état du projet : branche active, nom de fichier, script, version. 

- Taguer les termes : #ia, #rag, #vault, #git, #recovery, #phase-c, #zeta, #python, #gpu. 

- Si un terme est incertain, le marquer « à vérifier » plutôt que l’écrire comme vérité. 

- Quand un terme vient d’un log ou d’un script, conserver le chemin source. 

## **Modèle de fiche lexicale** 

# Terme : <nom> 

## Définition courte ... 

## Dans hprzeta / Riemann_Lab ... 

## Exemple concret ... 

## À ne pas confondre avec 

... 

- ## Sources / fichiers liés - chemin/fichier 

- commit ou date 

## Tags #ia #rag #phase-c 

## **7. Lexique minimal à créer en Markdown** 

mkdir -p brain-vault/01_lexique cat > brain-vault/01_lexique/lexique_ia_hprzeta.md <<'EOF' # Lexique IA hprzeta 

Ce fichier est le dictionnaire vivant du projet. Il évolue au fil des discussions, audits, scripts, PDF et phases Riemann_Lab. 

## Termes à suivre 

- Vault 

- Brain Vault 

- RAG 

- Embeddings 

- Vector store 

- Skill 

- Agent 

- MCP 

- Ollama 

- Grounding 

- Hallucination 

- Provenance 

- Manifest 

- Git bundle - Phase C EOF 

## **8. Priorités d’enrichissement pour les prochaines discussions** 

|Priorité|Contenu à ajouter|Pourquoi|
|---|---|---|
|1|Lexique Phase C complet|Nous allons tester C/libmpfr ce soir.|
|2|Lexique Recovery / migration|Pour réinstallation Ubuntu et restauration Git.|
|3|Lexique RAG local|Pour construire le cerveau documentaire.|
|4|Lexique prompt engineering|Pour stabiliser les reprises de session.|
|5|Lexique validation numérique|Pour distinguer expérience, preuve, conjecture,<br>benchmark.|



## **9. Mini-manuel de lecture rapide** 

- Si je dis « mets-le dans le Vault », cela signifie : créer une note durable, datée, sourcée, reliée à l’index. 

- Si je dis « source of truth », cela signifie : fichier ou ensemble de fichiers à considérer comme référence officielle. 

- Si je dis « RAG », cela signifie : réponse augmentée par recherche dans les documents du projet, pas simple mémoire de conversation. 

- Si je dis « Skill », cela signifie : procédure réutilisable, pas seulement une compétence vague. 

- Si je dis « runbook », cela signifie : suite de commandes testables et ordonnées. 

- Si je dis « artifact », cela signifie : résultat matériel généré, à classer et éventuellement hasher. 

- Si je dis « hallucination », cela signifie : affirmation non appuyée par source, log, test ou calcul. 

- Si je dis « grounding », cela signifie : ancrer la réponse dans des éléments fournis ou vérifiables. 

- Si je dis « Phase C », cela signifie : optimisation C/libmpfr autour d’Illinois, z_function et compute_zeros_v4.py. 

## **10. Rappel éthique et scientifique du projet** 

**Le lexique doit aider à rendre le projet plus clair et plus fiable. Il ne doit pas donner une apparence de preuve à des résultats expérimentaux. Dans Riemann_Lab, on distingue toujours : calcul expérimental, validation numérique, documentation, conjecture, preuve formelle. Cette distinction doit rester dans le Vault, les PDF, les scripts et les réponses IA.** 

## **11. Prochaine action proposée** 

Après ce PDF, créer une version Markdown synchronisée dans brain-vault/01_lexique/lexique_ia_hprzeta.md, puis l’enrichir à chaque session avec les nouveaux termes rencontrés. 


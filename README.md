# Inbox IA — staging public pour lecture par Claude

> Branche ORPHELINE, isolee du graphe de merge. PUBLIQUE et a historique permanent.

## Regle d'or
- On ne depose ICI QUE du safe-a-etre-public-pour-toujours.
- JAMAIS de secret (.mcp.json, token, cle) ni de log a chemins/identifiants sensibles.
  Ces fichiers-la se collent dans le chat Claude (zero trace), pas ici.
- git rm + archive = rangement, PAS confidentialite (l'historique git conserve tout).

## Workflow
1. git checkout inbox-ia
2. copier les fichiers a lire :  cp ~/chemin/fichier.md .
3. git add -A && git commit -m "inbox: pave du $(date +%F)" && git push origin inbox-ia
4. dire a Claude : « lis la branche inbox-ia »
5. une fois traite :
   mkdir -p ~/archive_ia/$(date +%Y%m%d) && cp *.md ~/archive_ia/$(date +%Y%m%d)/
   git rm *.md && git commit -m "inbox: archive + clear du $(date +%F)" && git push origin inbox-ia
6. git checkout Riemann_Lab_C  (retour au travail)

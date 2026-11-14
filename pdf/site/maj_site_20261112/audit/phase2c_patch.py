#!/usr/bin/env python3
# Patch après phase2b : [[texte\|page]] de Structure-Projet-Complet (cibles valides, vérifiées en ligne : a.internal.present)
import csv
p='liens_statut_final.csv'; r=list(csv.DictReader(open(p,encoding='utf-8')))
for x in r:
    if x['source'].endswith('Structure-Projet-Complet.md') and x['ligne'] in ('151','152'):
        x.update(statut='🟢',action='',note='[[texte\\|page]] : cibles Animations / Guide-Ollama-Pratique (a.internal.present)')
    if x['source'].endswith('zeta_demovisualisation.html'):
        x['note']=(x['note']+' ; ' if x['note'] else '')+'code tiers Plotly minifié'
w=csv.DictWriter(open(p,'w',newline='',encoding='utf-8'),fieldnames=list(r[0].keys())); w.writeheader(); w.writerows(r)

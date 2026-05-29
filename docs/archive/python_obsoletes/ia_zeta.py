#!/usr/bin/env python3
"""
AUTEUR : hprzeta- Exploration de l'Hypothèse de Riemann
DATE : 2026
"""
import requests
import json

def question_ia(prompt):
    """Envoie une question à Ollama et retourne la réponse"""
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'mathstral',
            'prompt': prompt,
            'stream': False
        }
    )
    return response.json()['response']

# Test
# reponse = question_ia("Explique l'hypothèse de Riemann simplement")
# print(reponse)
print("-" * 50) 
# reponse = question_ia("Calcule une valeur approchée de ζ(2) avec une précision de 6 décimales et explique la méthode.")
reponse = question_ia("Calcule une valeur approchée de ζ(2) avec une précision de 6 décimales et affiche juste  le temps de  passer aux calculs et le résultat en franc ais sans aucun détail de plus. Ut lise l'affiche grec du symbole zêta(2) .")
print(reponse)
print("-" * 50) 

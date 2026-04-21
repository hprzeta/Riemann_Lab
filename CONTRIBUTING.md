# 🧭 Contribuer à projet_zeta

Toutes les bonnes pratiques Git & GitHub pour ce projet sont documentées dans le Wiki :

👉 **[Guide Git & GitHub — projet_zeta](https://github.com/hprzeta/projet_zeta/wiki/🧭-Guide-Git-GitHub)**

---

## En résumé

> **Principe fondamental : tout se fait en LOCAL, puis on pousse vers GitHub.**

```bash
# Dépôt principal
cd ~/projet_zeta
git add .
git commit -m "docs: description du changement"
git push

# Wiki
cd ~/projet_zeta/Riemann_Lab.wiki
git add "nom-de-la-page.md"
git commit -m "docs: description de la page"
git push origin master
```

---

## Tags de commit

| Tag | Usage |
|-----|-------|
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction de bug |
| `docs` | Documentation |
| `test` | Tests |
| `refactor` | Réécriture de code |
| `chore` | Maintenance |

---

*Voir le [guide complet](https://github.com/hprzeta/projet_zeta/wiki/🧭-Guide-Git-GitHub) dans le Wiki.*

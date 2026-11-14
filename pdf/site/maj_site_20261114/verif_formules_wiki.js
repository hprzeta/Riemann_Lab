// verif_formules_wiki.js — détecteur de formules non rendues (wiki GitHub)
// RÉÉCRIT le 14/11/2026 à partir du prompt (l'original, issu du zip, est introuvable).
// STATUT : non validé — à comparer au bilan du 13/11 (20 zones rouges, 9 pages).
// Test 14/11 : Ch08 → rendu GitHub différé géré (attente max 8 s) ; 4 zones attendues (n°12-15).
// Lecture du résultat : exécuter le script, puis lire window.__vf.
// Usage : coller dans la console / outil javascript d'une page de wiki GitHub.
// Résultat : objet { page, rouges, verts, blocs, details[] } ; zones rouges = formule non rendue.
(async () => {
  // Nettoyage d'un éventuel passage précédent (rend le script ré-exécutable)
  document.querySelectorAll('[data-vf]').forEach(e => {
    e.style.outline = ''; e.style.background = ''; e.removeAttribute('data-vf');
  });
  // Zone de contenu du wiki
  const corps = document.querySelector('.markdown-body');
  if (!corps) return { erreur: 'aucun .markdown-body sur cette page' };

  // GitHub rend les formules en différé : attendre que chaque <math-renderer> contienne son rendu
  const fini = () => [...corps.querySelectorAll('math-renderer')].every(m => m.querySelector('.katex, mjx-container, svg, math'));
  for (let i = 0; i < 40 && !fini(); i++) await new Promise(r => setTimeout(r, 200));

  const details = [];
  let rouges = 0, verts = 0;
  const blocs = new Set();

  // Marque un élément (cadre rouge ou vert) et mémorise le bloc parent
  const marquer = (el, couleur, extrait) => {
    el.setAttribute('data-vf', couleur);
    el.style.outline = `3px solid ${couleur === 'rouge' ? '#e00' : '#0a0'}`;
    el.style.background = couleur === 'rouge' ? 'rgba(255,0,0,.12)' : 'rgba(0,200,0,.10)';
    const bloc = el.closest('p,li,blockquote,td,th,h1,h2,h3,h4,h5,h6') || el;
    if (couleur === 'rouge') {
      blocs.add(bloc);
      details.push({ n: details.length + 1, bloc: bloc.tagName.toLowerCase(), extrait: extrait.slice(0, 100) });
    }
  };

  // 1) Formules RENDUES : <math-renderer> (GitHub) avec contenu KaTeX/MathML/SVG, sans erreur
  corps.querySelectorAll('math-renderer, .js-inline-math, .js-display-math').forEach(m => {
    const txt = m.textContent || '';
    const erreur = m.querySelector('.katex-error, .color-fg-danger') || /unable to render|erreur/i.test(txt);
    const rendu = m.querySelector('.katex, .katex-mathml, mjx-container, svg, math');
    if (erreur || !rendu) { rouges++; marquer(m, 'rouge', 'rendu en erreur : ' + txt); }
    else { verts++; marquer(m, 'vert', txt); }
  });

  // 2) Formules NON rendues : texte brut contenant encore $...$ ou des commandes LaTeX
  const reDollar = /\$[^$\n]+\$|\$`[^`]+`\$/;
  const reLatex = /\\(?:mathbb|tfrac|frac|sigma|zeta|gamma|theta|sum|infty|cong|setminus|times|arg|text|Gamma|pi)\b|[\^_]\{/;
  const marche = document.createTreeWalker(corps, NodeFilter.SHOW_TEXT, {
    acceptNode: n => {
      const p = n.parentElement;
      if (!p) return NodeFilter.FILTER_REJECT;
      // On ignore le code (légitime), les formules déjà rendues et les marques posées
      if (p.closest('pre, code, math-renderer, .katex, mjx-container, script, style, [data-vf]')) return NodeFilter.FILTER_REJECT;
      return (reDollar.test(n.nodeValue) || reLatex.test(n.nodeValue)) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
    }
  });
  const noeuds = [];
  while (marche.nextNode()) noeuds.push(marche.currentNode);
  noeuds.forEach(n => {
    const el = n.parentElement;
    rouges++;
    marquer(el, 'rouge', n.nodeValue.trim());
  });

  // Défile jusqu'à la première zone rouge pour la montrer à l'écran
  const premier = document.querySelector('[data-vf="rouge"]');
  if (premier) premier.scrollIntoView({ block: 'center' });

  // Résultat exposé aussi dans window.__vf (l'outil javascript ne renvoie pas toujours une promesse)
  window.__vf = { page: location.pathname.split('/').pop(), rouges, verts, blocs: blocs.size, details };
  return window.__vf;
})();

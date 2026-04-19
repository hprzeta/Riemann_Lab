<html><head></head><body><h2>Théorie rapide</h2>
<h3>1- La fonction $$\zeta(s)$$  zêta de Riemann</h3>
<p><strong>Définition:</strong></p>
<p>$$\zeta(s) = \sum_{n=1}^{\infty} \tfrac{1}{n^s}$$</p>
<p>Où $S= \left( \sigma + it\right)$, est un <strong>nombre complexe</strong>  tel que ($\sigma$ = partie réelle, $t$  = partie imaginaire)<br>
avec $\sigma$, $t$ $\in \mathbb{R}$ et $i$ = Imaginaire pure tel que <strong>$i^2$=−1</strong></p>
<blockquote>
<p>Définie pour $\text{Re}(s) &gt; 1$, puis étendue par prolongement analytique.</p>
</blockquote>
<blockquote>
<p>Exemple concret : Si s=2  (réel) :</p>
</blockquote>
<blockquote>
<p>$\zeta(2) = 1 + \frac{1}{4} + \frac{1}{9} + \frac{1}{16} + \cdots = \tfrac{6}{(\pi)^2} \approx 1.6449$</p>
</blockquote>
<blockquote>
<p>C'est le célèbre problème de Bâle résolu par Euler en 1734.</p>
</blockquote>
<blockquote>
<p>Euler a montré que $\zeta(s)=0$  pour $s$= −2,−4,−6,…  (zéros triviaux).</p>
</blockquote>
<blockquote>
<p>Mais Riemann a découvert d'autres zéros mystérieux .</p>
</blockquote>
<hr>
<h3>La Droite Critique et les Zéros Non-Triviaux</h3>
<p>Les zéros non triviaux de $\zeta(s)$ se situent dans la <strong>bande critique</strong> :</p>
<p>$$0 &lt; \text{Re}(s) &lt; 1$$</p>
<blockquote>
<p>Hypothèse de Riemann : Tous ces zéros vérifient $\text{Re}(s) = \tfrac{1}{2}$ — C'est la <em>droite critique</em>.</p>
</blockquote>
<blockquote>
<p>$\zeta(s)$ sur la  droite critique s'écrit :  $\zeta \left(\tfrac{1}{2} + it\right)$</p>
</blockquote>
<hr>
<h3>2- La fonction $$Z(t)$$ de Hardy-Riemann</h3>
<p><strong>Définition:</strong></p>
<p>$$Z(t) = e^{i\theta(t)} \cdot \zeta \left(\tfrac{1}{2} + it\right) \in \mathbb{R}$$</p>
<h3>Propriétés fondamentales</h3>

Propriété | Énoncé
-- | --
Réalité | $Z(t) \in \mathbb{R}$ pour tout $t \in \mathbb{R}$
Zéros | $Z(t) = 0 \iff \zeta \left(\tfrac{1}{2}+it\right) = 0$


<p>Pour trouver les zéros Non-Triviaux:</p>
<blockquote>
<p>La fonction  <strong>$Z(t)$</strong> est définie pour travailler sur la droite critique $\text{σ} = \tfrac{1}{2}$</p>
</blockquote>
<blockquote>
<p>Plus pratique à exploiter, où <strong>$θ(t)$</strong> est choisi pour que <strong>$Z(t)$</strong> soit réelle quand
$\zeta \left(\frac{1}{2}+it\right)$  est sur la droite critique .</p>
</blockquote>
<ul>
<li>$Z(t)$ est <strong>réelle</strong>, ce qui permet de capter les <strong>changements de signe</strong>.</li>
<li>Chaque changement de signe $\leftrightarrow$ un zéro de $\zeta$ sur la droite critique.</li>
<li>Du coup, au lieu de chercher quand un nombre complexe vaut zéro (ce qui est dur), on cherche
quand <strong>$Z(t)$</strong> change de signe — ce qui est beaucoup plus simple à calculer et à visualiser.</li>
</ul>
<blockquote>
<p>Grâce à la propriété de réalité, on peut détecter les zéros par <strong>changement de signe</strong> :
si $Z(a) &gt; 0$ et $Z(b) &lt; 0$, le <strong>Théorème des Valeurs Intermédiaires (TVI)</strong> garantit l'existence d'un zéro dans l'intervalle $]a, b[$.</p>
</blockquote>
<hr>
<h3>3- La fonction $\theta(t)$  thêta de Riemann-Siegel</h3>
<p><strong>Définition :</strong></p>
<p>$$\theta(t) = \text{Im}\ \left[\ln \Gamma\ \left(\sigma + it\right)\right] - \frac{t}{2}\ln(\pi)$$</p>
<p><strong>Rôle :</strong> c'est la « phase » de $\zeta\ \left(\tfrac{1}{2} + it\right)$.</p>
<p>La fonction <strong>θ(t)</strong> est simplement un angle (une phase) qui dépend d'un nombre réel t.</p>
<p>Autrement dit, <strong>θ(t)</strong> mesure de combien l'angle a tourné à l'instant t.</p>
<p>On l'utilise pour "redresser" la fonction zêta et la rendre plus facile à analyser.</p>
<blockquote>
<p>En multipliant $\zeta$ par $e^{i\theta}$, on annule la partie imaginaire et on obtient une fonction <strong>réelle</strong> $Z(t)$.</p>
</blockquote>
> [▶ Ouvrir l'animation interactive](https://hprzeta.github.io/Riemann_Lab/animation_theta.html)

<iframe src="https://hprzeta.github.io/Riemann_Lab/animation_theta.html" width="100%" height="420" frameborder="0"></iframe>
<p><strong>Interprétation :</strong></p>
<ul>
<li><strong>À gauche</strong> — $\zeta!\left(\tfrac{1}{2}+it\right)$ est un vecteur oblique dans $\mathbb{C}$ : partie réelle + partie imaginaire (rouge).</li>
<li><strong>À droite</strong> — après multiplication par $e^{i\theta(t)}$, le vecteur pivote exactement du bon angle et atterrit sur l'axe réel. Im = <strong>0</strong>.</li>
<li>En jouant sur le curseur $\theta$, on voit que $Z(t)$ reste <strong>toujours réel</strong>, quelle que soit la phase initiale.</li>
</ul>
<blockquote>
<p><strong>En une phrase :</strong> $\theta(t)$ est la phase naturelle de $\zeta$ ; multiplier par $e^{i\theta}$ contra-rotationne ce vecteur d'exactement cet angle, ce qui annule l'inclinaison et produit une fonction réelle $Z(t)$.</p>
</blockquote>
&lt;/details&gt;
<blockquote>
<p><strong>$\theta(t)$</strong> permet de réécrire la fonction <strong>$\zeta \left(\frac{1}{2}+it\right)$</strong> de Riemann sous une forme plus simple
puisque <strong>$\theta(t)$</strong> "enlève la rotation" du nombre complexe <strong>$\zeta$</strong> qui tourne à mesure que <strong>$\theta(t)$</strong> augmente avec
<strong>$t$</strong>.</p>
</blockquote>
<blockquote>
<p>Exemple concret:</p>
</blockquote>
<blockquote>
<p>$\zeta \left(\frac{1}{2} + it\right) = e^{-i\theta(t)} \cdot Z(t)$</p>
</blockquote>
<p><strong>Notation1 :</strong>  $$\text{Im}\ \left[\ln \Gamma\ \left(\sigma + it\right)\right]$$ dans <strong>$$\theta(t)$$</strong></p>
<ul>
<li>$\Gamma$ — fonction Gamma (généralisation de la factorielle aux réels)</li>
<li>$\text{Im}[...]$ — partie imaginaire d'un nombre complexe</li>
<li>$\ln$ —  logarithme de la fonction Gamma</li>
</ul>
<p>Cette notation est la partie imaginaire d'un logarithme de Gamma où la fonction
$\Gamma$ est une généralisation de la factorielle !.</p>
<blockquote>
<p>Exemple concret : Si $\Gamma$ =1, 2, 3, 4  (réel) :</p>
</blockquote>
<blockquote>
<p>$\Gamma(1)$ = 1, $\Gamma(2)$ = 1, $\Gamma(3)$ = 2, $\Gamma(4)$ = 6 ...</p>
</blockquote>
<blockquote>
<p>En gros, $\Gamma(n)= (n−1)!$ pour les entiers.</p>
</blockquote>
<p>Mais ici, on l'évalue en un nombre complexe : $\sigma$ + $it$.</p>
<blockquote>
<p>Capture la rotation due à la fonction Gamma.</p>
</blockquote>
<p><strong>Notation2 :</strong> $$\frac{t}{2}\ln\pi$$  dans <strong>$$\theta(t)$$</strong></p>
<ul>
<li>Une correction logarithmique</li>
</ul>
<blockquote>
<p>Corrige la dérive de phase liée à π. Ce terme soustrait une quantité qui grandit doucement avec t. Il compense la "croissance" naturelle de la phase $\theta(t)$ quand t augmente.</p>
</blockquote>
<hr>
<h2>🔗 Lien crucial : Factorielle ↔ Gamma ↔ Zêta de Riemann</h2>
<h3>La relation fondamentale</h3>
<p>$$\boxed{\Gamma(n+1) = n! \quad \text{pour } n \in \mathbb{N}}$$</p>
<h3>Pourquoi Γ et pas ! pour les complexes ?</h3>
<p>La factorielle $n!$ n'est définie que pour $n$ entier positif. <strong>Euler</strong> a trouvé la fonction $\Gamma(z)$ qui :</p>
<ol>
<li><strong>Interpolle</strong> la factorielle : $\Gamma(n+1) = n!$</li>
<li><strong>Prolonge</strong> aux nombres complexes (sauf pôles en $0, -1, -2, \ldots$)</li>
<li><strong>Apparaît</strong> dans l'équation fonctionnelle de $\zeta(s)$ !</li>
</ol>
<hr>
<h3>Dans l'équation fonctionnelle de $\zeta(s)$</h3>
<p>$$\pi^{-s/2} \Gamma\left(\frac{s}{2}\right) \zeta(s) = \pi^{-(1-s)/2} \Gamma\left(\frac{1-s}{2}\right) \zeta(1-s)$$</p>
<p><strong>Le rôle de Γ</strong> : "Complète" $\zeta(s)$ pour donner la symétrie parfaite $\xi(s) = \xi(1-s)$.</p>
<hr>
<h3>La fonction ξ complétée</h3>
<p>$$\xi(s) = \underbrace{\frac{1}{2} s(s-1)}<em>{\text{élimine pôles}} \underbrace{\pi^{-s/2} \Gamma\left(\frac{s}{2}\right)}</em>{\text{facteur "gamma"}} \zeta(s)$$</p>
<p>C'est ce facteur gamma qui <strong>"tord"</strong> le plan complexe pour révéler la symétrie cachée de Riemann !</p></body></html>

#!/bin/bash
# ==============================================================================
# backup_cluster_map.sh — Cartes memoire cluster Riemann_Lab
# Auteur : hprzeta · MAJ : 2026-06-13
# Usage  : bash backup_cluster_map.sh pipeline  > pipeline.svg
#          bash backup_cluster_map.sh topo      > topo.svg
#          bash backup_cluster_map.sh all       → genere les 2 fichiers SVG
# ==============================================================================

svg_pipeline() {
cat << 'SVGEOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="900" height="640" viewBox="0 0 900 640"
     xmlns="http://www.w3.org/2000/svg" font-family="monospace,sans-serif">
<title>Pipeline backup Riemann_Lab</title>
<rect width="900" height="640" fill="#ffffff"/>

<!-- TITRE -->
<rect x="0" y="0" width="900" height="52" fill="#f8f8f8"/>
<line x1="0" y1="52" x2="900" y2="52" stroke="#e0e0e0" stroke-width="1"/>
<text x="450" y="22" text-anchor="middle" font-size="17" font-weight="700" fill="#1a1a1a">Pipeline Backup — Riemann_Lab</text>
<text x="450" y="42" text-anchor="middle" font-size="12" fill="#666">zeta-icor7 → zeta-livermore8 → Proton Drive · automatique chaque nuit · hprzeta 2026-06-13</text>

<!-- ── ICOR7 ── -->
<rect x="30" y="68" width="250" height="240" rx="12" fill="#e1f5ee" stroke="#0f6e56" stroke-width="1.5"/>
<text x="155" y="90" text-anchor="middle" font-size="15" font-weight="700" fill="#085041">zeta-icor7</text>
<text x="155" y="108" text-anchor="middle" font-size="11" fill="#0f6e56">riemann@zeta-icor7</text>
<text x="155" y="124" text-anchor="middle" font-size="13" font-weight="700" fill="#085041">192.168.1.24</text>
<text x="155" y="140" text-anchor="middle" font-size="10" fill="#1d9e75">wifi · wlp2s0</text>

<rect x="44" y="150" width="222" height="16" rx="3" fill="#c5eedd" stroke="#1d9e75" stroke-width="0.7"/>
<text x="54" y="162" font-size="10" fill="#085041">~/projet_zeta/logs/      ~1.8 MB</text>
<rect x="44" y="170" width="222" height="16" rx="3" fill="#c5eedd" stroke="#1d9e75" stroke-width="0.7"/>
<text x="54" y="182" font-size="10" fill="#085041">~/projet_zeta/Riemann_Lab.wiki/  ~3.7 MB</text>
<rect x="44" y="190" width="222" height="16" rx="3" fill="#c5eedd" stroke="#1d9e75" stroke-width="0.7"/>
<text x="54" y="202" font-size="10" fill="#085041">~/projet_zeta/pdf/       ~7.1 MB</text>

<rect x="44" y="214" width="222" height="26" rx="6" fill="#a8dfc9" stroke="#0f6e56" stroke-width="0.8"/>
<text x="54" y="226" font-size="10" font-weight="600" fill="#04342c">~/.ssh/id_acer  (ed25519 · sans MDP)</text>
<text x="54" y="237" font-size="9" fill="#085041">ssh-keygen -t ed25519 -C icor7-to-acer-backup</text>

<rect x="44" y="248" width="222" height="50" rx="6" fill="#fff3d4" stroke="#ba7517" stroke-width="0.8"/>
<text x="54" y="261" font-size="10" font-weight="700" fill="#633806">CRON  01h50 * * *</text>
<text x="54" y="274" font-size="9" fill="#412402">rsync -aq -e 'ssh -i ~/.ssh/id_acer'</text>
<text x="54" y="286" font-size="9" fill="#412402">  logs/ wiki/ pdf/ → 192.168.1.22:~/backup/</text>
<text x="54" y="298" font-size="9" fill="#412402">  >> ~/backup/rsync.log 2>&amp;1</text>

<!-- ── ACER ── -->
<rect x="490" y="68" width="250" height="240" rx="12" fill="#eeedfe" stroke="#534ab7" stroke-width="1.5"/>
<text x="615" y="90" text-anchor="middle" font-size="15" font-weight="700" fill="#3c3489">zeta-livermore8</text>
<text x="615" y="108" text-anchor="middle" font-size="11" fill="#534ab7">pjexosql@zeta-livermore8</text>
<text x="615" y="124" text-anchor="middle" font-size="13" font-weight="700" fill="#3c3489">192.168.1.22</text>
<text x="615" y="140" text-anchor="middle" font-size="10" fill="#7f77dd">ethernet · 100 Mbit/s</text>

<rect x="504" y="150" width="222" height="16" rx="3" fill="#d9d7fc" stroke="#7f77dd" stroke-width="0.7"/>
<text x="514" y="162" font-size="10" fill="#26215c">~/backup/logs/</text>
<rect x="504" y="170" width="222" height="16" rx="3" fill="#d9d7fc" stroke="#7f77dd" stroke-width="0.7"/>
<text x="514" y="182" font-size="10" fill="#26215c">~/backup/wiki/</text>
<rect x="504" y="190" width="222" height="16" rx="3" fill="#d9d7fc" stroke="#7f77dd" stroke-width="0.7"/>
<text x="514" y="202" font-size="10" fill="#26215c">~/backup/pdf/</text>
<rect x="504" y="210" width="222" height="16" rx="3" fill="#d9d7fc" stroke="#7f77dd" stroke-width="0.7"/>
<text x="514" y="222" font-size="10" fill="#26215c">~/backup/rclone_cron.log</text>

<rect x="504" y="232" width="222" height="16" rx="3" fill="#f7c1c1" stroke="#e24b4a" stroke-width="0.7"/>
<text x="514" y="244" font-size="9" fill="#501313">Python 3.5 · crontab -e casse → (echo ...) | crontab -</text>

<rect x="504" y="254" width="222" height="44" rx="6" fill="#fff3d4" stroke="#ba7517" stroke-width="0.8"/>
<text x="514" y="267" font-size="10" font-weight="700" fill="#633806">CRON  02h00 * * *</text>
<text x="514" y="280" font-size="9" fill="#412402">/usr/bin/rclone copy ~/backup/</text>
<text x="514" y="292" font-size="9" fill="#412402">  protondrive:hprzeta/Riemann_Lab/backup/</text>

<!-- ── HP ── -->
<rect x="30" y="330" width="250" height="130" rx="12" fill="#f1efe8" stroke="#5f5e5a" stroke-width="1.2"/>
<text x="155" y="352" text-anchor="middle" font-size="15" font-weight="700" fill="#2c2c2a">zeta-hp3647h</text>
<text x="155" y="368" text-anchor="middle" font-size="11" fill="#5f5e5a">emmabuntus@zeta-hp3647h</text>
<text x="155" y="384" text-anchor="middle" font-size="13" font-weight="700" fill="#2c2c2a">192.168.1.94</text>
<text x="155" y="400" text-anchor="middle" font-size="10" fill="#888780">ethernet 1 Gbit/s · carte mere HP 3647h</text>
<rect x="44" y="408" width="222" height="16" rx="3" fill="#e5e3db" stroke="#b4b2a9" stroke-width="0.7"/>
<text x="54" y="420" font-size="9" fill="#2c2c2a">Noeud secondaire · scripts · config · stockage</text>
<rect x="44" y="428" width="222" height="16" rx="3" fill="#fce8e8" stroke="#f09595" stroke-width="0.7"/>
<text x="54" y="440" font-size="9" fill="#a32d2d">Pas de wiki/pdf/logs (tout sur zeta-icor7)</text>
<text x="155" y="456" text-anchor="middle" font-size="9" fill="#888">SSH → Acer : fingerprint accepte 2026-06-13</text>

<!-- ── PROTON DRIVE ── -->
<rect x="490" y="330" width="250" height="130" rx="12" fill="#faeeda" stroke="#ba7517" stroke-width="1.5"/>
<text x="615" y="352" text-anchor="middle" font-size="15" font-weight="700" fill="#633806">Proton Drive</text>
<text x="615" y="368" text-anchor="middle" font-size="10" fill="#854f0b">protondrive:hprzeta/Riemann_Lab/backup/</text>
<rect x="504" y="376" width="222" height="15" rx="3" fill="#f9d88a" stroke="#ef9f27" stroke-width="0.7"/>
<text x="514" y="387" font-size="10" fill="#412402">backup/logs/  +  backup/wiki/  +  backup/pdf/</text>
<rect x="504" y="396" width="222" height="15" rx="3" fill="#f9d88a" stroke="#ef9f27" stroke-width="0.7"/>
<text x="514" y="407" font-size="9" fill="#412402">Erreur 401 → rclone config reconnect protondrive:</text>
<rect x="504" y="416" width="222" height="15" rx="3" fill="#f9d88a" stroke="#ef9f27" stroke-width="0.7"/>
<text x="514" y="427" font-size="9" fill="#412402">Erreur 422 → normal (fichier existe, skip)</text>
<text x="615" y="452" text-anchor="middle" font-size="9" fill="#854f0b">Acces via rclone depuis zeta-livermore8</text>

<!-- ── FLECHES ── -->
<defs>
<marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
<path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</marker>
</defs>

<!-- icor7 → Acer (rsync) -->
<line x1="280" y1="188" x2="490" y2="188" stroke="#0f6e56" stroke-width="2.5" marker-end="url(#ah)"/>
<rect x="350" y="170" width="80" height="30" rx="4" fill="#e1f5ee" stroke="#0f6e56" stroke-width="0.8"/>
<text x="390" y="182" text-anchor="middle" font-size="10" font-weight="700" fill="#085041">rsync + SSH</text>
<text x="390" y="195" text-anchor="middle" font-size="9" fill="#0f6e56">01h50  -aq</text>

<!-- Acer → Proton Drive (rclone) -->
<line x1="615" y1="308" x2="615" y2="330" stroke="#534ab7" stroke-width="2.5" stroke-dasharray="6 3" marker-end="url(#ah)"/>
<text x="628" y="316" font-size="10" font-weight="700" fill="#3c3489">rclone</text>
<text x="628" y="328" font-size="9" fill="#534ab7">02h00</text>

<!-- HP → Acer (SSH manuel) -->
<path d="M155 460 L155 490 Q155 500 165 500 L615 500 Q625 500 625 460" fill="none" stroke="#888780" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#ah)"/>
<text x="390" y="515" text-anchor="middle" font-size="9" fill="#888">SSH manuel zeta-hp3647h → zeta-livermore8 (mot de passe)</text>

<!-- ── LEGENDE + STATUT ── -->
<line x1="0" y1="530" x2="900" y2="530" stroke="#e0e0e0" stroke-width="1"/>
<line x1="30" y1="548" x2="80" y2="548" stroke="#0f6e56" stroke-width="2.5" marker-end="url(#ah)"/>
<text x="88" y="552" font-size="10" fill="#333">rsync auto (cle SSH id_acer)</text>
<line x1="240" y1="548" x2="290" y2="548" stroke="#534ab7" stroke-width="2.5" stroke-dasharray="6 3" marker-end="url(#ah)"/>
<text x="298" y="552" font-size="10" fill="#333">rclone Proton Drive</text>
<line x1="490" y1="548" x2="540" y2="548" stroke="#888" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#ah)"/>
<text x="548" y="552" font-size="10" fill="#333">SSH manuel</text>

<text x="30" y="574" font-size="10" font-weight="600" fill="#0f6e56">✓ SSH sans MDP (id_acer ed25519 · 2026-06-13)  ✓ Cron icor7 01h50  ✓ Cron Acer 02h00  ✓ rclone OK</text>
<text x="30" y="590" font-size="10" font-weight="600" fill="#0f6e56">✓ Hostnames zeta- uniformises : zeta-icor7 · zeta-hp3647h · zeta-livermore8</text>
<line x1="0" y1="600" x2="900" y2="600" stroke="#e0e0e0" stroke-width="1"/>
<rect x="0" y="600" width="900" height="40" fill="#f8f8f8"/>
<text x="450" y="624" text-anchor="middle" font-size="10" fill="#888">backup_cluster_map.svg · hprzeta · MAJ 2026-06-13</text>
</svg>
SVGEOF
}

svg_topo() {
cat << 'SVGEOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="900" height="720" viewBox="0 0 900 720"
     xmlns="http://www.w3.org/2000/svg" font-family="monospace,sans-serif">
<title>Topo materiel cluster Riemann_Lab</title>
<rect width="900" height="720" fill="#ffffff"/>

<!-- TITRE -->
<rect x="0" y="0" width="900" height="52" fill="#f8f8f8"/>
<line x1="0" y1="52" x2="900" y2="52" stroke="#e0e0e0" stroke-width="1"/>
<text x="450" y="22" text-anchor="middle" font-size="17" font-weight="700" fill="#1a1a1a">Materiel cluster — Riemann_Lab</text>
<text x="450" y="42" text-anchor="middle" font-size="12" fill="#666">Analyse capacite 3 machines pour calcul zeta · hprzeta 2026-06-13</text>

<!-- EN-TETES COLONNES -->
<rect x="20" y="60" width="280" height="28" rx="6" fill="#085041"/>
<text x="160" y="79" text-anchor="middle" font-size="13" font-weight="700" fill="#ffffff">zeta-icor7</text>
<rect x="314" y="60" width="268" height="28" rx="6" fill="#2c2c2a"/>
<text x="448" y="79" text-anchor="middle" font-size="13" font-weight="700" fill="#ffffff">zeta-hp3647h</text>
<rect x="596" y="60" width="284" height="28" rx="6" fill="#3c3489"/>
<text x="738" y="79" text-anchor="middle" font-size="13" font-weight="700" fill="#ffffff">zeta-livermore8</text>

<!-- SOUS-TITRES -->
<text x="160" y="106" text-anchor="middle" font-size="10" fill="#0f6e56">riemann@zeta-icor7</text>
<text x="448" y="106" text-anchor="middle" font-size="10" fill="#5f5e5a">emmabuntus@zeta-hp3647h</text>
<text x="738" y="106" text-anchor="middle" font-size="10" fill="#534ab7">pjexosql@zeta-livermore8</text>
<text x="160" y="120" text-anchor="middle" font-size="11" font-weight="700" fill="#1a1a1a">192.168.1.24</text>
<text x="448" y="120" text-anchor="middle" font-size="11" font-weight="700" fill="#1a1a1a">192.168.1.94</text>
<text x="738" y="120" text-anchor="middle" font-size="11" font-weight="700" fill="#1a1a1a">192.168.1.22</text>

<line x1="10" y1="130" x2="890" y2="130" stroke="#e0e0e0" stroke-width="1"/>

<!-- LIGNES COMPARAISON -->
<!-- Modele -->
<rect x="10" y="134" width="880" height="36" rx="0" fill="#f9f9f9"/>
<text x="16" y="148" font-size="10" font-weight="700" fill="#333">Modele</text>
<text x="160" y="148" text-anchor="middle" font-size="10" fill="#1a1a1a">Intel i7 moderne</text>
<text x="448" y="148" text-anchor="middle" font-size="10" fill="#1a1a1a">HP Compaq 8000 Elite CMT</text>
<text x="738" y="148" text-anchor="middle" font-size="10" fill="#1a1a1a">Compaq-Presario SG3210FR</text>
<text x="448" y="162" text-anchor="middle" font-size="9" fill="#666">Carte mere : HP 3647h · BIOS 2009</text>
<text x="738" y="162" text-anchor="middle" font-size="9" fill="#666">Carte mere : ECS Livermore8 · BIOS 2007</text>
<line x1="10" y1="170" x2="890" y2="170" stroke="#e8e8e8" stroke-width="0.8"/>

<!-- CPU -->
<rect x="10" y="170" width="880" height="48" rx="0" fill="#ffffff"/>
<text x="16" y="184" font-size="10" font-weight="700" fill="#333">CPU</text>
<text x="160" y="184" text-anchor="middle" font-size="10" fill="#1a1a1a">Intel i7 (multicoeur)</text>
<text x="448" y="184" text-anchor="middle" font-size="10" fill="#1a1a1a">Core 2 Duo E8400</text>
<text x="738" y="184" text-anchor="middle" font-size="10" fill="#1a1a1a">Pentium Dual E2140</text>
<text x="160" y="198" text-anchor="middle" font-size="9" fill="#0f6e56">GPU : GTX 960M · 4GB VRAM · CUDA</text>
<text x="448" y="198" text-anchor="middle" font-size="9" fill="#666">2 coeurs · 3.0 GHz · L2 6 MiB</text>
<text x="738" y="198" text-anchor="middle" font-size="9" fill="#a32d2d">2 coeurs · 1.6 GHz · L2 1 MiB</text>
<text x="448" y="210" text-anchor="middle" font-size="9" fill="#666">64 bits · FSB 1333 MHz</text>
<text x="738" y="210" text-anchor="middle" font-size="9" fill="#a32d2d">64 bits · FSB 200 MHz</text>
<line x1="10" y1="218" x2="890" y2="218" stroke="#e8e8e8" stroke-width="0.8"/>

<!-- RAM -->
<rect x="10" y="218" width="880" height="36" rx="0" fill="#f9f9f9"/>
<text x="16" y="232" font-size="10" font-weight="700" fill="#333">RAM</text>
<text x="160" y="232" text-anchor="middle" font-size="10" fill="#1a1a1a">8 GB + 16 GB swap</text>
<text x="448" y="232" text-anchor="middle" font-size="10" fill="#1a1a1a">4 GiB DDR3 1333 MHz</text>
<text x="738" y="232" text-anchor="middle" font-size="10" fill="#a32d2d">3 GiB DDR2 667 MHz</text>
<text x="160" y="246" text-anchor="middle" font-size="9" fill="#0f6e56">swap sur /mnt/data</text>
<text x="448" y="246" text-anchor="middle" font-size="9" fill="#0f6e56">2 slots libres → peut monter 8 GB</text>
<text x="738" y="246" text-anchor="middle" font-size="9" fill="#a32d2d">2 slots pleins · pas d'upgrade</text>
<line x1="10" y1="254" x2="890" y2="254" stroke="#e8e8e8" stroke-width="0.8"/>

<!-- Disques -->
<rect x="10" y="254" width="880" height="48" rx="0" fill="#ffffff"/>
<text x="16" y="268" font-size="10" font-weight="700" fill="#333">Disques</text>
<text x="160" y="268" text-anchor="middle" font-size="10" fill="#1a1a1a">SSD + /mnt/data</text>
<text x="448" y="268" text-anchor="middle" font-size="10" fill="#1a1a1a">80 GB sys + 500 GB /home</text>
<text x="738" y="268" text-anchor="middle" font-size="10" fill="#1a1a1a">250 GB (sys+home)</text>
<text x="448" y="282" text-anchor="middle" font-size="9" fill="#666">Seagate ST380815AS + Hitachi HDT72505</text>
<text x="738" y="282" text-anchor="middle" font-size="9" fill="#666">Hitachi HDT72502</text>
<text x="448" y="294" text-anchor="middle" font-size="9" fill="#0f6e56">500 GB /home disponible stockage</text>
<text x="738" y="294" text-anchor="middle" font-size="9" fill="#666">~190 GB /home</text>
<line x1="10" y1="302" x2="890" y2="302" stroke="#e8e8e8" stroke-width="0.8"/>

<!-- Reseau -->
<rect x="10" y="302" width="880" height="36" rx="0" fill="#f9f9f9"/>
<text x="16" y="316" font-size="10" font-weight="700" fill="#333">Reseau</text>
<text x="160" y="316" text-anchor="middle" font-size="10" fill="#1a1a1a">WiFi · wlp2s0</text>
<text x="448" y="316" text-anchor="middle" font-size="10" fill="#0f6e56">Gigabit ethernet · enp0s25</text>
<text x="738" y="316" text-anchor="middle" font-size="10" fill="#a32d2d">Fast ethernet 100 Mbit/s · enp1s0</text>
<text x="448" y="330" text-anchor="middle" font-size="9" fill="#0f6e56">Intel 82567LM-3 · 1 Gbit/s</text>
<text x="738" y="330" text-anchor="middle" font-size="9" fill="#a32d2d">Realtek RTL810xE · limite backup</text>
<line x1="10" y1="338" x2="890" y2="338" stroke="#e8e8e8" stroke-width="0.8"/>

<!-- OS/Python -->
<rect x="10" y="338" width="880" height="36" rx="0" fill="#ffffff"/>
<text x="16" y="352" font-size="10" font-weight="700" fill="#333">OS / Python</text>
<text x="160" y="352" text-anchor="middle" font-size="10" fill="#0f6e56">Ubuntu · Python 3.12</text>
<text x="448" y="352" text-anchor="middle" font-size="10" fill="#1a1a1a">Ubuntu · Python 3.x</text>
<text x="738" y="352" text-anchor="middle" font-size="10" fill="#a32d2d">Ubuntu · Python 3.5 · Linux 4.4</text>
<text x="160" y="366" text-anchor="middle" font-size="9" fill="#0f6e56">mpmath · Arb/FLINT · CuPy · Claude Code</text>
<text x="448" y="366" text-anchor="middle" font-size="9" fill="#666">config scripts</text>
<text x="738" y="366" text-anchor="middle" font-size="9" fill="#a32d2d">crontab -e casse · tres ancien</text>
<line x1="10" y1="374" x2="890" y2="374" stroke="#ccc" stroke-width="1"/>

<!-- EVALUATION -->
<rect x="10" y="374" width="880" height="24" rx="0" fill="#f0f0f0"/>
<text x="450" y="391" text-anchor="middle" font-size="12" font-weight="700" fill="#1a1a1a">Evaluation pour projet Zeta</text>
<line x1="10" y1="398" x2="890" y2="398" stroke="#ccc" stroke-width="1"/>

<rect x="20" y="406" width="260" height="220" rx="10" fill="#e1f5ee" stroke="#0f6e56" stroke-width="1.5"/>
<text x="150" y="428" text-anchor="middle" font-size="13" font-weight="700" fill="#085041">MACHINE PRINCIPALE</text>
<text x="150" y="446" text-anchor="middle" font-size="10" fill="#0f6e56">+ CPU i7 moderne · GPU CUDA</text>
<text x="150" y="462" text-anchor="middle" font-size="10" fill="#0f6e56">+ 8 GB RAM + 16 GB swap</text>
<text x="150" y="478" text-anchor="middle" font-size="10" fill="#0f6e56">+ Python 3.12 · mpmath · Arb</text>
<text x="150" y="494" text-anchor="middle" font-size="10" fill="#0f6e56">+ Claude Code · zeta_env</text>
<text x="150" y="510" text-anchor="middle" font-size="10" fill="#0f6e56">+ Wiki · PDF · logs ici</text>
<text x="150" y="530" text-anchor="middle" font-size="11" font-weight="700" fill="#085041">Calcul zeros T=100k</text>
<text x="150" y="546" text-anchor="middle" font-size="10" fill="#085041">runs · code · wiki · git</text>
<text x="150" y="562" text-anchor="middle" font-size="10" fill="#085041">TOUT le projet vit ici</text>
<text x="150" y="578" text-anchor="middle" font-size="10" fill="#085041">Cron 01h50 → rsync Acer</text>
<text x="150" y="618" text-anchor="middle" font-size="10" font-weight="700" fill="#0f6e56">Hostname : zeta-icor7</text>

<rect x="310" y="406" width="260" height="220" rx="10" fill="#f1efe8" stroke="#5f5e5a" stroke-width="1.5"/>
<text x="440" y="428" text-anchor="middle" font-size="13" font-weight="700" fill="#2c2c2a">NOEUD SECONDAIRE</text>
<text x="440" y="446" text-anchor="middle" font-size="10" fill="#5f5e5a">+ Core 2 Duo 3 GHz</text>
<text x="440" y="462" text-anchor="middle" font-size="10" fill="#5f5e5a">+ 4 GB DDR3 (peut → 8 GB)</text>
<text x="440" y="478" text-anchor="middle" font-size="10" fill="#5f5e5a">+ 500 GB /home libre</text>
<text x="440" y="494" text-anchor="middle" font-size="10" fill="#5f5e5a">+ Gigabit ethernet stable</text>
<text x="440" y="510" text-anchor="middle" font-size="10" fill="#5f5e5a">+ 2 slots RAM libres</text>
<text x="440" y="530" text-anchor="middle" font-size="11" font-weight="700" fill="#2c2c2a">Calcul leger possible</text>
<text x="440" y="546" text-anchor="middle" font-size="10" fill="#2c2c2a">scripts · config · stockage</text>
<text x="440" y="562" text-anchor="middle" font-size="10" fill="#2c2c2a">SSH manuel vers Acer</text>
<text x="440" y="578" text-anchor="middle" font-size="10" fill="#2c2c2a">Pas de wiki/pdf/logs</text>
<text x="440" y="618" text-anchor="middle" font-size="10" font-weight="700" fill="#5f5e5a">Hostname : zeta-hp3647h</text>

<rect x="600" y="406" width="280" height="220" rx="10" fill="#eeedfe" stroke="#534ab7" stroke-width="1.5"/>
<text x="740" y="428" text-anchor="middle" font-size="13" font-weight="700" fill="#3c3489">BACKUP H24</text>
<text x="740" y="446" text-anchor="middle" font-size="10" fill="#a32d2d">- Pentium 1.6 GHz (lent)</text>
<text x="740" y="462" text-anchor="middle" font-size="10" fill="#a32d2d">- 3 GB DDR2 667 MHz (lent)</text>
<text x="740" y="478" text-anchor="middle" font-size="10" fill="#a32d2d">- Reseau 100 Mbit/s</text>
<text x="740" y="494" text-anchor="middle" font-size="10" fill="#a32d2d">- Linux 4.4 · Python 3.5</text>
<text x="740" y="510" text-anchor="middle" font-size="10" fill="#a32d2d">- crontab -e casse</text>
<text x="740" y="530" text-anchor="middle" font-size="11" font-weight="700" fill="#3c3489">Ne PAS calculer ici</text>
<text x="740" y="546" text-anchor="middle" font-size="10" fill="#534ab7">backup nocturne cron 02h00</text>
<text x="740" y="562" text-anchor="middle" font-size="10" fill="#534ab7">rclone → Proton Drive</text>
<text x="740" y="578" text-anchor="middle" font-size="10" fill="#534ab7">Relais icor7 → cloud</text>
<text x="740" y="618" text-anchor="middle" font-size="10" font-weight="700" fill="#534ab7">Hostname : zeta-livermore8</text>

<line x1="0" y1="638" x2="900" y2="638" stroke="#e0e0e0" stroke-width="1"/>
<rect x="0" y="638" width="900" height="82" fill="#f8f8f8"/>
<text x="20" y="658" font-size="10" font-weight="700" fill="#333">Hostname conseille :</text>
<rect x="20" y="664" width="200" height="18" rx="4" fill="#085041"/>
<text x="120" y="677" text-anchor="middle" font-size="10" fill="#fff">zeta-icor7  ✓ actif</text>
<rect x="240" y="664" width="200" height="18" rx="4" fill="#2c2c2a"/>
<text x="340" y="677" text-anchor="middle" font-size="10" fill="#fff">zeta-hp3647h  ✓ actif</text>
<rect x="460" y="664" width="220" height="18" rx="4" fill="#3c3489"/>
<text x="570" y="677" text-anchor="middle" font-size="10" fill="#fff">zeta-livermore8  ✓ actif</text>
<text x="450" y="710" text-anchor="middle" font-size="10" fill="#888">topo_machines_zeta.svg · hprzeta · MAJ 2026-06-13</text>
</svg>
SVGEOF
}

case "${1:-all}" in
  pipeline)
    svg_pipeline
    ;;
  topo)
    svg_topo
    ;;
  all|*)
    svg_pipeline > backup_cluster_map.svg
    svg_topo > topo_machines_zeta.svg
    echo "Genere : backup_cluster_map.svg"
    echo "Genere : topo_machines_zeta.svg"
    ;;
esac

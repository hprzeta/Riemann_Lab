#!/usr/bin/env python3
"""
Module de visualisation des zéros de ζ(s).
Génère des graphiques avec matplotlib.
AUTEUR : hprzeta
"""

import logging
from pathlib import Path
from datetime import datetime

import matplotlib
matplotlib.use("Agg")  # mode sans affichage (serveur / CI)
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("docs/images")


def _ensure_output(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def plot_zeros_distribution(zeros: list[dict], comparison: dict) -> None:
    """
    Génère et sauvegarde les graphiques principaux :
    1. Distribution des zéros sur la droite critique
    2. Espacement entre zéros consécutifs
    3. Taux de correspondance LMFDB
    """
    _ensure_output(OUTPUT_DIR)

    if not zeros:
        logger.warning("Aucun zéro à visualiser")
        return

    t_values = np.array([z["t"] for z in zeros])
    n = len(t_values)

    # ── Graphique 1 : positions des zéros ────────────────────────────────────
    fig, ax = plt.subplots(figsize=(14, 4), facecolor="#080b0f")
    ax.set_facecolor("#0d1219")

    ax.scatter(t_values, np.zeros(n), c="#c9a84c", s=4, alpha=0.7, linewidths=0)
    ax.axhline(0, color="#4a5568", linewidth=0.5, linestyle="--")
    ax.set_xlabel("t  (partie imaginaire)", color="#d4cfc8")
    ax.set_title(
        f"Zéros non triviaux de ζ(1/2 + it)  —  {n} zéros calculés",
        color="#c9a84c", fontsize=13
    )
    ax.tick_params(colors="#8a8278")
    ax.spines[:].set_color("#4a5568")
    ax.set_yticks([])
    plt.tight_layout()
    out1 = OUTPUT_DIR / "zeros_distribution.png"
    fig.savefig(out1, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Graphique 1 sauvegardé → {out1}")

    # ── Graphique 2 : espacement entre zéros ─────────────────────────────────
    spacings = np.diff(t_values)
    fig, ax = plt.subplots(figsize=(10, 5), facecolor="#080b0f")
    ax.set_facecolor("#0d1219")

    ax.hist(spacings, bins=60, color="#c9a84c", edgecolor="#080b0f", alpha=0.85)
    mean_sp = spacings.mean()
    ax.axvline(mean_sp, color="#e8c97a", linewidth=1.5,
               linestyle="--", label=f"Moyenne : {mean_sp:.4f}")
    ax.set_xlabel("Espacement Δt entre zéros consécutifs", color="#d4cfc8")
    ax.set_ylabel("Fréquence", color="#d4cfc8")
    ax.set_title("Distribution des espacements", color="#c9a84c", fontsize=13)
    ax.tick_params(colors="#8a8278")
    ax.spines[:].set_color("#4a5568")
    ax.legend(facecolor="#0d1219", labelcolor="#d4cfc8")
    plt.tight_layout()
    out2 = OUTPUT_DIR / "zeros_spacing.png"
    fig.savefig(out2, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Graphique 2 sauvegardé → {out2}")

    # ── Graphique 3 : comparaison LMFDB ──────────────────────────────────────
    stats = comparison.get("stats", {})
    if stats:
        fig, ax = plt.subplots(figsize=(7, 5), facecolor="#080b0f")
        ax.set_facecolor("#0d1219")

        labels  = ["Correspondants\n(LMFDB)", "Non correspondants", "Manqués\n(LMFDB)"]
        values  = [stats.get("matched", 0), stats.get("unmatched", 0), stats.get("missing", 0)]
        colors  = ["#4ade80", "#f87171", "#fbbf24"]

        bars = ax.bar(labels, values, color=colors, edgecolor="#080b0f", width=0.5)
        for bar, v in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                str(v), ha="center", color="#d4cfc8", fontsize=11
            )

        ax.set_title(
            f"Comparaison LMFDB — taux : {stats.get('match_rate', 0):.1f}%",
            color="#c9a84c", fontsize=13
        )
        ax.tick_params(colors="#8a8278")
        ax.spines[:].set_color("#4a5568")
        ax.set_ylabel("Nombre de zéros", color="#d4cfc8")
        plt.tight_layout()
        out3 = OUTPUT_DIR / "zeros_lmfdb_comparison.png"
        fig.savefig(out3, dpi=150, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Graphique 3 sauvegardé → {out3}")

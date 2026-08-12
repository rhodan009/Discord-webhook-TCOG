#!/usr/bin/env python3
"""
The City of Gold — publication automatique de l'An N.

Calcule l'année dorée en cours (An 0 = lundi 13 octobre 2025, +1 par
lundi réel) et publie l'embed hebdomadaire dans #calendrier-dore.

UTILISATION LOCALE (test)
  export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
  python3 poster_an_n.py

Conçu pour tourner chaque lundi via GitHub Actions (voir le workflow
.github/workflows/an-n.yml fourni séparément) — mais fonctionne
identiquement en cron local ou en tâche planifiée.
"""

import os
import random
import urllib.request
import json
from datetime import date, timedelta

# ---------------------------------------------------------------- réglages

EPOCH = date(2025, 10, 13)          # Lundi — An 0, Jour 0
GOLD = 13214247                     # #C9A227

AMORCES = [
    "Votre Maison a une devise. Laquelle ?",
    "Un juge condamne à mort le fils d'un allié. Que faites-vous ?",
    "Votre comté n'a pas de sel. Vous négociez, ou vous vous en passez ?",
    "Faut-il pouvoir destituer un roi ?",
    "Quel métier prendriez-vous le premier jour ?",
    "Un maréchal arrête un membre de votre Institution. Vous intervenez ?",
    "Votre Religion perd son dernier fidèle ailleurs. Que retenez-vous de son histoire ?",
    "Un comté voisin vous propose une alliance. Qu'exigez-vous en retour ?",
]

# ------------------------------------------------------------------ calcul

def annee_doree(aujourdhui: date) -> int:
    """Nombre de lundis écoulés depuis l'An 0 (inclus)."""
    jours_ecoules = (aujourdhui - EPOCH).days
    return max(0, jours_ecoules // 7)


def prochaine_amorce(numero_annee: int) -> str:
    """Rotation déterministe : la même An N donne toujours la même amorce."""
    rng = random.Random(numero_annee)
    return rng.choice(AMORCES)


def construire_payload(numero_annee: int, amorce: str) -> dict:
    return {
        "content": None,
        "embeds": [
            {
                "title": f"⚜️  An {numero_annee} du Calendrier Doré",
                "description": f"Une nouvelle année s'ouvre sur Arkadia.\n\n*{amorce}*",
                "color": GOLD,
            }
        ],
    }


def envoyer(webhook_url: str, payload: dict) -> None:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        if resp.status not in (200, 204):
            raise RuntimeError(f"Discord a répondu {resp.status}")


def main() -> None:
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise SystemExit("Variable DISCORD_WEBHOOK_URL manquante.")

    today = date.today()
    n = annee_doree(today)
    amorce = prochaine_amorce(n)
    payload = construire_payload(n, amorce)

    print(f"Date réelle : {today.isoformat()}")
    print(f"An {n} du Calendrier Doré")
    print(f"Amorce : {amorce}")

    envoyer(webhook_url, payload)
    print("Message envoyé.")


if __name__ == "__main__":
    main()

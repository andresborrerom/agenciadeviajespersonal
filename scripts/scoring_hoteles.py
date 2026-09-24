#!/usr/bin/env python3
"""Calcula el rating general (0-100) de candidatos de hotel segun el
modelo ponderado descrito en agentes/scoring.md.

Uso:
    python3 scoring_hoteles.py candidatos.json [pesos.json]

candidatos.json: lista de objetos con las variables crudas por hotel.
pesos.json (opcional): pesos por variable; si no se pasa, usa los
defaults de agentes/scoring.md.
"""
import json
import sys

DEFAULT_WEIGHTS = {
    "reviews": 0.30,
    "distancia": 0.20,
    "precio": 0.20,
    "camas": 0.10,
    "categoria": 0.10,
    "cancelacion": 0.05,
    "zona_seguridad": 0.05,
}

REVIEW_PRIOR = 7.5
REVIEW_K = 100


def score_reviews(raw: float, n: int) -> float:
    adj = (n / (n + REVIEW_K)) * raw + (REVIEW_K / (n + REVIEW_K)) * REVIEW_PRIOR
    return adj / 10.0


def score_distancia(metros_caminando: float, d_max: float = 1600.0) -> float:
    return max(0.0, 1.0 - metros_caminando / d_max)


def score_precio(precio: float, ideal: float, techo: float) -> float:
    if precio <= ideal:
        return 1.0
    if precio <= techo:
        return 1.0 - 0.7 * (precio - ideal) / (techo - ideal)
    sobrepasado = precio - techo
    return max(0.0, 0.3 - 0.3 * sobrepasado / (0.5 * techo))


def calcular(hotel: dict, pesos: dict, ideal: float, techo: float):
    faltantes = []
    sub = {}
    sub["reviews"] = score_reviews(hotel["reviews_raw"], hotel["reviews_n"])
    sub["distancia"] = score_distancia(hotel["distancia_caminando_m"])
    if hotel.get("precio") is None:
        faltantes.append("precio")
        sub["precio"] = None
    else:
        sub["precio"] = score_precio(hotel["precio"], ideal, techo)
    sub["camas"] = hotel["camas"]
    sub["categoria"] = hotel["categoria"]
    sub["cancelacion"] = hotel["cancelacion"]
    sub["zona_seguridad"] = hotel["zona_seguridad"]

    usable_weight = sum(w for k, w in pesos.items() if sub.get(k) is not None)
    overall = 0.0
    for k, w in pesos.items():
        if sub.get(k) is not None:
            overall += (w / usable_weight) * sub[k]
    return round(overall * 100, 1), sub, faltantes


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    candidatos = json.load(open(sys.argv[1], encoding="utf-8"))
    pesos = DEFAULT_WEIGHTS
    if len(sys.argv) > 2:
        pesos = json.load(open(sys.argv[2], encoding="utf-8"))
    ideal = candidatos.get("_presupuesto", {}).get("ideal", 350)
    techo = candidatos.get("_presupuesto", {}).get("techo", 750)
    hoteles = candidatos["hoteles"] if isinstance(candidatos, dict) else candidatos

    filas = []
    for h in hoteles:
        overall, sub, faltantes = calcular(h, pesos, ideal, techo)
        filas.append((overall, h["nombre"], sub, faltantes))
    filas.sort(reverse=True, key=lambda f: f[0])

    for overall, nombre, sub, faltantes in filas:
        flag = "  [INCOMPLETO: falta " + ", ".join(faltantes) + "]" if faltantes else ""
        print(f"{overall:5.1f}  {nombre}{flag}")
        for k, v in sub.items():
            print(f"        {k}: {v}")


if __name__ == "__main__":
    main()

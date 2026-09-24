#!/usr/bin/env python3
"""Distancia caminando aproximada de una direccion a un poligono ancla
(ej. un parque), usando geocodificacion real en vez de bounding boxes.

Por que no un bounding box: la cuadricula de Manhattan esta rotada ~29
grados respecto al norte real, asi que el rectangulo que envuelve un
parque mete de mas o de menos segun el lado del hotel. Este script baja
el poligono real (Nominatim/OpenStreetMap) y calcula la distancia minima
punto-a-segmento contra cada arista del borde.

Uso:
    python3 distancia_a_punto.py "2175 Broadway, New York, NY 10024" "Central Park, New York, NY"

Requiere salida a internet (Nominatim). Respeta ~1 req/seg (política de
uso de Nominatim) si se llama varias veces seguidas.
"""
import json
import math
import sys
import time
import urllib.parse
import urllib.request

USER_AGENT = "AgenciaViajesPersonal/0.1 (uso interno)"
MANHATTAN_DETOUR = 1.3  # aproxima caminar en cuadricula vs. linea recta
WALK_M_PER_MIN = 80


def geocode(query: str) -> tuple[float, float]:
    url = (
        "https://nominatim.openstreetmap.org/search?format=json&limit=1&q="
        + urllib.parse.quote(query)
    )
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
    if not data:
        raise ValueError(f"Sin resultado de geocodificacion para: {query}")
    return float(data[0]["lat"]), float(data[0]["lon"])


def geocode_polygon(query: str) -> list[tuple[float, float]]:
    url = (
        "https://nominatim.openstreetmap.org/search?format=json&polygon_geojson=1&limit=1&q="
        + urllib.parse.quote(query)
    )
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
    if not data:
        raise ValueError(f"Sin resultado de geocodificacion para: {query}")
    geom = data[0]["geojson"]
    if geom["type"] == "Polygon":
        ring = geom["coordinates"][0]
    elif geom["type"] == "MultiPolygon":
        ring = max(geom["coordinates"], key=lambda p: len(p[0]))[0]
    else:
        raise ValueError(f"Geometria no soportada: {geom['type']} (se esperaba un area, no un punto)")
    return [(lat, lon) for lon, lat in ring]


def _to_xy(lat: float, lon: float, ref_lat: float) -> tuple[float, float]:
    m_per_deg_lat = 111320.0
    m_per_deg_lon = 111320.0 * math.cos(math.radians(ref_lat))
    return lon * m_per_deg_lon, lat * m_per_deg_lat


def _point_in_polygon(x: float, y: float, poly: list[tuple[float, float]]) -> bool:
    n = len(poly)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-15) + xi:
            inside = not inside
        j = i
    return inside


def _dist_point_segment(px, py, ax, ay, bx, by) -> float:
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    cx, cy = ax + t * dx, ay + t * dy
    return math.hypot(px - cx, py - cy)


def distancia_a_poligono_m(lat: float, lon: float, poligono: list[tuple[float, float]]) -> float:
    ref_lat = sum(p[0] for p in poligono) / len(poligono)
    x, y = _to_xy(lat, lon, ref_lat)
    poly_xy = [_to_xy(plat, plon, ref_lat) for plat, plon in poligono]
    if _point_in_polygon(x, y, poly_xy):
        return 0.0
    return min(
        _dist_point_segment(x, y, *poly_xy[i], *poly_xy[(i + 1) % len(poly_xy)])
        for i in range(len(poly_xy))
    )


def distancia_caminando(direccion: str, ancla: str, cache_ancla: list[tuple[float, float]] | None = None):
    lat, lon = geocode(direccion)
    if cache_ancla is None:
        time.sleep(1.1)
        cache_ancla = geocode_polygon(ancla)
    recta_m = distancia_a_poligono_m(lat, lon, cache_ancla)
    caminando_m = recta_m * MANHATTAN_DETOUR
    minutos = caminando_m / WALK_M_PER_MIN
    return {
        "direccion": direccion,
        "lat": lat,
        "lon": lon,
        "distancia_recta_m": round(recta_m),
        "distancia_caminando_m": round(caminando_m),
        "minutos_caminando": round(minutos, 1),
    }, cache_ancla


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    resultado, _ = distancia_caminando(sys.argv[1], sys.argv[2])
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

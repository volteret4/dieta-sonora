#!/usr/bin/env python3
"""Añade a albums.csv los lanzamientos recientes de los artistas que sigues en Muspy.

El feed por ID es público, así que basta MUSPY_USERID: no se usa ninguna contraseña.

Uso:
    python muspy_lanzamientos.py              # sobrescribe albums.csv
    python muspy_lanzamientos.py --append     # añade a lo que ya haya
    python muspy_lanzamientos.py --since 60   # últimos 60 días
"""
import argparse
import csv
import os
import re
import sys
from datetime import date, timedelta

import requests

API = 'https://muspy.com/api/1/releases'
PAGE = 100  # máximo que admite la API
MAX_PAGES = 20
FIELDS = ['artist', 'album', 'type']


def fecha(texto):
    """Muspy da AAAA, AAAA-MM o AAAA-MM-DD. Lo incompleto cuenta como el último día posible."""
    m = re.fullmatch(r'(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?', texto or '')
    if not m:
        return None
    año, mes, dia = int(m[1]), m[2], m[3]
    try:
        if dia:
            return date(año, int(mes), int(dia))
        if mes:
            siguiente = date(año + (mes == '12'), int(mes) % 12 + 1, 1)
            return siguiente - timedelta(days=1)
        return date(año, 12, 31)
    except ValueError:
        return None


def lanzamientos(userid, desde, hoy, tipos, get=requests.get):
    """Pagina hasta pasar la fecha límite. La API ordena de más nuevo a más viejo."""
    for pagina in range(MAX_PAGES):
        r = get(f'{API}/{userid}', params={'limit': PAGE, 'offset': pagina * PAGE},
                headers={'User-Agent': 'dieta-sonora'}, timeout=30)
        r.raise_for_status()
        filas = r.json()
        for rel in filas:
            d = fecha(rel.get('date'))
            if d is None or d > hoy:
                continue
            if d < desde:
                return
            if tipos and rel.get('type') not in tipos:
                continue
            artista = (rel.get('artist') or {}).get('name', '').strip()
            album = (rel.get('name') or '').strip()
            if artista and album:
                yield artista, album
        if len(filas) < PAGE:
            return


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--since', type=int, default=int(os.getenv('MUSPY_SINCE_DAYS') or 21))
    ap.add_argument('--append', action='store_true')
    ap.add_argument('-o', '--output', default='albums.csv')
    args = ap.parse_args()

    userid = (os.getenv('MUSPY_USERID') or '').strip()
    if not re.fullmatch(r'[0-9a-z]{30}', userid):
        sys.exit('MUSPY_USERID sin configurar o no válido (30 letras minúsculas y números).')
    tipos = {t.strip() for t in (os.getenv('MUSPY_TYPES') or 'Album,EP').split(',') if t.strip()}

    filas = []
    if args.append and os.path.exists(args.output):
        with open(args.output, newline='', encoding='utf-8') as f:
            filas = [{k: r.get(k, '') for k in FIELDS} for r in csv.DictReader(f)]
    vistos = {(r['artist'].lower(), r['album'].lower()) for r in filas}

    hoy = date.today()
    nuevos = 0
    for artista, album in lanzamientos(userid, hoy - timedelta(days=args.since), hoy, tipos):
        clave = (artista.lower(), album.lower())
        if clave not in vistos:
            vistos.add(clave)
            filas.append({'artist': artista, 'album': album, 'type': 'muspy'})
            nuevos += 1

    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(filas)
    print(f'{nuevos} lanzamientos de Muspy añadidos a {args.output}')


if __name__ == '__main__':
    main()

#!/usr/bin/env bash
# Guarda los datos generados en /data para que sobrevivan a un rebuild.
set -e
DATA="${DS_DATA_DIR:-/data}"
mkdir -p "$DATA"
[ -f "$DATA/albums.csv" ] || echo 'artist,album,type' > "$DATA/albums.csv"
[ -f "$DATA/resultado_flacs.json" ] || echo '[]' > "$DATA/resultado_flacs.json"
for f in embeds_cache.json lastfm_info_cache.json; do
[ -f "$DATA/$f" ] || echo '{}' > "$DATA/$f"
done
for f in albums.csv resultado_flacs.json embeds_cache.json lastfm_info_cache.json resumen_flacs.html; do
ln -sf "$DATA/$f" "/app/$f"
done
[ -s "$DATA/resumen_flacs.html" ] || python3 html_generator.py
exec "$@"

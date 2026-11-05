#!/usr/bin/env bash
# Actualización diaria: fuentes → qué ya tienes → NAS → web. Cada paso solo corre si está configurado.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
PYTHON="${PYTHON:-python3}"
CSV_FILE=albums.csv

[ -f "$CSV_FILE" ] || echo 'artist,album,type' > "$CSV_FILE"
[ -f resultado_flacs.json ] || echo '[]' > resultado_flacs.json

# Fuentes de lanzamientos. Si hay calendario, reescribe el CSV y Muspy añade.
append=""
if [ -n "${RADICALE_URL:-}" ] && [ -n "${CALENDAR_NAME:-}" ]; then
    "$PYTHON" revisor_calendario.py --since 21
    append="--append"
fi
if [ -n "${MUSPY_USERID:-}" ]; then
    "$PYTHON" muspy_lanzamientos.py $append
fi

# Lo más activo del NAS
"$PYTHON" top_semana.py

# Quitar lo que ya tienes
if [ -n "${AIRSONIC_USER:-}" ]; then
    "$PYTHON" airsonic_clean_csv.py --mode clean "$CSV_FILE"
fi
if [ -n "${QB_HOST:-}" ]; then
    "$PYTHON" qbittorrent_cleaner_csv.py --clean
fi

# Buscar en el NAS lo pendiente y limpiar lo que ya tengas de lo mostrado
"$PYTHON" buscar_nuevos.py
"$PYTHON" limpiar_ya_tengo.py

# Regenerar la web (resumen_flacs.html es un enlace al volumen de datos: usar cp, no mv)
"$PYTHON" html_generator.py

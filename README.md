# Dieta Sonora

Un panel con los discos nuevos de los artistas que sigues, pendientes de conseguir y escuchar.

## Para qué sirve

Si sigues a muchos artistas, los lanzamientos se pierden entre avisos. Dieta Sonora los junta en una pantalla con portada y dónde escucharlos, oculta lo que ya tienes y te deja descargar el resto desde tu NAS de música compartida con un clic.

- **Pendientes**: lanzamientos recientes de tus artistas, con vídeo, Bandcamp e información de Last.fm.
- **Top 10 del NAS**: lo más activo de la semana, el mes y el total.
- **Calendario** (opcional): lanzamientos del mes, desde un calendario CalDAV.

Se actualiza una vez al día, o al pulsar **Buscar novedades**.

## Fuentes y servicios

Todo es opcional salvo una fuente de lanzamientos. Lo que no configures se oculta en la web.

| Servicio | Variables | Para qué |
|---|---|---|
| [Muspy](https://muspy.com) | `MUSPY_USERID` | Fuente de lanzamientos. Tu ID son 30 caracteres y sale en el enlace de tu feed, `/feed?id=…`. No pide contraseña |
| CalDAV (Radicale) | `RADICALE_*`, `CALENDAR_*` | Otra fuente de lanzamientos y la pestaña de calendario |
| NAS de música compartida | `NAS_URL`, `NAS_API_KEY` | Buscar y descargar cada disco, y la pestaña Top 10 |
| Airsonic / Subsonic | `AIRSONIC_*` | Ocultar lo que ya tienes |
| qBittorrent | `QB_*` | Ocultar lo que ya has descargado |
| Last.fm | `LASTFM_API_KEY` | Información de artista y disco |

Sin NAS, los discos se muestran igualmente, solo que sin descargas.

El NAS debe ofrecer una API JSON en `<NAS_URL>/ajax.php` con autenticación por clave en la cabecera `Authorization` y las acciones `index`, `browse`, `torrentgroup` y `top10`, y descargas en `<NAS_URL>/torrents.php`. Los `.torrent` descargados se dejan en la carpeta `WATCH_TORRENTS_HOST_PATH`, que debe vigilar tu cliente.

## Instalación individual

Necesitas Docker con `docker compose`.

```bash
git clone https://github.com/volteret4/dieta-sonora.git
```

```bash
cd dieta-sonora && cp .env.example .env && mkdir -p data/watch_torrents
```

Edita `.env`, con al menos `MUSPY_USERID`, y arranca:

```bash
docker compose up -d --build
```

Se abre en <http://localhost:5010>. Para traer los discos por primera vez:

```bash
docker exec dieta-sonora bash main.sh
```

Para actualizar cada día, añade esto al cron del host:

```bash
0 1 * * * docker exec dieta-sonora bash main.sh
```

Los datos generados viven en `data/` y sobreviven a una reconstrucción.

## Instalación desde REPEAT-ONE

Este módulo forma parte de [REPEAT-ONE](https://github.com/volteret4/repeat-one-web), que permite elegir qué módulos instalar: [ver la instalación](https://github.com/volteret4/repeat-one-web#instalación). Allí se llama `dieta_sonora`.

## Versión pública

Hay una [versión para navegador](https://volteret4.github.io/repeat-one-web/dieta-sonora/) que no necesita servidor: obtiene los discos de tu cuenta de Muspy y los guarda en tu navegador, sin calendario, NAS ni descargas.

## Seguridad

Pensado para tu red local: no tiene usuarios. `/api/albums` devuelve tus enlaces de descarga personales, así que no lo expongas a internet sin un proxy con autenticación. El panel ⚙ solo muestra las credenciales si defines `SETTINGS_PASSWORD`.

Solo se descarga de `NAS_URL`: la web rechaza cualquier otro enlace. No subas `.env` ni `data/`.

## Cómo funciona

```text
Muspy / CalDAV → albums.csv → (Airsonic, qBittorrent: quita lo que ya tienes)
             → buscar_nuevos.py → resultado_flacs.json → html_generator.py → web
```

`main.sh` recorre esos pasos y se salta lo no configurado.

```bash
python3 test/test_muspy.py
```

## Licencia

Sin licencia por ahora: el código se puede leer, pero no concede permisos de reutilización.

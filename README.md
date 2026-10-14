# Plataforma de Noticias

API REST en Django para la gestión de publicaciones periodísticas: artículos, categorías, autores, lectores, comentarios e indicadores de lectura.

## Tecnologías
- Python 3.14, Django 5.2 LTS y Django REST Framework
- MySQL 8.0 con el driver `mysqlclient`
- `python-decouple` para leer las credenciales desde `.env`

## Instalación
1. `git clone https://github.com/JavierGeoffroy/noticias-backend-django.git`
2. `cd noticias-backend-django`
3. `py -m venv .venv`
4. `.venv\Scripts\Activate.ps1`
5. `pip install -r requirements.txt`
6. Crear la base de datos: ejecutar en MySQL los scripts de la carpeta `sql/` en orden (01, 02, 03). Antes, cambiar `CAMBIAR_CLAVE` en el script 02 por una clave real.
7. Copiar `.env.example` a `.env` y completar `SECRET_KEY` y `DB_PASSWORD` (la misma clave del paso anterior).
8. `python manage.py migrate`
9. `python manage.py loaddata pais rol estado categoria etiqueta`
10. `python manage.py createsuperuser`
11. `python manage.py runserver --insecure`

`--insecure` hace que el admin y la API se vean con estilos aunque `DEBUG=False`.

## Rutas principales
- `/` página de bienvenida
- `/api/` raíz de la API con los 13 endpoints: `paises`, `roles`, `estados`, `categorias`, `etiquetas`, `usuarios`, `perfiles`, `autores`, `articulos`, `historial-estados`, `comentarios`, `lecturas`, `favoritos`
- `/admin/` administrador de Django
- Cualquier otra ruta muestra la página 404 personalizada

## Estructura
- `noticias_core/`: configuración del proyecto (settings y urls)
- `noticias/`: app con `models.py`, `serializers.py`, `views.py`, `urls.py`, `admin.py`, `fixtures/` y `migrations/`
- `sql/`: scripts para crear la base de datos, el usuario y sus permisos

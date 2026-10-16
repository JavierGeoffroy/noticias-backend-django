# Plataforma de Noticias

API REST en Django para la gestión de publicaciones periodísticas: artículos, categorías, autores, lectores, comentarios e indicadores de lectura.

## Tecnologías
- Python 3.14, Django 5.2 LTS y Django REST Framework
- MySQL 8.0 con el driver `mysqlclient`
- `python-decouple` para leer la configuración desde el archivo `.env`

## Instalación
1. `git clone https://github.com/JavierGeoffroy/noticias-backend-django.git`
2. `cd noticias-backend-django`
3. `py -m venv .venv`
4. `.venv\Scripts\Activate.ps1`
5. `pip install -r requirements.txt`
6. Ejecutar como administrador en MySQL el script `sql/crear_base_datos.sql` (crea la base `noticias_db`, el usuario `noticias_user` y sus permisos). Por ejemplo, abriéndolo en MySQL Workbench.
7. El archivo `.env` ya está incluido en el repositorio con la configuración de conexión y la `SECRET_KEY`.
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
- `sql/`: script para crear la base de datos, el usuario y sus permisos

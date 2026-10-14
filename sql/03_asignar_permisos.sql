-- Script 3: da al usuario permisos solo sobre la base noticias_db (no sobre todo el servidor).
GRANT ALL PRIVILEGES ON noticias_db.* TO 'noticias_user'@'localhost';
FLUSH PRIVILEGES;

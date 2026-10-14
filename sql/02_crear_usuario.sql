-- Script 2: crea el usuario con el que Django se conecta a la base.
-- IMPORTANTE: reemplazar CAMBIAR_CLAVE por la clave real y usar la misma en el archivo .env (DB_PASSWORD).
CREATE USER IF NOT EXISTS 'noticias_user'@'localhost' IDENTIFIED BY 'CAMBIAR_CLAVE';

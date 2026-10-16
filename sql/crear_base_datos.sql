-- Evaluacion 2 - Programacion Backend - Plataforma de Noticias
-- Crea la base de datos, el usuario de la aplicacion y sus permisos.
-- Ejecutar como administrador (root) en MySQL 8.0 o superior.

-- 1. Crear la base de datos
CREATE DATABASE IF NOT EXISTS noticias_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 2. Crear el usuario de la aplicacion (misma clave que DB_PASSWORD en .env)
CREATE USER IF NOT EXISTS 'noticias_user'@'localhost' IDENTIFIED BY 'javiergeoffroy123';

-- 3. Asignar permisos solo sobre la base de la aplicacion
GRANT ALL PRIVILEGES ON noticias_db.* TO 'noticias_user'@'localhost';
FLUSH PRIVILEGES;

CREATE DATABASE IF NOT EXISTS sistema_biofiltros
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;


USE sistema_biofiltros;

CREATE TABLE USUARIOS (
id_usuario INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(50) NOT NULL UNIQUE,
password_hash CHAR(64) NOT NULL, -- SE USARA SHA-256
email VARCHAR(100) NOT NULL UNIQUE, 
estado ENUM('Activo','Inactivo','Bloqueado') DEFAULT('Activo'),
fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ROL (
id_rol INT AUTO_INCREMENT PRIMARY KEY,
nombre_rol VARCHAR(50),
descripcion LONGTEXT
);

CREATE TABLE USUARIO_ROLES (
    id_usuario INT,
    id_rol INT,
    asignado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_usuario, id_rol),
    FOREIGN KEY (id_usuario) REFERENCES USUARIOS(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_rol) REFERENCES ROL(id_rol) ON DELETE CASCADE
);

CREATE TABLE ERRORES (
id_error INT AUTO_INCREMENT PRIMARY KEY,
codigo VARCHAR(20) NOT NULL UNIQUE,
mensaje_usuario VARCHAR(255) NOT NULL,
mensaje_tecnico LONGTEXT,
severidad ENUM('baja','media','alta','critica') DEFAULT 'media',
fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



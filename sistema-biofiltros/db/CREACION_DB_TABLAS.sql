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
rol varchar(20) NOT NULL,
fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ROL (
id_rol INT AUTO_INCREMENT PRIMARY KEY,
nombre_rol VARCHAR(50),
descripcion LONGTEXT
);


CREATE TABLE ERRORES (
id_error INT AUTO_INCREMENT PRIMARY KEY,
codigo VARCHAR(20) NOT NULL UNIQUE,
mensaje_usuario VARCHAR(255) NOT NULL,
mensaje_tecnico LONGTEXT,
severidad ENUM('baja','media','alta','critica') DEFAULT 'media',
fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE biofiltros (
  id INT PRIMARY KEY,
  nombre_biofiltro VARCHAR(50),
  especie_vegetal VARCHAR(100),
  fecha_inicio DATE
);

CREATE TABLE lecturas_sensores (
  id INT PRIMARY KEY AUTO_INCREMENT,
  timestamp DATETIME,
  punto_muestreo ENUM('entrada', 'salida_biofiltro') NOT NULL,
  biofiltro_id INT NULL,
  od DECIMAL(4,2),
  ph DECIMAL(3,1),
  conductividad INT,
  solidos_solubles INT,
  turbidez INT,
  volumen_agua INT,
  numero_usuarios TINYINT,
  temperatura_agua DECIMAL(3,1),
  computed_eficiencia BOOLEAN
);

CREATE TABLE eficiencia_instantanea (
  id INT PRIMARY KEY AUTO_INCREMENT,
  timestamp DATETIME,
  eficiencia_od_global DECIMAL(5,2),
  eficiencia_turbidez_global DECIMAL(5,2),
  eficiencia_bf1_turbidez DECIMAL(5,2),
  eficiencia_bf2_turbidez DECIMAL(5,2),
  eficiencia_bf3_turbidez DECIMAL(5,2),
  cumple_norma BOOLEAN
);





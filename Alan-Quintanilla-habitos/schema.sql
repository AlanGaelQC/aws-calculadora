-- Sistema de Seguimiento de Hábitos
-- Equipo: Alan Gael Quintanilla Clemente

CREATE DATABASE IF NOT EXISTS `db-actividades`;
USE `db-actividades`;

CREATE TABLE IF NOT EXISTS habitos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    frecuencia ENUM('diaria', 'semanal') NOT NULL,
    meta VARCHAR(200),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS registros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    habito_id INT NOT NULL,
    fecha DATE NOT NULL,
    completado BOOLEAN DEFAULT TRUE,
    notas VARCHAR(200),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (habito_id) REFERENCES habitos(id)
);

CREATE TABLE IF NOT EXISTS rachas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    habito_id INT NOT NULL,
    racha_actual INT DEFAULT 0,
    racha_maxima INT DEFAULT 0,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (habito_id) REFERENCES habitos(id)
);

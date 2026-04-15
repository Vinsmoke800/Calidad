use parqueoDB
go

-- Tabla de usuarios
CREATE TABLE usuarios (
    id_usuario INT PRIMARY KEY IDENTITY(1,1),
    nombre VARCHAR(100) NOT NULL,
    correo_electronico VARCHAR(100) UNIQUE NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    identificacion VARCHAR(20) NOT NULL,
    numero_carne VARCHAR(20) NOT NULL,
    rol VARCHAR(50) NOT NULL,
    clave VARCHAR(100) NOT NULL DEFAULT 'Ulacit123',
);

-- Agregar una restricción CHECK para el rol
ALTER TABLE usuarios
ADD CONSTRAINT chk_rol CHECK (rol IN ('Administrador', 'Usuario'));

-- Tabla de parqueos
CREATE TABLE parqueos (
    id_parqueo INT PRIMARY KEY IDENTITY(1,1),
    nombre VARCHAR(100) NOT NULL,
    capacidad_espacios_regulares INT NOT NULL,
    capacidad_espacios_moto INT NOT NULL
);

-- Tabla de vehículos, con relación a usuarios y parqueos
CREATE TABLE vehiculos (
    id_vehiculo INT PRIMARY KEY IDENTITY(1,1),
    marca VARCHAR(50) NOT NULL,
    color VARCHAR(30) NOT NULL,
    numero_placa VARCHAR(20) UNIQUE NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    id_usuario INT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE, -- Si el usuario es eliminado, también se eliminan sus vehículos
);

-- Agregar una restricción CHECK para el tipo de vehículo
ALTER TABLE vehiculos
ADD CONSTRAINT chk_tipo_vehiculo CHECK (tipo IN ('Vehiculo', 'Moto'));

-- Tabla de espacios
CREATE TABLE espacios (
    id_espacio INT PRIMARY KEY IDENTITY(1,1),
    numero_espacio INT NOT NULL,
    tipo VARCHAR(20) NOT NULL, -- Regular, Moto, Ley7600
    id_parqueo INT NOT NULL,
    id_vehiculo INT NULL,

    -- Relaciones
    FOREIGN KEY (id_parqueo) REFERENCES parqueos(id_parqueo)
        ON DELETE CASCADE,

    FOREIGN KEY (id_vehiculo) REFERENCES vehiculos(id_vehiculo)
        ON DELETE SET NULL
);

ALTER TABLE espacios
ADD CONSTRAINT chk_tipo_espacio 
CHECK (tipo IN ('Regular', 'Moto', 'Ley7600'));

-- Eliminar las tablas
DROP TABLE IF EXISTS espacios;
DROP TABLE IF EXISTS vehiculos;
DROP TABLE IF EXISTS parqueos;
DROP TABLE IF EXISTS usuarios;
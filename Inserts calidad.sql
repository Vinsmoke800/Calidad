use parqueoDB
go

INSERT INTO usuarios (nombre, correo_electronico, fecha_nacimiento, identificacion, numero_carne, rol)
VALUES 
('Juan Perez', 'juan@correo.com', '2000-05-10', '123456789', '2020001', 'Administrador'),
('Maria Lopez', 'maria@correo.com', '1999-08-15', '987654321', '2020002', 'Usuario'),
('Carlos Ruiz', 'carlos@correo.com', '2001-02-20', '456789123', '2020003', 'Usuario');

INSERT INTO parqueos (nombre, capacidad_espacios_regulares, capacidad_espacios_moto)
VALUES
('Parqueo Central', 10, 5),
('Parqueo Norte', 8, 3);

INSERT INTO vehiculos (marca, color, numero_placa, tipo, id_usuario)
VALUES
('Toyota', 'Rojo', 'ABC123', 'Vehiculo', 1),
('Honda', 'Azul', 'XYZ789', 'Vehiculo', 2),
('Yamaha', 'Negro', 'MOTO1', 'Moto', 3),
('Suzuki', 'Blanco', 'MOTO2', 'Moto', 2);

INSERT INTO espacios (numero_espacio, tipo, id_parqueo, id_vehiculo)
VALUES
-- Parqueo 1 (Central)
(1, 'Regular', 1, 1),   -- ocupado (Toyota)
(2, 'Regular', 1, 2),   -- ocupado (Honda)
(3, 'Regular', 1, NULL),-- libre
(4, 'Moto', 1, 3),      -- ocupado (Yamaha)
(5, 'Moto', 1, NULL),   -- libre

-- Parqueo 2 (Norte)
(1, 'Regular', 2, NULL),
(2, 'Regular', 2, NULL),
(3, 'Moto', 2, 4),      -- ocupado (Suzuki)
(4, 'Moto', 2, NULL);

select * from usuarios
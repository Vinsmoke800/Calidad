# datos_parqueo.py
# Simulación simple de la base de datos del sistema de parqueos
# Adaptado a la estructura actual del proyecto

# ----------------------------------------
# LISTA SIMULADA DE VEHÍCULOS ESTACIONADOS
# ----------------------------------------

vehiculos_estacionados = [
    {
        "id": 1,
        "nombre_usuario": "Juan Pérez",
        "placa": "ABC-123",
        "tipo_vehiculo": "Vehiculo",
        "tipo_espacio": "Regular",
        "hora_ingreso": "08:30"
    },
    {
        "id": 2,
        "nombre_usuario": "María López",
        "placa": "MOTO-01",
        "tipo_vehiculo": "Moto",
        "tipo_espacio": "Moto",
        "hora_ingreso": "09:15"
    },
    {
        "id": 3,
        "nombre_usuario": "Pedro Gómez",
        "placa": "LEY-001",
        "tipo_vehiculo": "Vehiculo",
        "tipo_espacio": "Ley7600",
        "hora_ingreso": "10:00"
    },
    {
        "id": 4,
        "nombre_usuario": "Carlos Ruiz",
        "placa": "DEF-456",
        "tipo_vehiculo": "Vehiculo",
        "tipo_espacio": "Regular",
        "hora_ingreso": "11:20"
    }
]

# ----------------------------------------
# CUPOS TOTALES SEGÚN EL SISTEMA
# ----------------------------------------

cupos_totales = {
    "Regular": 50,
    "Moto": 10,
    "Ley7600": 5
}


# ----------------------------------------
# FUNCIONES
# ----------------------------------------

def obtener_vehiculos():
    """
    Retorna la lista de vehículos estacionados
    """
    return vehiculos_estacionados


def agregar_vehiculo(nombre_usuario, placa, tipo_vehiculo, tipo_espacio, hora_ingreso):
    """
    Agrega un nuevo vehículo a la lista simulada
    """

    if not nombre_usuario:
        raise TypeError("El nombre del usuario no puede estar vacío")

    nuevo_id = len(vehiculos_estacionados) + 1

    nuevo_vehiculo = {
        "id": nuevo_id,
        "nombre_usuario": nombre_usuario,
        "placa": placa,
        "tipo_vehiculo": tipo_vehiculo,
        "tipo_espacio": tipo_espacio,
        "hora_ingreso": hora_ingreso
    }

    vehiculos_estacionados.append(nuevo_vehiculo)

    return nuevo_id


def eliminar_vehiculo(placa):
    """
    Elimina un vehículo según su placa
    """

    for i, vehiculo in enumerate(vehiculos_estacionados):
        if vehiculo["placa"] == placa:
            vehiculos_estacionados.pop(i)
            return True

    return False


def contar_ocupados_por_tipo():
    """
    Cuenta cuántos espacios están ocupados por tipo
    """

    conteo = {
        "Regular": 0,
        "Moto": 0,
        "Ley7600": 0
    }

    for vehiculo in vehiculos_estacionados:
        tipo = vehiculo["tipo_espacio"]
        conteo[tipo] += 1

    return conteo


def calcular_disponibles():
    """
    Calcula espacios disponibles por tipo
    """

    ocupados = contar_ocupados_por_tipo()
    disponibles = {}

    for tipo in cupos_totales:
        disponibles[tipo] = cupos_totales[tipo] - ocupados[tipo]

        if disponibles[tipo] < 0:
            disponibles[tipo] = 0

    return disponibles
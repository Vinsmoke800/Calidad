# Prueba la base de datos de los vehiculos, conexión, y CRUD

import pytest
from datos_parqueo import (
    obtener_vehiculos,
    agregar_vehiculo,
    eliminar_vehiculo,
    contar_ocupados_por_tipo,
    calcular_disponibles,
    vehiculos_estacionados
)


# Se ejecuta antes de cada prueba
@pytest.fixture
def reiniciar_datos():
    datos_originales = [
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

    vehiculos_estacionados.clear()
    vehiculos_estacionados.extend(datos_originales)

    yield


def test_obtener_vehiculos_devuelve_lista(reiniciar_datos):
    usuarios = obtener_vehiculos()
    assert len(usuarios) == 4


def test_agregar_vehiculo_aumenta_lista(reiniciar_datos):
    antes = len(obtener_vehiculos())

    agregar_vehiculo(
        "Ana Martínez",
        "GHI-789",
        "Vehiculo",
        "Regular",
        "14:00"
    )

    despues = len(obtener_vehiculos())

    assert despues == antes + 1


def test_eliminar_vehiculo_disminuye_lista(reiniciar_datos):
    antes = len(obtener_vehiculos())

    resultado = eliminar_vehiculo("MOTO-01")

    despues = len(obtener_vehiculos())

    assert resultado is True
    assert despues == antes - 1


def test_contar_ocupados_por_tipo(reiniciar_datos):
    ocupados = contar_ocupados_por_tipo()

    assert ocupados["Regular"] == 2
    assert ocupados["Moto"] == 1
    assert ocupados["Ley7600"] == 1


def test_calcular_disponibles(reiniciar_datos):
    disponibles = calcular_disponibles()

    assert disponibles["Regular"] == 48
    assert disponibles["Moto"] == 9
    assert disponibles["Ley7600"] == 4


def test_no_agregar_vehiculo_sin_nombre(reiniciar_datos):
    with pytest.raises(TypeError):
        agregar_vehiculo(
            "",
            "XYZ-000",
            "Vehiculo",
            "Regular",
            "15:00"
        )
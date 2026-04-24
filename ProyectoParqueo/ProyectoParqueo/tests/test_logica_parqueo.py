
# Pruebas unitarias adaptadas a la estructura actual del proyecto, cupos, disponibilidad, reglas de parqueo

from logica_parqueo import calcular_cupos_disponibles


def test_cupos_regulares_normales():
    """
    Prueba: Escenario normal con espacios regulares

    Situación:
    50 espacios totales, 45 ocupados

    Resultado esperado:
    5 espacios disponibles
    """

    resultado = calcular_cupos_disponibles(
        50,
        45,
        "Regular"
    )

    assert resultado == 5


def test_cupos_regulares_saturados():
    """
    Prueba: Parqueo regular completamente lleno

    Situación:
    50 espacios totales, 50 ocupados

    Resultado esperado:
    0 espacios disponibles
    """

    resultado = calcular_cupos_disponibles(
        50,
        50,
        "Regular"
    )

    assert resultado == 0


def test_cupos_regulares_sobrecupo():
    """
    Prueba: Error de sobrecupo

    Situación:
    50 espacios totales, 55 ocupados

    Resultado esperado:
    0 (no se permiten negativos)
    """

    resultado = calcular_cupos_disponibles(
        50,
        55,
        "Regular"
    )

    assert resultado == 0


def test_cupos_ley7600_con_espacios():
    """
    Prueba: Espacios Ley 7600 con disponibilidad suficiente

    Situación:
    10 espacios, 5 ocupados

    Resultado esperado:
    5 espacios disponibles
    """

    resultado = calcular_cupos_disponibles(
        10,
        5,
        "Ley7600"
    )

    assert resultado == 5


def test_cupos_ley7600_sin_espacios():
    """
    Prueba: Espacios Ley 7600 completamente llenos

    Situación:
    10 espacios, 10 ocupados

    Resultado esperado:
    2 (regla especial mínima)
    """

    resultado = calcular_cupos_disponibles(
        10,
        10,
        "Ley7600"
    )

    assert resultado == 2


def test_cupos_motos_normales():
    """
    Prueba: Espacios para motos

    Situación:
    20 espacios, 15 ocupados

    Resultado esperado:
    5 espacios disponibles
    """

    resultado = calcular_cupos_disponibles(
        20,
        15,
        "Moto"
    )

    assert resultado == 5
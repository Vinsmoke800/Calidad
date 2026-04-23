# logica_parqueo.py
# Este archivo contiene la lógica de negocio del sistema de parqueos

def calcular_cupos_disponibles(capacidad_total, ocupados, tipo_espacio):
    """
    Calcula los espacios disponibles según el tipo de espacio.

    Parámetros:
    - capacidad_total: total de espacios registrados
      (ej: capacidad_espacios_regulares o capacidad_espacios_moto)
    - ocupados: cantidad de espacios actualmente ocupados
    - tipo_espacio: "Regular", "Moto" o "Ley7600"

    Retorna:
    - número de espacios disponibles (mínimo 0)
    - Para Ley7600: siempre deben existir al menos 2 espacios disponibles
    """

    disponibles = capacidad_total - ocupados

    # Regla especial para Ley 7600
    if tipo_espacio == "Ley7600" and disponibles < 2:
        return 2

    # Evitar valores negativos
    return disponibles if disponibles >= 0 else 0


def validar_tipo_vehiculo(tipo):
    """
    Valida si el tipo de vehículo es permitido
    según la base de datos.

    Tipos válidos:
    - Vehiculo
    - Moto
    """

    tipos_validos = ["Vehiculo", "Moto"]
    return tipo in tipos_validos


def asignar_tipo_espacio(tipo_vehiculo):
    """
    Determina automáticamente el tipo de espacio
    según el tipo de vehículo.

    Parámetros:
    - tipo_vehiculo: "Vehiculo" o "Moto"

    Retorna:
    - "Regular" si es Vehiculo
    - "Moto" si es Moto
    - None si no es válido
    """

    if tipo_vehiculo == "Vehiculo":
        return "Regular"

    elif tipo_vehiculo == "Moto":
        return "Moto"

    return None


# --------------------------------------------------
# PRUEBAS DEL ARCHIVO
# --------------------------------------------------
if __name__ == "__main__":

    print("===== PRUEBAS DE LOGICA PARQUEO =====")

    # Prueba 1: cupos regulares
    print("Prueba 1:",
          calcular_cupos_disponibles(50, 20, "Regular"))
    # Esperado: 30

    # Prueba 2: Ley 7600 con menos de 2 disponibles
    print("Prueba 2:",
          calcular_cupos_disponibles(10, 9, "Ley7600"))
    # Esperado: 2

    # Prueba 3: evitar negativos
    print("Prueba 3:",
          calcular_cupos_disponibles(10, 15, "Regular"))
    # Esperado: 0

    # Prueba 4: tipo válido
    print("Prueba 4:",
          validar_tipo_vehiculo("Vehiculo"))
    # Esperado: True

    # Prueba 5: tipo inválido
    print("Prueba 5:",
          validar_tipo_vehiculo("Bicicleta"))
    # Esperado: False

    # Prueba 6: asignación correcta
    print("Prueba 6:",
          asignar_tipo_espacio("Vehiculo"))
    # Esperado: Regular

    # Prueba 7: asignación correcta
    print("Prueba 7:",
          asignar_tipo_espacio("Moto"))
    # Esperado: Moto

    # Prueba 8: tipo inválido
    print("Prueba 8:",
          asignar_tipo_espacio("Bicicleta"))
    # Esperado: None
"""Batería de pruebas integrales para verificar datos.py y calculos.py."""

from backend.datos import (
    cargar_bancos,
    cargar_clientes,
    cargar_historial_tasas,
    buscar_cliente_por_cuit,
    listar_marcas,
    listar_bancos,
    listar_lineas,
    listar_plazos,
    obtener_tasa,
)
from backend.calculos import (
    ErrorDeSimulacion,
    calcular_monto_a_financiar,
    calcular_cuota,
    calcular_quebranto,
    calcular_relacion_cuota_ingreso,
    calcular_monto_max_por_cuota,
    calcular_tope_banco,
    calcular_monto_max_total,
    verificar_aptitud_cliente,
    simular_operacion,
    simular_por_cuit,
)


def probar_lectura_y_selectores() -> None:
    """1. Verifica la carga de DataFrames, columnas y selectores en cascada."""
    df_bancos = cargar_bancos()
    df_clientes = cargar_clientes()
    df_historial = cargar_historial_tasas()

    assert len(df_bancos) == 21, f"Se esperaban 21 tasas, hay {len(df_bancos)}"
    assert len(df_clientes) == 1000, f"Se esperaban 1000 clientes, hay {len(df_clientes)}"
    assert len(df_clientes.columns) == 19, "Faltan columnas en clientes_riesgo_nosis.csv"
    assert len(df_historial) == 48, f"Se esperaban 48 filas de historial, hay {len(df_historial)}"

    assert listar_marcas() == ["Ford", "Toyota", "Volkswagen"]
    assert "Santander" in listar_bancos("Ford")
    assert "Prendario Tasa Fija Subvencionada" in listar_lineas("Ford", "Santander")
    assert listar_plazos("Ford", "Santander", "Prendario Tasa Fija Subvencionada") == [24, 36, 48]

    # Tolerancia a mayúsculas/minúsculas y espacios en obtener_tasa
    tasa = obtener_tasa("  ford ", "SANTANDER", "préstamo tradicional fijo", 60)
    assert tasa is not None and tasa["id_tasa"] == "TAS-03"
    print("✅ [1/4] Lectura de CSVs, caché y selectores en cascada: OK")


def probar_busqueda_cuit() -> None:
    """2. Verifica búsqueda de clientes con guiones, sin guiones e inexistentes."""
    cuit_real = "20-89254563-6"  # CLI-1001
    cli_con_guiones = buscar_cliente_por_cuit(cuit_real)
    cli_sin_guiones = buscar_cliente_por_cuit("20892545636")
    cli_con_espacios = buscar_cliente_por_cuit("  20.89254563-6 ")

    assert cli_con_guiones is not None
    assert cli_con_guiones == cli_sin_guiones == cli_con_espacios
    assert buscar_cliente_por_cuit("99-99999999-9") is None
    assert buscar_cliente_por_cuit("") is None
    print("✅ [2/4] Búsqueda normalizada de clientes por CUIT: OK")


def probar_calculos_y_topes() -> None:
    """3. Verifica fórmulas matemáticas y detección inteligente de LTV vs. Tope Fijo."""
    assert calcular_monto_a_financiar(61_459_000, 30_176_740) == 31_282_260.0
    assert calcular_cuota(15_000_000, 42.2) == 633_000.0
    assert calcular_quebranto(15_000_000, 2.0) == 300_000.0
    assert calcular_relacion_cuota_ingreso(633_000, 2_000_000) == 31.65

    # LTV por porcentaje (80% de $60.000.000 = $48.000.000)
    assert calcular_tope_banco(80, 60_000_000) == 48_000_000.0
    # Tope fijo en pesos ($45.000.000 sobre un auto de $60.000.000 -> topea en $45.000.000)
    assert calcular_tope_banco(45_000_000, 60_000_000) == 45_000_000.0
    # Monto máximo combinando bolsillo del cliente vs tope fijo del banco
    assert calcular_monto_max_total(1_500_000, 29.34, 45_000_000, 60_000_000) == 45_000_000.0

    apto_ok, motivos_ok = verificar_aptitud_cliente(750, 24)
    assert apto_ok is True and motivos_ok == []

    apto_mal, motivos_mal = verificar_aptitud_cliente(450, 3)
    assert apto_mal is False and len(motivos_mal) == 2
    print("✅ [3/4] Fórmulas financieras, LTV porcentual y Tope Fijo ($45M): OK")


def probar_casos_borde_y_simulacion() -> None:
    """4. Verifica que los 7 bugs planteados lancen ErrorDeSimulacion correctamente."""
    casos_invalidos = [
        ("Ingreso 0 en relación cuota/ingreso", lambda: calcular_relacion_cuota_ingreso(100_000, 0)),
        ("NaN en calcular_cuota", lambda: calcular_cuota(1_000_000, float("nan"))),
        ("Inf en calcular_monto_a_financiar", lambda: calcular_monto_a_financiar(float("inf"), 1000)),
        ("NaN en calcular_monto_max_por_cuota", lambda: calcular_monto_max_por_cuota(float("nan"), 42.2)),
        ("Cuota prom <= 0 en monto_max_por_cuota", lambda: calcular_monto_max_por_cuota(500_000, 0)),
        ("Booleano camuflado como número", lambda: calcular_cuota(True, 42.2)),
        ("LTV negativo en calcular_tope_banco", lambda: calcular_tope_banco(-10, 20_000_000)),
        ("Anticipo mayor al precio del auto", lambda: calcular_monto_a_financiar(10_000_000, 12_000_000)),
        ("Columna faltante en diccionario", lambda: simular_operacion(20_000_000, 5_000_000, {}, {})),
        (
            "Celda vacía (None) en diccionario",
            lambda: simular_operacion(
                20_000_000,
                5_000_000,
                {
                    "nombre_apellido": "Juan Pérez",
                    "ingreso_mensual_neto": None,
                    "score_nosis": 700,
                    "antiguedad_laboral_meses": 12,
                    "cuota_maxima_afectable": 500_000,
                },
                obtener_tasa("Ford", "Santander", "Préstamo Tradicional Fijo", 60),
            ),
        ),
        (
            "CUIT inexistente en simular_por_cuit",
            lambda: simular_por_cuit("00-00000000-0", 20_000_000, 5_000_000, "Ford", "Santander", "Préstamo Tradicional Fijo", 60),
        ),
    ]

    for descripcion, funcion in casos_invalidos:
        try:
            funcion()
            raise AssertionError(f"FALLÓ: '{descripcion}' no lanzó ErrorDeSimulacion.")
        except ErrorDeSimulacion:
            pass

    # Simulación real de punta a punta con cliente aprobado (CLI-1013: 27-64634663-3)
    res = simular_por_cuit(
        cuit="27-64634663-3",
        precio_vehiculo=30_000_000,
        anticipo=15_000_000,
        marca="Ford",
        banco="Santander",
        nombre_tasa="Préstamo Tradicional Fijo",
        plazo=60,
    )
    assert res["monto_a_financiar"] == 15_000_000.0
    assert res["cuota_mensual"] == 633_000.0
    assert res["apto"] is True
    assert res["motivos_rechazo"] == []
    print("✅ [4/4] Blindaje de los 7 casos borde y simulación de punta a punta: OK")


if __name__ == "__main__":
    print("Iniciando pruebas del motor de datos y cálculos...\n")
    probar_lectura_y_selectores()
    probar_busqueda_cuit()
    probar_calculos_y_topes()
    probar_casos_borde_y_simulacion()
    print("\n🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE! El motor está listo para producción.")
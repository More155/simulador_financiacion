"""Módulo de cálculos financieros: cuota, quebranto y monto máximo financiable."""

import math
from typing import Any

# Reglas de aptitud del proyecto
SCORE_MINIMO = 600
ANTIGUEDAD_MINIMA_MESES = 6


class ErrorDeSimulacion(ValueError):
    """Excepción personalizada para errores esperados de negocio o entrada inválida."""
    pass


def _validar_finitos(**valores: Any) -> None:
    """Verifica que todos los parámetros numéricos sean finitos (no NaN, Inf ni booleanos)."""
    for nombre, valor in valores.items():
        if (
            isinstance(valor, bool)
            or not isinstance(valor, (int, float))
            or not math.isfinite(valor)
        ):
            raise ErrorDeSimulacion(
                f"El parámetro '{nombre}' debe ser un número finito válido (recibido: {valor})."
            )


def _extraer_numero(registro: dict, columna: str, origen: str) -> float:
    """Extrae y valida un valor numérico desde un diccionario (cliente o tasa)."""
    if not isinstance(registro, dict) or columna not in registro:
        raise ErrorDeSimulacion(f"Falta la columna obligatoria '{columna}' en {origen}.")

    valor = registro[columna]
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        raise ErrorDeSimulacion(f"La celda de la columna '{columna}' en {origen} está vacía.")

    try:
        numero = float(valor)
    except (ValueError, TypeError) as exc:
        raise ErrorDeSimulacion(
            f"El valor de '{columna}' en {origen} no es numérico ({valor})."
        ) from exc

    if not math.isfinite(numero):
        raise ErrorDeSimulacion(
            f"La celda de la columna '{columna}' en {origen} contiene un valor inválido (NaN/Inf)."
        )
    return numero


def _extraer_texto(registro: dict, columna: str, origen: str) -> str:
    """Extrae y valida un campo de texto obligatorio desde un diccionario."""
    if not isinstance(registro, dict) or columna not in registro:
        raise ErrorDeSimulacion(f"Falta la columna obligatoria '{columna}' en {origen}.")

    valor = registro[columna]
    if valor is None or (isinstance(valor, float) and not math.isfinite(valor)):
        raise ErrorDeSimulacion(f"La celda de la columna '{columna}' en {origen} está vacía.")

    texto = str(valor).strip()
    if not texto:
        raise ErrorDeSimulacion(f"La celda de la columna '{columna}' en {origen} está vacía.")
    return texto


def calcular_monto_a_financiar(precio_vehiculo: float, anticipo: float) -> float:
    _validar_finitos(precio_vehiculo=precio_vehiculo, anticipo=anticipo)
    if precio_vehiculo <= 0:
        raise ErrorDeSimulacion("El precio del vehículo debe ser mayor a 0.")
    if anticipo < 0:
        raise ErrorDeSimulacion("El anticipo no puede ser negativo.")
    if anticipo >= precio_vehiculo:
        raise ErrorDeSimulacion("El anticipo debe ser menor al precio del vehículo.")
    return round(precio_vehiculo - anticipo, 2)


def calcular_cuota(monto_a_financiar: float, cuota_promedio_1000: float) -> float:
    _validar_finitos(
        monto_a_financiar=monto_a_financiar,
        cuota_promedio_1000=cuota_promedio_1000,
    )
    if monto_a_financiar <= 0 or cuota_promedio_1000 <= 0:
        raise ErrorDeSimulacion(
            "El monto a financiar y la cuota promedio deben ser mayores a 0."
        )
    cuota = (monto_a_financiar / 1000.0) * cuota_promedio_1000
    return round(cuota, 2)


def calcular_quebranto(monto_a_financiar: float, quebranto_pct: float) -> float:
    _validar_finitos(monto_a_financiar=monto_a_financiar, quebranto_pct=quebranto_pct)
    if monto_a_financiar <= 0 or quebranto_pct < 0:
        raise ErrorDeSimulacion(
            "El monto debe ser positivo y el quebranto no puede ser negativo."
        )
    return round(monto_a_financiar * (quebranto_pct / 100.0), 2)


def calcular_relacion_cuota_ingreso(cuota: float, ingreso_mensual: float) -> float:
    _validar_finitos(cuota=cuota, ingreso_mensual=ingreso_mensual)
    if cuota < 0:
        raise ErrorDeSimulacion("La cuota no puede ser negativa.")
    if ingreso_mensual <= 0:
        raise ErrorDeSimulacion("El ingreso mensual debe ser mayor a 0.")
    return round((cuota / ingreso_mensual) * 100.0, 2)


def calcular_monto_max_por_cuota(
    cuota_maxima_afectable: float, cuota_promedio_1000: float
) -> float:
    _validar_finitos(
        cuota_maxima_afectable=cuota_maxima_afectable,
        cuota_promedio_1000=cuota_promedio_1000,
    )
    if cuota_promedio_1000 <= 0:
        raise ErrorDeSimulacion("La cuota promedio cada $1.000 debe ser mayor a 0.")
    if cuota_maxima_afectable <= 0:
        return 0.0
    monto_max = (cuota_maxima_afectable / cuota_promedio_1000) * 1000.0
    return float(math.floor(monto_max))


def calcular_tope_banco(ltv_o_tope: float, valor_vehiculo: float = 0.0) -> float:
    _validar_finitos(ltv_o_tope=ltv_o_tope, valor_vehiculo=valor_vehiculo)
    if ltv_o_tope <= 0:
        raise ErrorDeSimulacion("El parámetro LTV o tope fijo debe ser mayor a 0.")
    if ltv_o_tope > 100:
        return float(
            math.floor(
                min(ltv_o_tope, valor_vehiculo) if valor_vehiculo > 0 else ltv_o_tope
            )
        )
    if valor_vehiculo <= 0:
        return float("inf")
    return float(math.floor(valor_vehiculo * (ltv_o_tope / 100.0)))


def calcular_monto_max_total(
    cuota_maxima_afectable: float,
    cuota_promedio_1000: float,
    ltv_o_tope: float = 100.0,
    valor_vehiculo: float = 0.0,
) -> float:
    limite_cliente = calcular_monto_max_por_cuota(
        cuota_maxima_afectable, cuota_promedio_1000
    )
    limite_banco = calcular_tope_banco(ltv_o_tope, valor_vehiculo)
    return min(limite_cliente, limite_banco)


def verificar_aptitud_cliente(
    score_nosis: int, antiguedad_meses: int
) -> tuple[bool, list[str]]:
    """Verifica la aptitud y devuelve (es_apto, lista_de_motivos_de_rechazo)."""
    _validar_finitos(score_nosis=score_nosis, antiguedad_meses=antiguedad_meses)
    motivos = []
    if score_nosis < SCORE_MINIMO:
        motivos.append(f"Score crediticio insuficiente ({int(score_nosis)}).")
    if antiguedad_meses < ANTIGUEDAD_MINIMA_MESES:
        motivos.append(
            f"Antigüedad laboral menor a {ANTIGUEDAD_MINIMA_MESES} meses."
        )
    return len(motivos) == 0, motivos


def simular_operacion(
    precio_vehiculo: float,
    anticipo: float,
    cliente: dict,
    tasa: dict,
    cuota_maxima_predicha: float | None = None,
) -> dict:
    monto = calcular_monto_a_financiar(precio_vehiculo, anticipo)

    cuota_prom = _extraer_numero(tasa, "cuota_promedio_1000", "la tasa seleccionada")
    quebranto_pct = _extraer_numero(tasa, "quebranto_pct", "la tasa seleccionada")
    ltv_val = _extraer_numero(tasa, "ltv", "la tasa seleccionada")
    tna_pct = _extraer_numero(tasa, "tna_pct", "la tasa seleccionada")
    cftea_pct = _extraer_numero(tasa, "cftea_pct", "la tasa seleccionada")
    banco_nombre = _extraer_texto(tasa, "banco", "la tasa seleccionada")
    marca_nombre = _extraer_texto(tasa, "marca", "la tasa seleccionada")
    linea_nombre = _extraer_texto(tasa, "nombre_tasa", "la tasa seleccionada")

    ingreso = _extraer_numero(cliente, "ingreso_mensual_neto", "los datos del cliente")
    score = int(_extraer_numero(cliente, "score_nosis", "los datos del cliente"))
    antiguedad = int(
        _extraer_numero(cliente, "antiguedad_laboral_meses", "los datos del cliente")
    )
    cliente_nombre = _extraer_texto(cliente, "nombre_apellido", "los datos del cliente")

    if cuota_maxima_predicha is not None:
        _validar_finitos(cuota_maxima_predicha=cuota_maxima_predicha)
        cuota_max = float(cuota_maxima_predicha)
    else:
        cuota_max = _extraer_numero(
            cliente, "cuota_maxima_afectable", "los datos del cliente"
        )

    cuota = calcular_cuota(monto, cuota_prom)
    quebranto = calcular_quebranto(monto, quebranto_pct)
    monto_max = calcular_monto_max_total(
        cuota_max, cuota_prom, ltv_val, precio_vehiculo
    )

    es_apto, motivos = verificar_aptitud_cliente(score, antiguedad)

    if monto > monto_max:
        es_apto = False
        motivos.append(
            "El monto a financiar supera el límite permitido por el banco o los ingresos."
        )

    return {
        "cliente": {
            "nombre": cliente_nombre,
            "ingreso_neto": ingreso,
            "cuota_maxima_afectable": cuota_max,
        },
        "linea": {
            "banco": banco_nombre,
            "marca": marca_nombre,
            "nombre": linea_nombre,
            "tna_pct": tna_pct,
            "cftea_pct": cftea_pct,
        },
        "monto_a_financiar": monto,
        "cuota_mensual": cuota,
        "quebranto_pesos": quebranto,
        "monto_maximo_permitido": monto_max,
        "relacion_cuota_ingreso_pct": calcular_relacion_cuota_ingreso(cuota, ingreso),
        "apto": es_apto,
        "motivos_rechazo": motivos,
    }


def simular_por_cuit(
    cuit: str,
    precio_vehiculo: float,
    anticipo: float,
    marca: str,
    banco: str,
    nombre_tasa: str,
    plazo: int,
    cuota_maxima_predicha: float | None = None,
) -> dict:
    """
    Función fachada para el endpoint de simulación de FastAPI.
    Busca al cliente por CUIT, obtiene la tasa de interés según las opciones
    seleccionadas y ejecuta la simulación completa. Si se provee la 
    'cuota_maxima_predicha' desde el modelo de ML, sobreescribe la del cliente.

    Retorna:
        Un diccionario con la información financiera filtrada y lista para JSON.
    """
    from backend.datos import buscar_cliente_por_cuit, obtener_tasa

    cliente = buscar_cliente_por_cuit(cuit)
    if not cliente:
        raise ErrorDeSimulacion(f"No se encontró un cliente con el CUIT {cuit}.")

    tasa = obtener_tasa(marca, banco, nombre_tasa, plazo)
    if not tasa:
        raise ErrorDeSimulacion(
            "La línea de crédito seleccionada no existe o no está disponible para ese plazo."
        )

    return simular_operacion(precio_vehiculo, anticipo, cliente, tasa, cuota_maxima_predicha)
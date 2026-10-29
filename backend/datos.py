"""Módulo de lectura de archivos CSV y conversión a DataFrames de Pandas.

Lee los CSV de la carpeta data/ y los convierte en DataFrames de pandas.
Incluye funciones de consulta para clientes (por CUIT/CUIL) y para las
líneas de crédito de los bancos.
"""

import math
import os
from functools import lru_cache
from typing import Optional
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ARCHIVO_BANCOS = "bancos_tasas.csv"
ARCHIVO_CLIENTES = "clientes_riesgo_nosis.csv"
ARCHIVO_HISTORIAL = "historial_tasas.csv"

COLUMNAS_TEXTO = {"cuit_cuil", "id_cliente", "id_tasa"}


def _limpiar_fila_dict(fila: dict) -> dict:
    """
    Convierte valores NaN o Inf a None al exportar una fila individual.
    Así el DataFrame conserva los NaN para scikit-learn, pero FastAPI recibe
    un diccionario limpio compatible con JSON.
    """
    return {
        clave: (None if isinstance(valor, float) and not math.isfinite(valor) else valor)
        for clave, valor in fila.items()
    }


def leer_csv_a_dataframe(nombre_archivo: str) -> pd.DataFrame:
    nombre_seguro = os.path.basename(nombre_archivo)
    ruta_archivo = os.path.join(DATA_DIR, nombre_seguro)
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"El archivo {nombre_archivo} no fue encontrado.")

    configuraciones = [
        {"sep": ",", "encoding": "utf-8"},
        {"sep": ";", "encoding": "utf-8-sig"},
        {"sep": ";", "encoding": "latin-1", "decimal": ","},
        {"sep": ",", "encoding": "latin-1"},
    ]
    df = None
    for config in configuraciones:
        try:
            df = pd.read_csv(
                ruta_archivo,
                sep=config["sep"],
                encoding=config["encoding"],
                decimal=config.get("decimal", "."),
                dtype=str,
            )
            if len(df.columns) > 1:
                break
        except Exception:
            continue

    if df is None or len(df.columns) <= 1:
        raise ValueError(
            f"No se pudo leer el archivo {nombre_archivo}. Verifique el formato y separador."
        )

    if df.empty:
        raise ValueError(f"El archivo {nombre_archivo} está vacío.")

    df.columns = df.columns.str.strip()

    for columna in df.columns:
        if columna in COLUMNAS_TEXTO:
            df[columna] = df[columna].str.strip()
            continue

        serie_limpia = df[columna].astype(str).str.replace(",", ".").str.strip()
        try:
            df[columna] = pd.to_numeric(serie_limpia)
        except (ValueError, TypeError):
            pass

    return df


@lru_cache(maxsize=1)
def _bancos_cache() -> pd.DataFrame:
    return leer_csv_a_dataframe(ARCHIVO_BANCOS)


@lru_cache(maxsize=1)
def _clientes_cache() -> pd.DataFrame:
    return leer_csv_a_dataframe(ARCHIVO_CLIENTES)


@lru_cache(maxsize=1)
def _historial_cache() -> pd.DataFrame:
    return leer_csv_a_dataframe(ARCHIVO_HISTORIAL)


def cargar_bancos() -> pd.DataFrame:
    """Devuelve el DataFrame con las líneas de crédito de bancos_tasas.csv."""
    return _bancos_cache().copy()


def cargar_clientes() -> pd.DataFrame:
    """Devuelve el DataFrame con los clientes de clientes_riesgo_nosis.csv."""
    return _clientes_cache().copy()


def cargar_historial_tasas() -> pd.DataFrame:
    """Devuelve el historial de tasas por banco y mes."""
    return _historial_cache().copy()


def recargar_datos() -> None:
    """Vacía la caché si se modifican los CSV con el programa corriendo."""
    _bancos_cache.cache_clear()
    _clientes_cache.cache_clear()
    _historial_cache.cache_clear()


def _solo_digitos(valor) -> str:
    """Deja únicamente los dígitos: '23-43200604-7' -> '23432006047'."""
    return "".join(c for c in str(valor) if c.isdigit())


def buscar_cliente_por_cuit(cuit: str) -> Optional[dict]:
    """Busca un cliente por su CUIT/CUIL y devuelve sus datos como diccionario."""
    cuit_buscado = _solo_digitos(cuit)
    if not cuit_buscado:
        return None
    df_clientes = cargar_clientes()
    coincide = df_clientes["cuit_cuil"].map(_solo_digitos) == cuit_buscado
    cliente = df_clientes[coincide]
    if cliente.empty:
        return None
    return _limpiar_fila_dict(cliente.to_dict(orient="records")[0])


# ---------------------------------------------------------------------------
# Bancos y líneas de crédito (selectores en cascada del frontend)
# ---------------------------------------------------------------------------
def listar_marcas() -> list:
    """
    Lista todas las marcas de vehículos disponibles en la base de datos.
    Se utiliza para poblar el primer selector desplegable del frontend.
    """
    return sorted(cargar_bancos()["marca"].dropna().unique().tolist())


def listar_bancos(marca: str) -> list:
    """
    Filtra y devuelve los bancos que ofrecen financiación para una marca específica.
    Ignora diferencias de mayúsculas/minúsculas y espacios.
    """
    df = cargar_bancos()
    m = str(marca).strip().lower()
    filtro = df[df["marca"].astype(str).str.strip().str.lower() == m]
    return sorted(filtro["banco"].dropna().unique().tolist())


def listar_lineas(marca: str, banco: str) -> list:
    """
    Filtra las líneas de crédito (nombre_tasa) disponibles para una combinación
    de marca y banco elegida, normalizando los textos para evitar errores de tipeo.
    """
    df = cargar_bancos()
    m = str(marca).strip().lower()
    b = str(banco).strip().lower()
    filtro = df[
        (df["marca"].astype(str).str.strip().str.lower() == m)
        & (df["banco"].astype(str).str.strip().str.lower() == b)
    ]
    return sorted(filtro["nombre_tasa"].dropna().unique().tolist())


def listar_plazos(marca: str, banco: str, nombre_tasa: str) -> list:
    """
    Obtiene los plazos de financiación (en meses) disponibles para una línea
    de crédito específica de un banco y marca determinados.
    """
    df = cargar_bancos()
    m = str(marca).strip().lower()
    b = str(banco).strip().lower()
    t = str(nombre_tasa).strip().lower()
    filtro = df[
        (df["marca"].astype(str).str.strip().str.lower() == m)
        & (df["banco"].astype(str).str.strip().str.lower() == b)
        & (df["nombre_tasa"].astype(str).str.strip().str.lower() == t)
    ]
    return sorted(int(p) for p in filtro["plazo_meses"].dropna().unique())


def obtener_tasa(
    marca: str, banco: str, nombre_tasa: str, plazo_meses: int
) -> Optional[dict]:
    """
    Devuelve la fila completa de la tabla de tasas (como diccionario)
    para la combinación exacta de marca, banco, línea y plazo.
    Aplica normalización de textos para tolerar diferencias de formato.
    """
    df = cargar_bancos()
    m = str(marca).strip().lower()
    b = str(banco).strip().lower()
    t = str(nombre_tasa).strip().lower()
    filtro = df[
        (df["marca"].astype(str).str.strip().str.lower() == m)
        & (df["banco"].astype(str).str.strip().str.lower() == b)
        & (df["nombre_tasa"].astype(str).str.strip().str.lower() == t)
        & (df["plazo_meses"] == plazo_meses)
    ]
    if filtro.empty:
        return None
    return _limpiar_fila_dict(filtro.to_dict(orient="records")[0])
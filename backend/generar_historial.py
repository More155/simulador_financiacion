"""Genera data/historial_tasas.csv con la TNA mensual de cada banco (últimos 12 meses).

Usa datetime para las fechas y pandas para armar la tabla. El último mes
toma como valor la TNA promedio real de las líneas fijas de bancos_tasas.csv
(sin contar las campañas de tasa 0%); hacia atrás se simula una variación
mensual realista.

Uso (desde la raíz del proyecto):
    python -m backend.generar_historial
"""

import os
import random
from datetime import date
import pandas as pd
from backend.datos import DATA_DIR, ARCHIVO_HISTORIAL, cargar_bancos

MESES = 12
SEMILLA = 42  # misma semilla = mismo resultado cada vez


def _primer_dia_mes_atras(hoy: date, meses_atras: int) -> date:
    """Primer día del mes que está 'meses_atras' meses antes de hoy."""
    indice = hoy.year * 12 + (hoy.month - 1) - meses_atras
    return date(indice // 12, indice % 12 + 1, 1)


def generar_historial() -> pd.DataFrame:
    """
    Genera un historial simulado de variaciones de tasas de interés (TNA)
    hacia atrás por 12 meses, partiendo del promedio real de las líneas fijas.
    """
    random.seed(SEMILLA)
    bancos = cargar_bancos()
    hoy = date.today()
    fechas = [_primer_dia_mes_atras(hoy, m) for m in range(MESES - 1, -1, -1)]

    filas = []
    for banco, grupo in bancos.groupby("banco"):
        tasas_reales = grupo.loc[
            (grupo["tna_pct"] > 0) & (grupo["tipo_tasa"] == "Fija"), "tna_pct"
        ]
        tna_actual = float(tasas_reales.mean()) if not tasas_reales.empty else 0.0

        # Se arma de atrás hacia adelante: el mes actual coincide con el dato real
        serie = [tna_actual]
        for _ in range(MESES - 1):
            variacion = random.uniform(-1.5, 1.5) if tna_actual > 0 else 0.0
            serie.append(max(0.0, serie[-1] + variacion))
        serie.reverse()

        for fecha, tna in zip(fechas, serie):
            filas.append(
                {
                    "fecha": fecha.isoformat(),
                    "banco": banco,
                    "tna_pct": round(tna, 2),
                }
            )

    return pd.DataFrame(filas)


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    df = generar_historial()
    ruta = os.path.join(DATA_DIR, ARCHIVO_HISTORIAL)
    df.to_csv(ruta, index=False, encoding="utf-8")
    print(f"Se generaron {len(df)} filas en {ruta}")
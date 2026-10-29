"""Generador de dataset sintético para el modelo de Machine Learning.

Uso (desde la raíz del proyecto):
    python -m backend.generar_clientes
"""

import os
import random
import pandas as pd
from backend.datos import DATA_DIR, ARCHIVO_CLIENTES


def generar_cuit() -> str:
    """Genera un CUIT ficticio de 11 dígitos con formato XX-XXXXXXXX-X."""
    prefijo = random.choice(["20", "23", "24", "27", "30"])
    cuerpo = f"{random.randint(10000000, 99999999)}"
    sufijo = f"{random.randint(0, 9)}"
    return f"{prefijo}-{cuerpo}-{sufijo}"


def generar_dataset_clientes(cantidad: int = 1000) -> pd.DataFrame:
    """Genera clientes con ruido estadístico para entrenar el modelo de ML."""
    random.seed(42)  # Semilla para que los datos sean reproducibles

    nombres = [
        "Martín", "Carolina", "Lucas", "Valentina", "Mateo",
        "Camila", "Nicolás", "Sofía", "Santiago", "Lucía",
    ]
    apellidos = [
        "González", "Gómez", "Rodríguez", "Fernández", "López",
        "Díaz", "Martínez", "Pérez", "García", "Sánchez",
    ]
    empleos = ["Relación de Dependencia", "Monotributista", "Responsable Inscripto"]

    filas = []

    for i in range(1, cantidad + 1):
        edad = random.randint(20, 70)
        # Antigüedad coherente con la edad (asumiendo que empezó a trabajar a los 18)
        max_meses_posibles = (edad - 18) * 12
        antiguedad = random.randint(1, min(240, max_meses_posibles))

        ingreso = random.randint(800_000, 6_000_000)
        compromisos = random.randint(100_000, int(ingreso * 0.6))

        ingreso_libre = ingreso - compromisos
        porcentaje_afectable = random.uniform(0.25, 0.35)
        cuota_maxima = int((ingreso_libre * porcentaje_afectable) / 1000) * 1000

        score = random.randint(150, 999)
        monto_solicitado = random.randint(5_000_000, 35_000_000)
        plazo_meses = random.choice([12, 24, 36, 48, 60])
        cuota_simulada = (monto_solicitado / plazo_meses) * random.uniform(1.2, 2.5)
        relacion_cuota = round((cuota_simulada / ingreso) * 100, 2)

        aprobado = (
            1 if (score >= 600 and antiguedad >= 6 and relacion_cuota <= 30) else 0
        )
        if random.random() < 0.05:
            aprobado = 1 - aprobado

        filas.append(
            {
                "id_cliente": f"CLI-{1000 + i}",
                "cuit_cuil": generar_cuit(),
                "nombre_apellido": f"{random.choice(nombres)} {random.choice(apellidos)}",
                "edad": edad,
                "tipo_empleo": random.choice(empleos),
                "antiguedad_laboral_meses": antiguedad,
                "ingreso_mensual_neto": ingreso,
                "compromisos_mensuales": compromisos,
                "ratio_endeudamiento_pct": round((compromisos / ingreso) * 100, 1),
                "situacion_bcra": 1 if score > 700 else random.randint(1, 5),
                "score_nosis": score,
                "cheques_rechazados_24m": (
                    random.choice([0, 0, 0, 1, 2]) if score < 500 else 0
                ),
                "mora_maxima_dias_12m": (
                    random.choice([0, 0, 15, 30, 90]) if score < 600 else 0
                ),
                "consultas_entidades_30d": random.randint(0, 5),
                "monto_solicitado": monto_solicitado,
                "plazo_meses": plazo_meses,
                "relacion_cuota_ingreso_pct": relacion_cuota,
                "cuota_maxima_afectable": max(0, cuota_maxima),
                "aprobado_credito": aprobado,
            }
        )

    df = pd.DataFrame(filas)
    os.makedirs(DATA_DIR, exist_ok=True)
    ruta = os.path.join(DATA_DIR, ARCHIVO_CLIENTES)
    df.to_csv(ruta, index=False, encoding="utf-8")
    print(f"Se generaron {cantidad} clientes con éxito en {ruta}")
    return df


if __name__ == "__main__":
    generar_dataset_clientes()
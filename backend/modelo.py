"""Regresión lineal: predice la cuota máxima que puede afectar un cliente.

Uso (desde la raíz del proyecto):
    python -m backend.modelo
"""

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from backend.datos import cargar_clientes

VARIABLES = ["ingreso_mensual_neto", "compromisos_mensuales"]
OBJETIVO = "cuota_maxima_afectable"

def entrenar_modelo():
    """Entrena la regresión lineal y devuelve (modelo, r2 sobre datos de prueba)."""
    # carga los datos de clientes, separa en X (Ingreso y compromisos) e y (cuota máxima real)
    clientes = cargar_clientes()
    

    X = clientes[VARIABLES]
    y = clientes[OBJETIVO]

    # Divide en datos de entrenamiento y de prueba, reseva el 20% de los clientes para evaluar el modelo, random_state=42 fija el sorteo para que dé siempre lo mismo.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # LinearRegression() crea un modelo vacío, y .fit(X_train, y_train) lo entrena. Busca los números que mejor ajustan una recta a los 800 clientes:
    # cuota = 0,3007 × ingreso − 0,2981 × compromisos − 2.214
    modelo = LinearRegression()
    modelo.fit(X_train, y_train)

    r2 = r2_score(y_test, modelo.predict(X_test))
    return modelo, r2

def predecir_cuota_maxima(modelo, ingreso, compromisos):
    """Devuelve la cuota máxima predicha en pesos (nunca negativa)."""
    entrada = pd.DataFrame([[ingreso, compromisos]], columns=VARIABLES)
    cuota = float(modelo.predict(entrada)[0])
    return max(0.0, cuota) # evita valor negativo


if __name__ == "__main__":
    modelo, r2 = entrenar_modelo()
    print(f"R2 (datos de prueba): {r2:.4f}")
    print(f"Intercepto: {modelo.intercept_:,.0f}")
    for variable, coef in zip(VARIABLES, modelo.coef_):
        print(f"Coeficiente {variable}: {coef:.4f}")

    ejemplo = predecir_cuota_maxima(modelo, 3_000_000, 600_000)
    print(f"Ingreso $3.000.000 y compromisos $600.000 -> cuota máxima ${ejemplo:,.0f}")



from backend.datos import cargar_clientes
from backend.modelo import (OBJETIVO, VARIABLES, entrenar_modelo,
                            predecir_cuota_maxima)

modelo, r2 = entrenar_modelo()
a, b = modelo.coef_
print(f"R2: {r2:.4f}")
print(f"cuota = {a:.4f} * ingreso + ({b:.4f}) * compromisos + ({modelo.intercept_:.0f})")

df = cargar_clientes().sample(10, random_state=1)
df["predicha"] = modelo.predict(df[VARIABLES]).round()
df["error"] = df["predicha"] - df[OBJETIVO]
print(df[["id_cliente", *VARIABLES, OBJETIVO, "predicha", "error"]].to_string(index=False))

for ingreso, compromisos in [(1_000_000, 300_000), (3_000_000, 600_000), (5_000_000, 600_000), (3_000_000, 2_000_000)]:
    cuota = predecir_cuota_maxima(modelo, ingreso, compromisos)
    print(f"ingreso {ingreso:>9,} | compromisos {compromisos:>9,} -> cuota máxima {cuota:>9,.0f}")

df = cargar_clientes()
print(df.head())        # primeras 5 filas
print(df.describe())    # promedio, min y max de cada columna
print(df.shape)         # (1000, 19)    
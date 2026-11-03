"""Pruebas del modelo de regresión lineal"""

from backend.modelo import entrenar_modelo, predecir_cuota_maxima


def probar_r2() -> None:
    """Test 1: El modelo tiene que explicar bien la cuota máxima en datos de prueba (> 0,9)."""
    modelo, r2 = entrenar_modelo()
    assert r2 > 0.9, f"R2 demasiado bajo: {r2:.4f}"
    print(f"✦︎ [1] R2 de prueba mayor a 0,9 ({r2:.4f}): OK :) ✦︎")


def probar_coeficientes() -> None:
    """Test 2: Más ingreso sube la cuota y más compromisos la bajan."""
    modelo, _ = entrenar_modelo()
    coef_ingreso, coef_compromisos = modelo.coef_
    assert coef_ingreso > 0, f"Coeficiente de ingreso no positivo: {coef_ingreso:.4f}"
    assert coef_compromisos < 0, f"Coeficiente de compromisos no negativo: {coef_compromisos:.4f}"
    print(f"✦︎ [2] Coeficientes ingreso ({coef_ingreso:.4f}) y compromisos ({coef_compromisos:.4f}): OK :) ✦︎")


def probar_mas_ingreso_mas_cuota() -> None:
    """Test 3: Con los mismos compromisos, más ingreso da más cuota máxima."""
    modelo, _ = entrenar_modelo()
    cuota_baja = predecir_cuota_maxima(modelo, 3_000_000, 600_000)
    cuota_alta = predecir_cuota_maxima(modelo, 5_000_000, 600_000)
    assert cuota_alta > cuota_baja, f"{cuota_alta:,.0f} no es mayor que {cuota_baja:,.0f}"
    print(f"✦︎ [3] Más ingreso, más cuota ({cuota_baja:,.0f} -> {cuota_alta:,.0f}): OK :) ✦︎")


def probar_mas_compromisos_menos_cuota() -> None:
    """Test 4: Con el mismo ingreso, más compromisos dan menos cuota máxima."""
    modelo, _ = entrenar_modelo()
    cuota_alta = predecir_cuota_maxima(modelo, 3_000_000, 600_000)
    cuota_baja = predecir_cuota_maxima(modelo, 3_000_000, 2_000_000)
    assert cuota_baja < cuota_alta, f"{cuota_baja:,.0f} no es menor que {cuota_alta:,.0f}"
    print(f"✦︎ [4] Más compromisos, menos cuota ({cuota_alta:,.0f} -> {cuota_baja:,.0f}): OK :) ✦︎")


def probar_nunca_negativa() -> None:
    """Test 5: Si los compromisos superan al ingreso, la cuota es 0 y no negativa."""
    modelo, _ = entrenar_modelo()
    cuota = predecir_cuota_maxima(modelo, 500_000, 2_000_000)
    assert cuota == 0, f"Cuota esperada 0, se obtuvo {cuota:,.0f}"
    print("✦︎ [5] La predicción nunca es negativa: OK :) ✦︎")


def probar_reproducible() -> None:
    """Test 6: random_state=42 hace que dos entrenamientos den el mismo R2."""
    _, r2_a = entrenar_modelo()
    _, r2_b = entrenar_modelo()
    assert r2_a == r2_b, f"R2 distintos: {r2_a:.6f} vs {r2_b:.6f}"
    print(f"✦︎ [6] Entrenamiento reproducible (R2 {r2_a:.4f}): OK :) ✦︎")


if __name__ == "__main__":
    probar_r2()
    probar_coeficientes()
    probar_mas_ingreso_mas_cuota()
    probar_mas_compromisos_menos_cuota()
    probar_nunca_negativa()
    probar_reproducible()

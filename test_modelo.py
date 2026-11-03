"""Pruebas del modelo de regresión lineal"""

from backend.modelo import entrenar_modelo, predecir_cuota_maxima


def probar_r2() -> None:
    """Test 1: El modelo tiene que explicar bien la cuota máxima en datos de prueba (> 0,9)."""
    modelo, r2 = entrenar_modelo()
    assert r2 > 0.9, f"R2 demasiado bajo: {r2:.4f}"
    print(f"✦︎ [1] R2 de prueba mayor a 0,9 ({r2:.4f}): OK :) ✦︎")


if __name__ == "__main__":
    probar_r2()


"""
2. probar relacion ingreso/compromisos modelo.coef
3. probar predecir_cuota_maxima con casos a mano (mas cuota)
4. probar menos cuota maxima
5. probar que la prediccion nunca sea negativa
6. comprobar el random_state=42 de train_test_split usando dos entradas iguales y ver que r2 sea el mismo
"""    
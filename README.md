# Simulador de financiación de vehículos + predicción de cuota máxima

Proyecto Colaborativo: Exploración de Temas en Python + herramientas IA para desarrollo.

**Integrantes:** _Agustin Sanchez, Luciano Esquivel, Morena Nicora_

## Descripción

Simulador de créditos prendarios que trabaja con líneas de crédito de distintos bancos y marcas. Para cada línea calcula la cuota y el costo de quebranto para el concesionario. Además, un modelo de regresión lineal predice la cuota máxima que puede afectar un cliente según sus ingresos y compromisos mensuales, y con eso se obtiene el monto máximo que puede financiar en cada línea.

> **Los datos son ficticios.** Los bancos, tasas, clientes y puntajes de los archivos de `data/` fueron creados para este trabajo y no corresponden a personas ni a operaciones reales.

## Cómo funciona

1. El usuario elige **marca**, **banco** y **línea de crédito**, e ingresa el **monto a financiar**.
2. El sistema calcula la **cuota mensual**: `monto ÷ 1000 × cuota promedio por cada 1.000` (dato que informa el banco). Por ejemplo, $15.000.000 con una cuota promedio de 88,82 da una cuota de $1.332.300.
3. Calcula el **quebranto**: `monto × quebranto % ÷ 100`.
4. Con los datos del cliente (ingreso, compromisos, score y antigüedad):
   - verifica si es apto con una regla simple (score de 600 o más y antigüedad de 6 meses o más, observada en los datos),
   - predice su **cuota máxima afectable** con la regresión lineal,
   - calcula el **monto máximo financiable** en la línea elegida y avisa si el monto pedido entra.

## Modelo predictivo

- **Tipo:** regresión lineal (`LinearRegression` de scikit-learn).
- **Variables de entrada:** ingreso mensual neto y compromisos mensuales.
- **Variable a predecir:** cuota máxima afectable.
- **Datos de entrenamiento:** clientes aprobados (a los rechazados la base les asigna cuota máxima 0).
- **Evaluación:** R² y error medio absoluto sobre datos de prueba (`train_test_split`).

## Tecnologías

**Módulos de Python:** `csv` (lectura de datos), `math` (monto máximo), `datetime` (fecha de cada cotización).

| Librería | Uso |
|---|---|
| pandas | Manejo de los datos |
| scikit-learn | Regresión lineal y métricas |
| streamlit | Interfaz |

## Estructura del proyecto

```
data/
  bancos_tasas.csv            Líneas de crédito por banco y marca
  clientes_riesgo_nosis.csv   Perfiles de clientes
datos.py                      Lectura de los CSV y conversión de tipos
calculos.py                   Cuota, quebranto y monto máximo
modelo.py                     Entrenamiento y evaluación de la regresión
app.py                        Interfaz
probar.py                     Pruebas
requirements.txt              Librerías necesarias
```

## Instalación

Requiere Python 3.10 o superior.

```bash
git clone <https://github.com/More155/simulador_financiacion.git>
cd <proyecto>

python -m venv .venv
# Windows (PowerShell):  .venv\Scripts\Activate.ps1
# Mac/Linux:             source .venv/bin/activate

pip install -r requirements.txt
```

## Uso

Siempre desde la carpeta del proyecto, con el entorno activado:

```bash
python modelo.py          # entrena y muestra R² y coeficientes
python probar.py          # corre las pruebas
streamlit run app.py      # abre el simulador en el navegador
```

## Datos

**`bancos_tasas.csv`** (18 líneas): marca, banco, nombre y tipo de tasa (fija o UVA), plazo en meses, TNA, TEA, CFTEA, quebranto (%) y cuota por cada $1.000 financiados.

**`clientes_riesgo_nosis.csv`** (50 clientes): edad, tipo de empleo, antigüedad laboral, ingreso, compromisos, endeudamiento, situación BCRA, score, mora, cuota máxima afectable y si el crédito fue aprobado.

## Limitaciones

- **Datos ficticios y pocos:** el modelo se entrena con los 28 clientes aprobados. Con tan pocos casos, las métricas de prueba no son muy confiables.
- **R² muy alto:** la cuota máxima de la base se construyó como un porcentaje fijo del ingreso libre (ingreso menos compromisos). Por eso la regresión lo recupera casi perfecto. Con datos reales el ajuste sería menor.
- **Aprobación por regla:** la aprobación no la predice el modelo, se decide con una regla tomada de los datos.
- **Líneas UVA:** la cuota calculada es la cuota inicial. Se ajusta por inflación durante el plazo, por lo que la verificación contra la cuota máxima del cliente solo vale al momento de la compra.
- **Tasas fijas y UVA no son comparables entre sí:** la TNA de una línea UVA no incluye el ajuste por inflación futura.
# Simulador de financiación de vehículos + predicción de cuota máxima

Proyecto Colaborativo: Exploración de Temas en Python + herramientas IA para desarrollo.

**Integrantes:** _Agustin Sanchez, Luciano Esquivel, Morena Nicora_

## Descripción

Simulador de créditos prendarios que trabaja con líneas de crédito de distintos bancos y marcas. Para cada línea calcula la cuota y el costo de quebranto para el concesionario. Además, un modelo de regresión lineal predice la cuota máxima que puede afectar un cliente según sus ingresos y compromisos mensuales, y con eso se obtiene el monto máximo que puede financiar en cada línea.

> **Los datos son ficticios.** Los bancos, tasas, clientes y puntajes de los archivos de `data/` fueron creados para este trabajo y no corresponden a personas ni a operaciones reales.

## Cómo funciona

1. El usuario elige **marca**, **banco** y **línea de crédito**, e ingresa el **monto a financiar**.
2. El sistema calcula la **cuota mensual**: `monto ÷ 1000 × cuota promedio por cada 1.000` (dato que informa el banco). Por ejemplo, $15.000.000 con una cuota promedio de 88,82 da una cuota de $1.332.300.
3. Calcula el **quebranto**: `monto × quebranto %`.
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
simulador_financiacion/
│
├── data/                         <-- Carpeta CSV
│   ├── clientes_riesgo_nosis.csv
│   ├── bancos_tasas.csv
│   └── historial_tasas.csv
│
├── backend/                      <-- Lógica, API y Modelos
│   ├── init.py                   <-- Módulo Python
│   ├── main.py                   <-- Servidor FastAPI (Endpoints principales)
│   ├── datos.py                  <-- Lectura de CSVs (Pandas + normalización + caché)
│   ├── calculos.py               <-- Matemática financiera y función fantasma simular_por_cuit
│   ├── modelo.py                 <-- Modelo de Machine Learning (Regresión lineal)
│   ├── generar_clientes.py       <-- Generador del dataset random de 1.000 clientes
│   └── generar_historial.py      <-- Generador del historial de TNA a 12 meses
│
├── frontend/                     <-- Interfaz visual web
│   └── index.html                <-- UI y cliente JavaScript
│
├── test.py                       <-- testos 
├── .gitignore                    <-- Archivos ignorados por Git
├── requirements.txt              <-- Dependencias del proyecto
└── README.md                     <-- Documentación técnica y general

```

## Instalación

Requiere Python 3.10 o superior.

```bash
git clone https://github.com/More155/simulador_financiacion.git
cd simulador_financiacion

python -m venv .venv
# Windows (PowerShell):  .venv\Scripts\Activate.ps1
# Mac/Linux:             source .venv/bin/activate

pip install -r requirements.txt

## Uso
Siempre desde la carpeta raíz del proyecto (`simulador_financiacion`), con el entorno activado:

```bash
uvicorn backend.main:app --reload    # Levanta el servidor FastAPI
python backend/modelo.py             # Entrena y muestra métricas
python test.py                       # Corre las pruebas internas

## Datos

bancos_tasas.csv (21 líneas): marca, banco, nombre y tipo de tasa (fija o UVA), plazo en meses, TNA, TEA, CFTEA, quebranto (%) y cuota por cada $1.000 financiados.

clientes_riesgo_nosis.csv (1.000 clientes): edad, tipo de empleo, antigüedad laboral, ingreso, compromisos, endeudamiento, situación BCRA, score, mora, monto solicitado, plazo, cuota máxima afectable y aprobación crediticia.

historial_tasas.csv (48 registros): evolución histórica mensual de la TNA por banco (últimos 12 meses) para líneas de tasa fija.


## Limitaciones

Datos sintéticos: los clientes y operaciones fueron generados algorítmicamente para imitar el comportamiento del mercado crediticio real.

Líneas UVA: la cuota calculada representa el valor inicial al momento del otorgamiento. Se ajusta por inflación acumulada a lo largo del plazo contratado. 

Comparabilidad de tasas: la TNA de las líneas UVA no incluye el coeficiente de actualización inflacionario futuro, por lo que no debe compararse directamente de forma nominal con las líneas de Tasa Fija.
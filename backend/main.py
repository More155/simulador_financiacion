from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.tasas import obtener_historial_tasas
# Importamos las funciones de tus módulos internos
from backend.datos import (
    buscar_cliente_por_cuit,
    listar_marcas,
    listar_bancos,
    listar_lineas,
    listar_plazos,
)
from backend.calculos import simular_por_cuit, ErrorDeSimulacion
from backend.modelo import entrenar_modelo, predecir_cuota_maxima

# Entrenamos el modelo una sola vez al levantar el servidor
modelo_cuota, r2_modelo = entrenar_modelo()

app = FastAPI(
    title="API Simulador de Créditos Prendarios",
    description="Motor de originación, evaluación crediticia y cálculos financieros",
    version="1.0"
)

# Configuración de CORS para permitir peticiones locales
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Montamos la carpeta frontend para servir archivos estáticos (app.js, CSS, etc.)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# 2. Configuramos Jinja2 para que renderice las vistas HTML desde la carpeta views
templates = Jinja2Templates(directory="frontend/views")


# Modelo Pydantic para recibir los datos de la simulación desde el frontend (POST)
class PeticionSimulacion(BaseModel):
    cuit: str
    precio_vehiculo: float
    anticipo: float
    marca: str
    banco: str
    nombre_tasa: str
    plazo: int


# --- RUTA PRINCIPAL (Sirve la vista HTML unificada) ---
@app.get("/", response_class=HTMLResponse)
def raiz(request: Request):
    return templates.TemplateResponse(request, "inicio.html")

@app.get("/Simulador", response_class=HTMLResponse)
def simulador(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/api/cliente/{cuit}")
def consultar_cliente(cuit: str):
    """Busca al cliente por CUIT en el CSV usando el módulo datos.py."""
    cliente = buscar_cliente_por_cuit(cuit)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado en la base de datos.")
    return cliente


# ---------------------------------------------------------------------------
# Endpoints para los Selectores en Cascada del Frontend
# ---------------------------------------------------------------------------

@app.get("/api/marcas")
def obtener_marcas():
    """Devuelve la lista de marcas de vehículos disponibles."""
    return listar_marcas()


@app.get("/api/bancos/{marca}")
def obtener_bancos(marca: str):
    """Devuelve los bancos que financian una marca específica."""
    return listar_bancos(marca)


@app.get("/api/lineas")
def obtener_lineas(marca: str = Query(...), banco: str = Query(...)):
    """Devuelve las líneas de crédito (nombre_tasa) para una marca y banco."""
    return listar_lineas(marca, banco)


@app.get("/api/plazos")
def obtener_plazos(marca: str = Query(...), banco: str = Query(...), nombre_tasa: str = Query(...)):
    """Devuelve los plazos en meses disponibles para la línea seleccionada."""
    return listar_plazos(marca, banco, nombre_tasa)


# ---------------------------------------------------------------------------
# Endpoint de Simulación Financiera
# ---------------------------------------------------------------------------

@app.post("/api/simular")
def simular_operacion_endpoint(datos: PeticionSimulacion):
    """Ejecuta los cálculos financieros y validaciones de aptitud del cliente."""
    try:
        # Si el cliente existe, la cuota máxima sale del modelo de regresión
        cliente = buscar_cliente_por_cuit(datos.cuit)
        cuota_predicha = None
        if cliente:
            cuota_predicha = predecir_cuota_maxima(
                modelo_cuota,
                cliente["ingreso_mensual_neto"],
                cliente["compromisos_mensuales"],
            )

        resultado = simular_por_cuit(
            cuit=datos.cuit,
            precio_vehiculo=datos.precio_vehiculo,
            anticipo=datos.anticipo,
            marca=datos.marca,
            banco=datos.banco,
            nombre_tasa=datos.nombre_tasa,
            plazo=datos.plazo,
            cuota_maxima_predicha=cuota_predicha,
        )
        return resultado
        
    except ErrorDeSimulacion as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado en el servidor: {str(e)}")
    

# ---------------------------------------------------------------------------
# HISTÓRICO DE TASAS BANCARIAS
# ---------------------------------------------------------------------------

@app.get("/Tasas", response_class=HTMLResponse)
def dashboard_tasas(request: Request):
    try:
        datos = obtener_historial_tasas()
        return templates.TemplateResponse(request, "tasas.html", datos)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar las tasas: {str(e)}"
        )

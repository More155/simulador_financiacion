import pandas as pd
import plotly.express as px
from pathlib import Path


def obtener_historial_tasas():
    """
    Obtiene el historial mensual completo de tasas de todos los bancos.
    Devuelve una tabla comparativa y un gráfico de líneas sin filtros de período.
    """

    # --------------------------------------------------
    # 1. CARGAR DATOS
    # --------------------------------------------------

    ruta = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "historial_tasas.csv"
    )

    df = pd.read_csv(ruta)

    df["fecha"] = pd.to_datetime(df["fecha"])
    df["tna_pct"] = pd.to_numeric(df["tna_pct"])

    df = df.sort_values(["fecha", "banco"])

    if df.empty:
        raise ValueError("No existen registros en el historial.")

    # --------------------------------------------------
    # 2. TABLA COMPARATIVA
    # --------------------------------------------------

    tabla = df.pivot_table(
        index="fecha",
        columns="banco",
        values="tna_pct",
        aggfunc="mean"
    ).reset_index()

    tabla["fecha"] = tabla["fecha"].dt.strftime("%m/%Y")

    tabla = tabla.sort_values(
        "fecha",
        ascending=False
    )

    bancos = [
        columna for columna in tabla.columns
        if columna != "fecha"
    ]

    # Redondear tasas
    tabla[bancos] = tabla[bancos].round(2)

    # --------------------------------------------------
    # 3. GRÁFICO DE LÍNEAS
    # --------------------------------------------------

    grafico = px.line(
        df,
        x="fecha",
        y="tna_pct",
        color="banco",
        markers=True,
        title="Evolución mensual de tasas bancarias"
    )

    grafico.update_layout(
        template="plotly_white",
        xaxis_title="Período",
        yaxis_title="TNA (%)",
        hovermode="x unified",
        legend_title="Entidad bancaria"
    )

    grafico.update_traces(
        line=dict(width=3),
        marker=dict(size=7)
    )

    # --------------------------------------------------
    # 4. DEVOLVER RESULTADOS
    # --------------------------------------------------

    return {
        "sin_datos": False,
        "bancos": bancos,
        "tabla": tabla.to_dict(orient="records"),
        "grafico_lineas": grafico.to_html(
            full_html=False,
            include_plotlyjs="cdn",
            config={"responsive": True}
        )
    }
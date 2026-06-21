# ============================================================
# Dashboard - Análisis de Recetas de Cerveza Artesanal
# Presenta: Galindo Espinosa Ana Lilia / Herrera Moreno Sayuri
#
# Este dashboard presenta un análisis visual e interactivo de las
# características fisicoquímicas de recetas de cerveza artesanal.
# Para ejecutar:  streamlit run app.py
# ============================================================

import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Dashboard Cerveza Artesanal", layout="wide")

# Tipografía y estilo general 
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    html, body, [class*="css"], .stMarkdown, .stMetric { font-family: 'Nunito', sans-serif; }
    h1, h2, h3 { font-family: 'Nunito', sans-serif; font-weight: 800; color: #8B4513; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Paleta de colores para todas las gráficas 
PALETA = px.colors.qualitative.Antique           # tonos cálidos y elegantes
ESCALA_AMBAR = ["#FCEBD2", "#E8B923", "#C8742B", "#8B4513"]  # claro -> oscuro

# Plantilla común: fondo blanco + tipografía Nunito en las gráficas
pio.templates["cerveza"] = pio.templates["plotly_white"]
pio.templates["cerveza"].layout.font.family = "Nunito, sans-serif"
px.defaults.template = "cerveza"
px.defaults.color_discrete_sequence = PALETA

st.title("🍺 Dashboard - Recetas de Cerveza Artesanal")
st.markdown(
    "Análisis interactivo de las características fisicoquímicas de recetas de cerveza. "
    "Usa los filtros de la izquierda para explorar los datos."
)

# Variables numéricas del análisis
VARIABLES = ["ABV", "IBU", "Color", "OG", "FG", "Efficiency"]

# Diccionario de datos (significado de cada variable)
DICCIONARIO = pd.DataFrame({
    "Variable": ["ABV", "IBU", "Color", "OG", "FG", "Efficiency", "Style", "BrewMethod"],
    "Significado": [
        "Alcohol por volumen",
        "Amargor aportado por el lúpulo",
        "Color de la cerveza (escala SRM)",
        "Densidad inicial, antes de fermentar (azúcares)",
        "Densidad final, después de fermentar",
        "Eficiencia del proceso de elaboración",
        "Estilo de cerveza",
        "Método de elaboración",
    ],
    "Unidad": ["%", "escala IBU", "SRM", "gravedad específica",
               "gravedad específica", "%", "categórica", "categórica"],
})


# Carga de datos (cacheada para que sea rápida)
@st.cache_data
def cargar_datos():
    return pd.read_csv("datasets/df_limpio.csv")


df = cargar_datos()


# ============================================================
# BARRA LATERAL - FILTROS
# ============================================================
st.sidebar.header("Filtros")

# Por defecto mostramos los 15 estilos más frecuentes (legibilidad)
top15 = df["Style"].value_counts().nlargest(15).index.tolist()

estilos_sel = st.sidebar.multiselect(
    "Estilo", options=sorted(df["Style"].dropna().unique()), default=top15
)
metodos_sel = st.sidebar.multiselect(
    "Método de elaboración",
    options=sorted(df["BrewMethod"].dropna().unique()),
    default=sorted(df["BrewMethod"].dropna().unique()),
)

# Los rangos quedan agrupados en un desplegable para no saturar la barra
with st.sidebar.expander("Rangos numéricos (ABV / IBU)", expanded=False):
    abv_min, abv_max = st.slider(
        "Rango de ABV (%)",
        float(df["ABV"].min()), float(df["ABV"].max()),
        (float(df["ABV"].min()), float(df["ABV"].max())),
    )
    ibu_min, ibu_max = st.slider(
        "Rango de IBU",
        float(df["IBU"].min()), float(df["IBU"].max()),
        (float(df["IBU"].min()), float(df["IBU"].max())),
    )

# Aplicamos los filtros: todas las gráficas usan df_f
df_f = df[
    df["Style"].isin(estilos_sel)
    & df["BrewMethod"].isin(metodos_sel)
    & df["ABV"].between(abv_min, abv_max)
    & df["IBU"].between(ibu_min, ibu_max)
]

st.sidebar.markdown(f"**Recetas mostradas:** {len(df_f):,} de {len(df):,}")

# Aviso si el filtro deja todo vacío
if df_f.empty:
    st.warning("Ningún dato cumple los filtros seleccionados. Ajusta los filtros.")
    st.stop()


# ============================================================
# KPIs dinámicos (cambian con los filtros)
# ============================================================
c1, c2, c3, c4 = st.columns(4)
c1.metric("Recetas", f"{len(df_f):,}")
c2.metric("Estilos", df_f["Style"].nunique())
c3.metric("ABV promedio", f"{df_f['ABV'].mean():.2f} %")
c4.metric("IBU promedio", f"{df_f['IBU'].mean():.1f}")

st.divider()


# ============================================================
# DICCIONARIO DE DATOS (siempre visible, en el área principal)
# ============================================================
with st.expander("📖 Diccionario de datos — ¿qué significa cada variable?", expanded=False):
    st.dataframe(DICCIONARIO, use_container_width=True, hide_index=True)


# ============================================================
# PESTAÑAS
# ============================================================
tab_resumen, tab_dist, tab_rel, tab_datos = st.tabs(
    ["📊 Resumen", "📈 Distribuciones", "🔗 Relaciones", "📋 Datos"]
)


# ---------- TAB 1: RESUMEN ----------
with tab_resumen:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribución de estilos (selección)")
        conteo = df_f["Style"].value_counts().nlargest(15).reset_index()
        conteo.columns = ["Style", "Cantidad"]
        fig = px.bar(conteo, x="Cantidad", y="Style", orientation="h",
                     color="Cantidad", color_continuous_scale=ESCALA_AMBAR)
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Estilos más frecuentes (selección)")
        top10 = df_f["Style"].value_counts().nlargest(10).reset_index()
        top10.columns = ["Style", "Cantidad"]
        fig = px.pie(top10, names="Style", values="Cantidad", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)


# ---------- TAB 2: DISTRIBUCIONES ----------
with tab_dist:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Histograma de ABV (% alcohol)")
        fig = px.histogram(df_f, x="ABV", nbins=40,
                           color_discrete_sequence=["#B888DD"])
        fig.update_layout(bargap=0.05)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Histograma de IBU (amargor)")
        fig = px.histogram(df_f, x="IBU", nbins=40,
                           color_discrete_sequence=["#49928B"])
        fig.update_layout(bargap=0.05)
        st.plotly_chart(fig, use_container_width=True)


# ---------- TAB 3: RELACIONES ----------
with tab_rel:
    st.subheader("Relación entre variables")

    cols = st.columns(2)
    eje_x = cols[0].selectbox("Eje X", VARIABLES, index=0)   # ABV por defecto
    eje_y = cols[1].selectbox("Eje Y", VARIABLES, index=1)   # IBU por defecto

    fig = px.scatter(df_f, x=eje_x, y=eje_y, color="Style", opacity=0.6)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("PCA - Recetas en 2 componentes")
        fig = px.scatter(
            df_f, x="PC1", y="PC2", color="Style", opacity=0.6,
            labels={"PC1": "PC1 (fuerza/cuerpo)", "PC2": "PC2 (color vs amargor)"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Matriz de correlación (Pearson)")
        corr = df_f[VARIABLES].corr()
        fig = px.imshow(corr, text_auto=".2f", aspect="auto",
                        color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
        st.plotly_chart(fig, use_container_width=True)


# TAB 4: DATOS 
with tab_datos:
    st.subheader("Explorador de la tabla")
    estilo_buscar = st.text_input("Buscar por estilo (texto parcial):", "")
    tabla = df_f
    if estilo_buscar:
        tabla = tabla[tabla["Style"].str.contains(estilo_buscar, case=False, na=False)]
    st.dataframe(tabla, use_container_width=True, height=400)
    st.caption(f"Mostrando {len(tabla):,} registros.")


st.caption("Proyecto - Analítica y Visualización de Datos")

# streamlit_app.py
from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Configuración de la página ---
st.set_page_config(
    page_title="NBA - Análisis por temporada",
    page_icon="🏀",
    layout="wide",
)

# --- Cargar dataset ---
@st.cache_data
def load_data():
    csv_path = Path(__file__).parent / "datasets" / "nba_all_elo.csv"
    data = pd.read_csv(csv_path)
    data["date_game"] = pd.to_datetime(data["date_game"])
    return data

df = load_data()

# --- Barra lateral ---
st.sidebar.header("Filtros")

years = sorted(df["year_id"].unique())
selected_year = st.sidebar.selectbox(
    "Selecciona un año", years, index=len(years) - 1
)

teams = sorted(df["team_id"].unique())
selected_team = st.sidebar.selectbox("Selecciona un equipo", teams)

game_type = st.sidebar.pills(
    "Tipo de juegos",
    options=["Temporada regular", "Playoffs", "Ambos"],
    default="Ambos",
)

# --- Filtrado de datos ---
filtered_df = (
    df[(df["year_id"] == selected_year) & (df["team_id"] == selected_team)]
    .sort_values("date_game")
    .reset_index(drop=True)
    .copy()
)

if game_type == "Temporada regular":
    filtered_df = filtered_df[filtered_df["is_playoffs"] == 0]
elif game_type == "Playoffs":
    filtered_df = filtered_df[filtered_df["is_playoffs"] == 1]

filtered_df = filtered_df.reset_index(drop=True)

# --- Encabezado ---
st.title(f"🏀 {selected_team} — Temporada {selected_year}")
st.caption(f"Tipo de juegos: {game_type}")

if filtered_df.empty:
    st.warning(
        f"No hay juegos de {selected_team} en {selected_year} "
        f"con el filtro '{game_type}'."
    )
    st.stop()

# --- Métricas resumen ---
wins = int((filtered_df["game_result"] == "W").sum())
losses = int((filtered_df["game_result"] == "L").sum())
total = wins + losses
win_pct = (wins / total * 100) if total else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Juegos", total)
col2.metric("Ganados", wins)
col3.metric("Perdidos", losses)
col4.metric("% Victorias", f"{win_pct:.1f}%")

# --- Acumulados ---
filtered_df["wins_cum"] = (filtered_df["game_result"] == "W").cumsum()
filtered_df["losses_cum"] = (filtered_df["game_result"] == "L").cumsum()
filtered_df["game_number"] = range(1, len(filtered_df) + 1)

# --- Gráficas ---
col_line, col_pie = st.columns([2, 1])

with col_line:
    st.subheader("Acumulado de juegos ganados y perdidos")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(
        filtered_df["game_number"],
        filtered_df["wins_cum"],
        label="Ganados",
        color="#2ecc71",
        linewidth=2,
    )
    ax.plot(
        filtered_df["game_number"],
        filtered_df["losses_cum"],
        label="Perdidos",
        color="#e74c3c",
        linewidth=2,
    )
    ax.set_xlabel("Número de juego")
    ax.set_ylabel("Acumulado")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    st.pyplot(fig)

with col_pie:
    st.subheader("Porcentaje de victorias / derrotas")
    fig2, ax2 = plt.subplots(figsize=(5, 5))
    ax2.pie(
        [wins, losses],
        labels=["Ganados", "Perdidos"],
        autopct="%1.1f%%",
        colors=["#2ecc71", "#e74c3c"],
        startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )
    ax2.axis("equal")
    fig2.tight_layout()
    st.pyplot(fig2)

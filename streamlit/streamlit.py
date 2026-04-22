# streamlit_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Cargar dataset ---
df = pd.read_csv("../datasets/nba_all_elo.csv")

# --- Barra lateral ---
st.sidebar.header("Filtros")

# Selector de año
years = sorted(df["year"].unique())
selected_year = st.sidebar.selectbox("Selecciona un año", years)

# Selector de equipo
teams = sorted(df["team"].unique())
selected_team = st.sidebar.selectbox("Selecciona un equipo", teams)

# Selector de tipo de juegos
game_type = st.sidebar.pills(
    "Tipo de juegos",
    options=["Temporada regular", "Playoffs", "Ambos"],
    default="Ambos"
)

# --- Filtrado de datos ---
filtered_df = df[(df["year"] == selected_year) & (df["team"] == selected_team)]

if game_type == "Temporada regular":
    filtered_df = filtered_df[filtered_df["game_type"] == "Regular"]
elif game_type == "Playoffs":
    filtered_df = filtered_df[filtered_df["game_type"] == "Playoffs"]

# --- Gráficas de acumulado ---
filtered_df["wins_cum"] = (filtered_df["game_result"] == "W").cumsum()
filtered_df["losses_cum"] = (filtered_df["game_result"] == "L").cumsum()

fig, ax = plt.subplots()
ax.plot(filtered_df.index, filtered_df["wins_cum"], label="Ganados", color="green")
ax.plot(filtered_df.index, filtered_df["losses_cum"], label="Perdidos", color="red")
ax.set_title(f"Acumulado de juegos {selected_team} - {selected_year}")
ax.set_xlabel("Número de juego")
ax.set_ylabel("Acumulado")
ax.legend()
st.pyplot(fig)

# --- Gráfica de pastel ---
wins = (filtered_df["game_result"] == "W").sum()
losses = (filtered_df["game_result"] == "L").sum()

fig2, ax2 = plt.subplots()
ax2.pie([wins, losses], labels=["Ganados", "Perdidos"], autopct="%1.1f%%", colors=["green", "red"])
ax2.set_title(f"Porcentaje de juegos {selected_team} - {selected_year}")
st.pyplot(fig2)
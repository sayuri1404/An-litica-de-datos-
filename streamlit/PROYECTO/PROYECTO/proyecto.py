import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial.distance import pdist, squareform
from scipy.stats import pearsonr, chi2_contingency
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import plotly.express as px
import dash
from dash import dcc, html

# Carga y limpieza de datos
df = pd.read_csv("recipeData1.csv")

# Eliminar columnas irrelevantes
df = df.drop(columns=["URL","UserID"], errors="ignore")

# Eliminar duplicados
df = df.drop_duplicates()

# Rellenar valores faltantes con la mediana
for col in ["ABV","IBU","Color","OG","FG","Efficiency"]:
    if col in df.columns:
        df[col] = df[col].fillna(df[col].median())

# Detección y eliminación de outliers con IQR
for col in ["ABV","IBU","Color","OG","FG","Efficiency"]:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    df = df[(df[col] >= Q1 - 1.5*IQR) & (df[col] <= Q3 + 1.5*IQR)]

# Matriz de distancias
features = df[["ABV","IBU","Color","OG","FG"]]
dist_matrix = squareform(pdist(features, metric="euclidean"))

plt.figure(figsize=(8,6))
sns.heatmap(dist_matrix, cmap="viridis")
plt.title("Matriz de Distancias (Euclidiana)")
plt.savefig("heatmap.png")  # guardamos para mostrar en dashboard

# Correlaciones
print("ABV-IBU:", pearsonr(df["ABV"], df["IBU"]))
print("ABV-OG:", pearsonr(df["ABV"], df["OG"]))
print("IBU-Color:", pearsonr(df["IBU"], df["Color"]))

# Chi-cuadrada
contingency = pd.crosstab(df["Style"], df["BrewMethod"])
chi2, p, dof, expected = chi2_contingency(contingency)
print("Chi-cuadrada:", chi2, "p-value:", p)

# PCA
scaler = StandardScaler()
scaled = scaler.fit_transform(df[["ABV","IBU","Color","OG","FG","Efficiency"]])
pca = PCA(n_components=2)
components = pca.fit_transform(scaled)
df["PC1"], df["PC2"] = components[:,0], components[:,1]

# Gráficas interactivas
fig_hist_abv = px.histogram(df, x="ABV", title="Histograma ABV")
fig_hist_ibu = px.histogram(df, x="IBU", title="Histograma IBU")
fig_scatter = px.scatter(df, x="ABV", y="IBU", color="Style", title="Scatter ABV vs IBU")
fig_top_styles = px.bar(df["Style"].value_counts().nlargest(10), title="Top 10 estilos")
fig_pca = px.scatter(df, x="PC1", y="PC2", color="Style", title="PCA de Recetas")

# Dashboard con Dash
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Dashboard de Recetas de Cerveza Artesanal"),
    dcc.Graph(figure=fig_hist_abv),
    dcc.Graph(figure=fig_hist_ibu),
    dcc.Graph(figure=fig_scatter),
    dcc.Graph(figure=fig_top_styles),
    dcc.Graph(figure=fig_pca),
    html.Img(src="heatmap.png", style={"width":"70%"})
])

if __name__ == "__main__":
    app.run_server(debug=True)
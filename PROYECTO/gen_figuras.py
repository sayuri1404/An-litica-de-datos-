# Genera las figuras del análisis y las guarda en documento/figuras/
# Uso:  python gen_figuras.py
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial.distance import pdist, squareform
from sklearn.preprocessing import StandardScaler

SALIDA = "documento/figuras"
os.makedirs(SALIDA, exist_ok=True)

VARS = ["ABV", "IBU", "Color", "OG", "FG", "Efficiency"]
sns.set_theme(style="whitegrid")

df = pd.read_csv("datasets/df_limpio.csv")
top15 = df["Style"].value_counts().nlargest(15).index

# ---- Datos escalados con su estilo ----
X = StandardScaler().fit_transform(df[VARS])
Xs = pd.DataFrame(X, index=df.index, columns=VARS)
Xs["Style"] = df["Style"].values

# 1) Heatmap de distancias euclidianas entre estilos (top 15)
perfil = Xs[Xs["Style"].isin(top15)].groupby("Style")[VARS].mean()
D = pd.DataFrame(squareform(pdist(perfil, "euclidean")),
                 index=perfil.index, columns=perfil.index)
plt.figure(figsize=(11, 9))
sns.heatmap(D, annot=True, fmt=".1f", cmap="viridis_r")
plt.title("Matriz de distancias euclidianas entre estilos")
plt.tight_layout()
plt.savefig(f"{SALIDA}/dist_heatmap.png", dpi=150)
plt.close()

# 2) Matriz de correlación de Pearson
plt.figure(figsize=(8, 6))
sns.heatmap(df[VARS].corr(), annot=True, fmt=".2f", cmap="coolwarm",
            center=0, vmin=-1, vmax=1, square=True)
plt.title("Matriz de correlación de Pearson")
plt.tight_layout()
plt.savefig(f"{SALIDA}/correlacion.png", dpi=150)
plt.close()

# 3) PCA: dispersión de recetas (top 15 estilos)
df_top = df[df["Style"].isin(top15)]
plt.figure(figsize=(11, 8))
sns.scatterplot(data=df_top, x="PC1", y="PC2", hue="Style",
                palette="tab20", s=15, alpha=0.6)
plt.title("PCA de recetas de cerveza (coloreado por estilo)")
plt.xlabel("PC1 (fuerza/cuerpo)")
plt.ylabel("PC2 (color vs amargor)")
plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig(f"{SALIDA}/pca.png", dpi=150)
plt.close()

# 4) Histograma de ABV
plt.figure(figsize=(8, 5))
sns.histplot(df["ABV"], bins=40, color="#C8742B")
plt.title("Distribución de ABV (% alcohol)")
plt.xlabel("ABV (%)")
plt.tight_layout()
plt.savefig(f"{SALIDA}/hist_abv.png", dpi=150)
plt.close()

# 5) Histograma de IBU
plt.figure(figsize=(8, 5))
sns.histplot(df["IBU"], bins=40, color="#6B8E23")
plt.title("Distribución de IBU (amargor)")
plt.xlabel("IBU")
plt.tight_layout()
plt.savefig(f"{SALIDA}/hist_ibu.png", dpi=150)
plt.close()

# 6) Distribución de estilos (top 15)
plt.figure(figsize=(9, 6))
conteo = df["Style"].value_counts().nlargest(15)
sns.barplot(x=conteo.values, y=conteo.index, palette="YlOrBr_r")
plt.title("Top 15 estilos más frecuentes")
plt.xlabel("Número de recetas")
plt.tight_layout()
plt.savefig(f"{SALIDA}/dist_estilos.png", dpi=150)
plt.close()

# 7) Scatter ABV vs IBU (top 15 estilos)
plt.figure(figsize=(10, 7))
sns.scatterplot(data=df_top, x="ABV", y="IBU", hue="Style",
                palette="tab20", s=15, alpha=0.6)
plt.title("Relación entre ABV e IBU")
plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig(f"{SALIDA}/scatter_abv_ibu.png", dpi=150)
plt.close()

print("Figuras generadas en", SALIDA)

import os
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt

# Carpeta que contiene los archivos individuales
carpeta_individual = "PeriodosTotales/2016-2024/individual"

# Códigos de aglomerados del NEA
aglomerados_nea = [7, 8, 12, 15]

# Diccionario para guardar tasas por trimestre
tasas_por_trimestre = {}

# Función para calcular media ponderada
def media_ponderada(valores, pesos):
    valores = np.array(valores)
    pesos = np.array(pesos)
    media = np.average(valores, weights=pesos)
    return {"media": round(media * 100, 2)}

# Archivos individuales ordenados
archivos_txt = sorted(f for f in os.listdir(carpeta_individual) if f.endswith(".txt"))

for nombre_archivo in archivos_txt:
    archivo_individual = os.path.join(carpeta_individual, nombre_archivo)

    # Cargar base individual
    df = pd.read_csv(archivo_individual, sep=";", low_memory=False)

    # Filtrar aglomerados del NEA
    df_nea = df[df["AGLOMERADO"].isin(aglomerados_nea)].copy()

    # Crear variables binarias
    df_nea["es_activo"] = df_nea["ESTADO"].isin([1, 2]).astype(int)
    df_nea["es_ocupado"] = (df_nea["ESTADO"] == 1).astype(int)
    df_nea["es_desocupado"] = (df_nea["ESTADO"] == 2).astype(int)

    # Extraer nombre de trimestre
    trimestre = nombre_archivo.replace(".txt", "")

    # Guardar tasas
    tasas_por_trimestre[trimestre] = {
        "actividad": media_ponderada(df_nea["es_activo"], df_nea["PONDERA"]),
        "empleo": media_ponderada(df_nea["es_ocupado"], df_nea["PONDERA"]),
        "desocupacion": media_ponderada(
            df_nea[df_nea["es_activo"] == 1]["es_desocupado"],
            df_nea[df_nea["es_activo"] == 1]["PONDERA"]
        )
    }

# Crear DataFrame con resultados
df_tasas = pd.DataFrame({
    t: {
        "Actividad": v["actividad"]["media"],
        "Empleo": v["empleo"]["media"],
        "Desocupación": v["desocupacion"]["media"]
    }
    for t, v in tasas_por_trimestre.items()
}).T

# Renombrar índice para que diga '2016-1Trim' en lugar de 'Individual-2016-1T'
def renombrar_trimestre(tri_str):
    match = re.match(r"Individual-(\d{4})-(\d)T", tri_str)
    if match:
        anio, trimestre = match.groups()
        return f"{anio}-{trimestre}Trim"
    return tri_str

df_tasas.index = df_tasas.index.map(renombrar_trimestre)

# Ordenar índices por año y trimestre
def ordenar_trimestres(nombre):
    match = re.match(r"(\d{4})-(\d)Trim", nombre)
    if match:
        anio = int(match.group(1))
        trimestre = int(match.group(2))
        return anio * 10 + trimestre
    return 0

df_tasas["orden"] = df_tasas.index.map(ordenar_trimestres)
df_tasas = df_tasas.sort_values("orden").drop(columns="orden")

# Graficar
plt.figure(figsize=(16, 6))
for columna in df_tasas.columns:
    plt.plot(df_tasas.index, df_tasas[columna], marker='o', label=columna)

plt.xticks(rotation=60)
plt.yticks(np.arange(0, 101, 5))  # De 0 a 100 con saltos de 5%
plt.ylabel("Tasa (%)")
plt.title("Evolución de tasas de Actividad, Empleo y Desocupación (NEA 2016-2024)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
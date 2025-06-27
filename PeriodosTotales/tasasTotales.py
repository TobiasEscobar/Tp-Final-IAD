import os
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt

# Carpeta raíz que contiene subcarpetas 'individual' y 'hogar'
carpeta_raiz = "PeriodosTotales/2016-2024"
carpeta_individual = os.path.join(carpeta_raiz, "individual")
carpeta_hogar = os.path.join(carpeta_raiz, "hogar")

# Códigos para aglomerados del NEA
aglomerados_nea = [7, 8, 12, 15]

# Diccionario para guardar resultados
tasas_por_trimestre = {}

# Función para calcular la media ponderada
def media_ponderada(valores, pesos):
    valores = np.array(valores)
    pesos = np.array(pesos)
    media = np.average(valores, weights=pesos)
    return {"media": round(media * 100, 2)}

# Archivos de la carpeta 'individual'
archivos_txt = sorted(f for f in os.listdir(carpeta_individual) if f.endswith(".txt"))

for nombre_archivo in archivos_txt:
    archivo_individual = os.path.join(carpeta_individual, nombre_archivo)
    archivo_hogar = os.path.join(carpeta_hogar, nombre_archivo.replace("Individual", "Hogar"))

    if not os.path.exists(archivo_hogar):
        print(f"Archivo hogar no encontrado para: {nombre_archivo}")
        continue

    # Cargar ambas bases
    df_ind = pd.read_csv(archivo_individual, sep=";", low_memory=False)
    df_hogar = pd.read_csv(archivo_hogar, sep=";", low_memory=False)

    # Filtrar hogares por tipo de vivienda: casas o departamentos
    df_hogar_filtrado = df_hogar[df_hogar["IV1"].isin([1, 2])]

    # Merge para filtrar individuos en viviendas particulares
    df = pd.merge(
        df_ind,
        df_hogar_filtrado[["CODUSU", "NRO_HOGAR", "IV1"]],
        on=["CODUSU", "NRO_HOGAR"],
        how="inner"
    )

    # Filtrar por aglomerados NEA
    df_nea = df[df["AGLOMERADO"].isin(aglomerados_nea)].copy()

    # Crear columnas binarias para tasas
    df_nea["es_activo"] = df_nea["ESTADO"].isin([1, 2]).astype(int)
    df_nea["es_ocupado"] = (df_nea["ESTADO"] == 1).astype(int)
    df_nea["es_desocupado"] = (df_nea["ESTADO"] == 2).astype(int)

    # Nombre de trimestre (sin .txt)
    trimestre = nombre_archivo.replace(".txt", "")

    # Calcular y guardar tasas
    tasas_por_trimestre[trimestre] = {
        "actividad": media_ponderada(df_nea["es_activo"], df_nea["PONDERA"]),
        "empleo": media_ponderada(df_nea["es_ocupado"], df_nea["PONDERA"]),
        "desocupacion": media_ponderada(
            df_nea[df_nea["es_activo"] == 1]["es_desocupado"],
            df_nea[df_nea["es_activo"] == 1]["PONDERA"]
        )
    }

# Se va a distinguir por cada cuatrimestre, para ver año por año, hay lineas abajo para descomentarlas

# Convertimos a DataFrame 
df_tasas = pd.DataFrame({
    t: {
        "Actividad": v["actividad"]["media"],
        "Empleo": v["empleo"]["media"],
        "Desocupación": v["desocupacion"]["media"]
    }
    for t, v in tasas_por_trimestre.items()
}).T

# Renombrar índices para que se vean como '2016-2Trim' en lugar de 'Individual-2016-2T'
def renombrar_trimestre(tri_str):
    match = re.match(r"Individual-(\d{4})-(\d)T", tri_str)
    if match:
        anio, trimestre = match.groups()
        return f"{anio}-{trimestre}Trim"
    return tri_str  # por si no coincide el formato

df_tasas.index = df_tasas.index.map(renombrar_trimestre)


# Ordenar índices por año y trimestre
def ordenar_trimestres(nombre):
    match = re.match(r"Individual-(\d{4})-(\d)T", nombre)
    if match:
        anio = int(match.group(1))
        trimestre = int(match.group(2))
        return anio * 10 + trimestre
    return 0

df_tasas["orden"] = df_tasas.index.map(ordenar_trimestres)
df_tasas = df_tasas.sort_values("orden").drop(columns="orden")

# Graficar
plt.figure(figsize=(16, 6))
# plt.figure(figsize=(12, 6)) # Descomentar si se quiere ver año por año y comentar la linea 108
for columna in df_tasas.columns:
    plt.plot(df_tasas.index, df_tasas[columna], marker='o', label=columna)

plt.xticks(rotation=60)
# plt.xticks(ticks=range(0, len(df_tasas.index), 4), 
#         labels=[df_tasas.index[i] for i in range(0, len(df_tasas.index), 4)],    # Descomentar si se quiere ver año por año y comentar la linea 113
#         rotation=60)
plt.ylabel("Tasa (%)")
plt.title("Evolución de tasas de Actividad, Empleo y Desocupación (NEA 2016-2024)")
plt.legend()
plt.grid(True)
plt.tight_layout()




plt.show()


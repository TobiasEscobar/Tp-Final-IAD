import os
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt

# Carpeta raíz que contiene subcarpetas 'individual' y 'hogar'
carpeta_raiz = "periodos trimestrales/periodo 2021"

# Códigos oficiales INDEC para aglomerados del NEA
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
carpeta_individual = os.path.join(carpeta_raiz, "individual")
carpeta_hogar = os.path.join(carpeta_raiz, "hogar")

archivos_txt = sorted(f for f in os.listdir(carpeta_individual) if f.endswith(".txt"))

for nombre_archivo in archivos_txt:
    archivo_individual = os.path.join(carpeta_individual, nombre_archivo)
    archivo_hogar = os.path.join(carpeta_hogar, nombre_archivo.replace("individual", "hogar"))

    if not os.path.exists(archivo_hogar):
        print(f"Archivo hogar no encontrado para: {nombre_archivo}")
        continue

    df_ind = pd.read_csv(archivo_individual, sep=";", low_memory=False)
    df_hogar = pd.read_csv(archivo_hogar, sep=";", low_memory=False)

    df_hogar_filtrado = df_hogar[df_hogar["IV1"].isin([1, 2])]

    df = pd.merge(
        df_ind,
        df_hogar_filtrado[["CODUSU", "NRO_HOGAR", "IV1"]],
        on=["CODUSU", "NRO_HOGAR"],
        how="inner"
    )

    df_nea = df[df["AGLOMERADO"].isin(aglomerados_nea)].copy()

    # Crear columnas binarias para tasas
    df_nea["es_activo"] = df_nea["ESTADO"].isin([1, 2]).astype(int)
    df_nea["es_ocupado"] = (df_nea["ESTADO"] == 1).astype(int)
    df_nea["es_desocupado"] = (df_nea["ESTADO"] == 2).astype(int)

    trimestre = nombre_archivo.replace(".txt", "")

    tasas_por_trimestre[trimestre] = {
        "actividad": media_ponderada(df_nea["es_activo"], df_nea["PONDERA"]),
        "empleo": media_ponderada(df_nea["es_ocupado"], df_nea["PONDERA"]),
        "desocupacion": media_ponderada(
            df_nea[df_nea["es_activo"] == 1]["es_desocupado"],
            df_nea[df_nea["es_activo"] == 1]["PONDERA"]
        )
    }

# Mostrar resultados
for trimestre, tasas in tasas_por_trimestre.items():
    print(f"\nTrimestre: {trimestre}")
    print("=" * 60)
    for tipo_tasa, resultado in tasas.items():
        print(f"{tipo_tasa.capitalize():>15}: {resultado['media']:.4f}")
    print("=" * 60)





# Graficos

# Convertimos a DataFrame
df_tasas = pd.DataFrame({
    t: {
        "Actividad": v["actividad"]["media"],
        "Empleo": v["empleo"]["media"],
        "Desocupación": v["desocupacion"]["media"]
    }
    for t, v in tasas_por_trimestre.items()
}).T  # Transponemos para que los trimestres queden como índices

# Ordenar por trimestre 
def ordenar_trimestres(tri_str):
    # Extraer año y trimestre como enteros
    if tri_str.startswith("usu_individual_t"):
        tri = int(tri_str[17])  # ej: 1, 2, 3 o 4
        anio = int("20" + tri_str[18:20])  # ej: 2016, 2017...
        return anio * 10 + tri
    else:
        return 0  # por si el nombre no es esperado

df_tasas["orden"] = df_tasas.index.map(ordenar_trimestres)
df_tasas = df_tasas.sort_values("orden").drop(columns="orden")

# Graficar
plt.figure(figsize=(12, 6))
for columna in df_tasas.columns:
    plt.plot(df_tasas.index, df_tasas[columna], marker='o', label=columna)

plt.xticks(rotation=45)
plt.ylabel("Tasa (%)")
plt.title("Evolución de tasas en el NEA (EPH 2016 en adelante)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
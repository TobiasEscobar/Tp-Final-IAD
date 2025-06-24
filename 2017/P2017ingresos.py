import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gmean, trim_mean, skew
import os
import re

carpeta = "periodos trimestrales\periodo 2017\individual"

# Diccionario para guardar resultados por trimestre
estadisticas = {}

# Diccionario de ponderadores correspondientes
ponderadores = {
    "P21": "PONDIIO",
    "P47T": "PONDII"
}

# Diccionario para guardar resultados por trimestre
resultados_por_trimestre = {}

# Función para mediana ponderada
def mediana_ponderada(valores, pesos):

    orden = np.argsort(valores)
    
    valores_ordenados = np.array(valores)[orden]
    pesos_ordenados = np.array(pesos)[orden]

    acumulados = np.cumsum(pesos_ordenados)

    mitad = pesos_ordenados.sum() / 2

    return valores_ordenados[np.where(acumulados >= mitad)[0][0]]

# Función para resumen de estadísticas ponderadas
def resumen_ponderado(valores, pesos):

    valores = np.array(valores)
    pesos = np.array(pesos)

    media = np.average(valores, weights=pesos)

    mediana = mediana_ponderada(valores, pesos)

    try:
        moda = pd.Series(valores).mode().iloc[0]
    except IndexError:
        moda = None

    # FUNCIÓN auxiliar para percentiles ponderados
    def percentil_ponderado(p):
        pos = pesos.sum() * p

        orden = np.argsort(valores)

        valores_ordenados = valores[orden]
        pesos_ordenados = pesos[orden]

        acumulados = np.cumsum(pesos_ordenados)

        return valores_ordenados[np.where(acumulados >= pos)[0][0]]

    cuartiles = {q: percentil_ponderado(q) for q in [0.25, 0.5, 0.75]}

    deciles = {d / 10: percentil_ponderado(d / 10) for d in range(1, 10)}

    minimo = valores.min()
    maximo = valores.max()

    return {
        "media": media,
        "mediana": mediana,
        "moda": moda,
        "cuartiles": cuartiles,
        "deciles": deciles,
        "min": minimo,
        "max": maximo
    }

# Procesamiento general por archivo
for archivo in sorted(os.listdir(carpeta)):
    if archivo.endswith(".txt"):
        ruta = os.path.join(carpeta, archivo)
        df = pd.read_csv(ruta, sep=";", low_memory=False)

        if "REGION" in df.columns and "CH06" in df.columns:
            df_nea = df[(df["REGION"] == 41) & (df["CH06"] >= 14)]

            trimestre = archivo.replace(".txt", "")  

            estadisticas[trimestre] = {}

            for variable in ["P21", "P47T"]:
                ponderador = ponderadores[variable]
                if variable in df_nea.columns and ponderador in df_nea.columns:
                    df_var = df_nea[(df_nea[variable] != -9)].dropna(subset=[variable, ponderador])
                    resultado = resumen_ponderado(df_var[variable], df_var[ponderador])
                    estadisticas[trimestre][variable] = resultado


for trimestre, datos in estadisticas.items():
    print(f"\nResultados del archivo: {trimestre}")
    print("=" * 50)

    print("\nP21 (Ingreso de ocupación principal):")
    for clave, valor in datos["P21"].items():
        print(f"{clave}: {valor}")

    print("\n" + "-" * 50)

    print("P47T (Ingreso total individual):")
    for clave, valor in datos["P47T"].items():
        print(f"{clave}: {valor}")

    print("\n" + "=" * 50 + "\n")




# Grafico

medias = {"P21": {}, "P47T": {}}
medianas = {"P21": {}, "P47T": {}}

for trimestre, datos in estadisticas.items():
    for var in ["P21", "P47T"]:
        if var in datos:
            medias[var][trimestre] = datos[var]["media"]
            medianas[var][trimestre] = datos[var]["mediana"]

def ordenar_trimestres(tri_str):
    match = re.search(r"t(\d)(\d\d)", tri_str)
    if match:
        trim, anio = int(match.group(1)), int(match.group(2))
        return int(f"20{anio}") * 10 + trim
    return 0

def graficar_ingreso(titulo, valores_media, valores_mediana):
    df_media = pd.Series(valores_media).sort_index(key=lambda x: [ordenar_trimestres(i) for i in x])
    df_mediana = pd.Series(valores_mediana).sort_index(key=lambda x: [ordenar_trimestres(i) for i in x])

    plt.figure(figsize=(12, 6))
    plt.plot(df_media.index, df_media.values, marker='o', label="Media")
    plt.plot(df_mediana.index, df_mediana.values, marker='s', label="Mediana")
    plt.title(f"Evolución de {titulo} en la región NEA")
    plt.ylabel("Monto en pesos")
    plt.xlabel("Trimestre")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

graficar_ingreso("P21 (Ingreso de la ocupación principal)", medias["P21"], medianas["P21"])
graficar_ingreso("P47T (Ingreso total individual)", medias["P47T"], medianas["P47T"])
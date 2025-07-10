import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors
import geopandas as gpd
import contextily as ctx

from funcionesAuxiliares import *
from ipc_trimestral import *


aglom = gpd.read_file('aglomerados_eph.json')
aglom

aglo_41 = ["07","08","12","15"]

gdf_filtrado = aglom[aglom["eph_codagl"].isin(aglo_41)]

print(gdf_filtrado.head())

gdf_filtrado.plot()

gdf_filtrado = gdf_filtrado.to_crs(epsg=3857)


ax = gdf_filtrado.plot(figsize=(10,10), alpha=0.5, edgecolor='black')
ctx.add_basemap(ax, crs=gdf_filtrado.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

print(gdf_filtrado["eph_codagl"].unique())


plt.title("Aglomerados de la region Noreste analizados")
plt.axis('off')
plt.show()



def resumen_ponderado(valores, pesos):
    valores = np.array(valores)
    pesos = np.array(pesos)
    media = np.average(valores, weights=pesos)
    maximo = valores.max()
    return {"media": media, "max": maximo}

def analizar_ingresos_por_aglomerado(anio):
    carpeta = elegir_archivo(anio)
    nombre_archivos = transformar_nombres(anio)

    ponderadores = {
        "P21": "PONDIIO",
        "P47T": "PONDII"
    }

    estadisticas = {}

    for archivo in sorted(os.listdir(carpeta)):
        if archivo.endswith(".txt"):
            ruta = os.path.join(carpeta, archivo)
            df = pd.read_csv(ruta, sep=";", low_memory=False)

            if "REGION" in df.columns and "CH06" in df.columns and "AGLOMERADO" in df.columns:
                df_nea = df[(df["REGION"] == 41) & (df["CH06"] >= 14)]

                trimestre = nombre_archivos.get(archivo, archivo.replace(".txt", ""))
                estadisticas[trimestre] = {}

                for aglo in aglo_41:
                    codagl_int = int(aglo)
                    df_aglo = df_nea[df_nea["AGLOMERADO"] == codagl_int]

                    for variable in ["P21"]:
                        ponderador = ponderadores[variable]
                        if variable in df_aglo.columns and ponderador in df_aglo.columns:
                            df_var = df_aglo[(df_aglo[variable] != -9)].dropna(subset=[variable, ponderador])
                            if not df_var.empty:
                                resultado = resumen_ponderado(df_var[variable], df_var[ponderador])
                                if aglo not in estadisticas[trimestre]:
                                    estadisticas[trimestre][aglo] = {}
                                estadisticas[trimestre][aglo][variable] = resultado

    return estadisticas


def graficar_ingresos_mapa(anio):
    print(f"\nGenerando mapa de ingresos ajustados para {anio}...")

    estadisticas = analizar_ingresos_por_aglomerado(anio)

    if not estadisticas:
        print("No se encontraron datos para ese año.")
        return

    ultimo_trimestre = sorted(estadisticas.keys())[-1]
    datos_trimestre = estadisticas[ultimo_trimestre]

    # Crear diccionario de ingreso ajustado por aglomerado
    valores_por_aglo = {}
    for aglo, datos in datos_trimestre.items():
        ingreso_nominal = datos["P21"]["media"]
        ipc_actual = ipc_acumulado.get(ultimo_trimestre, 1.0)
        ingreso_ajustado = ingreso_nominal / ipc_actual
        valores_por_aglo[aglo] = ingreso_ajustado

    # Asignar al GeoDataFrame
    gdf_plot = gdf_filtrado.copy()
    gdf_plot["ingreso_ajustado"] = gdf_plot["eph_codagl"].map(valores_por_aglo)

    # Reproyección a Web Mercator
    gdf_plot = gdf_plot.to_crs(epsg=3857)

    fig, ax = plt.subplots(figsize=(10, 10))
    gdf_plot.plot(
        column="ingreso_ajustado",
        cmap="Blues",
        legend=True,
        edgecolor="black",
        linewidth=0.6,
        ax=ax,
        alpha=0.6
    )

    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=gdf_plot.crs)

    plt.title(f"Ingreso promedio ajustado (P21) - {ultimo_trimestre}", fontsize=14)
    plt.axis("off")
    plt.tight_layout()
    plt.show()



graficar_ingresos_mapa(2016)  

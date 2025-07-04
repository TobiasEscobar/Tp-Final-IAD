import os
import re
import pandas as pd
import numpy as np
from scipy.stats import gmean, trim_mean, skew
import matplotlib.pyplot as plt
from funcionesAuxiliares import *


def mostrar_menu():
    print("\n=== Menú de Análisis de la EPH ===")
    print("1. Ver tasas por año en forma trimestral")
    print("2. Ver estadísticas de ingreso por año en forma trimestral")
    print("3. Ver evolución trimestral de tasas desde 2016 hasta 2024")
    print("4. Salir")

def seleccionar_anio():
    anio = int(input("Ingrese el año (2016 a 2024): "))
    return anio

def menu_principal():
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            anio = seleccionar_anio()
            analizar_tasas(anio)

        elif opcion == "2":
            anio = seleccionar_anio()
            analizar_ingresos(anio)

        elif opcion == "3":
            graficar_evolucion_tasas()

        elif opcion == "4":
            print("Saliendo del programa...")
            sys.exit()

        else:
            print("Opción no válida. Intente nuevamente.")



def analizar_tasas(anio):
    print(f"\nAnálisis de tasas para {anio}")
    carpeta_individual = elegir_archivo(anio)

    aglomerados_nea = [7, 8, 12, 15]

    tasas_por_trimestre = {}

    def media_ponderada(valores, pesos):
        valores = np.array(valores)
        pesos = np.array(pesos)
        media = np.average(valores, weights=pesos)
        return {"media": round(media * 100, 1)} 

    # Nombres legibles para los trimestres
    nombre_archivos = transformar_nombres(anio)

    archivos_txt = sorted(f for f in os.listdir(carpeta_individual) if f.endswith(".txt"))

    for nombre_archivo in archivos_txt:
        archivo_individual = os.path.join(carpeta_individual, nombre_archivo)

        df = pd.read_csv(archivo_individual, sep=";", low_memory=False)

        df_nea = df[df["AGLOMERADO"].isin(aglomerados_nea)].copy()

        # Crear columnas binarias para tasas
        df_nea["es_activo"] = df_nea["ESTADO"].isin([1, 2]).astype(int)
        df_nea["es_ocupado"] = (df_nea["ESTADO"] == 1).astype(int)
        df_nea["es_desocupado"] = (df_nea["ESTADO"] == 2).astype(int)

        trimestre = nombre_archivos.get(nombre_archivo, nombre_archivo.replace(".txt", ""))

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
            print(f"{tipo_tasa.capitalize():>15}: {resultado['media']:.1f}")
        print("=" * 60)


    #Graficar
    df_tasas = pd.DataFrame({
    t: {
        "Actividad": v["actividad"]["media"],
        "Empleo": v["empleo"]["media"],
        "Desocupación": v["desocupacion"]["media"]
    }
    for t, v in tasas_por_trimestre.items()
    }).T  # Transponemos para que los trimestres queden como índices

    # Ordenar índices como string
    df_tasas = df_tasas.sort_index()

    ########################################## Graficos
    plt.figure(figsize=(12, 6))
    for columna in df_tasas.columns:
        plt.plot(df_tasas.index, df_tasas[columna], marker='o', label=columna)

    plt.xticks(rotation=45)
    plt.yticks(np.arange(0, 101, 5))
    plt.ylabel("Tasa (%)")
    plt.title("Evolución de las tasas en la región NEA")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()


def analizar_ingresos(anio):
    print(f"\nAnálisis de ingresos para {anio}")

    carpeta = elegir_archivo(anio)

    estadisticas = {}

    ponderadores = {
        "P21": "PONDIIO",
        "P47T": "PONDII"
    }

    resultados_por_trimestre = {}

    def mediana_ponderada(valores, pesos):
        orden = np.argsort(valores)
        
        valores_ordenados = np.array(valores)[orden]
        pesos_ordenados = np.array(pesos)[orden]

        acumulados = np.cumsum(pesos_ordenados)

        mitad = pesos_ordenados.sum() / 2

        return valores_ordenados[np.where(acumulados >= mitad)[0][0]]

    def resumen_ponderado(valores, pesos):

        valores = np.array(valores)
        pesos = np.array(pesos)

        media = np.average(valores, weights=pesos)

        minimo = valores.min()
        maximo = valores.max()

        return {
            "media": media,
            "min": minimo,
            "max": maximo
        }

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


    ############################################## Grafico

    medias = {"P21": {}, "P47T": {}}

    for trimestre, datos in estadisticas.items():
        for var in ["P21", "P47T"]:
            if var in datos:
                medias[var][trimestre] = datos[var]["media"]

    def ordenar_trimestres(tri_str):
        match = re.search(r"t(\d)(\d\d)", tri_str)
        if match:
            trim, anio = int(match.group(1)), int(match.group(2))
            return int(f"20{anio}") * 10 + trim
        return 0

    def graficar_ingreso(titulo, valores_media):
        df_media = pd.Series(valores_media).sort_index(key=lambda x: [ordenar_trimestres(i) for i in x])

        plt.figure(figsize=(12, 6))
        plt.plot(df_media.index, df_media.values, marker='o', label="Media")
        plt.title(f"Evolución de {titulo} en la región NEA")
        plt.ylabel("Monto en pesos")
        plt.xlabel("Trimestre")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    graficar_ingreso("P21 (Ingreso de la ocupación principal)", medias["P21"])
    graficar_ingreso("P47T (Ingreso total individual)", medias["P47T"])


def graficar_evolucion_tasas():
    print("\nGenerando gráfico de evolución de tasas 2016-2024...")
    
    carpeta_individual = "PeriodosTotales/2016-2024/individual"

    aglomerados_nea = [7, 8, 12, 15]

    tasas_por_trimestre = {}

    def media_ponderada(valores, pesos):
        valores = np.array(valores)
        pesos = np.array(pesos)
        media = np.average(valores, weights=pesos)
        return {"media": round(media * 100, 1)}

    archivos_txt = sorted(f for f in os.listdir(carpeta_individual) if f.endswith(".txt"))

    for nombre_archivo in archivos_txt:
        archivo_individual = os.path.join(carpeta_individual, nombre_archivo)

        df = pd.read_csv(archivo_individual, sep=";", low_memory=False)

        df_nea = df[df["AGLOMERADO"].isin(aglomerados_nea)].copy()

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


# Iniciar menu
menu_principal()
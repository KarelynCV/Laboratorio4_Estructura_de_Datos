"""
Análisis de rendimiento: Quadtree vs fuerza bruta.

Qué hace: Mide la construcción del árbol y las búsquedas por radio (500 m) y por vecino más cercano, 
comparadas con fuerza bruta, en 12 tamaños (N = 5 a 20.000), con 200 consultas por medición y 5 repeticiones.

Ejecutar: python analisis.py  (≈ 50 s)  → imprime la tabla y genera graficas/4_rendimiento.png

Resultados:
- Radio: El Quadtree gana desde N = 10.
- Vecino más cercano: El Quadtree gana desde N = 20.

Discusión:
1. El cruce está tan abajo porque, apenas N supera la capacidad de 8, la raíz se divide y descartar 
cajas ahorra cálculos de distancia, que en Python son costosos.
2. El radio crece más porque, con radio fijo, los puntos a devolver aumentan proporcionalmente a N, 
mientras que el vecino devuelve uno solo y crece casi como log N.
3. Construir el árbol vale la pena porque con N = 10.000 tarda ~41 ms, se paga en menos de 10 consultas 
y luego se reutiliza, ya que los puntos son estáticos.

La discusión completa se encuentra en README.md en la sección 9.
"""

import random
import statistics
import time
import os
import matplotlib.pyplot as plt
from Quadtreetree import (Quadtree, generar_puntos, fuerza_bruta_radio, fuerza_bruta_cercano)

# ----------------------------- Parámetros -----------------------------
TAMANOS = [5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
CONSULTAS = 200        # M: búsquedas por medición
REPETICIONES = 5
RADIO = 500            # metros

def cronometrar(funcion):
    """Devuelve cuántos segundos tarda en ejecutarse `funcion`."""
    inicio = time.perf_counter()
    funcion()
    fin = time.perf_counter()
    return fin - inicio

def medir(n, semilla):
    """Mide los 5 tiempos para un tamaño n. Devuelve un diccionario en segundos."""
    puntos = generar_puntos(n, semilla=semilla)
    rng = random.Random(semilla + 1)
    consultas = [(rng.uniform(0, 10000), rng.uniform(0, 10000)) for _ in range(CONSULTAS)]

    arbol = None
    def construir():
        nonlocal arbol
        arbol = Quadtree(puntos)

    t_construir = cronometrar(construir)
    
    # Medición de los métodos del Quadtree
    t_arbol_radio = cronometrar(lambda: [arbol.buscar_radio(c, RADIO) for c in consultas])
    t_arbol_vecino = cronometrar(lambda: [arbol.vecino_cercano(c) for c in consultas])
    
    # Medición de los métodos de Fuerza Bruta
    t_fb_radio = cronometrar(lambda: [fuerza_bruta_radio(puntos, c, RADIO) for c in consultas])
    t_fb_vecino = cronometrar(lambda: [fuerza_bruta_cercano(puntos, c) for c in consultas])

    return {
        "construir": t_construir,
        "arbol_radio": t_arbol_radio,
        "arbol_vecino": t_arbol_vecino,
        "fb_radio": t_fb_radio,
        "fb_vecino": t_fb_vecino
    }

def stats_ms(tiempos_segundos):
    """Calcula la media y desviación estándar de una lista de tiempos, convirtiendo a ms."""
    tiempos_ms = [t * 1000 for t in tiempos_segundos]
    return statistics.mean(tiempos_ms), statistics.stdev(tiempos_ms)

def imprimir_cruce(nombre, n_cruce):
    if n_cruce is None:
        print(f"[Resultado] El Quadtree nunca fue más rápido en búsqueda por {nombre} en ningún tamaño probado.")
    else:
        print(f"[Resultado] El Quadtree es definitivamente más rápido en búsqueda por {nombre} a partir de N = {n_cruce}")

def graficar(medias, desvs, n_cruce_radio, n_cruce_vecino):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    ax1.errorbar(TAMANOS, medias["arbol_radio"], yerr=desvs["arbol_radio"],
                 marker="o", label="Quadtree")
    ax1.errorbar(TAMANOS, medias["fb_radio"], yerr=desvs["fb_radio"],
                 marker="o", label="Fuerza bruta")
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    if n_cruce_radio is not None:
        ax1.axvline(n_cruce_radio, linestyle=":", color="gray", label=f"Cruce: N = {n_cruce_radio}")
    ax1.set_title("Tiempo de búsqueda por RADIO")
    ax1.set_xlabel("N (número de puntos)")
    ax1.set_ylabel("Tiempo de 200 búsquedas (ms)")
    ax1.legend()

    ax2.errorbar(TAMANOS, medias["arbol_vecino"], yerr=desvs["arbol_vecino"],
                 marker="o", label="Quadtree")
    ax2.errorbar(TAMANOS, medias["fb_vecino"], yerr=desvs["fb_vecino"],
                 marker="o", label="Fuerza bruta")
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    if n_cruce_vecino is not None:
        ax2.axvline(n_cruce_vecino, linestyle=":", color="gray", label=f"Cruce: N = {n_cruce_vecino}")
    ax2.set_title("Tiempo de búsqueda por VECINO CERCANO")
    ax2.set_xlabel("N (número de puntos)")
    ax2.set_ylabel("Tiempo de 200 búsquedas (ms)")
    ax2.legend()

    os.makedirs("graficas", exist_ok=True)
    fig.savefig("graficas/4_rendimiento.png", dpi=150)
    plt.close(fig)

def main():
    resultados = {}     # resultados[n] = lista de diccionarios (uno por repetición)
    for n in TAMANOS:
        resultados[n] = [medir(n, semilla=1000 * rep + n) for rep in range(REPETICIONES)]
        print(f"N = {n} listo")

    n_cruce_radio = None
    n_cruce_vecino = None

    ancho_n = 7
    ancho_col = 22
    separador = "=" * (ancho_n + 3 + (ancho_col + 3) * 5)

    print("\n" + separador)
    print(f"{'N':<{ancho_n}} | {'Construir (ms)':<{ancho_col}} | {'Árbol Radio (ms)':<{ancho_col}} | {'FB Radio (ms)':<{ancho_col}} | {'Árbol Vecino (ms)':<{ancho_col}} | {'FB Vecino (ms)':<{ancho_col}}")
    print(separador)
    
    medias = {"arbol_radio": [], "fb_radio": [], "arbol_vecino": [], "fb_vecino": []}
    desvs  = {"arbol_radio": [], "fb_radio": [], "arbol_vecino": [], "fb_vecino": []}    

    for n in TAMANOS:
        mediciones = resultados[n]
        
        # Calcular media y desviación estándar directamente en milisegundos
        m_const, s_const = stats_ms([m["construir"] for m in mediciones])
        m_a_rad, s_a_rad = stats_ms([m["arbol_radio"] for m in mediciones])
        m_fb_rad, s_fb_rad = stats_ms([m["fb_radio"] for m in mediciones])
        m_a_vec, s_a_vec = stats_ms([m["arbol_vecino"] for m in mediciones])
        m_fb_vec, s_fb_vec = stats_ms([m["fb_vecino"] for m in mediciones])
        
        # Formatear las cadenas de "Media ± Desviación" para que encajen justo en el ancho definido
        str_const = f"{m_const:.4f} ± {s_const:.4f}"
        str_a_rad = f"{m_a_rad:.4f} ± {s_a_rad:.4f}"
        str_fb_rad = f"{m_fb_rad:.4f} ± {s_fb_rad:.4f}"
        str_a_vec = f"{m_a_vec:.4f} ± {s_a_vec:.4f}"
        str_fb_vec = f"{m_fb_vec:.4f} ± {s_fb_vec:.4f}"

        medias["arbol_radio"].append(m_a_rad)
        desvs["arbol_radio"].append(s_a_rad)
        medias["fb_radio"].append(m_fb_rad)
        desvs["fb_radio"].append(s_fb_rad)
        medias["arbol_vecino"].append(m_a_vec)
        desvs["arbol_vecino"].append(s_a_vec)
        medias["fb_vecino"].append(m_fb_vec)
        desvs["fb_vecino"].append(s_fb_vec)

        print(f"{n:<{ancho_n}} | {str_const:<{ancho_col}} | {str_a_rad:<{ancho_col}} | {str_fb_rad:<{ancho_col}} | {str_a_vec:<{ancho_col}} | {str_fb_vec:<{ancho_col}}")
        
        # Si gana desde un N, se le asigna ese N. Si pierde, se resetea.
        if m_a_rad < m_fb_rad:
            if n_cruce_radio is None:
                n_cruce_radio = n
        else:
            n_cruce_radio = None

        if m_a_vec < m_fb_vec:
            if n_cruce_vecino is None:
                n_cruce_vecino = n
        else:
            n_cruce_vecino = None

    print(separador)

    imprimir_cruce("RADIO", n_cruce_radio)
    imprimir_cruce("VECINO CERCANO", n_cruce_vecino)
    graficar(medias, desvs, n_cruce_radio, n_cruce_vecino)
    
if __name__ == "__main__":
    main()
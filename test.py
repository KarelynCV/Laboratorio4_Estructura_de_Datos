import random
import math
import unittest
import os
from matplotlib import patches
import matplotlib.pyplot as plt

from Quadtreetree import (Quadtree, generar_puntos, fuerza_bruta_radio, fuerza_bruta_cercano, distancia)

def contar_puntos(nodo):
    """Cuenta cuántos puntos hay guardados en todas las hojas del árbol."""
    if not nodo.hijos:
        return len(nodo.puntos)
    return sum(contar_puntos(hijo) for hijo in nodo.hijos)

def consultas_aleatorias(cantidad, k=2, semilla=1):
    """Puntos de consulta al azar (reproducibles gracias a la semilla)."""
    rng = random.Random(semilla)
    return [tuple(rng.uniform(0, 10000) for _ in range(k)) for _ in range(cantidad)]

class PruebasQuadtree(unittest.TestCase):

    def test_1_todos_los_puntos_quedan_guardados(self):
        puntos = generar_puntos(10000)
        arbol = Quadtree(puntos)

        self.assertEqual(contar_puntos(arbol.raiz), 10000)

    def test_2_la_raiz_se_divide(self):
        puntos = generar_puntos(10000)
        arbol = Quadtree(puntos)

        self.assertIsNotNone(arbol.raiz.hijos)
        self.assertEqual(len(arbol.raiz.puntos), 0)

    def test_3_radio_igual_a_fuerza_bruta(self):
        puntos = generar_puntos(10000)
        arbol = Quadtree(puntos)
        consultas = consultas_aleatorias(100)
        radio = 500

        for c in consultas:
            resultado_quadtree = arbol.buscar_radio(c, radio)
            resultado_bruto = fuerza_bruta_radio(puntos, c, radio)

            self.assertEqual(sorted(resultado_quadtree),sorted(resultado_bruto))

    def test_4_vecino_igual_a_fuerza_bruta(self):
        puntos = generar_puntos(10000)
        arbol = Quadtree(puntos)
        consultas = consultas_aleatorias(100)

        for c in consultas:
            resultado_quadtree_vecino = arbol.vecino_cercano(c)
            resultado_bruto_vecino = fuerza_bruta_cercano(puntos, c)

            self.assertEqual(resultado_quadtree_vecino, resultado_bruto_vecino)

    def test_5_funciona_en_3d(self):
        puntos_3d = generar_puntos(10000, k=3)
        arbol_3d = Quadtree(puntos_3d, k=3) 
        consultas_3d = consultas_aleatorias(100, k=3)
        radio = 500
        
        for c in consultas_3d:
            resultado_quadtree = arbol_3d.buscar_radio(c, radio)
            resultado_bruto = fuerza_bruta_radio(puntos_3d, c, radio)
            resultado_quadtree_vecino = arbol_3d.vecino_cercano(c)
            resultado_bruto_vecino = fuerza_bruta_cercano(puntos_3d, c)
                        
            self.assertEqual(sorted(resultado_quadtree), sorted(resultado_bruto))
            self.assertEqual(resultado_quadtree_vecino, resultado_bruto_vecino)

    def test_6_puntos_repetidos(self):
        punto_repetido = (1.0, 1.0)
        puntos = [punto_repetido] * 20
        arbol = Quadtree(puntos)
        resultado_quadtree = arbol.buscar_radio(punto_repetido, 0)

        self.assertEqual(len(resultado_quadtree), 20)

        for p in resultado_quadtree:
            self.assertEqual(p, punto_repetido)

    def test_7_arbol_vacio(self):
        arbol_vacio = Quadtree([])
        c = (5000, 5000)
        resultado = arbol_vacio.vecino_cercano(c)

        self.assertEqual(resultado, (None, math.inf))

CARPETA_GRAFICAS = "graficas"

def graficar_radio(puntos, arbol, consulta, radio):
    encontrados = arbol.buscar_radio(consulta, radio)

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter([p[0] for p in puntos], [p[1] for p in puntos], s=5, color="lightgray", label="Puntos")
    ax.scatter([p[0] for p in encontrados], [p[1] for p in encontrados], s=20, color="red", label="Encontrados")
    ax.scatter(consulta[0], consulta[1], marker="*", s=300, color="blue", label="Consulta")
    circle = plt.Circle(consulta, radio, color='blue', fill=False, linestyle='--', label='Radio')
    ax.add_patch(circle)
    ax.set_xlim(consulta[0] - 1000, consulta[0] + 1000)
    ax.set_ylim(consulta[1] - 1000, consulta[1] + 1000)
    ax.set_aspect("equal")
    ax.set_title(f"Búsqueda por radio\nConsulta: {consulta} · Radio: {radio} m · Encontrados: {len(encontrados)} puntos")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.legend()
    fig.savefig(os.path.join(CARPETA_GRAFICAS, "1_busqueda_radio.png"), dpi=150)
    plt.close(fig)


def graficar_vecinos(puntos, arbol, consulta, cantidad=5):
    vecino, dist = arbol.vecino_cercano(consulta)
    encontrados = arbol.buscar_radio(consulta, 500) # Radio de 500 m: suficiente para encontrar los 5 más cercanos.
    encontrados = sorted(encontrados, key=lambda p: distancia(p, consulta))[:cantidad]

    fig, ax = plt.subplots(figsize=(7, 7))
    for i, p in enumerate(encontrados, start=1):
        ax.annotate(f"Punto {i} d= {distancia(p, consulta):.2f} m", (p[0], p[1]), textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8, color="black")
    ax.scatter([p[0] for p in puntos], [p[1] for p in puntos], s=5, color="lightgray", label="Puntos")
    ax.scatter([p[0] for p in encontrados], [p[1] for p in encontrados], s=20, color="red", label="Más cercanos")
    ax.scatter(consulta[0], consulta[1], marker="*", s=300, color="blue", label="Consulta")
    ax.plot([consulta[0], vecino[0]], [consulta[1], vecino[1]], color="green", linestyle="--", label="Distancia al más cercano")
    ax.set_xlim(consulta[0] - 300, consulta[0] + 300)
    ax.set_ylim(consulta[1] - 300, consulta[1] + 300)
    ax.set_aspect("equal")
    ax.set_title(f"Vecino más cercano\nConsulta: {consulta} · Distancia: {dist:.2f} m")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.legend()
    fig.savefig(os.path.join(CARPETA_GRAFICAS, "2_vecinos_cercanos.png"), dpi=150)
    plt.close(fig)

def obtener_hojas(nodo, hojas):
    if not nodo.hijos:
        hojas.append(nodo)
    else:
        for hijo in nodo.hijos:
            obtener_hojas(hijo, hojas)
    return hojas

def graficar_estructura(puntos, arbol, consulta, radio):
    hojas = obtener_hojas(arbol.raiz, [])
    
    revisadas = []
    descartadas = []
    for hoja in hojas:
        if hoja.distancia_a_caja(consulta) <= radio:
            revisadas.append(hoja)
        else:
            descartadas.append(hoja)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

    ax1.scatter([p[0] for p in puntos], [p[1] for p in puntos], s=1, color="lightgray", label="Puntos")
    
    for hoja in hojas:
        ancho = hoja.maximos[0] - hoja.minimos[0]
        alto = hoja.maximos[1] - hoja.minimos[1]
        rect = patches.Rectangle((hoja.minimos[0], hoja.minimos[1]), ancho, alto, linewidth=0.3, edgecolor="gray", facecolor="none")
        ax1.add_patch(rect)
        
    ax1.set_aspect("equal")
    ax1.set_title(f"Estructura Completa del Quadtree\nTotal de hojas: {len(hojas)}")
    ax1.set_xlabel("X (m)")
    ax1.set_ylabel("Y (m)")

    ax2.scatter([p[0] for p in puntos], [p[1] for p in puntos], s=1, color="lightgray")
    
    for hoja in descartadas:
        ancho = hoja.maximos[0] - hoja.minimos[0]
        alto = hoja.maximos[1] - hoja.minimos[1]
        rect = patches.Rectangle((hoja.minimos[0], hoja.minimos[1]), ancho, alto, linewidth=0.5, edgecolor="gainsboro", facecolor="none")
        ax2.add_patch(rect)

    etiqueta = "Hojas revisadas"
    for hoja in revisadas:
        ancho = hoja.maximos[0] - hoja.minimos[0]
        alto = hoja.maximos[1] - hoja.minimos[1]
        rect = patches.Rectangle((hoja.minimos[0], hoja.minimos[1]), ancho, alto, linewidth=1.5, edgecolor="red", facecolor="none", label=etiqueta)
        ax2.add_patch(rect)
        etiqueta = None

    ax2.scatter(consulta[0], consulta[1], marker="*", s=300, color="blue", label="Consulta", zorder=5)
    circle = plt.Circle(consulta, radio, color='blue', fill=False, linestyle='--', label='Radio', zorder=5)
    ax2.add_patch(circle)
    
    ax2.set_xlim(consulta[0] - 1000, consulta[0] + 1000)
    ax2.set_ylim(consulta[1] - 1000, consulta[1] + 1000)
    ax2.set_aspect("equal")
    ax2.set_title(f"Filtrado de Hojas\nRevisadas: {len(revisadas)} de {len(hojas)} hojas ({sum(contar_puntos(hoja) for hoja in revisadas)} de {len(puntos)} puntos)")
    ax2.set_xlabel("X (m)")
    ax2.set_ylabel("Y (m)")
    ax2.legend(loc="upper right", fontsize=8)

    fig.savefig(os.path.join(CARPETA_GRAFICAS, "3_estructura_quadtree.png"), dpi=150)
    plt.close(fig)

if __name__ == "__main__":
    os.makedirs(CARPETA_GRAFICAS, exist_ok=True)
    puntos = generar_puntos(10000)
    arbol = Quadtree(puntos)
    graficar_radio(puntos, arbol, (5000, 5000), 500)
    graficar_vecinos(puntos, arbol, (1234, 5678))
    graficar_estructura(puntos, arbol, (5000, 5000), 500)
    unittest.main(verbosity=2)
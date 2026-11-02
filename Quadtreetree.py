import random
import math
TAMANO_MINIMO = 1   # metros: un nodo más pequeño que esto ya no se divide

def generar_puntos(n, k=2, lado=10000, semilla=2026):
    """n puntos aleatorios en K dimensiones, en metros, dentro de [0, lado]."""
    rng = random.Random(semilla)
    return [tuple(rng.uniform(0, lado) for _ in range(k)) for _ in range(n)]

def distancia(a, b):
    """Distancia euclideana entre dos puntos de K dimensiones."""
    return math.sqrt(sum((a[d] - b[d]) ** 2 for d in range(len(a))))

class Nodo:
    def __init__(self, minimos, maximos, capacidad=8):
        self.minimos = minimos      # lista de K números
        self.maximos = maximos      # lista de K números
        self.capacidad = capacidad
        self.puntos = []
        self.hijos = None           # None = es hoja (no se ha dividido)

    def centro(self):
        return [(self.minimos[d] + self.maximos[d]) / 2 for d in range(len(self.minimos))]

    def indice_hijo(self, punto):
        centro = self.centro()
        indice = 0

        for d in range(len(punto)):
            if punto[d] >= centro[d]:
                indice |= (1 << d)   
        return indice

    def dividir(self):
        self.hijos = []

        for i in range(2 ** len(self.minimos)):
            minimos_hijo = []
            maximos_hijo = []

            for d in range(len(self.minimos)):
                if ((i >> d) & 1) == 0:
                    minimos_hijo.append(self.minimos[d])
                    maximos_hijo.append((self.minimos[d] + self.maximos[d]) / 2)
                else:
                    minimos_hijo.append((self.minimos[d] + self.maximos[d]) / 2)
                    maximos_hijo.append(self.maximos[d])
            self.hijos.append(Nodo(minimos_hijo, maximos_hijo, self.capacidad))

        for punto in self.puntos:
            indice = self.indice_hijo(punto)
            self.hijos[indice].insertar(punto)
        self.puntos = []

    def insertar(self, punto):

        if self.hijos is None:
            caja_minima = all(self.maximos[d] - self.minimos[d] <= TAMANO_MINIMO for d in range(len(self.minimos)))
            if len(self.puntos) < self.capacidad or caja_minima:
                self.puntos.append(punto)
            else:
                self.dividir()
                self.insertar(punto)
        else:
            indice = self.indice_hijo(punto)
            self.hijos[indice].insertar(punto)

    def distancia_a_caja(self, punto):
        """Distancia mínima entre un punto y la caja que representa este nodo."""
        distancia_cuadrada = 0

        for d in range(len(punto)):
            if punto[d] < self.minimos[d]:
                distancia_cuadrada += (self.minimos[d] - punto[d]) ** 2
            elif punto[d] > self.maximos[d]:
                distancia_cuadrada += (punto[d] - self.maximos[d]) ** 2
        return math.sqrt(distancia_cuadrada)

    def buscar_radio(self, consulta, radio, resultado):
        """Buscar todos los puntos dentro de un radio desde el centro."""
        distancia_caja = self.distancia_a_caja(consulta)

        if distancia_caja > radio:
            return  # Se descarta este nodo y sus hijos
        if self.hijos is None:
            # Es hoja, agregar puntos con distancia <= radio
            for p in self.puntos:
                if distancia(p, consulta) <= radio:
                    resultado.append(p)
        else:
            # Tiene hijos, llamar a buscar_radio en cada uno
            for hijo in self.hijos:
                hijo.buscar_radio(consulta, radio, resultado)

    def vecino_cercano(self, consulta, mejor):
        """Buscar el vecino más cercano a un punto de consulta."""
        distancia_caja = self.distancia_a_caja(consulta)

        if distancia_caja >= mejor[1]:
            return  # Se descarta este nodo y sus hijos
        if self.hijos is None:
            for p in self.puntos:
                d = distancia(p, consulta)
                if d < mejor[1]:
                    mejor[0] = p
                    mejor[1] = d
        else:
            # Ordenar hijos por distancia a la caja
            hijos_ordenados = sorted(self.hijos, key=lambda h: h.distancia_a_caja(consulta))
            for hijo in hijos_ordenados:
                hijo.vecino_cercano(consulta, mejor)

class Quadtree:
    def __init__(self, puntos, k=2, lado=10000, capacidad=8):
        self.raiz = Nodo([0] * k, [lado] * k, capacidad)
        
        for p in puntos:
            self.raiz.insertar(p)

    def buscar_radio(self, consulta, radio):
        resultado = []
        self.raiz.buscar_radio(consulta, radio, resultado)
        return resultado

    def vecino_cercano(self, consulta):
        mejor = [None, math.inf]
        self.raiz.vecino_cercano(consulta, mejor)
        return mejor[0], mejor[1]

def fuerza_bruta_radio(puntos, consulta, radio):
    # Buscar todos los puntos dentro de un radio desde el centro usando fuerza bruta.
    resultado = []

    for p in puntos:
        if distancia(p, consulta) <= radio:
            resultado.append(p)
    return resultado

def fuerza_bruta_cercano(puntos, consulta):
    mejor = [None, math.inf]

    for p in puntos:
        d = distancia(p, consulta)
        if d < mejor[1]:
            mejor[0] = p
            mejor[1] = d
    return mejor[0], mejor[1]

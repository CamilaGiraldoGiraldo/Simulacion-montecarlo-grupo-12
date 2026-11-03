# -*- coding: utf-8 -*-
"""Lógica del Yahtzee para dos jugadores + estrategias automáticas (Montecarlo)."""

import random
from collections import Counter

NUM_DADOS = 5
CARAS = 6
MAX_LANZAMIENTOS = 3

CATEGORIAS = ["Unos", "Doses", "Treses", "Cuatros", "Cincos", "Seises",
              "Trío", "Póker", "Full", "Escalera pequeña",
              "Escalera grande", "Yahtzee", "Suerte"]
SUPERIORES = CATEGORIAS[:6]
INFERIORES = CATEGORIAS[6:]

BONO_SUPERIOR_MIN = 63
BONO_SUPERIOR = 35
BONO_YAHTZEE = 100
PUNTOS_FIJOS = {"Full": 25, "Escalera pequeña": 30, "Escalera grande": 40, "Yahtzee": 50}


# ---------- Dados ----------
def lanzar_dados(cantidad=NUM_DADOS, rng=random):
    return [rng.randint(1, CARAS) for _ in range(cantidad)]


def relanzar(dados, indices_conservar, rng=random):
    return [d if i in indices_conservar else rng.randint(1, CARAS)
            for i, d in enumerate(dados)]


def jugar_lanzamientos(decidir_conservar, rng=random):
    dados = lanzar_dados(NUM_DADOS, rng)
    for lanzamiento in range(1, MAX_LANZAMIENTOS):
        conservar = set(decidir_conservar(dados, lanzamiento))
        if len(conservar) == NUM_DADOS:      # conserva todo: termina el turno
            break
        dados = relanzar(dados, conservar, rng)
    return dados


# ---------- Puntaje ----------
def es_yahtzee(dados):
    return len(set(dados)) == 1


def puntaje_base(dados, categoria):
    c = Counter(dados)
    cuentas = sorted(c.values(), reverse=True)
    unicos = set(dados)

    if categoria in SUPERIORES:
        n = SUPERIORES.index(categoria) + 1
        return n * c[n]
    if categoria == "Trío":
        return sum(dados) if cuentas[0] >= 3 else 0
    if categoria == "Póker":
        return sum(dados) if cuentas[0] >= 4 else 0
    if categoria == "Full":
        return 25 if cuentas == [3, 2] else 0
    if categoria == "Escalera pequeña":
        seguidos = [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]
        return 30 if any(s <= unicos for s in seguidos) else 0
    if categoria == "Escalera grande":
        return 40 if unicos in ({1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}) else 0
    if categoria == "Yahtzee":
        return 50 if es_yahtzee(dados) else 0
    return sum(dados)  # Suerte


def joker_activo(puntos, dados):
    return es_yahtzee(dados) and "Yahtzee" in puntos


def categorias_permitidas(puntos, dados):
    libres = [c for c in CATEGORIAS if c not in puntos]
    if not joker_activo(puntos, dados):
        return libres
    superior = SUPERIORES[dados[0] - 1]
    if superior in libres:
        return [superior]
    inferiores = [c for c in libres if c in INFERIORES]
    return inferiores if inferiores else libres


def calcular_puntaje(dados, categoria, puntos=None):
    if puntos is not None and joker_activo(puntos, dados) and categoria in PUNTOS_FIJOS:
        return PUNTOS_FIJOS[categoria]
    return puntaje_base(dados, categoria)


# ---------- Jugador ----------
class Jugador:
    def __init__(self, nombre, decidir_conservar=None, elegir_categoria=None):
        self.nombre = nombre
        self.puntos = {}                 # categoría -> puntaje
        self.bonos_yahtzee = 0           # cantidad de Yahtzee extra
        self.decidir_conservar = decidir_conservar    # None = humano
        self.elegir_categoria = elegir_categoria      # None = humano

    def categorias_libres(self):
        return [c for c in CATEGORIAS if c not in self.puntos]

    def categorias_permitidas(self, dados):
        return categorias_permitidas(self.puntos, dados)

    def puntaje(self, dados, categoria):
        return calcular_puntaje(dados, categoria, self.puntos)

    def anotar(self, dados, categoria):
        if es_yahtzee(dados) and self.puntos.get("Yahtzee") == 50:
            self.bonos_yahtzee += 1
        self.puntos[categoria] = self.puntaje(dados, categoria)
        return self.puntos[categoria]

    def subtotal_superior(self):
        return sum(self.puntos.get(c, 0) for c in SUPERIORES)

    def bono_superior(self):
        return BONO_SUPERIOR if self.subtotal_superior() >= BONO_SUPERIOR_MIN else 0

    def total(self):
        return (sum(self.puntos.values()) + self.bono_superior()
                + BONO_YAHTZEE * self.bonos_yahtzee)


# ---------- Jugador humano (consola) ----------
def conservar_humano(dados, lanzamiento):
    print(f"  Lanzamiento {lanzamiento}: {dados}  (posiciones 1 a 5)")
    r = input("  Posiciones a conservar (ej: 1 3 5), Enter = relanzar todos, "
              "t = conservar todos: ").strip().lower()
    if r == "t":
        return list(range(NUM_DADOS))
    try:
        return [int(x) - 1 for x in r.split() if 1 <= int(x) <= NUM_DADOS]
    except ValueError:
        print("  Entrada no válida, se relanzan todos.")
        return []


def categoria_humano(jugador, dados):
    opciones = jugador.categorias_permitidas(dados)
    print(f"  Dados finales: {dados}")
    for i, c in enumerate(opciones, 1):
        print(f"   {i:2}. {c:<17} -> {jugador.puntaje(dados, c)} pts")
    while True:
        try:
            return opciones[int(input("  Elige categoría (número): ")) - 1]
        except (ValueError, IndexError):
            print("  Opción no válida.")


# ---------- Estrategia automática básica (base para Montecarlo) ----------
def conservar_auto(dados, lanzamiento):
    """Conserva los dados del valor más repetido."""
    valor = Counter(dados).most_common(1)[0][0]
    return [i for i, d in enumerate(dados) if d == valor]


def categoria_auto(jugador, dados):
    """Elige la categoría permitida con mayor puntaje inmediato."""
    return max(jugador.categorias_permitidas(dados),
               key=lambda c: jugador.puntaje(dados, c))


# ---------- Turno y partida ----------
def jugar_turno(jugador, rng=random, verbose=True):
    if verbose:
        print(f"\nTurno de {jugador.nombre}")
    decidir = jugador.decidir_conservar or conservar_humano
    dados = jugar_lanzamientos(decidir, rng)
    elegir = jugador.elegir_categoria or categoria_humano
    cat = elegir(jugador, dados)
    pts = jugador.anotar(dados, cat)
    if verbose:
        print(f"  {jugador.nombre} anota {pts} en {cat}")
    return dados, cat


def jugar_partida(j1, j2, rng=random, verbose=True):
    for ronda in range(1, len(CATEGORIAS) + 1):
        if verbose:
            print(f"\n=== Ronda {ronda} de {len(CATEGORIAS)} ===")
        jugar_turno(j1, rng, verbose)
        jugar_turno(j2, rng, verbose)

    p1, p2 = j1.total(), j2.total()
    ganador = j1.nombre if p1 > p2 else j2.nombre if p2 > p1 else "Empate"
    if verbose:
        print("\n===== MARCADOR FINAL =====")
        print(f"{j1.nombre}: {p1}   |   {j2.nombre}: {p2}")
        print("Resultado:", "¡Empate!" if ganador == "Empate" else f"Gana {ganador}")
    return p1, p2, ganador

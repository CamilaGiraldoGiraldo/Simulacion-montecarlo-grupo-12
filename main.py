# -*- coding: utf-8 -*-
"""Punto de entrada.

  python main.py              -> interfaz gráfica (por defecto)
  python main.py consola      -> partida por consola (humano vs humano)
  python main.py simular      -> simulación Montecarlo (bot vs bot)
  python main.py simular -n 20000 --semilla 42
"""

import argparse
import random
import statistics

from yahtzee import (Jugador, categoria_auto, conservar_auto, jugar_partida)


def modo_consola():
    j1 = Jugador(input("Nombre jugador 1: ").strip() or "Jugador 1")
    j2 = Jugador(input("Nombre jugador 2: ").strip() or "Jugador 2")
    jugar_partida(j1, j2)


def modo_simulacion(n, semilla):
    rng = random.Random(semilla)
    puntajes, victorias_a, victorias_b, empates, bonos = [], 0, 0, 0, 0
    for _ in range(n):
        a = Jugador("A", conservar_auto, categoria_auto)
        b = Jugador("B", conservar_auto, categoria_auto)
        pa, pb, ganador = jugar_partida(a, b, rng, verbose=False)
        puntajes += [pa, pb]
        bonos += (a.bono_superior() > 0) + (b.bono_superior() > 0)
        if ganador == "A":
            victorias_a += 1
        elif ganador == "B":
            victorias_b += 1
        else:
            empates += 1

    print(f"Simulación Montecarlo: {n} partidas (bot vs bot, estrategia básica)")
    print(f"  Puntaje medio       : {statistics.mean(puntajes):.2f}")
    print(f"  Desviación estándar : {statistics.pstdev(puntajes):.2f}")
    print(f"  Mínimo / Máximo     : {min(puntajes)} / {max(puntajes)}")
    print(f"  Bono superior       : {100 * bonos / (2 * n):.1f}% de los jugadores")
    print(f"  Victorias A / B / empates: {victorias_a} / {victorias_b} / {empates}")


def main():
    p = argparse.ArgumentParser(description="Yahtzee + Montecarlo")
    p.add_argument("modo", nargs="?", default="gui", choices=["gui", "consola", "simular"])
    p.add_argument("-n", type=int, default=10000, help="partidas a simular")
    p.add_argument("--semilla", type=int, default=None, help="semilla aleatoria")
    args = p.parse_args()

    if args.modo == "gui":
        from gui import main as gui_main
        gui_main()
    elif args.modo == "consola":
        modo_consola()
    else:
        modo_simulacion(args.n, args.semilla)


if __name__ == "__main__":
    main()

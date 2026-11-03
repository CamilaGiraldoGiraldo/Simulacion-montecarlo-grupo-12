# -*- coding: utf-8 -*-
"""Interfaz gráfica del Yahtzee con tkinter (viene incluido con Python)."""

import random
import tkinter as tk
from tkinter import ttk

from yahtzee import (BONO_SUPERIOR, BONO_SUPERIOR_MIN, BONO_YAHTZEE, CARAS,
                     CATEGORIAS, MAX_LANZAMIENTOS, NUM_DADOS, SUPERIORES,
                     Jugador, es_yahtzee, joker_activo, lanzar_dados, relanzar)

# Puntos en cuadrícula 3x3 (0 = arriba izquierda, 8 = abajo derecha)
PUNTOS_DADO = {1: [4], 2: [0, 8], 3: [0, 4, 8], 4: [0, 2, 6, 8],
               5: [0, 2, 4, 6, 8], 6: [0, 2, 3, 5, 6, 8]}
TAM = 76


class JuegoVisual(tk.Tk):
    def __init__(self, rng=random, animar=True):
        super().__init__()
        self.title("Yahtzee para dos jugadores")
        self.rng = rng
        self.animar = animar
        self.nombres = ("Jugador 1", "Jugador 2")
        self.marco = ttk.Frame(self, padding=12)
        self.marco.pack(fill="both", expand=True)
        self._pantalla_inicio()

    def _limpiar(self):
        for w in self.marco.winfo_children():
            w.destroy()

    # ---------- Inicio ----------
    def _pantalla_inicio(self):
        self._limpiar()
        ttk.Label(self.marco, text="Yahtzee para dos jugadores",
                  font=("Arial", 16, "bold")).pack(pady=(0, 8))
        ttk.Label(self.marco, text="Escribe los nombres y pulsa «Empezar partida».").pack()
        self.in1 = tk.StringVar(value=self.nombres[0])
        self.in2 = tk.StringVar(value=self.nombres[1])
        for etiqueta, var in (("Jugador 1:", self.in1), ("Jugador 2:", self.in2)):
            f = ttk.Frame(self.marco)
            f.pack(pady=3)
            ttk.Label(f, text=etiqueta, width=10).pack(side="left")
            ttk.Entry(f, textvariable=var, width=25).pack(side="left")
        ttk.Button(self.marco, text="Empezar partida", command=self._empezar).pack(pady=10)

    def _empezar(self):
        n1 = self.in1.get().strip() or "Jugador 1"
        n2 = self.in2.get().strip() or "Jugador 2"
        if n1 == n2:
            n2 += " (2)"
        self.nombres = (n1, n2)
        self._nueva_partida()

    # ---------- Partida ----------
    def _nueva_partida(self):
        self.jugadores = [Jugador(self.nombres[0]), Jugador(self.nombres[1])]
        self.turno, self.ronda, self.lanzamiento = 0, 1, 0
        self.dados, self.historial = [], []
        self._limpiar()

        self.titulo = ttk.Label(self.marco, font=("Arial", 13, "bold"))
        self.titulo.pack(anchor="w")

        fila = ttk.Frame(self.marco)
        fila.pack(pady=8)
        self.canvas, self.keep, self.checks = [], [], []
        for i in range(NUM_DADOS):
            col = ttk.Frame(fila)
            col.pack(side="left", padx=6)
            c = tk.Canvas(col, width=TAM, height=TAM, highlightthickness=0)
            c.pack()
            v = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(col, text="Conservar", variable=v,
                                  command=lambda i=i: self._pintar_dado(i))
            chk.pack()
            self.canvas.append(c)
            self.keep.append(v)
            self.checks.append(chk)

        self.info = ttk.Label(self.marco, font=("Arial", 11))
        self.info.pack(anchor="w", pady=4)
        self.btn_lanzar = ttk.Button(self.marco, command=self._lanzar)
        self.btn_lanzar.pack(pady=4)

        fila2 = ttk.Frame(self.marco)
        fila2.pack(pady=4)
        ttk.Label(fila2, text="Categoría:").pack(side="left")
        self.combo = ttk.Combobox(fila2, state="disabled", width=36)
        self.combo.pack(side="left", padx=6)
        self.btn_anotar = ttk.Button(fila2, text="Anotar", state="disabled",
                                     command=self._anotar)
        self.btn_anotar.pack(side="left")

        self.tabla = ttk.Treeview(self.marco, columns=("c", "j1", "j2"),
                                  show="headings", height=len(CATEGORIAS) + 3)
        self.tabla.pack(pady=8, fill="x")
        self.tabla.column("c", width=230)
        self.tabla.column("j1", width=110, anchor="center")
        self.tabla.column("j2", width=110, anchor="center")

        self.hist = ttk.Label(self.marco, justify="left", font=("Arial", 9))
        self.hist.pack(anchor="w")
        self._nuevo_turno()

    @property
    def jugador(self):
        return self.jugadores[self.turno]

    # ---------- Dibujo ----------
    def _dibujar(self, i, valor, conservado=False):
        c = self.canvas[i]
        c.delete("all")
        borde = "#2e7d32" if conservado else "#555"
        fondo = "#e8f5e9" if conservado else "#ffffff"
        c.create_rectangle(3, 3, TAM - 3, TAM - 3, outline=borde,
                           width=4 if conservado else 2, fill=fondo)
        if valor is None:
            c.create_text(TAM / 2, TAM / 2, text="?", font=("Arial", 28), fill="#999")
            return
        for p in PUNTOS_DADO[valor]:
            x = 19 + (p % 3) * 19 + 0
            y = 19 + (p // 3) * 19 + 0
            c.create_oval(x - 6, y - 6, x + 6, y + 6, fill="#111", outline="")

    def _pintar_dado(self, i):
        valor = self.dados[i] if self.dados else None
        conservado = self.keep[i].get() and 0 < self.lanzamiento < MAX_LANZAMIENTOS
        self._dibujar(i, valor, conservado)

    def _refrescar_tabla(self):
        j1, j2 = self.jugadores
        self.tabla.heading("c", text="Categoría")
        self.tabla.heading("j1", text=("▶ " if self.turno == 0 else "") + j1.nombre)
        self.tabla.heading("j2", text=("▶ " if self.turno == 1 else "") + j2.nombre)
        self.tabla.delete(*self.tabla.get_children())
        for n, c in enumerate(CATEGORIAS):
            self.tabla.insert("", "end", values=(c, j1.puntos.get(c, "-"), j2.puntos.get(c, "-")))
            if n == len(SUPERIORES) - 1:
                self.tabla.insert("", "end", values=(
                    f"Subtotal superior ({BONO_SUPERIOR_MIN} = bono)",
                    f"{j1.subtotal_superior()}/{BONO_SUPERIOR_MIN}",
                    f"{j2.subtotal_superior()}/{BONO_SUPERIOR_MIN}"))
        self.tabla.insert("", "end", values=(f"Bono superior (+{BONO_SUPERIOR})",
                                             j1.bono_superior(), j2.bono_superior()))
        self.tabla.insert("", "end", values=(f"Bonos Yahtzee extra ({BONO_YAHTZEE} c/u)",
                                             BONO_YAHTZEE * j1.bonos_yahtzee,
                                             BONO_YAHTZEE * j2.bonos_yahtzee))
        self.tabla.insert("", "end", values=("TOTAL", j1.total(), j2.total()))

    def _refrescar_historial(self):
        ultimas = list(reversed(self.historial[-6:]))
        self.hist.config(text=("Últimas jugadas:\n" + "\n".join("• " + h for h in ultimas))
                         if ultimas else "")

    # ---------- Flujo ----------
    def _nuevo_turno(self):
        self.lanzamiento = 0
        self.dados = []
        for i in range(NUM_DADOS):
            self.keep[i].set(False)
            self.checks[i].state(["disabled"])
            self._pintar_dado(i)
        self.info.config(text="Pulsa «Lanzar». Después marca los dados a conservar "
                              "y relanza el resto.")
        self.btn_lanzar.config(state="normal", text=f"Lanzar ({MAX_LANZAMIENTOS} lanzamientos)")
        self.combo.set("")
        self.combo.config(values=[], state="disabled")
        self.btn_anotar.config(state="disabled")
        self.titulo.config(text=f"Ronda {self.ronda} de {len(CATEGORIAS)} — "
                                f"Turno de {self.jugador.nombre}")
        self._refrescar_tabla()
        self._refrescar_historial()

    def _lanzar(self):
        self.btn_lanzar.config(state="disabled")
        self.btn_anotar.config(state="disabled")
        primero = self.lanzamiento == 0
        conservar = set() if primero else {i for i, v in enumerate(self.keep) if v.get()}
        libres = [i for i in range(NUM_DADOS) if i not in conservar]
        pasos = 5 if self.animar else 0
        self._animar(libres, pasos, primero, conservar)

    def _animar(self, libres, pasos, primero, conservar):
        if pasos > 0:
            for i in libres:
                self._dibujar(i, random.randint(1, CARAS))
            self.after(60, self._animar, libres, pasos - 1, primero, conservar)
        else:
            self._terminar_lanzamiento(primero, conservar)

    def _terminar_lanzamiento(self, primero, conservar):
        if primero:
            self.dados = lanzar_dados(NUM_DADOS, self.rng)
        else:
            self.dados = relanzar(self.dados, conservar, self.rng)
        self.lanzamiento += 1

        restantes = MAX_LANZAMIENTOS - self.lanzamiento
        for i in range(NUM_DADOS):
            if restantes == 0:
                self.keep[i].set(False)
                self.checks[i].state(["disabled"])
            else:
                self.checks[i].state(["!disabled"])
            self._pintar_dado(i)

        if restantes == 0:
            self.btn_lanzar.config(text="Sin lanzamientos", state="disabled")
        else:
            self.btn_lanzar.config(text=f"Relanzar (quedan {restantes})", state="normal")

        aviso = ""
        if es_yahtzee(self.dados):
            if self.jugador.puntos.get("Yahtzee") == 50:
                aviso = "   ¡Yahtzee extra! +100 de bono y Joker."
            elif joker_activo(self.jugador.puntos, self.dados):
                aviso = "   ¡Yahtzee! Se aplica la regla del Joker."
            else:
                aviso = "   ¡YAHTZEE!"
        self.info.config(text=f"Lanzamiento {self.lanzamiento} de {MAX_LANZAMIENTOS}{aviso}")

        permitidas = sorted(self.jugador.categorias_permitidas(self.dados),
                            key=lambda c: -self.jugador.puntaje(self.dados, c))
        self.opciones = permitidas
        self.combo.config(values=[f"{c}  →  {self.jugador.puntaje(self.dados, c)} pts"
                                  for c in permitidas], state="readonly")
        self.combo.current(0)
        self.btn_anotar.config(state="normal")

    def _anotar(self):
        idx = self.combo.current()
        if idx < 0:
            return
        cat = self.opciones[idx]
        pts = self.jugador.anotar(self.dados, cat)
        self.historial.append(f"Ronda {self.ronda} · {self.jugador.nombre}: "
                              f"{self.dados} → {cat} ({pts} pts)")
        self.turno = 1 - self.turno
        if self.turno == 0:
            self.ronda += 1
        if self.ronda > len(CATEGORIAS):
            self._fin()
        else:
            self._nuevo_turno()

    def _fin(self):
        j1, j2 = self.jugadores
        p1, p2 = j1.total(), j2.total()
        res = (f"¡Gana {j1.nombre}!" if p1 > p2 else
               f"¡Gana {j2.nombre}!" if p2 > p1 else "¡Empate!")
        self._refrescar_tabla()
        self.titulo.config(text=f"Fin de la partida — {j1.nombre}: {p1} | {j2.nombre}: {p2} — {res}")
        self.info.config(text="")
        self.btn_lanzar.config(text="Nueva partida", state="normal",
                               command=self._pantalla_inicio)
        self.btn_anotar.config(state="disabled")
        self.combo.config(state="disabled")


def main():
    JuegoVisual().mainloop()


if __name__ == "__main__":
    main()

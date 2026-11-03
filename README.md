# Yahtzee + Simulación Montecarlo

Modelos y simulación – Ejercicio 1. Yahtzee para dos jugadores en Python,
con interfaz visual (como en Colab), modo consola y simulación Montecarlo.

## Requisitos
- Python 3.8 o superior
- Para la interfaz visual: `pip install -r requirements.txt`
- En VS Code: extensión **Jupyter** (y la de Python)

## Interfaz visual (dados, botones y tabla)
Abre `juego.ipynb` en VS Code, elige tu intérprete de Python (arriba a la derecha,
«Seleccionar kernel») y ejecuta las celdas en orden.

## Otros modos
```bash
python main.py consola                  # partida por consola
python main.py simular -n 10000         # Montecarlo (bot vs bot)
python main.py simular -n 20000 --semilla 42
python main.py                          # versión alternativa con tkinter
```

## Estructura
- `yahtzee.py`: reglas, puntajes, jugador y estrategias automáticas.
- `juego_visual.py`: interfaz visual con ipywidgets.
- `juego.ipynb`: notebook que lanza la interfaz visual.
- `gui.py`: interfaz alternativa con tkinter (sin notebook).
- `main.py`: punto de entrada y simulación Montecarlo.

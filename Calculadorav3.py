# Calculadora con historial persistente en JSON
import tkinter as tk
import ast
import operator as op
import json
import os

# ---------- CONFIGURACIÓN DEL ARCHIVO ----------
# Intentamos guardar el JSON en la misma carpeta del script; si falla usamos el directorio actual.
try:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
except NameError:
    BASE_DIR = os.getcwd()
HISTORIAL_FILE = os.path.join(BASE_DIR, "historial_calculadora.json")

# ---------- LÓGICA DE EVALUACIÓN SEGURA ----------
# Permitir solo operaciones aritméticas básicas
OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}

def safe_eval(expr):
    """
    Evalúa una expresión aritmética de forma segura usando ast.
    Soporta + - * / ** % y paréntesis. Lanza excepciones en caso de operaciones no permitidas.
    """
    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            else:
                raise ValueError("Valor no permitido")
        if isinstance(node, ast.Num):  # antiguas versiones de Python
            return node.n
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)
            if op_type in OPS:
                return OPS[op_type](left, right)
            else:
                raise ValueError("Operación no permitida")
        if isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            op_type = type(node.op)
            if op_type in OPS:
                return OPS[op_type](operand)
            else:
                raise ValueError("Operación unaria no permitida")
        if isinstance(node, ast.Call):
            raise ValueError("Llamadas no permitidas")
        raise ValueError("Expresión no permitida")
    parsed = ast.parse(expr, mode='eval')
    return _eval(parsed)

# ---------- HISTORIAL (cargado/guardado en JSON) ----------
historial = []            # lista de dicts: {"expr": ..., "result": ...}
history_index = None      # índice de navegación; None cuando no estamos navegando
MAX_HISTORY = None        # opcional: poner un número para limitar historial, e.g. 1000

def cargar_historial():
    global historial
    if os.path.exists(HISTORIAL_FILE):
        try:
            with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # validar estructura esperada (lista de objetos con expr y result)
                if isinstance(data, list):
                    cleaned = []
                    for item in data:
                        if isinstance(item, dict) and "expr" in item and "result" in item:
                            cleaned.append({"expr": item["expr"], "result": item["result"]})
                    historial = cleaned
        except Exception:
            # si hay un error al leer, simplemente dejamos historial vacío
            historial = []
    else:
        historial = []

def guardar_historial():
    """Escribe el historial actual en HISTORIAL_FILE (JSON)."""
    try:
        # aplicar límite si se definió MAX_HISTORY
        to_save = historial if not MAX_HISTORY else historial[-MAX_HISTORY:]
        with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
            json.dump(to_save, f, ensure_ascii=False, indent=2)
    except Exception as e:
        # no queremos que falle la app por un fallo de disco; opcionalmente podríamos loguear
        pass

# cargar historial al inicio
cargar_historial()

# ---------- INTERFAZ / FUNCIONES ----------
def click_boton(valor):
    global history_index
    # Si estábamos navegando por el historial, al empezar a escribir se resetea el índice
    history_index = None
    actual = str(pantalla.get())
    pantalla.delete(0, tk.END)
    pantalla.insert(0, actual + str(valor))

def limpiar():
    global history_index
    pantalla.delete(0, tk.END)
    history_index = None

def calcular():
    global history_index, historial
    operacion_original = pantalla.get()
    try:
        # Reemplazos para símbolos comunes
        operacion = operacion_original.replace("x", "*").replace("÷", "/")
        # Evaluación segura
        resultado = safe_eval(operacion)
        # Guardamos en el historial como dict
        entry = {"expr": operacion_original, "result": resultado}
        historial.append(entry)
        # aplicar límite si se definió
        if MAX_HISTORY and len(historial) > MAX_HISTORY:
            historial = historial[-MAX_HISTORY:]
        # guardar inmediatamente en disco
        guardar_historial()
        # Mostrar resultado en pantalla (sin .0 si es entero)
        if isinstance(resultado, float) and resultado.is_integer():
            pantalla.delete(0, tk.END)
            pantalla.insert(0, str(int(resultado)))
        else:
            pantalla.delete(0, tk.END)
            pantalla.insert(0, str(resultado))
        history_index = None
    except Exception:
        pantalla.delete(0, tk.END)
        pantalla.insert(0, "Error")

def borrar_uno():
    global history_index
    actual = pantalla.get()
    if actual:
        pantalla.delete(len(actual)-1, tk.END)
    history_index = None

def mostrar_historial(idx):
    """Muestra la entrada del historial en formato 'expr = resultado'."""
    item = historial[idx]
    pantalla.delete(0, tk.END)
    pantalla.insert(0, f"{item['expr']} = {item['result']}")

def historial_arriba():
    """Ir al elemento anterior del historial (↑)."""
    global history_index
    if not historial:
        return
    # Si no estábamos navegando, empezamos desde el final
    if history_index is None:
        history_index = len(historial) - 1
    else:
        if history_index > 0:
            history_index -= 1
    mostrar_historial(history_index)

def historial_abajo():
    """Ir al elemento siguiente del historial (↓)."""
    global history_index
    if not historial:
        return
    if history_index is None:
        # nada que mostrar hacia abajo si no comenzamos
        return
    else:
        if history_index < len(historial) - 1:
            history_index += 1
            mostrar_historial(history_index)
        else:
            # si pasamos del último, limpiamos la pantalla y salimos del modo historial
            history_index = None
            pantalla.delete(0, tk.END)

# ---------- INTERFAZ GRÁFICA ----------
ventana = tk.Tk()
ventana.title("Calculadora GOAT (con historial persistente)")
ventana.config(bg="#ff8777")

pantalla = tk.Entry(ventana, font=("Arial", 24), borderwidth=8, relief="ridge", justify="right", bg="#CAA3A3", fg="black")
pantalla.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="we")

# Definición de botones (texto, fila, columna)
botones = [
    ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("÷", 1, 3),
    ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("x", 2, 3),
    ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
    ("0", 4, 0), (".", 4, 1), ("=", 4, 2), ("+", 4, 3),
    ("↑", 5, 0), ("↓", 5, 1)
]

operadores = {"+", "-", "x", "÷"}

for (texto, fila, columna) in botones:
    if texto == "=":
        tk.Button(ventana, text=texto, width=10, height=2, font=("Arial", 14),
                  bg="#03627E", fg="white", command=calcular)\
            .grid(row=fila, column=columna, padx=5, pady=5)
    elif texto in operadores:
        tk.Button(ventana, text=texto, width=10, height=2, font=("Arial", 14),
                  bg="#45a056", fg="white", command=lambda t=texto: click_boton(t))\
            .grid(row=fila, column=columna, padx=5, pady=5)
    elif texto == "↑":
        tk.Button(ventana, text=texto, width=10, height=2, font=("Arial", 14),
                  bg="#f0c419", fg="black", command=historial_arriba)\
            .grid(row=fila, column=columna, padx=5, pady=5)
    elif texto == "↓":
        tk.Button(ventana, text=texto, width=10, height=2, font=("Arial", 14),
                  bg="#f0c419", fg="black", command=historial_abajo)\
            .grid(row=fila, column=columna, padx=5, pady=5)
    else:
        tk.Button(ventana, text=texto, width=10, height=2, font=("Arial", 14),
                  bg="#CAA3A3", fg="black", command=lambda t=texto: click_boton(t))\
            .grid(row=fila, column=columna, padx=5, pady=5)

# BOTÓN CE (backspace)
tk.Button(ventana, text="CE", width=10, height=2, font=("Arial", 14),
          bg="#0e604b", fg="white", command=borrar_uno)\
    .grid(row=5, column=2, padx=5, pady=5)

# BOTÓN AC (clear all)
tk.Button(ventana, text="AC", width=10, height=2, font=("Arial", 14),
          bg="#ff2c2c", fg="white", command=limpiar)\
    .grid(row=5, column=3, padx=5, pady=5)

# Ajuste de pesos para que la UI sea responsiva al cambiar tamaño
for c in range(4):
    ventana.grid_columnconfigure(c, weight=1)
ventana.grid_rowconfigure(0, weight=0)

# Guardar historial al cerrar la ventana
def on_closing():
    guardar_historial()
    ventana.destroy()

ventana.protocol("WM_DELETE_WINDOW", on_closing)

# Opcional: bindings de teclado básicos
def key_enter(event=None):
    calcular()

def key_backspace(event=None):
    borrar_uno()

def key_up(event=None):
    historial_arriba()

def key_down(event=None):
    historial_abajo()

ventana.bind("<Return>", key_enter)
ventana.bind("<BackSpace>", key_backspace)
ventana.bind("<Up>", key_up)
ventana.bind("<Down>", key_down)

ventana.mainloop()

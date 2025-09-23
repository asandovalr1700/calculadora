# Calculadora con historial persistente en JSON + memoria (MC, MR, M+, M-)
import tkinter as tk
import ast
import operator as op
import json
import os

# ---------- CONFIGURACIÓN DEL ARCHIVO ----------
try:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
except NameError:
    BASE_DIR = os.getcwd()
HISTORIAL_FILE = os.path.join(BASE_DIR, "historial_calculadora.json")

# ---------- LÓGICA DE EVALUACIÓN SEGURA ----------
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
    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            else:
                raise ValueError("Valor no permitido")
        if isinstance(node, ast.Num):
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

# ---------- HISTORIAL y MEMORIA (cargado/guardado en JSON) ----------
historial = []            # lista de dicts: {"expr": ..., "result": ...}
history_index = None
memory = 0.0              # valor de memoria
MAX_HISTORY = None        # opcional, e.g. 1000

def cargar_historial_y_memoria():
    global historial, memory
    if os.path.exists(HISTORIAL_FILE):
        try:
            with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Soportar dos formatos: antiguo (lista) y nuevo (dict con history+memory)
                if isinstance(data, list):
                    # formato antiguo: lista directamente
                    cleaned = []
                    for item in data:
                        if isinstance(item, dict) and "expr" in item and "result" in item:
                            cleaned.append({"expr": item["expr"], "result": item["result"]})
                    historial = cleaned
                    memory = 0.0
                elif isinstance(data, dict):
                    h = data.get("history", [])
                    cleaned = []
                    for item in h:
                        if isinstance(item, dict) and "expr" in item and "result" in item:
                            cleaned.append({"expr": item["expr"], "result": item["result"]})
                    historial = cleaned
                    mem_val = data.get("memory", 0.0)
                    try:
                        memory = float(mem_val)
                    except Exception:
                        memory = 0.0
                else:
                    historial = []
                    memory = 0.0
        except Exception:
            historial = []
            memory = 0.0
    else:
        historial = []
        memory = 0.0

def guardar_historial_y_memoria():
    try:
        to_save_history = historial if not MAX_HISTORY else historial[-MAX_HISTORY:]
        data = {"history": to_save_history, "memory": memory}
        with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        # no queremos crashear la app por un fallo de disco
        pass

# cargar al inicio
cargar_historial_y_memoria()

# ---------- HELPERS para UI y parsing ----------
def format_number_for_display(n):
    if isinstance(n, float) and n.is_integer():
        return str(int(n))
    return str(n)

def parse_display_value():
    """
    Intenta extraer un número del contenido actual de la pantalla.
    - Si es una expresión válida, intenta evaluarla (safe_eval).
    - Si es 'expr = result', toma result.
    - Si es un número literal, lo parsea.
    Lanza ValueError si no es posible.
    """
    text = pantalla.get().strip()
    if not text:
        raise ValueError("Pantalla vacía")
    # Si contiene '=' intentar tomar la parte derecha
    if "=" in text:
        parts = text.split("=")
        candidate = parts[-1].strip()
    else:
        candidate = text
    # Reemplazos de símbolos comunes
    candidate_eval = candidate.replace("x", "*").replace("÷", "/")
    # Intentar parsear como número directo
    try:
        if "." in candidate_eval:
            return float(candidate_eval)
        else:
            return int(candidate_eval)
    except Exception:
        # Intentar evaluar como expresión
        try:
            val = safe_eval(candidate_eval)
            return val
        except Exception:
            raise ValueError("No es un número válido")

# ---------- INTERFAZ / FUNCIONES ----------
def click_boton(valor):
    global history_index
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
        operacion = operacion_original.replace("x", "*").replace("÷", "/")
        resultado = safe_eval(operacion)
        entry = {"expr": operacion_original, "result": resultado}
        historial.append(entry)
        if MAX_HISTORY and len(historial) > MAX_HISTORY:
            historial = historial[-MAX_HISTORY:]
        guardar_historial_y_memoria()
        pantalla.delete(0, tk.END)
        pantalla.insert(0, format_number_for_display(resultado))
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
    item = historial[idx]
    pantalla.delete(0, tk.END)
    pantalla.insert(0, f"{item['expr']} = {format_number_for_display(item['result'])}")

def historial_arriba():
    global history_index
    if not historial:
        return
    if history_index is None:
        history_index = len(historial) - 1
    else:
        if history_index > 0:
            history_index -= 1
    mostrar_historial(history_index)

def historial_abajo():
    global history_index
    if not historial:
        return
    if history_index is None:
        return
    else:
        if history_index < len(historial) - 1:
            history_index += 1
            mostrar_historial(history_index)
        else:
            history_index = None
            pantalla.delete(0, tk.END)

# ---------- FUNCIONES DE MEMORIA ----------
def update_memory_label():
    """Actualiza el label que muestra el estado de la memoria."""
    # Mostrar 'M: 0' o 'M: 123' (sin .0 si entero)
    mem_label.config(text=f"Mem: {format_number_for_display(memory)}")

def mem_clear():
    global memory
    memory = 0.0
    guardar_historial_y_memoria()
    update_memory_label()

def mem_recall():
    # Inserta el valor de memoria en la pantalla (reemplaza contenido actual)
    pantalla.delete(0, tk.END)
    pantalla.insert(0, format_number_for_display(memory))

def mem_add():
    global memory
    try:
        val = parse_display_value()
        memory = float(memory) + float(val)
        guardar_historial_y_memoria()
        update_memory_label()
    except Exception:
        pantalla.delete(0, tk.END)
        pantalla.insert(0, "Error")

def mem_sub():
    global memory
    try:
        val = parse_display_value()
        memory = float(memory) - float(val)
        guardar_historial_y_memoria()
        update_memory_label()
    except Exception:
        pantalla.delete(0, tk.END)
        pantalla.insert(0, "Error")

# ---------- INTERFAZ GRÁFICA ----------
ventana = tk.Tk()
ventana.title("Calculadora GOAT (historial persistente + memoria)")
ventana.config(bg="#ff8777")

pantalla = tk.Entry(ventana, font=("Arial", 24), borderwidth=8, relief="ridge", justify="right", bg="#CAA3A3", fg="black")
pantalla.grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 2), sticky="we")

# Label para memoria
mem_label = tk.Label(ventana, text="", font=("Arial", 10), bg="#ff8777", anchor="w")
mem_label.grid(row=1, column=0, columnspan=4, sticky="w", padx=12)
update_memory_label()

# Definición de botones (texto, fila, columna)
botones = [
    ("7", 2, 0), ("8", 2, 1), ("9", 2, 2), ("÷", 2, 3),
    ("4", 3, 0), ("5", 3, 1), ("6", 3, 2), ("x", 3, 3),
    ("1", 4, 0), ("2", 4, 1), ("3", 4, 2), ("-", 4, 3),
    ("0", 5, 0), (".", 5, 1), ("=", 5, 2), ("+", 5, 3),
    ("↑", 6, 0), ("↓", 6, 1)
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
    .grid(row=6, column=2, padx=5, pady=5)

# BOTÓN AC (clear all)
tk.Button(ventana, text="AC", width=10, height=2, font=("Arial", 14),
          bg="#ff2c2c", fg="white", command=limpiar)\
    .grid(row=6, column=3, padx=5, pady=5)

# BOTONES DE MEMORIA (fila 7)
tk.Button(ventana, text="MC", width=10, height=2, font=("Arial", 12), bg="#8b0000", fg="white", command=mem_clear)\
    .grid(row=7, column=0, padx=5, pady=(5,10))
tk.Button(ventana, text="MR", width=10, height=2, font=("Arial", 12), bg="#8b0000", fg="white", command=mem_recall)\
    .grid(row=7, column=1, padx=5, pady=(5,10))
tk.Button(ventana, text="M+", width=10, height=2, font=("Arial", 12), bg="#8b0000", fg="white", command=mem_add)\
    .grid(row=7, column=2, padx=5, pady=(5,10))
tk.Button(ventana, text="M-", width=10, height=2, font=("Arial", 12), bg="#8b0000", fg="white", command=mem_sub)\
    .grid(row=7, column=3, padx=5, pady=(5,10))

# Ajuste de pesos para que la UI sea responsiva
for c in range(4):
    ventana.grid_columnconfigure(c, weight=1)
ventana.grid_rowconfigure(0, weight=0)

# Guardar historial+memoria al cerrar la ventana
def on_closing():
    guardar_historial_y_memoria()
    ventana.destroy()

ventana.protocol("WM_DELETE_WINDOW", on_closing)

# Bindings de teclado básicos
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

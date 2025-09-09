#LÓGICA DE LA CALCULADORA
import tkinter as tk #Se importa la librería Tkinter (librería estándar de Python para crear interfaces gráficas) con el alías tk
historial = [] #Lista para guardar el historial
def click_boton(valor):
    actual = str(pantalla.get()) #Obtiene lo que ya está en la pantalla
    pantalla.delete(0, tk.END) #Borra la pantalla
    pantalla.insert(0, actual + str(valor)) #Vuelve a escribir lo que tenía más el nuevo valor para ir construyendo la operación

def limpiar():
    pantalla.delete(0, tk.END) #All Clean que borra todo lo que hay en la pantalla

def calcular():  # evalúa la expresión matemática
    try:
        operacion = pantalla.get()
        # Reemplazamos símbolos por los que entiende Python
        operacion = operacion.replace("x", "*").replace("÷", "/")
        resultado = eval(operacion)
        historial.append(f"{pantalla.get()} = {resultado}")  # guardamos con los símbolos originales
        pantalla.delete(0, tk.END)
        pantalla.insert(0, str(resultado))
    except:
        pantalla.delete(0, tk.END)
        pantalla.insert(0, "Error")
        
def borrar_uno():
    actual = pantalla.get()
    if actual:  # Si no está vacío
        pantalla.delete(len(actual)-1, tk.END)

#VENTANA PRINCIPAL
ventana = tk.Tk() #crea la ventana principal.
ventana.title("Calculadora GOAT") #le pone título a la ventana
ventana.config(bg="#ff8777")  # fondo rosa 

#PANTALLA 
pantalla = tk.Entry(ventana, font=("Arial", 24), borderwidth=8, relief="ridge", justify="right", bg="#CAA3A3", fg="black")
pantalla.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

#LISTA DE BOTONES
botones = [
    ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("÷", 1, 3),
    ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("x", 2, 3),
    ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
    ("0", 4, 0), (".", 4, 1), ("=", 4, 2), ("+", 4, 3),
    ("↑", 5, 0), ("↓", 5, 1) 
]

#CREACIÓN DE BOTONES
operadores = {"+", "-", "x", "÷"}

for (texto, fila, columna) in botones:
    if texto == "=":
        #Botón "=" → azul 
        tk.Button(ventana, text=texto, width=10, height=2, font=("Arial", 14), 
                  bg="#03627E", fg="white", command=calcular)\
            .grid(row=fila, column=columna, padx=5, pady=5)
    elif texto in operadores:
        #Botones de operación
        tk.Button(ventana, text=texto, width=10, height=2, font=("Arial", 14),
                  bg="#45a056", fg="white", command=lambda t=texto: click_boton(t))\
            .grid(row=fila, column=columna, padx=5, pady=5)
    else:
        #Botones de números y punto
        tk.Button(ventana, text=texto, width=10, height=2, font=("Arial", 14),
                  bg="#CAA3A3", fg="black", command=lambda t=texto: click_boton(t))\
            .grid(row=fila, column=columna, padx=5, pady=5)
            
#BOTÓN DE ALL CLEAN
tk.Button(ventana, text="AC", width=10, height=2, font=("Arial", 14),
          bg="#ff2c2c", fg="white", command=limpiar)\
    .grid(row=5, column=3, columnspan=4, padx=5, pady=5)
    
#BOTÓN BACKSPACE O CLEAR ENTRY PARA LOS CUATES
tk.Button(ventana, text="CE", width=10, height=2, font=("Arial", 14),
          bg="#0e604b", fg="white", command=borrar_uno)\
    .grid(row=5, column=1, columnspan=3, padx=5, pady=5)
    
#CICLO PRINCIPAL
ventana.mainloop() #Hace que la ventana se quede abierta y responda a los clics en los botones. Sin esto, la ventana se cerraría inmediatamente al ejecutar el programa
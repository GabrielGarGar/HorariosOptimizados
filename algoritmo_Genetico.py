import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import random
import unicodedata

class HorarioGenetico:
    def __init__(self, materias, poblacion_size, Pcruce, Pmuta, iteraciones):
        self.materias = materias  # Diccionario con materias y sus horarios posibles
        self.poblacion_size = max(poblacion_size, 50)  # Asegurar un mínimo de 20 individuos
        self.Pcruce = Pcruce
        self.Pmuta = Pmuta
        self.iteraciones = max(iteraciones, 1000)  # Asegurar un mínimo de 500 iteraciones
        self.poblacion = self.inicializar_poblacion()
    
    def inicializar_poblacion(self):
        return [np.array([np.random.randint(0, len(self.materias[materia])) for materia in self.materias]) for _ in range(self.poblacion_size)]
    
    def convertir_a_intervalo(self, bloque):
        dias_semana = {
            "lunes": "Lunes", "martes": "Martes", "miércoles": "Miércoles", "miercoles": "Miércoles",
            "jueves": "Jueves", "viernes": "Viernes", "sábado": "Sábado", "sabado": "Sábado", "domingo": "Domingo"
        }
        try:
            partes = bloque.lower().split(" ")
            if len(partes) != 2:
                return None
            dia, horas = partes
            dia = dias_semana.get(unicodedata.normalize('NFKD', dia).encode('ASCII', 'ignore').decode('ASCII'), None)
            if dia is None:
                return None
            hora_inicio, hora_fin = map(int, horas.split("-"))
            return dia, (hora_inicio, hora_fin)
        except ValueError:
            return None
    
    def evaluar_fitness(self, individuo):
        penalizacion = 0
        horarios_usados = {}
        
        for i, materia in enumerate(self.materias.keys()):
            horario = self.materias[materia][individuo[i]]
            
            for bloque in horario:
                resultado = self.convertir_a_intervalo(bloque)
                if resultado is None:
                    continue
                dia, intervalo = resultado
                
                if dia in horarios_usados:
                    for intervalo_existente in horarios_usados[dia]:
                        if not (intervalo[1] <= intervalo_existente[0] or intervalo[0] >= intervalo_existente[1]):
                            penalizacion += 1
                    horarios_usados[dia].append(intervalo)
                else:
                    horarios_usados[dia] = [intervalo]
        
        return -penalizacion
    
    def seleccion(self, fitness):
        probabilidades = np.exp(fitness) / np.sum(np.exp(fitness))
        return self.poblacion[np.random.choice(range(self.poblacion_size), p=probabilidades)]
    
    def cruce(self, padre1, padre2):
        if np.random.rand() < self.Pcruce and len(padre1) > 1:
            punto = np.random.randint(1, len(padre1))
            return np.concatenate((padre1[:punto], padre2[punto:])), np.concatenate((padre2[:punto], padre1[punto:]))
        return padre1, padre2
    
    def mutacion(self, individuo):
        for i in range(len(individuo)):
            if np.random.rand() < self.Pmuta:
                individuo[i] = np.random.randint(0, len(self.materias[list(self.materias.keys())[i]]))
        return individuo
    
    def evolucionar(self):
        mejor_fitness = -np.inf
        mejor_individuo = None
        for _ in range(self.iteraciones):
            fitness = np.array([self.evaluar_fitness(ind) for ind in self.poblacion])
            nueva_poblacion = []
            
            for _ in range(self.poblacion_size // 2):
                padre1, padre2 = self.seleccion(fitness), self.seleccion(fitness)
                hijo1, hijo2 = self.cruce(padre1, padre2)
                nueva_poblacion.extend([self.mutacion(hijo1), self.mutacion(hijo2)])
            
            self.poblacion = nueva_poblacion[:self.poblacion_size]
            
            max_fitness = np.max(fitness)
            if max_fitness > mejor_fitness:
                mejor_fitness = max_fitness
                mejor_individuo = self.poblacion[np.argmax(fitness)]
            
            if mejor_fitness == 0:
                break
        
        return mejor_individuo

def actualizar_lista_materias():
    lista_materias.delete(0, tk.END)
    for materia in materias.keys():
        lista_materias.insert(tk.END, materia)
    actualizar_lista_horarios()

def actualizar_lista_horarios():
    lista_horarios.delete(0, tk.END)
    for materia, horarios in materias.items():
        for horario in horarios:
            lista_horarios.insert(tk.END, f"{materia}: {horario}")

def abrir_ventana_horarios():
    seleccion = lista_materias.curselection()
    if not seleccion:
        messagebox.showerror("Error", "Debe seleccionar una materia de la lista.")
        return
    
    materia_seleccionada = lista_materias.get(seleccion)
    
    ventana_horarios = tk.Toplevel(root)
    ventana_horarios.title(f"Ingreso de Horarios para {materia_seleccionada}")
    ventana_horarios.geometry("600x400")  # Ajustar el tamaño de la ventana
    
    tk.Label(ventana_horarios, text="Horarios (separados por coma, bloques por punto y coma):").grid(row=0, column=0)
    entry_horarios = tk.Entry(ventana_horarios)
    entry_horarios.grid(row=0, column=1)
    
    def guardar_horarios():
        horarios = entry_horarios.get().split(",")
        if horarios:
            materias[materia_seleccionada] = [tuple(h.split(";")) for h in horarios]
            ventana_horarios.destroy()
            actualizar_lista_horarios()
        else:
            messagebox.showerror("Error", "Debe ingresar al menos un bloque de horario.")
    
    tk.Button(ventana_horarios, text="Guardar Horarios", command=guardar_horarios).grid(row=1, column=0, columnspan=2)

def agregar_materia():
    materia = entry_materia.get()
    profesor = entry_profesor.get()
    
    if materia and profesor:
        nombre_completo = f"{materia} - {profesor}"
        materias[nombre_completo] = []
        entry_materia.delete(0, tk.END)
        entry_profesor.delete(0, tk.END)
        actualizar_lista_materias()
    else:
        messagebox.showerror("Error", "Todos los campos deben ser completados.")

def mostrar_horario():
    root = tk.Tk()
    root.title("Horario Optimizado")
    root.geometry("1000x800")  # Ajustar el tamaño de la ventana
    
    columnas = ["Hora", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    tree = ttk.Treeview(root, columns=columnas, show="headings", height=20)  # Ajustar la altura de la tabla
    
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    
    horas = [f"{h}:00" for h in range(7, 23)]
    horario_tabla = {hora: {dia: "---" for dia in columnas[1:]} for hora in horas}
    
    for i, materia in enumerate(materias.keys()):
        for bloque in materias[materia][mejor_horario[i]]:
            resultado = HorarioGenetico.convertir_a_intervalo(None, bloque)
            if resultado is None:
                continue
            dia, (inicio, fin) = resultado
            for h in range(inicio, fin):
                if 7 <= h < 23:  # Asegurarse de que las horas estén dentro del rango de 7 a 22
                    horario_tabla[f"{h}:00"][dia] = materia
    
    for hora in horas:
        tree.insert("", "end", values=[hora] + [horario_tabla[hora][dia] for dia in columnas[1:]])
    
    tree.pack(expand=True, fill=tk.BOTH)  # Asegurarse de que la tabla se expanda y llene la ventana
    root.mainloop()

def ejecutar_algoritmo():
    global mejor_horario
    genetico = HorarioGenetico(materias, poblacion_size=10, Pcruce=0.8, Pmuta=0.1, iteraciones=500)
    mejor_horario = genetico.evolucionar()
    mostrar_horario()

# Inicializar interfaz de ingreso de materias
materias = {
    "Matemáticas - Prof. Pérez": [("lunes 7-9", "martes 9-11"), ("miércoles 7-9", "jueves 9-11")],
    "Física - Prof. García": [("lunes 9-11", "martes 11-13"), ("miércoles 9-11", "jueves 11-13")],
    "Química - Prof. López": [("viernes 7-9", "sábado 9-11"), ("viernes 11-13", "sábado 13-15")],
    "Biología - Prof. Rodríguez": [("lunes 11-13", "martes 13-15"), ("miércoles 11-13", "jueves 13-15")],
    "Historia - Prof. Martínez": [("viernes 9-11", "sábado 11-13"), ("viernes 12-14", "sábado 14-15")],
    "Geografía - Prof. Sánchez": [("lunes 13-15", "martes 15-17"), ("miércoles 13-15", "jueves 15-17")],
    "Literatura - Prof. Gómez": [("viernes 15-17", "sábado 17-19"), ("viernes 17-19", "sábado 19-21")]
}

root = tk.Tk()
root.title("Ingreso de Materias")
root.geometry("600x400")  # Ajustar el tamaño de la ventana

tk.Label(root, text="Materia:").grid(row=0, column=0)
entry_materia = tk.Entry(root)
entry_materia.grid(row=0, column=1)

tk.Label(root, text="Profesor:").grid(row=1, column=0)
entry_profesor = tk.Entry(root)
entry_profesor.grid(row=1, column=1)

tk.Button(root, text="Agregar Materia", command=agregar_materia).grid(row=2, column=0)
tk.Button(root, text="Ingresar Horarios", command=abrir_ventana_horarios).grid(row=2, column=1)
tk.Button(root, text="Generar Horario", command=ejecutar_algoritmo).grid(row=3, column=0, columnspan=2)

# Lista de materias agregadas
tk.Label(root, text="Materias ingresadas:").grid(row=4, column=0, columnspan=2)
lista_materias = tk.Listbox(root, height=10, width=50)
lista_materias.grid(row=5, column=0, columnspan=2)

# Lista de horarios ingresados
tk.Label(root, text="Horarios ingresados:").grid(row=6, column=0, columnspan=2)
lista_horarios = tk.Listbox(root, height=10, width=50)
lista_horarios.grid(row=7, column=0, columnspan=2)

# Actualizar las listas con los datos predeterminados
actualizar_lista_materias()

root.mainloop()

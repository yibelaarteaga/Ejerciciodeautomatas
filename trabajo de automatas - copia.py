
from tkinter import *
from tkinter import simpledialog
import pulp
import statistics

# Función para ejecutar la optimización y mostrar los resultados en la ventana
def ejecutar_optimizacion():
    # Limpiar el cuadro de resultados
    text_resultados.delete(1.0, END)

    # Obtener el texto del cuadro de texto con los datos ingresados
    datos_salones = text_salones.get("1.0", END).strip()

    # Procesar los datos para obtener los salones y sus capacidades
    salones = {}
    for linea in datos_salones.splitlines():
        try:
            nombre_salon, capacidad = linea.split(":")
            nombre_salon = nombre_salon.strip()
            capacidad = int(capacidad.strip())
            if capacidad > 65:
                capacidad = 65  # Limitar la capacidad a 65
            salones[nombre_salon] = capacidad
        except ValueError:
            text_resultados.insert(END, f"Error al procesar la línea: {linea}\n")
            continue

    # Mostrar los nombres y capacidades de los salones en el cuadro de texto
    text_resultados.insert(END, "Salones ingresados y sus capacidades:\n")
    for salon, capacidad in salones.items():
        text_resultados.insert(END, f"{salon}: {capacidad} estudiantes de capacidad\n")
    text_resultados.insert(END, "\n")

    # Solicitar al usuario que ingrese el número total de estudiantes a distribuir
    try:
        total_estudiantes = int(entry_total_estudiantes.get())
    except ValueError:
        text_resultados.insert(END, "Por favor, ingresa un número válido de estudiantes.\n")
        return

    # Calcular la capacidad total de los salones ingresados
    capacidad_total_salones = sum(salones.values())

    # Verificar si la capacidad total de los salones es suficiente
    if total_estudiantes > capacidad_total_salones:
        text_resultados.insert(END, "La capacidad actual de los salones no es suficiente.\n")
        text_resultados.insert(END, "Se agregarán automáticamente nuevos salones para satisfacer la demanda.\n")
        
        # Agregar salones adicionales automáticamente hasta cubrir la demanda
        num_nuevos_salones = 1
        while capacidad_total_salones < total_estudiantes:
            nuevo_salon = f"Salon_Extra_{num_nuevos_salones}"
            salones[nuevo_salon] = 65  # Capacidad máxima permitida por salón
            capacidad_total_salones += 65
            num_nuevos_salones += 1
        
        text_resultados.insert(END, f"Se han agregado {num_nuevos_salones - 1} salones adicionales con capacidad de 65 estudiantes cada uno.\n")

    # Inicializamos el problema de optimización (minimización)
    problem = pulp.LpProblem("Optimización_Distribución_Estudiantes", pulp.LpMinimize)

    # Variables de decisión: número de estudiantes asignados a cada salón
    x = pulp.LpVariable.dicts("Asignación", salones.keys(), lowBound=0, upBound=65, cat='Integer')

    # Variables binarias para indicar si un salón es utilizado o no
    y = pulp.LpVariable.dicts("Uso_Salon", salones.keys(), cat='Binary')

    # Restricción de asignación: la suma total de estudiantes asignados no debe exceder el número total de estudiantes
    problem += pulp.lpSum(x[salon] for salon in salones) == total_estudiantes, "Total_Estudiantes"

    # Restricción de capacidad: ningún salón puede tener más estudiantes de los que permite su capacidad
    for salon in salones:
        problem += x[salon] <= salones[salon], f"Capacidad_{salon}"
        # Relacionar la variable de uso con la asignación
        problem += x[salon] <= y[salon] * salones[salon], f"Uso_{salon}"

    # Función objetivo: minimizar el número de salones usados
    problem += pulp.lpSum(y[salon] for salon in salones), "Minimizar_Salones"

    # Resolución del problema
    problem.solve()

    # Mostrar resultados
    text_resultados.insert(END, f"\nEstado de la optimización: {pulp.LpStatus[problem.status]}\n\n")
    text_resultados.insert(END, "Asignación óptima de estudiantes a salones:\n")
    for salon in salones:
        if x[salon].varValue > 0:
            text_resultados.insert(END, f"{salon}: {int(x[salon].varValue)} estudiantes asignados (capacidad: {salones[salon]})\n")

    text_resultados.insert(END, "\nResumen de distribución:\n")
    total_asignado = sum(int(x[salon].varValue) for salon in salones)
    text_resultados.insert(END, f"Total de estudiantes asignados: {total_asignado} de {total_estudiantes}\n")
    
    # Análisis de datos y recomendaciones
    text_resultados.insert(END, "\nAnálisis de datos:\n")
    capacidades = list(salones.values())
    if capacidades:
        promedio_capacidad = statistics.mean(capacidades)
        desviacion_estandar = statistics.stdev(capacidades) if len(capacidades) > 1 else 0
        text_resultados.insert(END, f"Promedio de capacidad de los salones: {promedio_capacidad:.2f}\n")
        text_resultados.insert(END, f"Desviación estándar de la capacidad de los salones: {desviacion_estandar:.2f}\n")
    
    text_resultados.insert(END, "\nRecomendaciones:\n")
    if total_estudiantes > capacidad_total_salones:
        text_resultados.insert(END, "Se recomienda aumentar el número de salones o la capacidad de los salones existentes.\n")
    else:
        text_resultados.insert(END, "La capacidad actual de los salones es suficiente para acomodar a todos los estudiantes.\n")
    
    if desviacion_estandar > 10:
        text_resultados.insert(END, "Se recomienda revisar la distribución de capacidades de los salones para reducir la variabilidad.\n")
    else:
        text_resultados.insert(END, "La distribución de capacidades de los salones es adecuada.\n")

# Crear la ventana principal de Tkinter
raiz = Tk()
raiz.title("Optimización de la Distribución de Estudiantes en Salones de Clases V1.0")
raiz.resizable(True, True)
raiz.geometry("810x650")
raiz.config(bg="#F5E8E4")  # color de fondo

# Configurar tipo de letra
font_label = ("Helvetica", 12, "bold")
font_entry = ("Helvetica", 12)
font_result = ("Helvetica", 14, "italic")

# Etiquetas y entradas de texto con grid
Label(raiz, text="Número total de estudiantes:", bg="#F5E8E4", fg="#4B4453", font=font_label).grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_total_estudiantes = Entry(raiz, font=font_entry)
entry_total_estudiantes.grid(row=0, column=1, padx=10, pady=5, sticky="w")

# Etiqueta y cuadro de texto para que el usuario ingrese los salones y sus capacidades
Label(raiz, text="Ingrese los salones y capacidades (Formato: Salon1: 30)", bg="#F5E8E4", fg="#4B4453", font=font_label).grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="n")
text_salones = Text(raiz, width=50, height=10, font=font_entry)
text_salones.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

# Botón para ejecutar la optimización
Button(raiz, text="Ejecutar Optimización", command=ejecutar_optimizacion, font=font_label, bg="#E8DFF5", fg="#4B4453").grid(row=3, column=0, columnspan=2, pady=10)

# Cuadro de texto para mostrar los resultados centrados
text_resultados = Text(raiz, width=70, height=20, font=font_result, bg="#FFFFFF", fg="#4B4453")
text_resultados.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Ejecutar el bucle principal de la ventana
raiz.mainloop()



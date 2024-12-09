# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 12:17:46 2024

@author: jared
"""
from experta import *

# Función para conectar a la base de datos
import pymysql

def conectar_bd():
    return pymysql.connect(
        host="localhost",
        user="root",  # Cambiar si tienes otro usuario
        password="",  # Cambiar si tienes
        port= 3306,
        database="sistema experto"
    )

# Función para obtener la rutina desde la base de datos
def obtener_rutina(objetivo, nivel, dias_necesarios):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    query = """
    SELECT descripcion FROM Rutinas
    WHERE objetivo = %s AND nivel = %s AND dias_necesarios = %s
    """
    cursor.execute(query, (objetivo, nivel, dias_necesarios))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado[0] if resultado else None

# Función para excluir ejercicios en caso de lesiones
def ejercicios_por_lesion(lesion):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    query = """
    SELECT nombre FROM Ejercicios
    WHERE lesiones_evitar LIKE %s
    """
    cursor.execute(query, (f"%{lesion}%",))
    resultados = cursor.fetchall()
    conexion.close()
    return [ejercicio[0] for ejercicio in resultados]

# Motor de inferencia
class SistemaEntrenador(KnowledgeEngine):
    
    # Declaración de hechos iniciales
    @DefFacts()
    def hechos_iniciales(self):
        yield Fact("Sistema de entrenamiento iniciado")

    # Reglas para evaluar objetivo, nivel y días disponibles
    @Rule(
        Fact(objetivo=MATCH.objetivo),
        Fact(nivel=MATCH.nivel),
        Fact(dias_disponibles=MATCH.dias_disponibles),
       NOT( Fact(lesion=MATCH.lesion))
    )
    def recomendar_rutina_sin_lesion(self, objetivo, nivel, dias_disponibles):
        rutina = obtener_rutina(objetivo, nivel, dias_disponibles)
        if rutina:
            print(f"\nRutina recomendada:\n{rutina}")
            
        else:
            print("\nNo hay rutinas disponibles para tus necesidades.")

    # Regla para evaluar si hay lesiones y manejar ejercicios a evitar
    @Rule(
        Fact(objetivo=MATCH.objetivo),
        Fact(nivel=MATCH.nivel),
        Fact(dias_disponibles=MATCH.dias_disponibles),
        Fact(lesion=MATCH.lesion))
    def manejar_lesion(self, objetivo, nivel, dias_disponibles, lesion):
        ejercicios_excluidos = ejercicios_por_lesion(lesion)
        rutina = obtener_rutina(objetivo, nivel, dias_disponibles)
        
        # Mostrar la rutina sin importar la lesión
        #rutina = obtener_rutina(MATCH.objetivo, MATCH.nivel, MATCH.dias_disponibles)
        if rutina:
            print(f"\nRutina recomendada:\n{rutina}")
        else:
            print("\nNo hay rutinas disponibles para tus necesidades.")
        
        # Mostrar los ejercicios a evitar debido a la lesión
        if ejercicios_excluidos:
            print(f"\nEjercicios a evitar debido a la lesión ({lesion}):")
            print(", ".join(ejercicios_excluidos))
        else:
            print(f"\nNo se encontraron ejercicios específicos para evitar con la lesión ({lesion}).")



if __name__ == "__main__":
    print("Bienvenido al sistema experto de entrenamiento personalizado.\n")

    while True:  # Bucle para ejecutar el sistema repetidamente
        # Solicitar datos al usuario
        objetivo = input(
            "Introduce 'salir' para terminar\nIntroduce tu objetivo (hipertrofia, perdida_grasa, resistencia): "
        ).strip().lower()

        if objetivo == "salir":  # Condición de salida del bucle
            print("Gracias por usar el sistema experto. ¡Hasta luego!")
            break

        nivel = input("Introduce tu nivel (principiante, intermedio, avanzado): ").strip().lower()
        dias_disponibles = int(input("¿Cuántos días puedes entrenar a la semana? "))
        lesion = input(
            "(lesiones comunes o a evitar - *Hombro* *Rodilla* *Muñeca* *Espalda baja* )\n"
            "¿Tienes alguna lesión? (Deja vacío si no tienes): "
        ).strip().lower()

        # Crear y ejecutar el sistema experto
        sistema = SistemaEntrenador()
        sistema.reset()

        # Declarar los hechos según los datos proporcionados
        sistema.declare(Fact(objetivo=objetivo))
        sistema.declare(Fact(nivel=nivel))
        sistema.declare(Fact(dias_disponibles=dias_disponibles))
        if lesion:
            sistema.declare(Fact(lesion=lesion))

        # Ejecutar el motor de inferencia
        sistema.run()

        print("\n---\n")  # Separador entre ejecuciones para mejor legibilidad

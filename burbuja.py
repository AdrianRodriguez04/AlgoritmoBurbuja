import tkinter as tk
from tkinter import messagebox
import random
import time
from threading import Thread
import mysql.connector
from mysql.connector import Error

class BubbleSortApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ordenamiento de Burbuja con Animación")
        self.root.geometry("800x600")
        
        # Variables
        self.numbers = []
        self.sorting = False
        self.speed = 100  # Velocidad de animación (ms)
        self.db_connection = self.create_db_connection()
        
        # Crear interfaz
        self.create_widgets()
        
    def create_db_connection(self):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='Cortana33',
                database='burbuja',
                auth_plugin='mysql_native_password'
            )
            print("Conexión a BD establecida correctamente")
            return connection
        except Error as e:
            messagebox.showerror("Error de BD", f"No se pudo conectar a MySQL: {e}")
            print(f"Error de conexión: {e}")
            return None
        
    def save_to_database(self, original, sorted_list):
        print(f"Intentando guardar: {original} -> {sorted_list}")  # Debug
        if self.db_connection is None:
            print("Error: No hay conexión a BD")
            return
            
        try:
            cursor = self.db_connection.cursor()
            query = "INSERT INTO intentos_ordenamiento (intento, resultados) VALUES (%s, %s)"
            cursor.execute(query, (str(original), str(sorted_list)))
            self.db_connection.commit()
            cursor.close()
            print("Datos guardados correctamente en BD")
            self.status.set("Resultados guardados en la base de datos")
        except Error as e:
            messagebox.showerror("Error de BD", f"No se pudo guardar: {e}")
            print(f"Error al guardar: {e}")
    
    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de entrada
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Etiqueta y entrada para números
        tk.Label(input_frame, text="Ingrese números separados por comas:").pack(side=tk.LEFT)
        self.entry = tk.Entry(input_frame, width=40)
        self.entry.pack(side=tk.LEFT, padx=5)
        
        # Botón para agregar números
        add_btn = tk.Button(input_frame, text="Agregar", command=self.add_numbers)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame de botones
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botón para generar números aleatorios
        random_btn = tk.Button(btn_frame, text="Generar 20 números aleatorios", 
                              command=self.generate_random_numbers)
        random_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón para ordenar
        sort_btn = tk.Button(btn_frame, text="Ordenar", 
                             command=self.start_sorting_thread)
        sort_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón para reiniciar
        reset_btn = tk.Button(btn_frame, text="Reiniciar", 
                             command=self.reset)
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Control de velocidad
        speed_frame = tk.Frame(btn_frame)
        speed_frame.pack(side=tk.LEFT, padx=20)
        tk.Label(speed_frame, text="Velocidad:").pack(side=tk.LEFT)
        self.speed_scale = tk.Scale(speed_frame, from_=10, to=500, orient=tk.HORIZONTAL,
                                   command=self.set_speed)
        self.speed_scale.set(self.speed)
        self.speed_scale.pack(side=tk.LEFT)
        
        # Canvas para visualización
        self.canvas = tk.Canvas(main_frame, bg="white", height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Barra de estado
        self.status = tk.StringVar()
        self.status.set("Listo. Ingrese números o genere aleatorios.")
        status_bar = tk.Label(main_frame, textvariable=self.status, 
                             bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X)
    
    def set_speed(self, val):
        self.speed = int(val)
    
    def add_numbers(self):
        if self.sorting:
            messagebox.showwarning("Advertencia", "Espere a que termine el ordenamiento actual")
            return
            
        input_str = self.entry.get()
        try:
            new_numbers = [int(num.strip()) for num in input_str.split(",") if num.strip()]
            self.numbers.extend(new_numbers)
            self.entry.delete(0, tk.END)
            self.draw_numbers()
            self.status.set(f"Se agregaron {len(new_numbers)} números. Total: {len(self.numbers)}")
        except ValueError:
            messagebox.showerror("Error", "Ingrese solo números separados por comas")
    
    def generate_random_numbers(self):
        if self.sorting:
            messagebox.showwarning("Advertencia", "Espere a que termine el ordenamiento actual")
            return
            
        self.numbers = [random.randint(1, 100) for _ in range(20)]
        self.draw_numbers()
        self.status.set(f"Se generaron 20 números aleatorios")
    
    def reset(self):
        if self.sorting:
            messagebox.showwarning("Advertencia", "Espere a que termine el ordenamiento actual")
            return
            
        self.numbers = []
        self.canvas.delete("all")
        self.status.set("Listo. Ingrese números o genere aleatorios.")
    
    def draw_numbers(self, highlights=None):
        self.canvas.delete("all")
        if not self.numbers:
            return
            
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        max_num = max(self.numbers) if self.numbers else 1
        bar_width = canvas_width / len(self.numbers)
        
        if highlights is None:
            highlights = []
        
        for i, num in enumerate(self.numbers):
            # Calcular posición y tamaño de la barra
            x0 = i * bar_width
            y0 = canvas_height
            x1 = (i + 1) * bar_width
            y1 = canvas_height - (num / max_num) * (canvas_height - 20)
            
            # Color de la barra (rojo si está siendo comparada)
            color = "red" if i in highlights else "blue"
            
            # Dibujar la barra
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")
            
            # Mostrar el valor numérico
            self.canvas.create_text(x0 + bar_width/2, y1 - 10, text=str(num))
        
        self.canvas.update()
    
    def bubble_sort(self):
        if self.sorting:
            return
            
        if not self.numbers:
            messagebox.showwarning("Advertencia", "No hay números para ordenar")
            return
            
        self.sorting = True
        n = len(self.numbers)
        swapped = True
        
        # Guardar copia del estado original ANTES de ordenar
        original_numbers = self.numbers.copy()
        
        self.status.set("Ordenando...")
        
        while swapped:
            swapped = False
            for i in range(n - 1):
                if not self.sorting:
                    return
                    
                self.draw_numbers([i, i+1])
                time.sleep(self.speed / 1000)
                
                if self.numbers[i] > self.numbers[i + 1]:
                    self.numbers[i], self.numbers[i + 1] = self.numbers[i + 1], self.numbers[i]
                    swapped = True
                    self.draw_numbers([i, i+1])
                    time.sleep(self.speed / 1000)
        
        # Guardar en BD: original_numbers (desordenado) y self.numbers (ordenado)
        self.save_to_database(original_numbers, self.numbers.copy())
        
        self.sorting = False
        self.status.set("Ordenamiento completado!")
        self.draw_numbers()
    
    def start_sorting_thread(self):
        if not self.sorting:
            thread = Thread(target=self.bubble_sort)
            thread.daemon = True
            thread.start()

    def __del__(self):
        if hasattr(self, 'db_connection') and self.db_connection:
            self.db_connection.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = BubbleSortApp(root)
    root.mainloop()
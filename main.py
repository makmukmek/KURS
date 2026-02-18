import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import math
import random
from graph import floyd_warshall
from matrix import matrix_multiplication, generate_matrix
from sort import compare_sorts
from database import db

class GraphCanvas:
    def __init__(self, canvas, width=800, height=600):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.vertices = []  # [(x, y, id), ...]
        self.edges = []  # [(from_id, to_id, weight), ...]
        self.vertex_id_counter = 0
        self.selected_vertex = None
        self.edge_start = None
        self.mode = "add_vertex"  # "add_vertex", "add_edge", "delete"
        self.vertex_radius = 20
        
    def add_vertex(self, x, y):
        """Добавление вершины"""
        # Проверяем, не слишком ли близко к существующим вершинам
        for vx, vy, vid in self.vertices:
            if math.sqrt((x - vx)**2 + (y - vy)**2) < self.vertex_radius * 2:
                return False
        
        self.vertices.append((x, y, self.vertex_id_counter))
        self.vertex_id_counter += 1
        self.draw()
        return True
    
    def get_vertex_at(self, x, y):
        """Получить вершину по координатам клика"""
        for vx, vy, vid in self.vertices:
            if math.sqrt((x - vx)**2 + (y - vy)**2) <= self.vertex_radius:
                return vid
        return None
    
    def add_edge(self, from_id, to_id, weight=1):
        """Добавление ребра"""
        if from_id == to_id:
            return False
        
        # Проверяем, не существует ли уже такое ребро
        for f, t, w in self.edges:
            if (f == from_id and t == to_id) or (f == to_id and t == from_id):
                return False
        
        self.edges.append((from_id, to_id, weight))
        self.draw()
        return True
    
    def delete_vertex(self, vertex_id):
        """Удаление вершины и всех связанных рёбер"""
        self.vertices = [(x, y, vid) for x, y, vid in self.vertices if vid != vertex_id]
        self.edges = [(f, t, w) for f, t, w in self.edges if f != vertex_id and t != vertex_id]
        self.draw()
    
    def on_click(self, event):
        """Обработка клика на canvas"""
        x, y = event.x, event.y
        
        if self.mode == "add_vertex":
            self.add_vertex(x, y)
        elif self.mode == "add_edge":
            vid = self.get_vertex_at(x, y)
            if vid is not None:
                if self.edge_start is None:
                    self.edge_start = vid
                    self.selected_vertex = vid
                    self.draw()
                else:
                    if self.edge_start != vid:
                        # Запрашиваем вес ребра
                        weight = self.get_edge_weight()
                        if weight is not None:
                            self.add_edge(self.edge_start, vid, weight)
                        self.edge_start = None
                        self.selected_vertex = None
                        self.draw()
        elif self.mode == "delete":
            vid = self.get_vertex_at(x, y)
            if vid is not None:
                self.delete_vertex(vid)
    
    def get_edge_weight(self):
        """Диалог для ввода веса ребра"""
        dialog = tk.Toplevel()
        dialog.title("Вес ребра")
        dialog.geometry("500x200")
        dialog.transient()
        dialog.grab_set()
        
        result = [None]
        
        # Центрируем окно
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"500x200+{x}+{y}")
        
        tk.Label(dialog, text="Введите вес ребра:", font=("Arial", 12)).pack(pady=20)
        entry = tk.Entry(dialog, font=("Arial", 14), width=20)
        entry.pack(pady=10)
        entry.insert(0, "1")
        entry.focus()
        entry.select_range(0, tk.END)
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def ok():
            try:
                result[0] = int(entry.get())
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите целое число")
        
        def cancel():
            dialog.destroy()
        
        tk.Button(button_frame, text="OK", command=ok, font=("Arial", 11), 
                 width=10, height=2).pack(side=tk.LEFT, padx=20)
        tk.Button(button_frame, text="Отмена", command=cancel, font=("Arial", 11),
                 width=10, height=2).pack(side=tk.LEFT, padx=20)
        
        # Обработка Enter
        entry.bind("<Return>", lambda e: ok())
        entry.bind("<Escape>", lambda e: cancel())
        
        dialog.wait_window()
        return result[0]
    
    def clear(self):
        """Очистка графа"""
        self.vertices = []
        self.edges = []
        self.vertex_id_counter = 0
        self.selected_vertex = None
        self.edge_start = None
        self.draw()
    
    def generate_random_graph(self, num_vertices=5, num_edges=8):
        """Генерация случайного графа"""
        self.clear()
        
        # Размещаем вершины по кругу
        center_x, center_y = self.width // 2, self.height // 2
        radius = min(self.width, self.height) // 3
        
        vertex_ids = []
        for i in range(num_vertices):
            angle = 2 * math.pi * i / num_vertices
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            vid = self.vertex_id_counter
            self.vertices.append((x, y, vid))
            vertex_ids.append(vid)
            self.vertex_id_counter += 1
        
        # Добавляем случайные рёбра
        max_edges = min(num_edges, num_vertices * (num_vertices - 1) // 2)
        added = 0
        attempts = 0
        while added < max_edges and attempts < max_edges * 2:
            from_id = random.choice(vertex_ids)
            to_id = random.choice(vertex_ids)
            if from_id != to_id:
                weight = random.randint(1, 10)
                if self.add_edge(from_id, to_id, weight):
                    added += 1
            attempts += 1
        
        self.draw()
    
    def to_matrix(self):
        """Преобразование графа в матрицу смежности"""
        if not self.vertices:
            return None
        
        n = len(self.vertices)
        matrix = [[0] * n for _ in range(n)]
        
        # Создаём словарь для быстрого доступа
        id_to_index = {vid: idx for idx, (_, _, vid) in enumerate(self.vertices)}
        
        for from_id, to_id, weight in self.edges:
            from_idx = id_to_index[from_id]
            to_idx = id_to_index[to_id]
            matrix[from_idx][to_idx] = weight
            matrix[to_idx][from_idx] = weight  # Неориентированный граф
        
        return matrix
    
    def draw(self):
        """Отрисовка графа"""
        self.canvas.delete("all")
        
        # Рисуем рёбра
        id_to_pos = {vid: (x, y) for x, y, vid in self.vertices}
        
        for from_id, to_id, weight in self.edges:
            x1, y1 = id_to_pos[from_id]
            x2, y2 = id_to_pos[to_id]
            
            # Рисуем линию
            self.canvas.create_line(x1, y1, x2, y2, width=2, fill="gray")
            
            # Рисуем вес ребра
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            # Создаём белый фон для текста через прямоугольник
            self.canvas.create_rectangle(mid_x - 15, mid_y - 10, mid_x + 15, mid_y + 10, 
                                        fill="white", outline="white")
            self.canvas.create_text(mid_x, mid_y, text=str(weight), fill="blue", 
                                   font=("Arial", 10, "bold"))
        
        # Рисуем вершины
        for x, y, vid in self.vertices:
            color = "red" if vid == self.selected_vertex else "lightblue"
            self.canvas.create_oval(x - self.vertex_radius, y - self.vertex_radius,
                                   x + self.vertex_radius, y + self.vertex_radius,
                                   fill=color, outline="black", width=2)
            self.canvas.create_text(x, y, text=str(vid), font=("Arial", 12, "bold"))


class GraphTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        
        # Левая панель - управление
        left_panel = ttk.Frame(self.frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Кнопки режимов
        ttk.Label(left_panel, text="Режимы работы:", font=("Arial", 10, "bold")).pack(pady=5)
        
        self.mode_var = tk.StringVar(value="add_vertex")
        ttk.Radiobutton(left_panel, text="Добавить вершину", variable=self.mode_var,
                       value="add_vertex", command=self.change_mode).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(left_panel, text="Добавить ребро", variable=self.mode_var,
                       value="add_edge", command=self.change_mode).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(left_panel, text="Удалить", variable=self.mode_var,
                       value="delete", command=self.change_mode).pack(anchor=tk.W, pady=2)
        
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Кнопки действий
        ttk.Button(left_panel, text="Очистить граф", command=self.clear_graph).pack(pady=5, fill=tk.X)
        ttk.Button(left_panel, text="Сгенерировать случайный граф", 
                  command=self.generate_random).pack(pady=5, fill=tk.X)
        ttk.Button(left_panel, text="Запустить алгоритм", 
                  command=self.run_algorithm).pack(pady=5, fill=tk.X)
        
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Работа с БД
        ttk.Label(left_panel, text="База данных:", font=("Arial", 10, "bold")).pack(pady=5)
        ttk.Button(left_panel, text="Сохранить граф", 
                  command=self.save_graph).pack(pady=5, fill=tk.X)
        ttk.Button(left_panel, text="Загрузить граф", 
                  command=self.load_graph).pack(pady=5, fill=tk.X)
        
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Настройки генерации
        ttk.Label(left_panel, text="Настройки генерации:", font=("Arial", 10, "bold")).pack(pady=5)
        ttk.Label(left_panel, text="Вершин:").pack(anchor=tk.W)
        self.vertices_var = tk.StringVar(value="5")
        ttk.Entry(left_panel, textvariable=self.vertices_var, width=10).pack(pady=2)
        ttk.Label(left_panel, text="Рёбер:").pack(anchor=tk.W, pady=(5, 0))
        self.edges_var = tk.StringVar(value="8")
        ttk.Entry(left_panel, textvariable=self.edges_var, width=10).pack(pady=2)
        
        # Canvas для графа
        canvas_frame = ttk.Frame(self.frame)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, width=800, height=600, bg="white", 
                               cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.graph_canvas = GraphCanvas(self.canvas, 800, 600)
        self.canvas.bind("<Button-1>", self.graph_canvas.on_click)
        
        # Правая панель - вывод результатов
        right_panel = ttk.Frame(self.frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        
        ttk.Label(right_panel, text="Результаты:", font=("Arial", 10, "bold")).pack(pady=5)
        
        self.output_text = scrolledtext.ScrolledText(right_panel, width=40, height=30,
                                                     wrap=tk.WORD, font=("Courier", 9))
        self.output_text.pack(fill=tk.BOTH, expand=True)
    
    def change_mode(self):
        """Изменение режима работы"""
        self.graph_canvas.mode = self.mode_var.get()
        if self.mode_var.get() != "add_edge":
            self.graph_canvas.edge_start = None
            self.graph_canvas.selected_vertex = None
            self.graph_canvas.draw()
    
    def clear_graph(self):
        """Очистка графа"""
        self.graph_canvas.clear()
        self.output_text.delete(1.0, tk.END)
    
    def generate_random(self):
        """Генерация случайного графа"""
        try:
            num_vertices = int(self.vertices_var.get())
            num_edges = int(self.edges_var.get())
            if num_vertices < 2:
                messagebox.showerror("Ошибка", "Минимум 2 вершины")
                return
            if num_edges < 1:
                messagebox.showerror("Ошибка", "Минимум 1 ребро")
                return
            self.graph_canvas.generate_random_graph(num_vertices, num_edges)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числа")
    
    def run_algorithm(self):
        """Запуск алгоритма Флойда-Уоршелла"""
        matrix = self.graph_canvas.to_matrix()
        if matrix is None:
            messagebox.showwarning("Предупреждение", "Граф пуст. Добавьте вершины и рёбра.")
            return
        
        if len(matrix) < 2:
            messagebox.showwarning("Предупреждение", "Граф должен содержать минимум 2 вершины.")
            return
        
        # Запускаем алгоритм
        dist_matrix, comparisons, time_taken = floyd_warshall(matrix)
        
        # Выводим результаты
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "=== Алгоритм Флойда-Уоршелла ===\n\n")
        self.output_text.insert(tk.END, f"Количество вершин: {len(matrix)}\n")
        self.output_text.insert(tk.END, f"Количество рёбер: {len(self.graph_canvas.edges)}\n")
        self.output_text.insert(tk.END, f"Сравнений: {comparisons}\n")
        self.output_text.insert(tk.END, f"Время выполнения: {time_taken:.6f} сек\n\n")
        
        self.output_text.insert(tk.END, "Матрица смежности (входная):\n")
        for row in matrix:
            self.output_text.insert(tk.END, " ".join(f"{val:>4}" for val in row) + "\n")
        
        self.output_text.insert(tk.END, "\nМатрица кратчайших расстояний:\n")
        for i, row in enumerate(dist_matrix):
            formatted_row = []
            for val in row:
                if val == float('inf'):
                    formatted_row.append(" inf")
                else:
                    formatted_row.append(f"{int(val):>4}")
            self.output_text.insert(tk.END, " ".join(formatted_row) + "\n")
    
    def save_graph(self):
        """Сохранить граф в БД"""
        matrix = self.graph_canvas.to_matrix()
        if matrix is None:
            messagebox.showwarning("Предупреждение", "Граф пуст. Невозможно сохранить.")
            return
        
        name = simpledialog.askstring("Сохранение графа", "Введите название графа:")
        if name:
            try:
                vertices = len(self.graph_canvas.vertices)
                edges = len(self.graph_canvas.edges)
                db.save_graph(name, vertices, edges, matrix)
                messagebox.showinfo("Успех", f"Граф '{name}' сохранен в базу данных!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить граф: {e}")
    
    def load_graph(self):
        """Загрузить граф из БД"""
        graphs = db.get_all_graphs()
        if not graphs:
            messagebox.showinfo("Информация", "В базе данных нет сохраненных графов.")
            return
        
        # Создаем диалог выбора
        dialog = tk.Toplevel()
        dialog.title("Загрузить граф")
        dialog.geometry("500x400")
        dialog.transient()
        dialog.grab_set()
        
        ttk.Label(dialog, text="Выберите граф для загрузки:", font=("Arial", 11)).pack(pady=10)
        
        # Список графов
        listbox = tk.Listbox(dialog, height=15, font=("Courier", 9))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for graph in graphs:
            listbox.insert(tk.END, f"{graph['name']} ({graph['vertices']} вершин, {graph['edges']} рёбер) - {graph['created_at']}")
        
        selected_graph = [None]
        
        def load():
            selection = listbox.curselection()
            if selection:
                selected_graph[0] = graphs[selection[0]]
                dialog.destroy()
            else:
                messagebox.showwarning("Предупреждение", "Выберите граф из списка")
        
        def cancel():
            dialog.destroy()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Загрузить", command=load, font=("Arial", 11),
                 width=12, height=2).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Отмена", command=cancel, font=("Arial", 11),
                 width=12, height=2).pack(side=tk.LEFT, padx=10)
        
        dialog.wait_window()
        
        if selected_graph[0]:
            graph = selected_graph[0]
            # Восстанавливаем граф из матрицы
            self.graph_canvas.clear()
            matrix = graph['matrix']
            n = len(matrix)
            
            # Размещаем вершины по кругу
            center_x, center_y = 400, 300
            radius = 200
            
            for i in range(n):
                angle = 2 * math.pi * i / n
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                self.graph_canvas.vertices.append((x, y, i))
                self.graph_canvas.vertex_id_counter = max(self.graph_canvas.vertex_id_counter, i + 1)
            
            # Восстанавливаем рёбра
            for i in range(n):
                for j in range(i + 1, n):
                    if matrix[i][j] != 0:
                        self.graph_canvas.edges.append((i, j, matrix[i][j]))
            
            self.graph_canvas.draw()
            messagebox.showinfo("Успех", f"Граф '{graph['name']}' загружен!")


class MatrixTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        
        # Левая панель - управление
        left_panel = ttk.Frame(self.frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        ttk.Label(left_panel, text="Управление матрицами:", font=("Arial", 10, "bold")).pack(pady=5)
        
        # Настройки размера матрицы A
        ttk.Label(left_panel, text="Матрица A:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(10, 0))
        a_size_frame = ttk.Frame(left_panel)
        a_size_frame.pack(pady=2)
        ttk.Label(a_size_frame, text="Строк:").pack(side=tk.LEFT, padx=2)
        self.rows_a_var = tk.StringVar(value="3")
        ttk.Entry(a_size_frame, textvariable=self.rows_a_var, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(a_size_frame, text="Столбцов:").pack(side=tk.LEFT, padx=2)
        self.cols_a_var = tk.StringVar(value="3")
        ttk.Entry(a_size_frame, textvariable=self.cols_a_var, width=8).pack(side=tk.LEFT, padx=2)
        
        # Настройки размера матрицы B
        ttk.Label(left_panel, text="Матрица B:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(10, 0))
        b_size_frame = ttk.Frame(left_panel)
        b_size_frame.pack(pady=2)
        ttk.Label(b_size_frame, text="Строк:").pack(side=tk.LEFT, padx=2)
        self.rows_b_var = tk.StringVar(value="3")
        ttk.Entry(b_size_frame, textvariable=self.rows_b_var, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(b_size_frame, text="Столбцов:").pack(side=tk.LEFT, padx=2)
        self.cols_b_var = tk.StringVar(value="3")
        ttk.Entry(b_size_frame, textvariable=self.cols_b_var, width=8).pack(side=tk.LEFT, padx=2)
        
        # Кнопки действий
        ttk.Button(left_panel, text="Сгенерировать матрицы", 
                  command=self.generate_matrices).pack(pady=5, fill=tk.X)
        ttk.Button(left_panel, text="Очистить", 
                  command=self.clear_matrices).pack(pady=5, fill=tk.X)
        ttk.Button(left_panel, text="Умножить матрицы", 
                  command=self.multiply_matrices).pack(pady=5, fill=tk.X)
        
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Редактирование матриц
        ttk.Label(left_panel, text="Редактирование:", font=("Arial", 10, "bold")).pack(pady=5)
        ttk.Button(left_panel, text="Редактировать матрицу A", 
                  command=lambda: self.edit_matrix("A")).pack(pady=5, fill=tk.X)
        ttk.Button(left_panel, text="Редактировать матрицу B", 
                  command=lambda: self.edit_matrix("B")).pack(pady=5, fill=tk.X)
        
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Работа с БД
        ttk.Label(left_panel, text="База данных:", font=("Arial", 10, "bold")).pack(pady=5)
        ttk.Button(left_panel, text="Сохранить матрицы", 
                  command=self.save_matrices).pack(pady=5, fill=tk.X)
        ttk.Button(left_panel, text="Загрузить матрицы", 
                  command=self.load_matrices).pack(pady=5, fill=tk.X)
        
        # Центральная панель - матрицы
        center_panel = ttk.Frame(self.frame)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Матрица A
        matrix_a_frame = ttk.LabelFrame(center_panel, text="Матрица A")
        matrix_a_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.matrix_a_text = scrolledtext.ScrolledText(matrix_a_frame, width=25, height=15,
                                                       wrap=tk.NONE, font=("Courier", 10))
        self.matrix_a_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Матрица B
        matrix_b_frame = ttk.LabelFrame(center_panel, text="Матрица B")
        matrix_b_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.matrix_b_text = scrolledtext.ScrolledText(matrix_b_frame, width=25, height=15,
                                                       wrap=tk.NONE, font=("Courier", 10))
        self.matrix_b_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Правая панель - результат
        right_panel = ttk.Frame(self.frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        
        ttk.Label(right_panel, text="Результат (A × B):", font=("Arial", 10, "bold")).pack(pady=5)
        
        self.result_text = scrolledtext.ScrolledText(right_panel, width=40, height=30,
                                                     wrap=tk.NONE, font=("Courier", 9))
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        self.matrix_a = None
        self.matrix_b = None
    
    def generate_matrices(self):
        """Генерация случайных матриц"""
        try:
            rows_a = int(self.rows_a_var.get())
            cols_a = int(self.cols_a_var.get())
            rows_b = int(self.rows_b_var.get())
            cols_b = int(self.cols_b_var.get())
            
            if rows_a < 1 or rows_a > 20 or cols_a < 1 or cols_a > 20:
                messagebox.showerror("Ошибка", "Размеры матрицы A должны быть от 1 до 20")
                return
            
            if rows_b < 1 or rows_b > 20 or cols_b < 1 or cols_b > 20:
                messagebox.showerror("Ошибка", "Размеры матрицы B должны быть от 1 до 20")
                return
            
            # Проверяем возможность умножения
            if cols_a != rows_b:
                messagebox.showwarning("Предупреждение", 
                    f"Количество столбцов матрицы A ({cols_a}) должно равняться "
                    f"количеству строк матрицы B ({rows_b}) для умножения")
            
            self.matrix_a = generate_matrix(rows_a, cols_a)
            self.matrix_b = generate_matrix(rows_b, cols_b)
            
            self.update_matrix_display()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числа")
    
    def update_matrix_display(self):
        """Обновление отображения матриц"""
        self.matrix_a_text.delete(1.0, tk.END)
        self.matrix_b_text.delete(1.0, tk.END)
        
        if self.matrix_a:
            rows_a = len(self.matrix_a)
            cols_a = len(self.matrix_a[0]) if self.matrix_a else 0
            self.matrix_a_text.insert(tk.END, f"Размер: {rows_a}×{cols_a}\n\n")
            for row in self.matrix_a:
                self.matrix_a_text.insert(tk.END, " ".join(f"{val:>4}" for val in row) + "\n")
        
        if self.matrix_b:
            rows_b = len(self.matrix_b)
            cols_b = len(self.matrix_b[0]) if self.matrix_b else 0
            self.matrix_b_text.insert(tk.END, f"Размер: {rows_b}×{cols_b}\n\n")
            for row in self.matrix_b:
                self.matrix_b_text.insert(tk.END, " ".join(f"{val:>4}" for val in row) + "\n")
    
    def clear_matrices(self):
        """Очистка матриц"""
        self.matrix_a = None
        self.matrix_b = None
        self.matrix_a_text.delete(1.0, tk.END)
        self.matrix_b_text.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)
    
    def parse_matrix(self, text):
        """Парсинг матрицы из текста"""
        lines = text.strip().split('\n')
        matrix = []
        for line in lines:
            if line.strip():
                try:
                    row = [int(x) for x in line.split()]
                    matrix.append(row)
                except ValueError:
                    return None
        return matrix if matrix else None
    
    def edit_matrix(self, matrix_name):
        """Редактирование матрицы"""
        dialog = tk.Toplevel()
        dialog.title(f"Редактирование матрицы {matrix_name}")
        dialog.geometry("700x500")
        dialog.transient()
        dialog.grab_set()
        
        # Центрируем окно
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"700x500+{x}+{y}")
        
        # Получаем текущую матрицу
        current_matrix = self.matrix_a if matrix_name == "A" else self.matrix_b
        current_rows = len(current_matrix) if current_matrix else 3
        current_cols = len(current_matrix[0]) if current_matrix and current_matrix[0] else 3
        
        # Поля для размеров
        size_frame = ttk.Frame(dialog)
        size_frame.pack(pady=10)
        ttk.Label(size_frame, text="Строк:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        rows_var = tk.StringVar(value=str(current_rows))
        rows_entry = ttk.Entry(size_frame, textvariable=rows_var, width=8)
        rows_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(size_frame, text="Столбцов:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        cols_var = tk.StringVar(value=str(current_cols))
        cols_entry = ttk.Entry(size_frame, textvariable=cols_var, width=8)
        cols_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(dialog, text=f"Введите матрицу {matrix_name} (по одной строке, числа через пробел):", 
                 font=("Arial", 11)).pack(pady=5)
        
        text_area = scrolledtext.ScrolledText(dialog, width=60, height=18, 
                                              wrap=tk.NONE, font=("Courier", 10))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заполняем текущей матрицей
        if current_matrix:
            for row in current_matrix:
                text_area.insert(tk.END, " ".join(str(val) for val in row) + "\n")
        
        text_area.focus()
        
        def ok():
            try:
                rows = int(rows_var.get())
                cols = int(cols_var.get())
                if rows < 1 or rows > 20 or cols < 1 or cols > 20:
                    messagebox.showerror("Ошибка", "Размеры должны быть от 1 до 20")
                    return
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные размеры")
                return
            
            text = text_area.get(1.0, tk.END)
            matrix = self.parse_matrix(text)
            if matrix is None:
                messagebox.showerror("Ошибка", "Неверный формат матрицы")
                return
            
            # Проверяем размер
            if len(matrix) == 0:
                messagebox.showerror("Ошибка", "Матрица не может быть пустой")
                return
            
            # Проверяем соответствие размеров
            if len(matrix) != rows:
                messagebox.showerror("Ошибка", 
                    f"Количество строк не совпадает. Ожидается {rows}, получено {len(matrix)}")
                return
            
            if not all(len(row) == cols for row in matrix):
                messagebox.showerror("Ошибка", 
                    f"Количество столбцов не совпадает. Ожидается {cols}, но строки имеют разную длину")
                return
            
            if matrix_name == "A":
                self.matrix_a = matrix
                self.rows_a_var.set(str(rows))
                self.cols_a_var.set(str(cols))
            else:
                self.matrix_b = matrix
                self.rows_b_var.set(str(rows))
                self.cols_b_var.set(str(cols))
            
            self.update_matrix_display()
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="OK", command=ok, font=("Arial", 11),
                 width=12, height=2).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Отмена", command=cancel, font=("Arial", 11),
                 width=12, height=2).pack(side=tk.LEFT, padx=10)
    
    def multiply_matrices(self):
        """Умножение матриц"""
        if self.matrix_a is None or self.matrix_b is None:
            messagebox.showwarning("Предупреждение", "Сначала сгенерируйте или введите матрицы")
            return
        
        rows_a = len(self.matrix_a)
        cols_a = len(self.matrix_a[0]) if self.matrix_a else 0
        rows_b = len(self.matrix_b)
        cols_b = len(self.matrix_b[0]) if self.matrix_b else 0
        
        if cols_a != rows_b:
            messagebox.showerror("Ошибка", 
                               f"Количество столбцов матрицы A ({cols_a}) должно "
                               f"равняться количеству строк матрицы B ({rows_b})")
            return
        
        try:
            # Запускаем умножение
            result_matrix, comparisons, time_taken = matrix_multiplication(self.matrix_a, self.matrix_b)
            
            # Выводим результаты
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "=== Умножение матриц ===\n\n")
            self.result_text.insert(tk.END, f"Размер A: {rows_a}×{cols_a}\n")
            self.result_text.insert(tk.END, f"Размер B: {rows_b}×{cols_b}\n")
            self.result_text.insert(tk.END, f"Размер результата: {len(result_matrix)}×{len(result_matrix[0])}\n")
            self.result_text.insert(tk.END, f"Сравнений: {comparisons}\n")
            self.result_text.insert(tk.END, f"Время выполнения: {time_taken:.6f} сек\n\n")
            
            self.result_text.insert(tk.END, "Результирующая матрица:\n")
            for row in result_matrix:
                self.result_text.insert(tk.END, " ".join(f"{val:>6}" for val in row) + "\n")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def save_matrices(self):
        """Сохранить матрицы в БД"""
        if self.matrix_a is None or self.matrix_b is None:
            messagebox.showwarning("Предупреждение", "Матрицы пусты. Невозможно сохранить.")
            return
        
        name = simpledialog.askstring("Сохранение матриц", "Введите название:")
        if name:
            try:
                result = None
                # Пытаемся получить результат из текстового поля
                result_text = self.result_text.get(1.0, tk.END).strip()
                if "Результирующая матрица:" in result_text:
                    # Можно попытаться распарсить результат, но для простоты оставим None
                    pass
                
                db.save_matrices(name, self.matrix_a, self.matrix_b, result)
                messagebox.showinfo("Успех", f"Матрицы '{name}' сохранены в базу данных!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
    
    def load_matrices(self):
        """Загрузить матрицы из БД"""
        matrices = db.get_all_matrices()
        if not matrices:
            messagebox.showinfo("Информация", "В базе данных нет сохраненных матриц.")
            return
        
        # Создаем диалог выбора
        dialog = tk.Toplevel()
        dialog.title("Загрузить матрицы")
        dialog.geometry("500x400")
        dialog.transient()
        dialog.grab_set()
        
        ttk.Label(dialog, text="Выберите матрицы для загрузки:", font=("Arial", 11)).pack(pady=10)
        
        listbox = tk.Listbox(dialog, height=15, font=("Courier", 9))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for m in matrices:
            size_a = f"{len(m['matrix_a'])}×{len(m['matrix_a'][0]) if m['matrix_a'] else 0}"
            size_b = f"{len(m['matrix_b'])}×{len(m['matrix_b'][0]) if m['matrix_b'] else 0}"
            listbox.insert(tk.END, f"{m['name']} (A: {size_a}, B: {size_b}) - {m['created_at']}")
        
        selected_matrix = [None]
        
        def load():
            selection = listbox.curselection()
            if selection:
                selected_matrix[0] = matrices[selection[0]]
                dialog.destroy()
            else:
                messagebox.showwarning("Предупреждение", "Выберите матрицы из списка")
        
        def cancel():
            dialog.destroy()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Загрузить", command=load, font=("Arial", 11),
                 width=12, height=2).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Отмена", command=cancel, font=("Arial", 11),
                 width=12, height=2).pack(side=tk.LEFT, padx=10)
        
        dialog.wait_window()
        
        if selected_matrix[0]:
            m = selected_matrix[0]
            self.matrix_a = m['matrix_a']
            self.matrix_b = m['matrix_b']
            self.rows_a_var.set(str(len(self.matrix_a)))
            self.cols_a_var.set(str(len(self.matrix_a[0]) if self.matrix_a else 0))
            self.rows_b_var.set(str(len(self.matrix_b)))
            self.cols_b_var.set(str(len(self.matrix_b[0]) if self.matrix_b else 0))
            self.update_matrix_display()
            if m['result']:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "Результирующая матрица:\n")
                for row in m['result']:
                    self.result_text.insert(tk.END, " ".join(f"{val:>6}" for val in row) + "\n")
            messagebox.showinfo("Успех", f"Матрицы '{m['name']}' загружены!")


class SortTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        
        # Левая панель - управление
        left_panel = ttk.Frame(self.frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        ttk.Label(left_panel, text="Управление сортировкой:", font=("Arial", 10, "bold")).pack(pady=5)
        
        # Настройки размера массива
        ttk.Label(left_panel, text="Размер массива:").pack(anchor=tk.W, pady=(10, 0))
        self.size_var = tk.StringVar(value="100")
        size_entry = ttk.Entry(left_panel, textvariable=self.size_var, width=15)
        size_entry.pack(pady=5)
        
        # Диапазон значений
        ttk.Label(left_panel, text="Диапазон значений:").pack(anchor=tk.W, pady=(10, 0))
        range_frame = ttk.Frame(left_panel)
        range_frame.pack(pady=5)
        self.min_var = tk.StringVar(value="1")
        self.max_var = tk.StringVar(value="1000")
        ttk.Entry(range_frame, textvariable=self.min_var, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(range_frame, text=" - ").pack(side=tk.LEFT)
        ttk.Entry(range_frame, textvariable=self.max_var, width=8).pack(side=tk.LEFT, padx=2)
        
        # Кнопки действий
        ttk.Button(left_panel, text="Сгенерировать массив", 
                  command=self.generate_array).pack(pady=5, fill=tk.X)
        ttk.Button(left_panel, text="Очистить", 
                  command=self.clear_array).pack(pady=5, fill=tk.X)
        ttk.Button(left_panel, text="Запустить сравнение", 
                  command=self.run_comparison).pack(pady=5, fill=tk.X)
        
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Редактирование массива
        ttk.Label(left_panel, text="Редактирование:", font=("Arial", 10, "bold")).pack(pady=5)
        ttk.Button(left_panel, text="Редактировать массив", 
                  command=self.edit_array).pack(pady=5, fill=tk.X)
        
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Работа с БД
        ttk.Label(left_panel, text="База данных:", font=("Arial", 10, "bold")).pack(pady=5)
        ttk.Button(left_panel, text="Сохранить результат", 
                  command=self.save_sort_result).pack(pady=5, fill=tk.X)
        ttk.Button(left_panel, text="Загрузить результаты", 
                  command=self.load_sort_results).pack(pady=5, fill=tk.X)
        
        # Центральная панель - входной массив
        center_panel = ttk.Frame(self.frame)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Входной массив
        input_frame = ttk.LabelFrame(center_panel, text="Входной массив")
        input_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.input_text = scrolledtext.ScrolledText(input_frame, width=40, height=15,
                                                    wrap=tk.NONE, font=("Courier", 9))
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Результаты сортировки
        results_frame = ttk.LabelFrame(center_panel, text="Результаты сортировки")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, width=40, height=15,
                                                      wrap=tk.WORD, font=("Courier", 9))
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Правая панель - сравнение алгоритмов
        right_panel = ttk.Frame(self.frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        
        ttk.Label(right_panel, text="Сравнение алгоритмов:", font=("Arial", 10, "bold")).pack(pady=5)
        
        self.comparison_text = scrolledtext.ScrolledText(right_panel, width=50, height=30,
                                                         wrap=tk.WORD, font=("Courier", 9))
        self.comparison_text.pack(fill=tk.BOTH, expand=True)
        
        self.array = None
        self.last_results = None
    
    def generate_array(self):
        """Генерация случайного массива"""
        try:
            size = int(self.size_var.get())
            min_val = int(self.min_var.get())
            max_val = int(self.max_var.get())
            
            if size < 1:
                messagebox.showerror("Ошибка", "Размер должен быть больше 0")
                return
            if min_val >= max_val:
                messagebox.showerror("Ошибка", "Минимальное значение должно быть меньше максимального")
                return
            
            self.array = [random.randint(min_val, max_val) for _ in range(size)]
            self.update_input_display()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числа")
    
    def update_input_display(self):
        """Обновление отображения входного массива"""
        self.input_text.delete(1.0, tk.END)
        if self.array:
            # Показываем первые 50 элементов, если массив большой
            if len(self.array) <= 50:
                self.input_text.insert(tk.END, ", ".join(str(x) for x in self.array))
            else:
                preview = ", ".join(str(x) for x in self.array[:50])
                self.input_text.insert(tk.END, f"{preview}...\n\n")
                self.input_text.insert(tk.END, f"Всего элементов: {len(self.array)}")
    
    def clear_array(self):
        """Очистка массива"""
        self.array = None
        self.input_text.delete(1.0, tk.END)
        self.results_text.delete(1.0, tk.END)
        self.comparison_text.delete(1.0, tk.END)
    
    def parse_array(self, text):
        """Парсинг массива из текста"""
        try:
            # Пробуем разные разделители
            text = text.strip()
            if ',' in text:
                arr = [int(x.strip()) for x in text.split(',') if x.strip()]
            elif ' ' in text:
                arr = [int(x) for x in text.split() if x.strip()]
            else:
                arr = [int(text)]
            return arr if arr else None
        except ValueError:
            return None
    
    def edit_array(self):
        """Редактирование массива"""
        dialog = tk.Toplevel()
        dialog.title("Редактирование массива")
        dialog.geometry("700x400")
        dialog.transient()
        dialog.grab_set()
        
        # Центрируем окно
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"700x400+{x}+{y}")
        
        ttk.Label(dialog, text="Введите массив (числа через запятую или пробел):", 
                 font=("Arial", 11)).pack(pady=10)
        
        text_area = scrolledtext.ScrolledText(dialog, width=60, height=15, 
                                              wrap=tk.NONE, font=("Courier", 10))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заполняем текущим массивом
        if self.array:
            text_area.insert(tk.END, ", ".join(str(x) for x in self.array))
        
        text_area.focus()
        
        def ok():
            text = text_area.get(1.0, tk.END)
            arr = self.parse_array(text)
            if arr is None:
                messagebox.showerror("Ошибка", "Неверный формат массива. Используйте числа через запятую или пробел")
                return
            
            if len(arr) == 0:
                messagebox.showerror("Ошибка", "Массив не может быть пустым")
                return
            
            self.array = arr
            self.update_input_display()
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="OK", command=ok, font=("Arial", 11),
                 width=12, height=2).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Отмена", command=cancel, font=("Arial", 11),
                 width=12, height=2).pack(side=tk.LEFT, padx=10)
    
    def run_comparison(self):
        """Запуск сравнения алгоритмов сортировки"""
        if self.array is None or len(self.array) == 0:
            messagebox.showwarning("Предупреждение", "Сначала сгенерируйте или введите массив")
            return
        
        # Запускаем сравнение
        results = compare_sorts(self.array.copy())
        
        # Выводим результаты
        self.results_text.delete(1.0, tk.END)
        self.comparison_text.delete(1.0, tk.END)
        
        self.results_text.insert(tk.END, f"Исходный массив ({len(self.array)} элементов):\n")
        if len(self.array) <= 20:
            self.results_text.insert(tk.END, ", ".join(str(x) for x in self.array) + "\n\n")
        else:
            preview = ", ".join(str(x) for x in self.array[:20])
            self.results_text.insert(tk.END, f"{preview}...\n\n")
        
        # Сравнение алгоритмов
        self.comparison_text.insert(tk.END, "=== Сравнение алгоритмов сортировки ===\n\n")
        self.comparison_text.insert(tk.END, f"Размер массива: {len(self.array)} элементов\n\n")
        
        # Сортируем по времени выполнения
        sorted_results = sorted(results.items(), key=lambda x: x[1]['time'])
        
        for i, (name, data) in enumerate(sorted_results, 1):
            self.comparison_text.insert(tk.END, f"{i}. {name}:\n")
            self.comparison_text.insert(tk.END, f"   Время: {data['time']:.6f} сек\n")
            self.comparison_text.insert(tk.END, f"   Сравнений: {data['comparisons']}\n")
            
            # Показываем отсортированный массив (первые элементы)
            sorted_arr = data['sorted_array']
            if len(sorted_arr) <= 20:
                self.comparison_text.insert(tk.END, f"   Результат: {', '.join(str(x) for x in sorted_arr)}\n")
            else:
                preview = ", ".join(str(x) for x in sorted_arr[:20])
                self.comparison_text.insert(tk.END, f"   Результат: {preview}...\n")
            
            self.comparison_text.insert(tk.END, "\n")
        
        # Показываем лучший результат в results_text
        best_name, best_data = sorted_results[0]
        self.results_text.insert(tk.END, f"Лучший алгоритм: {best_name}\n")
        self.results_text.insert(tk.END, f"Время: {best_data['time']:.6f} сек\n")
        self.results_text.insert(tk.END, f"Сравнений: {best_data['comparisons']}\n\n")
        
        sorted_arr = best_data['sorted_array']
        self.results_text.insert(tk.END, "Отсортированный массив:\n")
        if len(sorted_arr) <= 50:
            self.results_text.insert(tk.END, ", ".join(str(x) for x in sorted_arr))
        else:
            preview = ", ".join(str(x) for x in sorted_arr[:50])
            self.results_text.insert(tk.END, f"{preview}...\n")
            self.results_text.insert(tk.END, f"\nВсего элементов: {len(sorted_arr)}")
        
        # Сохраняем результаты в БД
        self.last_results = results
    
    def save_sort_result(self):
        """Сохранить результаты сортировки в БД"""
        if not hasattr(self, 'last_results') or not self.last_results:
            messagebox.showwarning("Предупреждение", "Сначала запустите сравнение алгоритмов.")
            return
        
        if self.array is None:
            messagebox.showwarning("Предупреждение", "Массив пуст.")
            return
        
        name = simpledialog.askstring("Сохранение результатов", "Введите название:")
        if name:
            try:
                for algorithm_name, data in self.last_results.items():
                    db.save_sort_result(
                        name=f"{name} - {algorithm_name}",
                        array_size=len(self.array),
                        input_array=self.array,
                        algorithm=algorithm_name,
                        sorted_array=data['sorted_array'],
                        comparisons=data['comparisons'],
                        time_taken=data['time']
                    )
                messagebox.showinfo("Успех", f"Результаты '{name}' сохранены в базу данных!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
    
    def load_sort_results(self):
        """Загрузить результаты сортировки из БД"""
        sorts = db.get_all_sorts()
        if not sorts:
            messagebox.showinfo("Информация", "В базе данных нет сохраненных результатов.")
            return
        
        # Создаем диалог выбора
        dialog = tk.Toplevel()
        dialog.title("Загрузить результаты")
        dialog.geometry("600x500")
        dialog.transient()
        dialog.grab_set()
        
        ttk.Label(dialog, text="Выберите результаты для загрузки:", font=("Arial", 11)).pack(pady=10)
        
        listbox = tk.Listbox(dialog, height=20, font=("Courier", 9))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for s in sorts:
            listbox.insert(tk.END, f"{s['name']} | {s['algorithm']} | Размер: {s['array_size']} | Время: {s['time_taken']:.6f}с")
        
        selected_sort = [None]
        
        def load():
            selection = listbox.curselection()
            if selection:
                selected_sort[0] = sorts[selection[0]]
                dialog.destroy()
            else:
                messagebox.showwarning("Предупреждение", "Выберите результат из списка")
        
        def cancel():
            dialog.destroy()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Загрузить", command=load, font=("Arial", 11),
                 width=12, height=2).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Отмена", command=cancel, font=("Arial", 11),
                 width=12, height=2).pack(side=tk.LEFT, padx=10)
        
        dialog.wait_window()
        
        if selected_sort[0]:
            s = selected_sort[0]
            self.array = s['input_array']
            self.update_input_display()
            
            # Показываем результаты
            self.results_text.delete(1.0, tk.END)
            self.comparison_text.delete(1.0, tk.END)
            
            self.results_text.insert(tk.END, f"Загруженный массив ({s['array_size']} элементов):\n")
            if len(s['input_array']) <= 20:
                self.results_text.insert(tk.END, ", ".join(str(x) for x in s['input_array']) + "\n\n")
            else:
                preview = ", ".join(str(x) for x in s['input_array'][:20])
                self.results_text.insert(tk.END, f"{preview}...\n\n")
            
            self.results_text.insert(tk.END, f"Алгоритм: {s['algorithm']}\n")
            self.results_text.insert(tk.END, f"Время: {s['time_taken']:.6f} сек\n")
            self.results_text.insert(tk.END, f"Сравнений: {s['comparisons']}\n\n")
            
            sorted_arr = s['sorted_array']
            self.results_text.insert(tk.END, "Отсортированный массив:\n")
            if len(sorted_arr) <= 50:
                self.results_text.insert(tk.END, ", ".join(str(x) for x in sorted_arr))
            else:
                preview = ", ".join(str(x) for x in sorted_arr[:50])
                self.results_text.insert(tk.END, f"{preview}...\n")
                self.results_text.insert(tk.END, f"\nВсего элементов: {len(sorted_arr)}")
            
            self.comparison_text.insert(tk.END, f"=== {s['algorithm']} ===\n\n")
            self.comparison_text.insert(tk.END, f"Время: {s['time_taken']:.6f} сек\n")
            self.comparison_text.insert(tk.END, f"Сравнений: {s['comparisons']}\n")
            
            messagebox.showinfo("Успех", f"Результаты '{s['name']}' загружены!")


class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("KursPy - Визуализация алгоритмов")
        self.root.geometry("1400x700")
        
        # Создаём notebook для вкладок
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Создаём вкладки
        self.graph_tab = GraphTab(self.notebook)
        self.matrix_tab = MatrixTab(self.notebook)
        self.sort_tab = SortTab(self.notebook)
        
        self.notebook.add(self.graph_tab.frame, text="Графы")
        self.notebook.add(self.matrix_tab.frame, text="Матрицы")
        self.notebook.add(self.sort_tab.frame, text="Сортировка")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()


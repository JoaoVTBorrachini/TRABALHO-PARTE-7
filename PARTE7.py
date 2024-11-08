
import tkinter as tk
from tkinter import simpledialog, messagebox
import math

class Object2D:
    def __init__(self, name, obj_type, x1, y1, x2=None, y2=None):
        self.name = name
        self.obj_type = obj_type
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def draw(self, canvas, window_x, window_y, zoom):
        x1, y1 = to_screen_coords(self.x1, self.y1, canvas.winfo_width(), canvas.winfo_height(), window_x, window_y, zoom)
        if self.obj_type == "point":
            canvas.create_rectangle(x1 - 2, y1 - 2, x1 + 2, y1 + 2, fill="black")
        elif self.obj_type == "line":
            x2, y2 = to_screen_coords(self.x2, self.y2, canvas.winfo_width(), canvas.winfo_height(), window_x, window_y, zoom)
            canvas.create_line(x1, y1, x2, y2, fill="black")

    def apply_transformation(self, matrix):
        x1, y1, _ = matrix * Matriz.from_point(self.x1, self.y1)
        self.x1, self.y1 = x1, y1
        if self.obj_type == "line" and self.x2 is not None and self.y2 is not None:
            x2, y2, _ = matrix * Matriz.from_point(self.x2, self.y2)
            self.x2, self.y2 = x2, y2

class Matriz:
    def __init__(self, linhas, colunas):
        self.linhas = linhas
        self.colunas = colunas
        self.matriz = [[0.0 for _ in range(colunas)] for _ in range(linhas)]

    def set_valor(self, linha, coluna, valor):
        self.matriz[linha][coluna] = valor

    def get_valor(self, linha, coluna):
        return self.matriz[linha][coluna]

    def __mul__(self, outra):
        if self.colunas != outra.linhas:
            raise ValueError("Multiplicação impossível: número de colunas da primeira matriz deve ser igual ao número de linhas da segunda matriz.")
        resultado = Matriz(self.linhas, outra.colunas)
        for i in range(self.linhas):
            for j in range(outra.colunas):
                soma = 0.0
                for k in range(self.colunas):
                    soma += self.matriz[i][k] * outra.matriz[k][j]
                resultado.set_valor(i, j, soma)
        return resultado

    @staticmethod
    def from_point(x, y):
        matriz = Matriz(3, 1)
        matriz.set_valor(0, 0, x)
        matriz.set_valor(1, 0, y)
        matriz.set_valor(2, 0, 1)
        return matriz

    @staticmethod
    def translation(dx, dy):
        matriz = Matriz(3, 3)
        matriz.set_valor(0, 0, 1)
        matriz.set_valor(1, 1, 1)
        matriz.set_valor(2, 2, 1)
        matriz.set_valor(0, 2, dx)
        matriz.set_valor(1, 2, dy)
        return matriz

    @staticmethod
    def rotation(angle_degrees):
        angle_radians = math.radians(angle_degrees)
        cos_theta = math.cos(angle_radians)
        sin_theta = math.sin(angle_radians)
        matriz = Matriz(3, 3)
        matriz.set_valor(0, 0, cos_theta)
        matriz.set_valor(0, 1, -sin_theta)
        matriz.set_valor(1, 0, sin_theta)
        matriz.set_valor(1, 1, cos_theta)
        matriz.set_valor(2, 2, 1)
        return matriz

    @staticmethod
    def scaling(sx, sy):
        matriz = Matriz(3, 3)
        matriz.set_valor(0, 0, sx)
        matriz.set_valor(1, 1, sy)
        matriz.set_valor(2, 2, 1)
        return matriz

    @staticmethod
    def rotation_around_point(angle_degrees, cx, cy):
        angle_radians = math.radians(angle_degrees)
        cos_theta = math.cos(angle_radians)
        sin_theta = math.sin(angle_radians)
        translation_to_origin = Matriz.translation(-cx, -cy)
        rotation = Matriz(3, 3)
        rotation.set_valor(0, 0, cos_theta)
        rotation.set_valor(0, 1, -sin_theta)
        rotation.set_valor(1, 0, sin_theta)
        rotation.set_valor(1, 1, cos_theta)
        rotation.set_valor(2, 2, 1)
        translation_back = Matriz.translation(cx, cy)
        return translation_back * rotation * translation_to_origin

    @staticmethod
    def scaling_from_point(sx, sy, px, py):
        translation_to_origin = Matriz.translation(-px, -py)
        scaling = Matriz(3, 3)
        scaling.set_valor(0, 0, sx)
        scaling.set_valor(1, 1, sy)
        scaling.set_valor(2, 2, 1)
        translation_back = Matriz.translation(px, py)
        return translation_back * scaling * translation_to_origin

def to_screen_coords(x, y, canvas_width, canvas_height, window_x, window_y, zoom):
    x = (x - window_x) * zoom
    y = (y - window_y) * zoom
    return (canvas_width // 2 + int(x), canvas_height // 2 - int(y))

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Básico 2D | João Vitor Thomazoni Borrachini |")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.objects = []
        self.window_x, self.window_y = 0, 0
        self.zoom = 1.0
        self.canvas = tk.Canvas(self, bg="white", width=WIDTH, height=HEIGHT)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.sidebar = tk.Frame(self, width=200, bg="lightgray")
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox = tk.Listbox(self.sidebar, bg="white")
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.button_frame = tk.Frame(self.sidebar)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Button(self.button_frame, text="Adicionar Ponto", command=self.add_point).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.button_frame, text="Adicionar Linha", command=self.add_line).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.button_frame, text="Remover Objeto", command=self.remove_object).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.button_frame, text="Transladar", command=self.translate_object).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.button_frame, text="Rotacionar", command=self.rotate_object).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.button_frame, text="Escalonar", command=self.scale_object).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.button_frame, text="Rotacionar em torno de ponto", command=self.rotate_object_around_point).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.button_frame, text="Escalonar a partir do primeiro vértice", command=self.scale_object_from_first_vertex).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.button_frame, text="Panning Esquerda", command=lambda: self.pan(-20, 0)).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.button_frame, text="Panning Direita", command=lambda: self.pan(20, 0)).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.button_frame, text="Panning Cima", command=lambda: self.pan(0, -20)).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.button_frame, text="Panning Baixo", command=lambda: self.pan(0, 20)).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.button_frame, text="Zoom In", command=self.zoom_in).pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(self.button_frame, text="Zoom Out", command=self.zoom_out).pack(side=tk.TOP, padx=5, pady=5)
        self.update_viewport()

    def add_point(self):
        x = simpledialog.askfloat("Adicionar Ponto", "Coord X:")
        y = simpledialog.askfloat("Adicionar Ponto", "Coord Y:")
        if x

 is not None and y is not None:
            obj = Object2D("Ponto", "point", x, y)
            self.objects.append(obj)
            self.listbox.insert(tk.END, obj.name)
            self.update_viewport()

    def add_line(self):
        x1 = simpledialog.askfloat("Adicionar Linha", "Coord X1:")
        y1 = simpledialog.askfloat("Adicionar Linha", "Coord Y1:")
        x2 = simpledialog.askfloat("Adicionar Linha", "Coord X2:")
        y2 = simpledialog.askfloat("Adicionar Linha", "Coord Y2:")
        if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
            obj = Object2D("Linha", "line", x1, y1, x2, y2)
            self.objects.append(obj)
            self.listbox.insert(tk.END, obj.name)
            self.update_viewport()

    def remove_object(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            del self.objects[index]
            self.listbox.delete(index)
            self.update_viewport()

    def update_viewport(self):
        self.canvas.delete("all")
        for obj in self.objects:
            obj.draw(self.canvas, self.window_x, self.window_y, self.zoom)

    def pan(self, dx, dy):
        self.window_x += dx
        self.window_y += dy
        self.update_viewport()

    def zoom_in(self):
        self.zoom *= 1.1
        self.update_viewport()

    def zoom_out(self):
        self.zoom /= 1.1
        self.update_viewport()

    def get_selected_object(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            return self.objects[index]
        return None

    def translate_object(self):
        selected = self.get_selected_object()
        if selected:
            dx = simpledialog.askfloat("Translação", "Deslocamento em X:")
            dy = simpledialog.askfloat("Translação", "Deslocamento em Y:")
            if dx is not None and dy is not None:
                matrix = Matriz.translation(dx, dy)
                selected.apply_transformation(matrix)
                self.update_viewport()

    def rotate_object(self):
        selected = self.get_selected_object()
        if selected:
            angle = simpledialog.askfloat("Rotação", "Ângulo de rotação (graus):")
            if angle is not None:
                matrix = Matriz.rotation(angle)
                selected.apply_transformation(matrix)
                self.update_viewport()

    def rotate_object_around_point(self):
        selected = self.get_selected_object()
        if selected:
            angle = simpledialog.askfloat("Rotação", "Ângulo de rotação (graus):")
            cx = simpledialog.askfloat("Centro de rotação", "Coord X do ponto de rotação:")
            cy = simpledialog.askfloat("Centro de rotação", "Coord Y do ponto de rotação:")
            if angle is not None and cx is not None and cy is not None:
                matrix = Matriz.rotation_around_point(angle, cx, cy)
                selected.apply_transformation(matrix)
                self.update_viewport()

    def scale_object(self):
        selected = self.get_selected_object()
        if selected:
            sx = simpledialog.askfloat("Escalonamento", "Fator de escala em X:")
            sy = simpledialog.askfloat("Escalonamento", "Fator de escala em Y:")
            if sx is not None and sy is not None:
                matrix = Matriz.scaling(sx, sy)
                selected.apply_transformation(matrix)
                self.update_viewport()

    def scale_object_from_first_vertex(self):
        selected = self.get_selected_object()
        if selected:
            sx = simpledialog.askfloat("Escalonamento", "Fator de escala em X:")
            sy = simpledialog.askfloat("Escalonamento", "Fator de escala em Y:")
            if sx is not None and sy is not None:
                matrix = Matriz.scaling_from_point(sx, sy, selected.x1, selected.y1)
                selected.apply_transformation(matrix)
                self.update_viewport()

if __name__ == "__main__":
    WIDTH, HEIGHT = 800, 600
    app = Application()
    app.mainloop()
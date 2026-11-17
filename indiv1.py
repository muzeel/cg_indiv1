
import tkinter as tk
from tkinter import messagebox
import random


# ==========================================
# НАСТРОЙКИ ПРОГРАММЫ
# ==========================================

WIDTH = 800
HEIGHT = 600

BACKGROUND = "white"
POINT_COLOR = "blue"
HULL_COLOR = "red"
CURRENT_COLOR = "orange"

POINT_RADIUS = 4


# ==========================================
# РАБОТА С ПИКСЕЛЯМИ
# ==========================================

class Raster:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.image = tk.PhotoImage(
            width=width,
            height=height
        )

    def clear(self):
        self.image = tk.PhotoImage(
            width=self.width,
            height=self.height
        )

    def set_pixel(self, x, y, color):
        """Закрашивает один пиксель."""

        if 0 <= x < self.width and 0 <= y < self.height:
            self.image.put(color, (int(x), int(y)))

    def draw_line(self, x1, y1, x2, y2, color):
        """
        Алгоритм Брезенхема.
        Строит отрезок путем выбора отдельных пикселей.
        """

        x1, y1 = int(x1), int(y1)
        x2, y2 = int(x2), int(y2)

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1

        error = dx - dy

        while True:
            self.set_pixel(x1, y1, color)

            if x1 == x2 and y1 == y2:
                break

            error2 = 2 * error

            if error2 > -dy:
                error -= dy
                x1 += sx

            if error2 < dx:
                error += dx
                y1 += sy

    def draw_point(self, x, y, radius, color):
        """Рисует заполненный круг пикселями."""

        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):

                if dx * dx + dy * dy <= radius * radius:
                    self.set_pixel(x + dx, y + dy, color)


# ==========================================
# ГЕОМЕТРИЧЕСКИЕ ВЫЧИСЛЕНИЯ
# ==========================================

def cross_product(a, b, c):
    """
    Векторное произведение AB и AC.

    Положительное значение:
    одна сторона прямой AB.

    Отрицательное значение:
    противоположная сторона.

    Ноль:
    точки лежат на одной прямой.
    """

    return (
        (b[0] - a[0]) * (c[1] - a[1])
        - (b[1] - a[1]) * (c[0] - a[0])
    )


def distance_squared(a, b):
    """Квадрат расстояния между точками."""

    dx = a[0] - b[0]
    dy = a[1] - b[1]

    return dx * dx + dy * dy


# ==========================================
# АЛГОРИТМ ДЖАРВИСА
# ==========================================

def jarvis_march(points):
    """
    Построение выпуклой оболочки методом Джарвиса.

    Возвращает список вершин оболочки
    в порядке обхода.
    """

    if len(points) < 3:
        return points.copy()

    # Удаляем повторяющиеся точки.
    points = list(set(points))

    if len(points) < 3:
        return points

    # Находим самую левую точку.
    start = min(points, key=lambda p: (p[0], p[1]))

    hull = []
    current = start

    while True:

        hull.append(current)

        # Выбираем любую другую точку.
        candidate = next(
            p for p in points if p != current
        )

        # Ищем следующую вершину оболочки.
        for p in points:

            if p == current or p == candidate:
                continue

            turn = cross_product(current, candidate, p)

            # Выбираем наиболее подходящее направление.
            if turn < 0:
                candidate = p

            # Если точки лежат на одной прямой,
            # выбираем наиболее удаленную.
            elif turn == 0:
                if distance_squared(current, p) > \
                   distance_squared(current, candidate):

                    candidate = p

        current = candidate

        # Завершаем обход при возвращении к началу.
        if current == start:
            break

    return hull


# ==========================================
# ГРАФИЧЕСКИЙ ИНТЕРФЕЙС
# ==========================================

class JarvisApplication:

    def __init__(self, root):

        self.root = root
        self.root.title("Выпуклая оболочка — алгоритм Джарвиса")
        self.root.resizable(False, False)

        self.points = []
        self.hull = []
        self.current_step = 0

        self.raster = Raster(WIDTH, HEIGHT)

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            background=BACKGROUND,
            highlightthickness=1
        )

        self.canvas.pack(padx=10, pady=10)

        self.canvas.create_image(
            0, 0,
            anchor=tk.NW,
            image=self.raster.image
        )

        self.canvas.bind(
            "<Button-1>",
            self.add_point
        )

        # Панель управления.
        controls = tk.Frame(root)
        controls.pack(pady=5)

        tk.Button(
            controls,
            text="Случайные точки",
            command=self.generate_points,
            width=17
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            controls,
            text="Очистить",
            command=self.clear,
            width=12
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            controls,
            text="Построить оболочку",
            command=self.build_hull,
            width=19
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            controls,
            text="Следующий шаг",
            command=self.next_step,
            width=15
        ).pack(side=tk.LEFT, padx=4)

        self.status = tk.Label(
            root,
            text="Добавьте точки щелчком мыши.",
            font=("Arial", 11)
        )

        self.status.pack(pady=5)

        self.redraw()

    # --------------------------------------
    # ДОБАВЛЕНИЕ ТОЧЕК
    # --------------------------------------

    def add_point(self, event):

        point = (event.x, event.y)

        if point not in self.points:
            self.points.append(point)

        self.hull = []
        self.current_step = 0

        self.status.config(
            text=f"Количество точек: {len(self.points)}"
        )

        self.redraw()

    # --------------------------------------
    # ГЕНЕРАЦИЯ СЛУЧАЙНЫХ ТОЧЕК
    # --------------------------------------

    def generate_points(self):

        self.points = []

        for _ in range(30):

            x = random.randint(30, WIDTH - 30)
            y = random.randint(30, HEIGHT - 30)

            self.points.append((x, y))

        self.hull = []
        self.current_step = 0

        self.status.config(
            text="Сгенерировано 30 случайных точек."
        )

        self.redraw()

    # --------------------------------------
    # ОЧИСТКА
    # --------------------------------------

    def clear(self):

        self.points = []
        self.hull = []
        self.current_step = 0

        self.status.config(
            text="Рабочее поле очищено."
        )

        self.redraw()

    # --------------------------------------
    # ПОСТРОЕНИЕ ОБОЛОЧКИ
    # --------------------------------------

    def build_hull(self):

        if len(self.points) < 3:

            messagebox.showwarning(
                "Предупреждение",
                "Для построения оболочки необходимо "
                "не менее трех различных точек."
            )

            return

        self.hull = jarvis_march(self.points)
        self.current_step = 0

        self.status.config(
            text=f"Оболочка найдена. Вершин: {len(self.hull)}. "
                 f"Нажимайте «Следующий шаг»."
        )

        self.redraw()

    # --------------------------------------
    # ПОШАГОВАЯ ОТРИСОВКА
    # --------------------------------------

    def next_step(self):

        if not self.hull:

            self.build_hull()

            if not self.hull:
                return

        if self.current_step < len(self.hull):

            self.current_step += 1

            self.redraw()

            if self.current_step == len(self.hull):

                self.status.config(
                    text="Построение завершено!"
                )

            else:

                self.status.config(
                    text=f"Построено ребер: "
                         f"{self.current_step} из {len(self.hull)}"
                )

    # --------------------------------------
    # ПОЛНАЯ ПЕРЕРИСОВКА
    # --------------------------------------

    def redraw(self):

        self.raster.clear()

        # Отрисовываем точки.
        for point in self.points:

            self.raster.draw_point(
                point[0],
                point[1],
                POINT_RADIUS,
                POINT_COLOR
            )

        # Отрисовываем уже построенные ребра.
        for i in range(self.current_step):

            a = self.hull[i]

            b = self.hull[
                (i + 1) % len(self.hull)
            ]

            self.raster.draw_line(
                a[0], a[1],
                b[0], b[1],
                HULL_COLOR
            )

        # Подсвечиваем текущее ребро.
        if self.hull and self.current_step < len(self.hull):

            a = self.hull[self.current_step]

            b = self.hull[
                (self.current_step + 1) % len(self.hull)
            ]

            self.raster.draw_line(
                a[0], a[1],
                b[0], b[1],
                CURRENT_COLOR
            )

        # Поверх линий снова рисуем точки,
        # чтобы вершины были хорошо видны.
        for point in self.points:

            self.raster.draw_point(
                point[0],
                point[1],
                POINT_RADIUS,
                POINT_COLOR
            )

        self.canvas.itemconfig(
            self.canvas.find_all()[0],
            image=self.raster.image
        )


# ==========================================
# ЗАПУСК ПРОГРАММЫ
# ==========================================

if __name__ == "__main__":

    root = tk.Tk()

    app = JarvisApplication(root)

    root.mainloop()

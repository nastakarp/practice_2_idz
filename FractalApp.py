import tkinter as tk
from math import sqrt


class FractalNode:
    def __init__(self, depth, p1, p2, p3, color):
        self.depth = depth
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.color = color
        self.children = []
        self.tree_x = 0  # Координаты узла в дереве
        self.tree_y = 0

    def add_child(self, child):
        self.children.append(child)


class FractalTree:
    def __init__(self, max_depth):
        self.max_depth = max_depth
        self.root = None
        self.colors = [
            '#1a237e', '#283593', '#3949ab',
            '#5c6bc0', '#7986cb', '#9fa8da',
            '#c5cae9', '#e8eaf6', '#d1c4e9',
            '#b39ddb', '#9575cd', '#7e57c2'
        ]

    def build(self, p1, p2, p3):
        self.root = self._build_recursive(p1, p2, p3, 0)

    def _build_recursive(self, p1, p2, p3, depth):
        color = self.colors[depth % len(self.colors)]
        node = FractalNode(depth, p1, p2, p3, color)

        if depth < self.max_depth:
            m12 = self.midpoint(p1, p2)
            m23 = self.midpoint(p2, p3)
            m31 = self.midpoint(p3, p1)

            center_top = self.midpoint(m12, p3)
            center_left = self.midpoint(m31, p2)
            center_right = self.midpoint(m23, p1)

            node.add_child(self._build_recursive(p1, m12, m31, depth + 1))
            node.add_child(self._build_recursive(m12, p2, m23, depth + 1))
            node.add_child(self._build_recursive(m31, m23, p3, depth + 1))
            node.add_child(self._build_recursive(center_top, center_left, center_right, depth + 1))

        return node

    @staticmethod
    def midpoint(p1, p2):
        return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


class FractalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Фрактал и дерево построения")

        # Параметры
        self.max_depth = 5
        self.base_size = 300
        self.tree_width = 800
        self.tree_height = 500
        self.selected_level = None
        self.node_radius = 15

        # Создание холстов
        self.fractal_canvas = tk.Canvas(root, width=600, height=500, bg='white')
        self.tree_canvas = tk.Canvas(root, width=self.tree_width, height=self.tree_height, bg='white')

        # Элементы управления
        self.control_frame = tk.Frame(root)

        # Управление уровнями
        self.level_control_frame = tk.Frame(self.control_frame)
        self.level_label = tk.Label(self.level_control_frame, text="Выберите уровень (0-5):")
        self.level_scale = tk.Scale(self.level_control_frame, from_=0, to=self.max_depth, orient=tk.HORIZONTAL,
                                    command=self.select_level)
        self.level_scale.set(self.max_depth)

        # Управление глубиной
        self.depth_control_frame = tk.Frame(self.control_frame)
        self.depth_label = tk.Label(self.depth_control_frame, text="Макс. уровней (1-5):")
        self.depth_scale = tk.Scale(self.depth_control_frame, from_=1, to=5, orient=tk.HORIZONTAL,
                                    command=self.change_max_depth)
        self.depth_scale.set(self.max_depth)

        # Размещение элементов
        self.fractal_canvas.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tree_canvas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.control_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")

        self.level_control_frame.pack(fill=tk.X, padx=5, pady=5)
        self.level_label.pack(side=tk.LEFT)
        self.level_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.depth_control_frame.pack(fill=tk.X, padx=5, pady=5)
        self.depth_label.pack(side=tk.LEFT)
        self.depth_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Инициализация фрактала и дерева
        self.init_fractal()
        self.calculate_tree_layout()  # Рассчитываем координаты дерева

        # Начальное отображение
        self.show_all_levels()

        # Привязка событий
        self.tree_canvas.bind("<Button-1>", self.on_tree_click)
        #self.root.bind("<Configure>", self.on_window_resize)  # Обработка изменения размеров окна

    def init_fractal(self):
        """Инициализация фрактала (без масштабирования)"""
        height = self.base_size * sqrt(3) / 2

        p1 = (100, 400)
        p2 = (100 + self.base_size, 400)
        p3 = (100 + self.base_size / 2, 400 - height)

        self.fractal_tree = FractalTree(self.max_depth)
        self.fractal_tree.build(p1, p2, p3)

    def calculate_tree_layout(self):
        """Предварительный расчет координат узлов дерева"""
        if not hasattr(self, 'fractal_tree') or not self.fractal_tree.root:
            return

        initial_dx = self.tree_width / (2 ** (self.fractal_tree.max_depth + 1))
        dy = 80

        # Рекурсивно вычисляем координаты
        self._calculate_node_position(
            self.fractal_tree.root,
            self.tree_width // 2, 30,
            initial_dx * 5, dy
        )

    def _calculate_node_position(self, node, x, y, dx, dy):
        """Рекурсивный расчет позиции узла и его детей"""
        node.tree_x = x
        node.tree_y = y

        if node.children:
            total_width = dx * (len(node.children) - 1)
            start_x = x - total_width / 2

            for i, child in enumerate(node.children):
                child_x = start_x + i * dx
                child_y = y + dy
                self._calculate_node_position(child, child_x, child_y, dx / 2, dy)

    def draw_fractal(self, node, selected_depth=None):
        """Отрисовка фрактала"""
        if selected_depth is None or node.depth == selected_depth:
            self.fractal_canvas.create_polygon(
                [node.p1, node.p2, node.p3],
                fill=node.color, outline='white'
            )

        for child in node.children:
            self.draw_fractal(child, selected_depth)

    def draw_tree(self, node):
        """Отрисовка дерева (использует предварительно рассчитанные координаты)"""
        if node is None:
            return

        outline = 'red' if self.selected_level == node.depth else 'black'
        width = 3 if self.selected_level == node.depth else 1

        self.tree_canvas.create_oval(
            node.tree_x - self.node_radius, node.tree_y - self.node_radius,
            node.tree_x + self.node_radius, node.tree_y + self.node_radius,
            fill=node.color, outline=outline, width=width
        )

        self.tree_canvas.create_text(
            node.tree_x, node.tree_y, text=str(node.depth),
            font=('Arial', 10), fill='white'
        )

        for child in node.children:
            self.tree_canvas.create_line(
                node.tree_x, node.tree_y + self.node_radius,
                child.tree_x, child.tree_y - self.node_radius,
                fill=node.color, width=2
            )
            self.draw_tree(child)

    def on_tree_click(self, event):
        clicked_node = self.find_clicked_node(self.fractal_tree.root, event.x, event.y)
        if clicked_node:
            self.selected_level = clicked_node.depth
            self.level_scale.set(self.selected_level)
            self.update_display()

    def find_clicked_node(self, node, x, y):
        if ((node.tree_x - x) ** 2 + (node.tree_y - y) ** 2) <= self.node_radius ** 2:
            return node

        for child in node.children:
            found = self.find_clicked_node(child, x, y)
            if found:
                return found
        return None

    def update_display(self):
        self.fractal_canvas.delete("all")
        self.tree_canvas.delete("all")

        if self.selected_level is not None:
            self.draw_fractal(self.fractal_tree.root, self.selected_level)
        else:
            self.draw_fractal(self.fractal_tree.root)

        self.draw_tree(self.fractal_tree.root)

    def select_level(self, value):
        self.selected_level = int(value)
        self.update_display()

    def change_max_depth(self, value):
        self.max_depth = int(value)
        self.level_scale.config(to=self.max_depth)
        self.init_fractal()
        self.calculate_tree_layout()  # Пересчитываем координаты дерева
        self.show_all_levels()

    def on_window_resize(self, event):
        """Обработка изменения размеров окна"""
        if event.widget == self.root:
            new_tree_width = event.width // 2
            new_tree_height = event.height - 100

            if new_tree_width > 0 and new_tree_height > 0:
                self.tree_width = new_tree_width
                self.tree_height = new_tree_height
                self.tree_canvas.config(width=self.tree_width, height=self.tree_height)
                self.calculate_tree_layout()  # Пересчитываем координаты дерева
                self.update_display()

    def show_all_levels(self):
        self.selected_level = None
        self.level_scale.set(self.max_depth)
        self.update_display()


if __name__ == "__main__":
    root = tk.Tk()
    app = FractalApp(root)
    root.mainloop()
import tkinter as tk
import random
BOARD_SIZE = 10
FLEET_SIZES = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
def get_neighbors(x, y):
    neighbors = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0: continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE: neighbors.append((nx, ny))
    return neighbors
class Board:
    def __init__(self):
        self.grid = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.ships = []
    def can_place_ship(self, x, y, length, horizontal):
        cells = []
        for i in range(length):
            cell_x = x + i if horizontal else x
            cell_y = y if horizontal else y + i
            if not (0 <= cell_x < BOARD_SIZE and 0 <= cell_y < BOARD_SIZE): return False
            if self.grid[cell_y][cell_x] != 0: return False
            cells.append((cell_x, cell_y))
        for cell_x, cell_y in cells:
            for nx, ny in get_neighbors(cell_x, cell_y):
                if self.grid[ny][nx] == 1: return False
        return True
    def place_ship(self, x, y, length, horizontal):
        if not self.can_place_ship(x, y, length, horizontal): return False
        ship_cells = []
        for i in range(length):
            cell_x = x + i if horizontal else x
            cell_y = y if horizontal else y + i
            self.grid[cell_y][cell_x] = 1
            ship_cells.append((cell_x, cell_y))
        self.ships.append(set(ship_cells))
        return True
    def remove_ship_at(self, x, y):
        for ship in list(self.ships):
            if (x, y) in ship:
                for cell_x, cell_y in ship:
                    self.grid[cell_y][cell_x] = 0
                self.ships.remove(ship)
                return len(ship)
        return 0
    def randomize_fleet(self):
        self.__init__()
        for ship_size in FLEET_SIZES:
            for _ in range(3000):
                horizontal = random.choice([True, False])
                max_x = BOARD_SIZE - ship_size if horizontal else BOARD_SIZE - 1
                max_y = BOARD_SIZE - 1 if horizontal else BOARD_SIZE - ship_size
                x = random.randint(0, max_x)
                y = random.randint(0, max_y)
                if self.place_ship(x, y, ship_size, horizontal): break
        return True
    def shoot(self, x, y):
        cell_value = self.grid[y][x]
        if cell_value in (-1, 2, 3): return "repeat", None
        if cell_value == 0:
            self.grid[y][x] = -1
            return "miss", None
        self.grid[y][x] = 2
        for ship in self.ships:
            if (x, y) in ship:
                if all(self.grid[cy][cx] == 2 for cx, cy in ship):
                    for cx, cy in ship:
                        self.grid[cy][cx] = 3
                    for cx, cy in ship:
                        for nx, ny in get_neighbors(cx, cy):
                            if self.grid[ny][nx] == 0:
                                self.grid[ny][nx] = -1
                    return "sunk", ship
                return "hit", ship
        return "miss", None
    def all_ships_sunk(self):
        for ship in self.ships:
            for x, y in ship:
                if self.grid[y][x] != 3: return False
        return True
class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Морской бой")
        self.root.geometry("1200x720")
        self.player_board = Board()
        self.enemy_board = Board()
        self.game_phase = "prep"
        self.dragging_ship = None
        self.ship_horizontal = True
        self.ships_to_place = {1: 4, 2: 3, 3: 2, 4: 1}
        self.last_mouse_pos = (0, 0)
        self.canvas = tk.Canvas(self.root, width=1200, height=720, bg="black")
        self.canvas.pack()
        self.padding = 32
        self.cell_size = 28
        self.player_board_pos = (self.padding + 220 + 16, 140)
        self.enemy_board_pos = (self.player_board_pos[0] + BOARD_SIZE * self.cell_size + 80, 140)
        self.panel_pos = (self.padding, 140)
        self.message = tk.StringVar()
        self.message.set("Расставьте флот и нажмите «Старт».")
        tk.Label(self.root, textvariable=self.message, bg="black", fg="white", font=("Arial", 11)).place(relx=0.5, y=68,
                                                                                                         anchor="n")
        self.create_toolbar()
        self.bind_events()
        self.draw()
    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bg="black")
        toolbar.place(relx=0.5, rely=1.0, x=0, y=-28, anchor="s")
        tk.Button(toolbar, text="Случайно", command=self.randomize_player_fleet, bg="gray", fg="white").grid(row=0,
                                                                                                             column=0,                                                                                                  padx=6)
        tk.Button(toolbar, text="Очистить", command=self.clear_player_fleet, bg="gray", fg="white").grid(row=0,
                                                                                                         column=1,
                                                                                                         padx=6)
        tk.Button(toolbar, text="Старт", command=self.start_game, bg="gray", fg="white").grid(row=0, column=2, padx=16)
        tk.Button(toolbar, text="Новая игра", command=self.new_game, bg="gray", fg="white").grid(row=0, column=3,
                                                                                                 padx=6)
    def bind_events(self):
        self.root.bind("<Button-1>", self.on_mouse_down)
        self.root.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.root.bind("<Motion>", self.on_mouse_move)
        self.root.bind("<Key-r>", self.rotate_ship)
        self.root.bind("<Key-n>", lambda e: self.new_game())
    def new_game(self):
        self.player_board = Board()
        self.enemy_board = Board()
        self.game_phase = "prep"
        self.dragging_ship = None
        self.ship_horizontal = True
        self.ships_to_place = {1: 4, 2: 3, 3: 2, 4: 1}
        self.message.set("Новая игра. Расставьте корабли или нажмите «Случайно».")
        self.draw()
    def draw(self):
        self.canvas.delete("all")
        self.draw_background()
        self.draw_boards()
        if self.game_phase == "prep":
            self.draw_ship_panel()
            self.draw_drag_preview()
    def draw_background(self):
        self.canvas.create_rectangle(0, 0, 1200, 720, fill="black")
        self.canvas.create_rectangle(0, 56, self.panel_pos[0] + 200, 720, fill="#111")
    def draw_boards(self):
        self.draw_grid(self.player_board_pos[0], self.player_board_pos[1], "ТВОЙ ФЛОТ", "blue", True)
        self.draw_cells(self.player_board, self.player_board_pos[0], self.player_board_pos[1], True)
        show_enemy_ships = self.game_phase != "battle"
        self.draw_grid(self.enemy_board_pos[0], self.enemy_board_pos[1], "ФЛОТ БОТА", "red", False)
        self.draw_cells(self.enemy_board, self.enemy_board_pos[0], self.enemy_board_pos[1], show_enemy_ships)
    def draw_grid(self, x, y, title, color, show_coords):
        self.canvas.create_rectangle(x - 10, y - 10, x + BOARD_SIZE * self.cell_size + 10,
                                     y + BOARD_SIZE * self.cell_size + 10, outline="gray", width=2)
        self.canvas.create_text(x + BOARD_SIZE * self.cell_size / 2, y - 40, text=title, fill=color)
        if show_coords:
            for i in range(BOARD_SIZE):
                self.canvas.create_text(x + i * self.cell_size + self.cell_size / 2, y - 4, fill="white",
                                        text=chr(65 + i))
                self.canvas.create_text(x - 14, y + i * self.cell_size + self.cell_size / 2, fill="white",
                                        text=str(i + 1))
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x1 = x + col * self.cell_size
                y1 = y + row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="gray", width=1)
    def draw_cells(self, board, x, y, show_ships):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                cell_value = board.grid[row][col]
                x1 = x + col * self.cell_size
                y1 = y + row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                if show_ships and cell_value == 1:
                    self.canvas.create_rectangle(x1 + 3, y1 + 6, x2 - 3, y2 - 6, fill="green", outline="")
                elif cell_value == -1:
                    self.canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10, outline="gray", width=2)
                elif cell_value == 2:
                    self.canvas.create_oval(x1 + 6, y1 + 6, x2 - 6, y2 - 6, fill="orange", outline="")
                elif cell_value == 3:
                    self.canvas.create_rectangle(x1 + 4, y1 + 4, x2 - 4, y2 - 4, fill="red", outline="")
    def draw_ship_panel(self):
        x, y = self.panel_pos
        height = BOARD_SIZE * self.cell_size
        self.canvas.create_rectangle(x - 8, y - 16, x + 196, y + height + 24, fill="#111", outline="gray", width=2)
        self.canvas.create_text(x + 96, y - 24, fill="cyan", text="Док кораблей")
        self.ship_rectangles = []
        current_y = y + 8
        for size in [4, 3, 2, 1]:
            self.canvas.create_rectangle(x + 12, current_y, x + 184, current_y + 32, outline="gray", width=1)
            for i in range(size):
                self.canvas.create_rectangle(x + 16 + i * 26, current_y + 6, x + 16 + i * 26 + 22, current_y + 26,
                                             fill="green", outline="")
            count = self.ships_to_place.get(size, 0)
            self.canvas.create_text(x + 170, current_y + 16, fill="white", text=f"x{count}")
            self.ship_rectangles.append((size, (x + 12, current_y, x + 184, current_y + 32)))
            current_y += 38
    def draw_drag_preview(self):
        if not self.dragging_ship: return
        mouse_x, mouse_y = self.last_mouse_pos
        board_x, board_y = self.player_board_pos
        cell = self.get_cell_from_coords(board_x, board_y, mouse_x, mouse_y)
        if not cell: return
        ship_size = self.dragging_ship["size"]
        horizontal = self.dragging_ship["horizontal"]
        can_place = self.player_board.can_place_ship(cell[0], cell[1], ship_size, horizontal)
        for i in range(ship_size):
            cell_x = cell[0] + i if horizontal else cell[0]
            cell_y = cell[1] if horizontal else cell[1] + i
            if 0 <= cell_x < BOARD_SIZE and 0 <= cell_y < BOARD_SIZE:
                x1 = board_x + cell_x * self.cell_size
                y1 = board_y + cell_y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                color = "lightgreen" if can_place else "red"
                self.canvas.create_rectangle(x1 + 3, y1 + 3, x2 - 3, y2 - 3, outline=color, width=2, dash=(4, 2))
    def get_cell_from_coords(self, board_x, board_y, mouse_x, mouse_y):
        cell_x = (mouse_x - board_x) // self.cell_size
        cell_y = (mouse_y - board_y) // self.cell_size
        if 0 <= cell_x < BOARD_SIZE and 0 <= cell_y < BOARD_SIZE:
            return (cell_x, cell_y)
        return None
    def get_ship_from_panel(self, x, y):
        for size, (x1, y1, x2, y2) in self.ship_rectangles:
            if x1 <= x <= x2 and y1 <= y <= y2:
                return size
        return None
    def rotate_ship(self, event=None):
        if self.game_phase != "prep": return
        if self.dragging_ship:
            self.dragging_ship["horizontal"] = not self.dragging_ship["horizontal"]
        else:
            self.ship_horizontal = not self.ship_horizontal
        self.draw()
    def on_mouse_down(self, event):
        self.last_mouse_pos = (event.x, event.y)
        if self.game_phase == "prep":
            self.handle_prep_phase_click(event.x, event.y)
        elif self.game_phase == "battle":
            self.handle_battle_phase_click(event.x, event.y)
    def handle_prep_phase_click(self, x, y):
        board_x, board_y = self.player_board_pos
        cell = self.get_cell_from_coords(board_x, board_y, x, y)
        if cell and self.player_board.grid[cell[1]][cell[0]] == 1:
            ship_size = self.player_board.remove_ship_at(cell[0], cell[1])
            if ship_size:
                self.ships_to_place[ship_size] = self.ships_to_place.get(ship_size, 0) + 1
                self.draw()
                return
        ship_size = self.get_ship_from_panel(x, y)
        if ship_size and self.ships_to_place.get(ship_size, 0) > 0:
            self.dragging_ship = {"size": ship_size, "horizontal": self.ship_horizontal}
    def handle_battle_phase_click(self, x, y):
        board_x, board_y = self.enemy_board_pos
        cell = self.get_cell_from_coords(board_x, board_y, x, y)
        if cell:
            self.player_shoot(cell[0], cell[1])
    def on_mouse_move(self, event):
        self.last_mouse_pos = (event.x, event.y)
        if self.game_phase == "prep" and self.dragging_ship:
            self.draw()
    def on_mouse_up(self, event):
        self.last_mouse_pos = (event.x, event.y)
        if self.game_phase != "prep" or not self.dragging_ship: return
        board_x, board_y = self.player_board_pos
        cell = self.get_cell_from_coords(board_x, board_y, event.x, event.y)
        if cell:
            ship_size = self.dragging_ship["size"]
            horizontal = self.dragging_ship["horizontal"]
            if self.player_board.place_ship(cell[0], cell[1], ship_size, horizontal):
                self.ships_to_place[ship_size] -= 1
        self.dragging_ship = None
        self.draw()
    def randomize_player_fleet(self):
        if self.game_phase != "prep": return
        self.player_board.randomize_fleet()
        self.ships_to_place = {1: 0, 2: 0, 3: 0, 4: 0}
        self.draw()
    def clear_player_fleet(self):
        if self.game_phase != "prep": return
        self.player_board = Board()
        self.ships_to_place = {1: 4, 2: 3, 3: 2, 4: 1}
        self.dragging_ship = None
        self.draw()
    def start_game(self):
        if self.game_phase != "prep": return
        if any(count > 0 for count in self.ships_to_place.values()):
            self.message.set("Сначала расставьте все корабли или нажмите «Случайно».")
            return
        self.enemy_board.randomize_fleet()
        self.game_phase = "battle"
        self.message.set("Бой начался. Стреляйте по правому полю.")
        self.draw()
    def player_shoot(self, x, y):
        result, _ = self.enemy_board.shoot(x, y)
        if result == "repeat": return
        self.draw()
        if self.enemy_board.all_ships_sunk():
            self.message.set("Вы победили! N - новая игра.")
            self.game_phase = "end"
            return
        if result == "miss":
            self.root.after(300, self.ai_turn)
        else: self.message.set("Попадание. Стреляйте снова.")
    def ai_turn(self):
        if self.player_board.all_ships_sunk():
            self.message.set("Бот победил. N - новая игра.")
            self.game_phase = "end"
            self.draw()
            return
        x, y = self.choose_ai_target()
        result, _ = self.player_board.shoot(x, y)
        self.draw()
        if result == "hit":
            self.message.set(f"бот попал в {chr(65 + x)}{y + 1} и продолжает атаку…")
            self.root.after(220, self.ai_turn)
            return
        elif result == "sunk":
            self.message.set("бот потопил ваш корабль.")
            self.root.after(220, self.ai_turn)
            return
        else: self.message.set("бот промахнулся. Ваш ход.")
    def choose_ai_target(self):
        board = self.player_board.grid
        hits = []
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if board[y][x] == 2:
                    hits.append((x, y))
        random.shuffle(hits)
        for hx, hy in hits:
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = hx + dx, hy + dy
                if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                    if board[ny][nx] not in (-1, 2, 3):
                        return nx, ny
        candidates = []
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if board[y][x] not in (-1, 2, 3):
                    candidates.append((x, y))
        return random.choice(candidates) if candidates else (0, 0)
if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()
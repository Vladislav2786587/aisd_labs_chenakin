import tkinter as tk
from tkinter import messagebox
import winsound
from enum import Enum
from PIL import Image, ImageTk, ImageDraw
import os

class MicrowaveState(Enum):
    WAITING = "waiting"
    RUNNING = "running"
    FINISHED = "finished"
    PAUSED = "paused"

class Microwave:
    def __init__(self):
        self.state = MicrowaveState.WAITING
        self.time_left = 0
        self.is_door_open = False
        self.selected_food = None
        self.max_time = 60 * 60

    def set_time(self, seconds):
        if self.state == MicrowaveState.RUNNING:
            return False
        if not isinstance(seconds, int) or seconds < 0 or seconds > self.max_time:
            return False
        self.time_left = seconds
        return True

    def add_time(self, seconds):
        return self.set_time(self.time_left + seconds)

    def subtract_time(self, seconds):
        return self.set_time(self.time_left - seconds)

    def start(self):
        if self.is_door_open or self.time_left <= 0 or self.selected_food is None:
            return False
        if self.state in [MicrowaveState.WAITING, MicrowaveState.PAUSED, MicrowaveState.FINISHED]:
            self.state = MicrowaveState.RUNNING
            return True
        return False

    def stop(self):
        self.state = MicrowaveState.WAITING
        self.time_left = 0
        self.selected_food = None
        return True

    def open_door(self):
        self.is_door_open = True
        if self.state == MicrowaveState.RUNNING:
            self.state = MicrowaveState.PAUSED
        return True

    def close_door(self):
        self.is_door_open = False
        return True

    def tick(self):
        if self.state != MicrowaveState.RUNNING:
            return False
        if self.time_left > 0:
            self.time_left -= 1
            if self.time_left == 0:
                self.state = MicrowaveState.FINISHED
                return "finished"
            return "tick"
        return False

    def get_time_display(self):
        return f"{self.time_left // 60:02d}:{self.time_left % 60:02d}"

    def can_start(self):
        return not self.is_door_open and self.time_left > 0 and self.state in [MicrowaveState.WAITING, MicrowaveState.PAUSED]

class MicrowaveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Микроволновая печь")
        self.root.geometry("750x400")
        self.root.resizable(False, False)

        self.microwave = Microwave()
        self.time_left = 0
        self.timer_id = None
        self.rotation_angle = 0
        self.food_on_plate = None
        self.food_images = {}

        self.load_food_images()

        self.canvas = tk.Canvas(self.root, width=750, height=375, bg="#1E1E1E", highlightthickness=0)
        self.canvas.pack()

        self.display_text_id = None
        self.door_button = None
        
        self.blink_state = True
        self.blink_job = None

        self.steam_ids = []
        self.rotation_angle_y = 0 
        
        self.draw_microwave()
        self.create_buttons()
        self.create_food_selection()
        self.update_display()

    def load_food_images(self):
        """Загружает изображения продуктов"""
        food_dir = "foods"
        for food_name in ["Курица", "Пельмени", "Сосиски", "Хачапури", "Чебурек", "Шава"]:
            file_name = food_name.lower() + ".png"
            path = os.path.join(food_dir, file_name)
            if os.path.exists(path):
                try:
                    img = Image.open(path).convert("RGBA")
                    self.food_images[food_name] = img
                except Exception as e:
                    print(f"Ошибка загрузки {file_name}: {e}")

    def create_food_selection(self):
        frame = tk.Frame(self.root, bg="#1E1E1E", height=30)
        frame.pack(side=tk.BOTTOM, fill=tk.X, pady=0)

        tk.Label(frame, text="Выберите продукт:", bg="#1E1E1E", fg="#E0E0E0", font=("Consolas", 10)).pack(side=tk.LEFT, padx=10)

        foods = ["Курица", "Пельмени", "Сосиски", "Хачапури", "Чебурек", "Шава"]
        for food in foods:
            btn = tk.Button(
                frame,
                text=food,
                width=8,
                font=("Consolas", 9),
                bg="#333333",
                fg="#E0E0E0",
                activebackground="#444444",
                activeforeground="#4CFF96",
                command=lambda f=food: self.select_food(f)
            )
            btn.pack(side=tk.LEFT, padx=5)

        self.food_label = tk.Label(frame, text="Не выбрано", bg="#1E1E1E", fg="#FF6B6B", font=("Consolas", 10))
        self.food_label.pack(side=tk.RIGHT, padx=20)

    def select_food(self, food_name):
        if not self.microwave.is_door_open:
            return
        
        self.microwave.selected_food = food_name
        self.food_label.config(text=f"Выбрано: {food_name}", fg="#4CFF96")
        self.update_display()

    def draw_microwave(self):
        self.canvas.delete("microwave")


        body_x1, body_y1 = 80, 40
        body_x2, body_y2 = 700, 330
        self.canvas.create_rectangle(
            body_x1, body_y1, body_x2, body_y2,
            fill="#d0d0d0", outline="#8f8f8f", width=3,
            tags="microwave"
        )

        self.canvas.create_rectangle(
            body_x1, body_y1, body_x2, body_y1 + 10,
            fill="#e5e5e5", outline="",
            tags="microwave"
        )
        self.canvas.create_rectangle(
            body_x1, body_y2 - 12, body_x2, body_y2,
            fill="#b0b0b0", outline="",
            tags="microwave"
        )

        door_x1, door_y1 = 100, 60
        door_x2, door_y2 = 470, 310

        if not self.microwave.is_door_open:
            self.canvas.create_rectangle(
                door_x1, door_y1, door_x2, door_y2,
                fill="#202020", outline="#101010", width=2,
                tags="microwave"
            )

            glass_margin = 18
            glass_x1 = door_x1 + glass_margin
            glass_y1 = door_y1 + glass_margin
            glass_x2 = door_x2 - glass_margin
            glass_y2 = door_y2 - glass_margin

            self.canvas.create_rectangle(
                glass_x1, glass_y1, glass_x2, glass_y2,
                fill="#2f2f2f", outline="#050505", width=1,
                tags="microwave"
            )

            for x in range(glass_x1 + 5, glass_x2, 10):
                self.canvas.create_line(
                    x, glass_y1 + 3, x, glass_y2 - 3,
                    fill="#3a3a3a",
                    tags="microwave"
                )
            for y in range(glass_y1 + 5, glass_y2, 10):
                self.canvas.create_line(
                    glass_x1 + 3, y, glass_x2 - 3, y,
                    fill="#3a3a3a",
                    tags="microwave"
                )
            
            self.canvas.create_oval(
                170, 290, 400, 265,
                fill="#f7f7f7", outline="#bfbfbf",
                tags="microwave"
            )


            handle_x1 = door_x2 - 18
            handle_x2 = door_x2 - 4
            self.canvas.create_rectangle(
                handle_x1, door_y1 + 25, handle_x2, door_y2 - 25,
                fill="#e0e0e0", outline="#a0a0a0", width=2,
                tags="microwave"
            )

            self.draw_food_inside()
        else:
            self.canvas.create_rectangle(
                door_x1 - 6, door_y1 + 20, door_x1, door_y2 - 20,
                fill="#8f8f8f", outline="#5f5f5f", width=1,
                tags="microwave"
            )

            open_x1 = 30
            open_y1 = 70
            open_x2 = door_x1
            open_y2 = door_y2 - 10

            self.canvas.create_polygon(
                open_x1, open_y1,
                open_x2, door_y1,
                open_x2, door_y2,
                open_x1, open_y2,
                fill="#252525", outline="#101010", width=2,
                tags="microwave"
            )

            inner_margin = 14
            self.canvas.create_polygon(
                open_x1 + inner_margin, open_y1 + inner_margin,
                open_x2 - inner_margin, door_y1 + inner_margin,
                open_x2 - inner_margin, door_y2 - inner_margin,
                open_x1 + inner_margin, open_y2 - inner_margin,
                fill="#1E1E1E", outline="#050505", width=1,
                tags="microwave"
            )

            self.canvas.create_rectangle(
                open_x1 + 4, open_y1 + 40,
                open_x1 + 14, open_y2 - 40,
                fill="#e0e0e0", outline="#a0a0a0", width=1,
                tags="microwave"
            )

            cavity_x1 = door_x1 + 5
            cavity_y1 = door_y1 + 10
            cavity_x2 = door_x2 - 5
            cavity_y2 = door_y2 - 10
            self.canvas.create_rectangle(
                cavity_x1, cavity_y1, cavity_x2, cavity_y2,
                fill="#3a3a3a", outline="#1e1e1e", width=1,
                tags="microwave"
            )

            self.canvas.create_oval(
                145, 260, 425, 295,
                fill="#f7f7f7", outline="#bfbfbf",
                tags="microwave"
            )
            
            self.draw_food_inside()

        panel_x1 = 480
        panel_y1 = 55
        panel_x2 = 690
        panel_y2 = 315
        self.canvas.create_rectangle(
            panel_x1, panel_y1, panel_x2, panel_y2,
            fill="#151515", outline="#050505", width=2,
            tags="microwave"
        )

        display_x1 = panel_x1 + 10
        display_y1 = panel_y1 + 10
        display_x2 = panel_x2 - 10
        display_y2 = panel_y1 + 60
        self.canvas.create_rectangle(
            display_x1, display_y1, display_x2, display_y2,
            fill="#111111", outline="#333333", width=2,
            tags="microwave"
        )

        self.canvas.create_text(
            (display_x1 + display_x2) // 2,
            (display_y1 + display_y2) // 2,
            text="",
            fill="#4CFF96",
            font=("Consolas", 18, "bold"),
            tags="microwave"
        )
        self.update_display_text()

        self.canvas.create_text(
            (body_x1 + body_x2) // 2, body_y2 + 15,
            text="MICROWAVE 900W",
            fill="#808080",
            font=("Calibri", 11),
            tags="microwave"
        )

    def draw_food_inside(self):
        if self.food_on_plate:
            self.canvas.delete(self.food_on_plate)
            self.food_on_plate = None

        if not self.microwave.selected_food:
            return

        cam_left, cam_top = 140, 120
        cam_right, cam_bottom = 420, 300
        cam_width = cam_right - cam_left
        cam_height = cam_bottom - cam_top

        center_x = cam_width // 2
        center_y = cam_height // 2

        cam_img = Image.new("RGBA", (cam_width, cam_height), (0, 0, 0, 0))

        food_name = self.microwave.selected_food
        if food_name in self.food_images:
            food_img = self.food_images[food_name]
            food_size = 200
            food_img = food_img.resize((food_size, food_size), Image.LANCZOS)

            display_img = self.y_rotate_image(food_img, self.rotation_angle_y)

            food_pos = (
                center_x - food_size // 2,
                center_y - food_size // 2
            )
            cam_img.paste(display_img, food_pos, display_img)

        cam_photo = ImageTk.PhotoImage(cam_img)
        self.food_on_plate = self.canvas.create_image(
            cam_left, cam_top, image=cam_photo, anchor="nw", tags="food"
        )
        self.canvas.cam_cache = cam_photo

    def create_buttons(self):
        btn_font = ("Segoe UI", 10, "bold")

        self.btn_start = tk.Button(
            self.root, text="START / PAUSE", width=10, height=2,
            bg="#33aa33", fg="white", activebackground="#44cc44",
            font=btn_font, bd=0, relief="flat",
            command=self.start
        )

        self.btn_stop = tk.Button(
            self.root, text="STOP / RESET", width=10, height=2,
            bg="#cc3333", fg="white", activebackground="#ee4444",
            font=btn_font, bd=0, relief="flat",
            command=self.stop
        )

        self.btn_30 = tk.Button(
            self.root, text="+30 sec", width=10, height=2,
            bg="#444444", fg="#f0f0f0", activebackground="#555555",
            font=btn_font, bd=0, relief="flat",
            command=lambda: self.add_time(30)
        )

        self.btn_60 = tk.Button(
            self.root, text="+1 min", width=10, height=2,
            bg="#444444", fg="#f0f0f0", activebackground="#555555",
            font=btn_font, bd=0, relief="flat",
            command=lambda: self.add_time(60)
        )

        self.btn_minus10 = tk.Button(
            self.root, text="-10 sec", width=10, height=2,
            bg="#444444", fg="#f0f0f0", activebackground="#555555",
            font=btn_font, bd=0, relief="flat",
            command=lambda: self.subtract_time(10)
        )

        self.door_button = tk.Button(
            self.root, text="OPEN\nDOOR", width=10, height=2,
            bg="#888888", fg="white", activebackground="#aaaaaa",
            font=btn_font, bd=0, relief="flat",
            command=self.toggle_door
        )

        self.btn_start.place(x=490, y=140)
        self.btn_stop.place(x=590, y=140)

        self.btn_minus10.place(x=490, y=200)
        self.btn_30.place(x=590, y=200)
        self.btn_60.place(x=490, y=260)

        self.door_button.place(x=590, y=260)

    def update_display_text(self):
        if self.display_text_id:
            self.canvas.delete(self.display_text_id)

        if self.microwave.is_door_open:
            if self.microwave.selected_food:
                text = "ДВЕРЬ ОТКРЫТА\nзакройте дверь"
            else:
                text = "ДВЕРЬ ОТКРЫТА\nвыберите продукт"
            color = "#FFD666"  
        else:
            time_str = self.microwave.get_time_display()
            
            if self.microwave.state == MicrowaveState.PAUSED:
                if not self.blink_state:
                    time_str = time_str.replace(":", " ")
            else:
                self.blink_state = True
            
            if self.microwave.selected_food:
                text = f"{time_str}\n{self.microwave.selected_food}"
            else:
                text = f"{time_str}\nоткройте дверцу"
            color = "#4CFF96" 

        self.display_text_id = self.canvas.create_text(
            585, 90, text=text, fill=color,
            font=("Consolas", 15, "bold"), justify="center", tags="microwave"
        )
        
    def start_blink(self):
        if self.blink_job is not None:
            return
        self._blink_tick()
    
    def stop_blink(self):
        if self.blink_job is not None:
            self.root.after_cancel(self.blink_job)
            self.blink_job = None
            self.blink_state = True
            self.update_display_text()
        
    def _blink_tick(self):
        if self.microwave.state != MicrowaveState.PAUSED:
            self.stop_blink()
            return
        self.blink_state = not self.blink_state
        self.update_display_text()
        self.blink_job = self.root.after(500, self._blink_tick)
    
    def update_display(self):
        self.time_left = self.microwave.time_left
        self.update_display_text()
        if self.door_button:
            self.door_button.config(text="закрыть\nдверь" if self.microwave.is_door_open else "открыть\nдверь")
        self.draw_microwave()

    def add_time(self, seconds):
        if not self.microwave.is_door_open and not self.microwave.state == MicrowaveState.RUNNING:
            self.microwave.add_time(seconds)
            self.update_display()

    def subtract_time(self, seconds):
        if not self.microwave.is_door_open and not self.microwave.state == MicrowaveState.RUNNING:
            self.microwave.subtract_time(seconds)
            self.update_display()

    def start(self):
        if self.microwave.state == MicrowaveState.RUNNING:
            self.microwave.state = MicrowaveState.PAUSED
            self.cancel_timer()
            self.start_blink()
            self.update_display()
            return

        if self.microwave.state == MicrowaveState.PAUSED:
            self.stop_blink()

        if self.microwave.start():
            self.update_display()
            self.rotation_angle_y = 0
            self.start_rotation_animation()
            self.run_timer()

    def stop(self):
        self.microwave.stop()
        self.cancel_timer()
        self.rotation_angle = 0
        self.stop_blink()
        self.update_display()

    def toggle_door(self):
        was_open = self.microwave.is_door_open
        if was_open:
            self.microwave.close_door()
        else:
            self.microwave.open_door()
        self.draw_microwave()
        self.update_display()

    def start_rotation_animation(self):
        if self.microwave.state == MicrowaveState.RUNNING and not self.microwave.is_door_open:
            self.animate_rotation()

    def animate_rotation(self):
        if self.microwave.state != MicrowaveState.RUNNING or self.microwave.is_door_open:
            return
        self.rotation_angle_y = (self.rotation_angle_y + 10) % 360
        self.draw_food_inside()
        self.root.after(100, self.animate_rotation)

    def run_timer(self):
        self.cancel_timer()
        self._tick()

    def cancel_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def _tick(self):
        if self.microwave.state == MicrowaveState.RUNNING:
            result = self.microwave.tick()
            self.update_display()
            if result == "finished":
                self.on_finish()
                return    
            self.timer_id = self.root.after(1000, self._tick)

    def on_finish(self):
        self.rotation_angle = 0
        self.cancel_timer()

        self.microwave.open_door()
        self.update_display()

        self.draw_steam()
        
        def play_beep(times_left):
            if times_left <= 0:
                return
            try:
                winsound.Beep(1000, 1000)  # 1 секунды
            except:
                pass
            self.root.after(500, lambda: play_beep(times_left - 1))

        play_beep(3)
        
    def draw_steam(self):
        for sid in getattr(self, "steam_ids", []):
            self.canvas.delete(sid)
        self.steam_ids = []

        if not self.microwave.selected_food:
            return

        cam_left, cam_top = 140, 50
        cam_right, cam_bottom = 420, 270
        cam_center_x = (cam_left + cam_right) // 2

        base_y = cam_top + 40
        h = 55
        color = "#d8d8d8"

        offsets = [-30, 0, 30]

        for dx in offsets:
            x = cam_center_x + dx

            points = [
                x,          base_y + h,
                x - 10,     base_y + h*0.7,
                x + 10,     base_y + h*0.4,
                x - 8,      base_y + h*0.2,
                x + 5,      base_y,
            ]

            sid = self.canvas.create_line(
                points,
                smooth=True,
                splinesteps=20,
                width=3,
                fill=color,
                capstyle="round",
                tags="steam"
            )
            self.steam_ids.append(sid)
        
    def y_rotate_image(self, img, angle):
        import math

        a = angle % 360

        if a <= 90 or 270 <= a <= 360:
            front = True
            a_local = a
        else:
            front = False
            a_local = 360 - a

        k = abs(math.cos(math.radians(a_local)))
        k = max(0.1, k)

        w, h = img.size
        new_w = max(1, int(w * k))

        base = img
        if not front:
            base = img.transpose(Image.FLIP_LEFT_RIGHT)

        squeezed = base.resize((new_w, h), Image.LANCZOS)

        result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        x_offset = (w - new_w) // 2
        result.paste(squeezed, (x_offset, 0), squeezed)

        return result
        
if __name__ == "__main__":
    root = tk.Tk()
    app = MicrowaveApp(root)
    root.mainloop()
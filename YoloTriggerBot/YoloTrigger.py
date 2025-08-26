import win32api, win32con, win32gui
import ctypes # for dynamic resolution
import json # for gun settings
import tkinter as tk
from customtkinter import *
import numpy as np
import ultralytics
import threading
import math
import time 
import cv2
import mss
import random
import winsound

# добавить в settings к оружию индивидуальную настройку shoot delay для автоматической стрельбы

# for showing Ai work in GUI
from PIL import Image, ImageTk

from tkinter import ttk

# RECOIL LOAD NAME.TXT
import json

def load_spray_pattern(filename):
    patterns_path = os.path.join(os.path.dirname(__file__), "patterns")
    full_path = os.path.join(patterns_path, filename)

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = json.load(f)  # Пробуем как JSON
    except json.JSONDecodeError:
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = eval(f.read())  # Fallback для старых файлов
                print(f"[WARNING] Used eval fallback for {filename}. Consider resaving.")
        except Exception as e:
            print(f"[ERROR] Failed to load {filename}: {e}")
            return [], [], []  # name, steps, step_delay from file

    pattern = content.get("pattern", [])
    steps = content.get("steps", [])
    step_delay = content.get("step_delay", [])
    return pattern, steps, step_delay

#=== MODES FOR MOUSE BUTTON
mode_index = 0  # текущий режим
MODES = ["AI_OFF", "AI_ON", "AI/RECOIL_ON"]

# SWITCH MODE
def switch_mode():
    global mode_index
    mode_index = (mode_index + 1) % len(MODES)
    mode = MODES[mode_index]
    print(f"[MODE] Switched to: {mode}")

    # Цвета прицела в зависимости от режима
    colors = {
        "AI_OFF": "red",
        "AI_ON": "hotpink",
        "AI/RECOIL_ON": "purple"
    }

    # Логика переключения режимов
    if mode == "AI_OFF":
        config.AimToggle = False
        config.recoil_control = False
        #winsound.Beep(400, 100)

    elif mode == "AI_ON":
        config.AimToggle = True
        config.recoil_control = False
        #winsound.Beep(800, 100)

    elif mode == "AI/RECOIL_ON":
        config.AimToggle = True
        config.recoil_control = True
        #winsound.Beep(1200, 100)

    # Обновление надписи
    if 'mode_label' in globals():
        mode_label.config(text=f"[MODE] {mode}", fg=colors[mode])

    # Обновление цвета прицела в Canvas
    if hasattr(config, 'canvas') and hasattr(config, 'fovC'):
        try:
            config.canvas.itemconfig(config.fovC, outline=colors[mode])
        except:
            pass

    # Обновляем чекбокс Recoil, если есть
    if 'recoil_var' in globals():
        recoil_var.set(config.recoil_control)


class Config:
    def __init__(self):

        user32 = ctypes.windll.user32
        self.width = user32.GetSystemMetrics(0)
        self.height = user32.GetSystemMetrics(1)
        
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        
        # small AI area
        self.capture_width = 150  # Area for detecting X
        self.capture_height = 140  # Area for detecting Y

        self.capture_left = self.center_x - self.capture_width // 2
        self.capture_top = self.center_y - self.capture_height // 2
        self.crosshairX = self.capture_width // 2
        self.crosshairY = self.capture_height // 2
        
        # Rectangle area for AI detecting and after sending to mss.grab(config.region)
        self.region = {
            "top": self.capture_top,
            "left": self.capture_left,
            "width": self.capture_width,
            "height": self.capture_height + 100
        }

        self.Running = True
        self.AimToggle = True
        self.delay = 0.5 # shoot delay
        self.radius = 6 # crosshair size

        # AIM parameters
        self.target_offset_y = 0
        self.aim_threshold_x = 0.3  # % от ширины цели (обводка)
        self.aim_threshold_y = 0.3   # % от высоты цели (обводка)

        self.target_dot = None  # точка в дебаге

        self.detect_classes = [0, 2]  # CT / T
        self.target_name = "T" # default

        self.show_debug_window = 0     # Показывать окно с картинкой от ИИ
        self.show_fps = 0              # Показывать FPS в углу
        self.show_gui_menu = 1         # Показывать GUI меню tkinter

        self.recoil_control = False  # Состояние Отдачи
        self.recoil_random_range = 0

        self.selected_weapon = "ak"
        pattern, steps, delay = load_spray_pattern(f"{self.selected_weapon}.txt")
        self.spray_pattern = pattern
        self.recoil_steps = steps
        self.recoil_step_delay = delay

config = Config()

is_firing = False  # для обновления потока выстрела

current_recoil_index = -1  # индексация текущей координаты мыши для рекоила

def CreateOverlay():

    root = tk.Tk()
    root.title("Menu")
    root.geometry('250x850')  # Size
    #root.configure(bg="black")
    #tk.Label(root, text="Example menu title", font=("Helvetica", 14)).pack()

#== QUIT
    def quitProgram():
        config.AimToggle = False
        config.Running = False
        root.quit()

#== GLOBAL VAR
    # AI SHOW IN GUI
    global ai_image_label

    # RECOIL CHECKBOX
    global recoil_var

    # MODE STATUS
    global mode_label

#== 
    ai_image_label = tk.Label(root)
    ai_image_label.pack()

# == MODE STATUS LABEL -> GUI VIEWER
    #mode_label = tk.Label(root, text=mode_index, font=("Helvetica", 12, "bold"), fg="red")
    #mode_label.pack(pady=5)

#== TABS

    # === TAB: CREATING ===
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    # === TAB: Main ===
    main_tab = tk.Frame(notebook)
    notebook.add(main_tab, text="🎯 Aim Settings")

    # === TAB: Recoil ===
    recoil_tab = tk.Frame(notebook)
    notebook.add(recoil_tab, text="🌀 Recoil Pattern")

# === DROPDOWN: Weapon selection ===
    #tk.Label(recoil_tab, text="Choose Weapon").pack(pady=5)

    weapon_options = ["ak", "m4a4", "m4s", "galil", "famas", "mac"]
    weapon_var = tk.StringVar(value=config.selected_weapon)

    def on_weapon_select(choice):
        config.selected_weapon = choice
        try:
            pattern, steps, step_delay = load_spray_pattern(f"{choice}.txt")
            config.spray_pattern = pattern
            config.recoil_steps = steps
            config.recoil_step_delay = step_delay

            print(f"[RECOIL] Loaded {choice}.txt with {steps=} and {step_delay=}")
            
            # Обновляем GUI записи
            for widget in pattern_frame.winfo_children():
                widget.destroy()
            recoil_entries.clear()
            for i, (dx, dy) in enumerate(config.spray_pattern):
                row = tk.Frame(pattern_frame)
                row.pack()
                tk.Label(row, text=f"{i+1:02d}").pack(side=tk.LEFT)
                dx_entry = tk.Entry(row, width=5)
                dx_entry.insert(0, str(dx))
                dx_entry.pack(side=tk.LEFT)
                dy_entry = tk.Entry(row, width=5)
                dy_entry.insert(0, str(dy))
                dy_entry.pack(side=tk.LEFT)
                recoil_entries.append((dx_entry, dy_entry, row))
        except Exception as e:
            print(f"[ERROR] Failed to load {choice}.txt: {e}")

    tk.OptionMenu(recoil_tab, weapon_var, *weapon_options, command=on_weapon_select).pack()

    # Сейчас при загрузке .txt файла не происходит авто-обновление steps, recoil_steps
    # Нужно сделать переключение цвета при переключении режима на кнопку мыши

    # === RECOIL STEPS / STEP_DELAY
    def update_recoil_steps(val):
        config.recoil_steps = int(float(val))

    def update_recoil_step_delay(val):
        config.recoil_step_delay = float(val)

    tk.Label(recoil_tab, text="Recoil Steps").pack()
    tk.Scale(recoil_tab, from_=1, to=15, orient=tk.HORIZONTAL, command=update_recoil_steps).pack()
    tk.Label(recoil_tab, text="Recoil Step Delay").pack()
    tk.Scale(recoil_tab, from_=0.001, to=0.1, resolution=0.001, orient=tk.HORIZONTAL, command=update_recoil_step_delay).pack()

    # === RECOIL COORDINATE EDITOR ===
    tk.Label(recoil_tab, text="<-- X +-> / Y +DOWN", font=("Helvetica", 12, "bold")).pack(pady=5)

    pattern_frame = tk.Frame(recoil_tab)
    pattern_frame.pack()

    recoil_entries = []

    def update_pattern_from_entries():
        new_pattern = []
        for dx_entry, dy_entry, _ in recoil_entries:
            try:
                dx = int(dx_entry.get())
                dy = int(dy_entry.get())
                new_pattern.append((dx, dy))
            except ValueError:
                continue
        config.spray_pattern = new_pattern

    for i, (dx, dy) in enumerate(config.spray_pattern):
        row = tk.Frame(pattern_frame)
        row.pack()
        tk.Label(row, text=f"{i+1:02d}").pack(side=tk.LEFT)

        dx_entry = tk.Entry(row, width=5)
        dx_entry.insert(0, str(dx))
        dx_entry.pack(side=tk.LEFT)

        dy_entry = tk.Entry(row, width=5)
        dy_entry.insert(0, str(dy))
        dy_entry.pack(side=tk.LEFT)

        recoil_entries.append((dx_entry, dy_entry, row))  # x, y, ячейка

    # === Button: Apply recoil changes ===
    apply_button = tk.Button(recoil_tab, text="✅ Apply New Recoil")
    apply_button.pack(pady=5)

    def on_apply_click():
        update_pattern_from_entries()
        apply_button.config(bg='green')
        root.after(2000, lambda: apply_button.config(bg='SystemButtonFace'))  # Возврат к стандартному цвету

    apply_button.config(command=on_apply_click)

    # === Button: Save to File ===
    save_button = tk.Button(recoil_tab, text="💾 Save to File")
    save_button.pack(pady=5)

    def save_pattern_to_file():
        update_pattern_from_entries()
        
        # Путь к папке patterns (рядом с этим .py файлом)
        patterns_path = os.path.join(os.path.dirname(__file__), "patterns")
        os.makedirs(patterns_path, exist_ok=True)  # Создаём, если нет
        
        # Полный путь к файлу
        file_path = os.path.join(patterns_path, f"{config.selected_weapon}.txt")
        
        data = {
            "pattern": config.spray_pattern,
            "steps": config.recoil_steps,
            "step_delay": config.recoil_step_delay
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)  # Запись с отступами для читаемости
        
        print(f"[DEBUG] Pattern Saved: {os.path.abspath(file_path)}")
        
        save_button.config(bg='green')
        root.after(2000, lambda: save_button.config(bg='SystemButtonFace'))

    save_button.config(command=save_pattern_to_file)

    # === CURRENT CELL (ячейка) HIGHLIGHT ===
    def highlight_active_recoil():
        for i, (_, _, row) in enumerate(recoil_entries):
            try:
                bg = 'red' if i == current_recoil_index else 'SystemButtonFace'
                row.config(bg=bg)
            except tk.TclError:
                pass
        root.after(20, highlight_active_recoil)

    root.after(20, highlight_active_recoil) # root.через(20 мс, функция)

    # SHOOT DELAY
    def DelayConfigurator(Delay):
        config.delay = float(Delay)

    # TARGET OFFSET Y
    def TargetOffsetY(val):
        config.target_offset_y = int(float(val))

    # AIM THRESHOLD X
    def AimThresholdX(val):
        config.aim_threshold_x = float(val)

    # AIM THRESHOLD Y
    def AimThresholdY(val):
        config.aim_threshold_y = float(val)

    # === CHECKBOX: DEBUG WINDOW ===
    def toggle_debug_window():
        config.show_debug_window = debug_var.get()

    debug_var = tk.IntVar(value=config.show_debug_window)
    tk.Checkbutton(main_tab, text="Show AI Window", variable=debug_var,
                command=toggle_debug_window).pack()

    # === CHECKBOX: FPS ===
    def toggle_fps():
        config.show_fps = fps_var.get()

    fps_var = tk.IntVar(value=config.show_fps)
    tk.Checkbutton(main_tab, text="Show FPS", variable=fps_var,
                command=toggle_fps).pack()

    # === BUTTON: SWITCH CT / T ===
    def toggle_target():
        if config.target_name == "CT":
            config.detect_classes = [2]  # T
            config.target_name = "T"
            target_button.config(text="Target: T")
        else:
            config.detect_classes = [0]  # CT
            config.target_name = "CT"
            target_button.config(text="Target: CT")

    target_button = tk.Button(main_tab, text=f"Target: {config.target_name}",
                            command=toggle_target)
    target_button.pack(pady=5)

    # === CHECKBOX: RECOIL CONTROL ===
    def toggle_recoil():
        config.recoil_control = recoil_var.get()

    recoil_var = tk.IntVar(value=config.recoil_control)
    tk.Checkbutton(main_tab, text="Recoil", variable=recoil_var,
                command=toggle_recoil_state).pack()

#== SLIDER
    # CREATE SLIDER
    def CreateSlider(root, LabelText, fromV, toV, resolution, command, setValue):
        tk.Label(root, text=LabelText).pack()
        Slider = tk.Scale(root, from_=fromV, to=toV, resolution=resolution, orient=tk.HORIZONTAL, command = command)
        Slider.pack()
        Slider.set(setValue)

    # Delay Slider
    CreateSlider(main_tab, "Delay after shot", 0.003, 1.5, 0.001, DelayConfigurator, config.delay)
    # Target Offset Y
    CreateSlider(main_tab, "Target Offset Y -UP +DOWN", -100, 100, 1, TargetOffsetY, 0)
    # Box Treshold X
    CreateSlider(main_tab, "Box Treshold X (%) 0.2", 0.01, 1.0, 0.01, AimThresholdX, config.aim_threshold_x)
    # Box Treshold Y
    CreateSlider(main_tab, "Box Treshold Y (%) 0.3", 0.01, 1.0, 0.01, AimThresholdY, config.aim_threshold_y)

    # === SLIDER: Recoil Random Range ===
    tk.Label(recoil_tab, text="Randomization Range").pack(pady=5)
    random_range_slider = tk.Scale(recoil_tab, from_=0, to=10, orient=tk.HORIZONTAL, resolution=1,
                                command=update_random_range)
    random_range_slider.set(config.recoil_random_range)
    random_range_slider.pack()
    
    # Quit Button
    QuitButton = tk.Button(main_tab, text="Quit", command=quitProgram)
    QuitButton.pack()

    # Ingame Overlay
    overlay = tk.Toplevel(root)
    overlay.geometry(f'150x150+{str(config.center_x - config.radius)}+{str(config.center_y - config.radius)}')
    overlay.overrideredirect(True)
    overlay.attributes('-topmost', True)
    overlay.attributes('-transparentcolor', 'blue')

    # Canvas
    canvas = tk.Canvas(overlay, width=150, height=150, bg='blue', bd=0, highlightthickness=0)
    canvas.pack()

    config.canvas = canvas  # saving Canvas to config.canvas
    # fovC round in center
    config.fovC = canvas.create_oval(0, 0, config.radius*2, config.radius*2, outline='purple')

    overlay.mainloop()

# AI TARGET BLUE DOT
def UpdateTargetDot(x, y):
    if hasattr(config, 'canvas') and hasattr(config, 'target_dot'):
        try:
            config.canvas.coords(config.target_dot, x-3, y-3, x+3, y+3)
        except tk.TclError:
            pass

# FIRE
def fire():
    global is_firing
    # Проверяем, удерживается ли левая кнопка мыши
    left_pressed = win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000
    if left_pressed:
        # Кнопка уже нажата — не трогаем
        return

    is_firing = True
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.001)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    time.sleep(config.delay)
    is_firing = False

# RECOIL CONTROL
def smooth_mouse_move(dx, dy, steps=None, step_delay=None):
    step_dx = dx / steps
    step_dy = dy / steps
    for _ in range(steps):
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(step_dx), int(step_dy), 0, 0)
        print(steps, step_delay)
        time.sleep(step_delay)

# RECOIL LOOP
def recoil_loop():
    global current_recoil_index
    last_state = False

    print("[RECOIL] Toggle with Num Lock or Checkbox")

    while config.Running:
        # numlock or checkbox is activate?
        key_down = win32api.GetAsyncKeyState(win32con.VK_NUMLOCK) & 1
        if key_down and not last_state:
            toggle_recoil_state()
            time.sleep(0.1)
        last_state = key_down

        # config.recoil_control activate STATUS
        if config.recoil_control and win32api.GetKeyState(0x01) < 0:
            for i, (dx, dy) in enumerate(config.spray_pattern):
                current_recoil_index = i  # обновляем индекс

                # Рандомизация координат по оси X и Y
                rand_dx = dx + random.randint(-config.recoil_random_range, config.recoil_random_range)
                rand_dy = dy + random.randint(-config.recoil_random_range, config.recoil_random_range)

                # sending randx randy to mouse_move func
                smooth_mouse_move(
                    rand_dx,
                    rand_dy,
                    steps=config.recoil_steps,
                    step_delay=config.recoil_step_delay
                )

                if win32api.GetKeyState(0x01) >= 0:
                    break
        else:
            current_recoil_index = -1  # если не стреляет

# RANDOMIZING RANGE FOR RECOIL CONTROL
def update_random_range(val):
    config.recoil_random_range = int(float(val))

# CHECK RECOIL CONDITION GLOBAL
def toggle_recoil_state():
    config.recoil_control = not config.recoil_control
    recoil_var.set(config.recoil_control)
    print(f"[RECOIL] {'ENABLED' if config.recoil_control else 'DISABLED'}")


# SHOW AI WORK ON GUI MENU
def update_gui_ai_frame(frame):
    if config.show_debug_window and 'ai_image_label' in globals():
        try:
            # BGR to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = image.resize((200, 200))  # уменьши для GUI
            photo = ImageTk.PhotoImage(image)
            ai_image_label.configure(image=photo)
            ai_image_label.image = photo
        except:
            print("window is not active")

# MAIN
def main():

    # FIRE CONSTANT
    global is_firing

    # FPS COUNTER
    prev_time = time.time()
    fps = 0

    # MAIN MOUSE
    x1 = y1 = x2 = y2 = 0
    moveX = moveY = 0
    displacementX = displacementY = -1
    noDetectionIteration = 1

    # AI
    model = ultralytics.YOLO("bestv3.pt")  # yolov8n.pt
    screenCapture = mss.mss()  # screen capture

    # OVERLAY MENU
    if config.show_gui_menu:
        overlayThread = threading.Thread(target=CreateOverlay)
        overlayThread.start()

    # Запуск контроля отдачи
    threading.Thread(target=recoil_loop, daemon=True).start()


    while config.Running:
       # time.sleep(0.001)

        # ACTIVATE / DEACTIVATE BY MOUSE BUTTON LEFT SECOND
        if win32api.GetAsyncKeyState(0x05) & 1:
            switch_mode()
            time.sleep(0.1)

        if not config.AimToggle:
            continue

        GameFrame = np.array(screenCapture.grab(config.region))
        GameFrame = cv2.cvtColor(GameFrame, cv2.COLOR_BGRA2BGR)

        results = model.predict(source=GameFrame,
                                 conf=0.50, 
                                 classes=config.detect_classes, 
                                 verbose=False, 
                                 max_det=4,
                                 stream=False,
                                 imgsz=640)
        # classes=[0]
        # {0: 'CT', 1: 'CT_HEAD', 2: 'T', 3: 'T_HEAD'}

        boxes = results[0].boxes.xyxy

        if len(boxes) > 0:

            for box in boxes:
                x1, y1, x2, y2 = box.tolist()
                displacementX = x2 - x1
                displacementY = y2 - y1

                # Точка прицеливания смещена вверх (на 1/3 высоты)
                target_x = int(x1 + displacementX / 2)
                target_y = int(y1 + displacementY / 3) + config.target_offset_y  # прицел в верхнюю треть (примерно голова)

                # Смещение между центром экрана и точкой прицела
                moveX = target_x - config.crosshairX
                moveY = target_y - config.crosshairY
                noDetectionIteration = 0

                # Рисуем прямоугольник цели при обнаружении ИИ
                cv2.rectangle(GameFrame, (int(x1), int(y1)), (int(x2), int(y2)), (100, 100, 255), 1)
    
                # Отладочная точка прицеливания
                cv2.circle(GameFrame, (target_x, target_y), 3, (255, 0, 0), -1)
                UpdateTargetDot(config.crosshairX + moveX, config.crosshairY + moveY)  # обновление позиции из GUI

        else:
            # Сброс при отсутствии цели
            x1 = y1 = x2 = y2 = 0
            displacementX = displacementY = -1
            moveX = moveY = 9999
            noDetectionIteration += 1
            UpdateTargetDot(-10, -10)

        # === Условие для выстрела ===
        aim_threshold_x = displacementX * config.aim_threshold_x
        aim_threshold_y = displacementY * config.aim_threshold_y

        if (
            abs(moveX) <= aim_threshold_x and
            abs(moveY) <= aim_threshold_y and
            noDetectionIteration <= 1 and
            not is_firing
        ):
            noDetectionIteration += 1
            threading.Thread(target=fire).start()  # start fire in new thread


        # FPS
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time


        if config.show_fps:
            cv2.putText(GameFrame, f"FPS: {fps:.2f}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                        0.50, (0, 255, 0), 1)

        # DEBUGGING WINDOW
        if config.show_debug_window:
            update_gui_ai_frame(GameFrame)
        
        del GameFrame

        # Quit?
        if cv2.waitKey(1) & 0xFF == ord('q'):
            config.Running = False
            break

    overlayThread.join()
    cv2.destroyAllWindows() # ai debug window
                 
if __name__ == "__main__":
    main()
import win32api, win32con 
# window API win32con.KEYEVENTF_KEYUP = 0x0002 (unpress key)  // win32api.keybd_event(0x57, 0, 0, 0) (press W)
import win32gui # find window by name, open/close etc..
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

from config import cfg
from debug import debug_print as dp
from spray_settings import load_spray_pattern, save_spray_pattern

# добавить в settings к оружию индивидуальную настройку shoot delay для автоматической стрельбы

# for showing Ai work in GUI
from PIL import Image, ImageTk

from tkinter import ttk

#=== MODES FOR MOUSE BUTTON
mode_index = 0  # текущий режим
MODES = ["AI_OFF", "AI_ON", "AI/RECOIL_ON"]

# SWITCH MODE
def switch_mode():
    global mode_index
    mode_index = (mode_index + 1) % len(MODES)
    mode = MODES[mode_index]

    dp(cfg.switch_mode_debug, f"mode // Switched to: {mode}")

    # Цвета прицела в зависимости от режима
    colors = {
        "AI_OFF": "red",
        "AI_ON": "hotpink",
        "AI/RECOIL_ON": "purple"
    }

    # Логика переключения режимов
    if mode == "AI_OFF":
        cfg.AiToggle = False
        cfg.recoil_control = False
        #winsound.Beep(400, 100)

    elif mode == "AI_ON":
        cfg.AiToggle = True
        cfg.recoil_control = False
        #winsound.Beep(800, 100)

    elif mode == "AI/RECOIL_ON":
        cfg.AiToggle = True
        cfg.recoil_control = True
        #winsound.Beep(1200, 100)

    # Обновление надписи
    if 'mode_label' in globals():
        mode_label.cfg(text=f"[MODE] {mode}", fg=colors[mode])

    # Обновление цвета прицела в Canvas
    if hasattr(cfg, 'canvas') and hasattr(cfg, 'fovC'):
        try:
            cfg.canvas.itemconfig(cfg.fovC, outline=colors[mode])
        except:
            pass

    # Обновляем чекбокс Recoil, если есть
    if 'recoil_var' in globals():
        recoil_var.set(cfg.recoil_control)

def CreateOverlay():

    root = tk.Tk()
    root.title("Menu")
    root.geometry('250x850')  # Size
    #root.configure(bg="black")
    #tk.Label(root, text="Example menu title", font=("Helvetica", 14)).pack()

#== QUIT
    def quitProgram():
        cfg.AiToggle = False
        cfg.Running = False
        root.quit()

#== GLOBAL VAR
    # AI SHOW IN GUI
    global ai_image_label  # Label in Tkinter where the image is placed

    #== AI SHOW IN GUI
    ai_image_label = tk.Label(root)
    ai_image_label.pack()

    # RECOIL CHECKBOX
    global recoil_var

    # MODE STATUS
    global mode_label

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
    weapon_var = tk.StringVar(value=cfg.selected_weapon)

    def on_weapon_select(choice):
        cfg.selected_weapon = choice
        try:
            pattern_data, steps_data, step_delay_data = load_spray_pattern(f"{choice}.txt")
            
            cfg.spray_pattern = pattern_data
            cfg.recoil_steps = steps_data
            cfg.recoil_step_delay = step_delay_data
            
            # Clear old widgets
            for widget in pattern_frame.winfo_children():
                widget.destroy()
            recoil_entries.clear()

            # Create new Box Entry for each step of the pattern
            for i, (dx, dy) in enumerate(cfg.spray_pattern):
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

    # === RECOIL STEPS / STEP_DELAY
    def update_recoil_steps(val):
        cfg.recoil_steps = int(float(val))

    def update_recoil_step_delay(val):
        cfg.recoil_step_delay = float(val)

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
        cfg.spray_pattern = new_pattern

    for i, (dx, dy) in enumerate(cfg.spray_pattern):
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

    # SAVE PATTERN
    def save_pattern_to_file():
        # Берём данные из GUI (Entry, Spinbox и т.п.)
        update_pattern_from_entries()  # обновляет cfg.spray_pattern, cfg.recoil_steps, cfg.recoil_step_delay

        # Сохраняем через универсальную функцию из spray_patterns.py
        save_spray_pattern(
            f"{cfg.selected_weapon}.txt",
            cfg.spray_pattern,
            cfg.recoil_steps,
            cfg.recoil_step_delay
        )
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
        cfg.delay = float(Delay)

    # TARGET OFFSET Y
    def TargetOffsetY(val):
        cfg.target_offset_y = int(float(val))

    # AIM THRESHOLD X
    def AimThresholdX(val):
        cfg.aim_threshold_x = float(val)

    # AIM THRESHOLD Y
    def AimThresholdY(val):
        cfg.aim_threshold_y = float(val)

    # === CHECKBOX: DEBUG WINDOW ===
    def toggle_debug_window():
        cfg.show_debug_window = debug_var.get()  # get show_debug_window 0 or 1

        # Check show_debug_window condition
        if cfg.show_debug_window == 1:
            print("activated")
        else:
            print("deactivated")

    debug_var = tk.IntVar(value=cfg.show_debug_window)

    tk.Checkbutton(main_tab, text="Show AI Window", variable=debug_var,
                command=toggle_debug_window).pack()

    # === CHECKBOX: FPS ===
    def toggle_fps():
        cfg.show_fps = fps_var.get()

    fps_var = tk.IntVar(value=cfg.show_fps)
    tk.Checkbutton(main_tab, text="Show FPS", variable=fps_var,
                command=toggle_fps).pack()

    # === BUTTON: SWITCH CT / T ===
    def toggle_target():
        if cfg.target_name == "CT":
            cfg.detect_classes = [2]  # T
            cfg.target_name = "T"
            target_button.config(text="Target: T")
        else:
            cfg.detect_classes = [0]  # CT
            cfg.target_name = "CT"
            target_button.config(text="Target: CT")

    target_button = tk.Button(main_tab, text=f"Target: {cfg.target_name}",
                            command=toggle_target)
    target_button.pack(pady=5)

    # === CHECKBOX: RECOIL CONTROL ===
    def toggle_recoil():
        cfg.recoil_control = recoil_var.get()

    recoil_var = tk.IntVar(value=cfg.recoil_control)
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
    CreateSlider(main_tab, "Delay after shot", 0.003, 1.5, 0.001, DelayConfigurator, cfg.delay)
    # Target Offset Y
    CreateSlider(main_tab, "Target Offset Y -UP +DOWN", -100, 100, 1, TargetOffsetY, 0)
    # Box Treshold X
    CreateSlider(main_tab, "Box Treshold X (%) 0.2", 0.01, 1.0, 0.01, AimThresholdX, cfg.aim_threshold_x)
    # Box Treshold Y
    CreateSlider(main_tab, "Box Treshold Y (%) 0.3", 0.01, 1.0, 0.01, AimThresholdY, cfg.aim_threshold_y)

    # === SLIDER: Recoil Random Range ===
    tk.Label(recoil_tab, text="Randomization Range").pack(pady=5)
    random_range_slider = tk.Scale(recoil_tab, from_=0, to=10, orient=tk.HORIZONTAL, resolution=1,
                                command=update_random_range)
    random_range_slider.set(cfg.recoil_random_range)
    random_range_slider.pack()
    
    # Quit Button
    QuitButton = tk.Button(main_tab, text="Quit", command=quitProgram)
    QuitButton.pack()

    # Ingame Overlay
    overlay = tk.Toplevel(root)
    overlay.geometry(f'150x150+{str(cfg.center_x - cfg.radius)}+{str(cfg.center_y - cfg.radius)}')
    overlay.overrideredirect(True)
    overlay.attributes('-topmost', True)
    overlay.attributes('-transparentcolor', 'blue')

    # Canvas
    canvas = tk.Canvas(overlay, width=150, height=150, bg='blue', bd=0, highlightthickness=0)
    canvas.pack()

    cfg.canvas = canvas  # saving Canvas to cfg.canvas
    # fovC round in center
    cfg.fovC = canvas.create_oval(0, 0, cfg.radius*2, cfg.radius*2, outline='purple')

    overlay.mainloop()

# AI TARGET BLUE DOT
def UpdateTargetDot(x, y):
    if hasattr(cfg, 'canvas') and hasattr(cfg, 'target_dot'):
        try:
            cfg.canvas.coords(cfg.target_dot, x-3, y-3, x+3, y+3)
        except tk.TclError:
            pass

# FIRE
def fire():
    # Check if the left mouse button is pressed?
    left_pressed = win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000

    if left_pressed:
        dp(cfg.is_firing_debug, f"fire is already pressed // {left_pressed}")
        return  # skip step

    cfg.is_firing = True
    dp(cfg.is_firing_debug, f"fire // {cfg.is_firing}")

    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0) # LEFT DOWN
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0) # LEFT UP

    time.sleep(cfg.delay)
    cfg.is_firing = False
    dp(cfg.is_firing_debug, f"fire // {cfg.is_firing}")

# RECOIL CONTROL
def smooth_mouse_move(dx, dy, steps=None, step_delay=None):
    step_dx = dx / steps
    step_dy = dy / steps
    for _ in range(steps):
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(step_dx), int(step_dy), 0, 0)

        dp(cfg.smooth_mouse_move_debug,
           f"smooth mouse move // {cfg.selected_weapon, steps, step_delay}")
        
        time.sleep(step_delay)

# RECOIL LOOP
def recoil_loop():
    global current_recoil_index
    last_state = False

    print("[RECOIL] Toggle with Num Lock or Checkbox")

    while cfg.Running:
        # numlock or checkbox is activate?
        key_down = win32api.GetAsyncKeyState(win32con.VK_NUMLOCK) & 1
        if key_down and not last_state:
            toggle_recoil_state()
            time.sleep(0.1)
        last_state = key_down

        # cfg.recoil_control activate STATUS
        if cfg.recoil_control and win32api.GetKeyState(0x01) < 0:  # 0x01 left mouse button
            for i, (dx, dy) in enumerate(cfg.spray_pattern):
                current_recoil_index = i  # обновляем индекс

                # Рандомизация координат по оси X и Y
                rand_dx = dx + random.randint(-cfg.recoil_random_range, cfg.recoil_random_range)
                rand_dy = dy + random.randint(-cfg.recoil_random_range, cfg.recoil_random_range)

                # sending randx randy to mouse_move func
                smooth_mouse_move(
                    rand_dx,
                    rand_dy,
                    steps=cfg.recoil_steps,
                    step_delay=cfg.recoil_step_delay
                )

                if win32api.GetKeyState(0x01) >= 0:
                    break
        else:
            current_recoil_index = -1  # если не стреляет

# RANDOMIZING RANGE FOR RECOIL CONTROL
def update_random_range(val):
    cfg.recoil_random_range = int(float(val))

# CHECK RECOIL CONDITION GLOBAL
def toggle_recoil_state():
    cfg.recoil_control = not cfg.recoil_control
    recoil_var.set(cfg.recoil_control)
    print(f"[RECOIL] {'ENABLED' if cfg.recoil_control else 'DISABLED'}")


# SHOW AI WORK ON GUI MENU
def update_gui_ai_frame(debug_frame):
    if cfg.show_debug_window == 1:
        try:
            # BGR to RGB
            image = cv2.cvtColor(debug_frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = image.resize((200, 200))  # smaller size for AI
            photo = ImageTk.PhotoImage(image)
            ai_image_label.configure(image=photo)
            ai_image_label.image = photo
        except:
            print("ai image label does not exist or tkinter window is destroyed")

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
    if cfg.show_gui_menu:
        overlayThread = threading.Thread(target=CreateOverlay)
        overlayThread.start()

    # Start Recoil Control in new Thread
    threading.Thread(target=recoil_loop, daemon=True).start()


    while cfg.Running:

        # ACTIVATE / DEACTIVATE BY MOUSE BUTTON LEFT SECOND
        if win32api.GetAsyncKeyState(0x05) & 1:
            switch_mode()
            time.sleep(0.1)

        if not cfg.AiToggle:
            continue

        GameFrame = np.array(screenCapture.grab(cfg.region))
        GameFrame = cv2.cvtColor(GameFrame, cv2.COLOR_BGRA2BGR)

        results = model.predict(source=GameFrame,
                                 conf=0.50, 
                                 classes=cfg.detect_classes, 
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

                # Aiming point is shifted upwards (by 1/3 of the height)
                target_x = int(x1 + displacementX / 2)
                target_y = int(y1 + displacementY / 3) + cfg.target_offset_y  # aim at the upper third (almost head)

                # Offset between the center of the screen and the aiming point
                moveX = target_x - cfg.crosshairX
                moveY = target_y - cfg.crosshairY
                noDetectionIteration = 0

                # Draw a target-rectangle when AI detects it
                cv2.rectangle(GameFrame, (int(x1), int(y1)), (int(x2), int(y2)), (100, 100, 255), 1)
    
                # Blue DOT 
                cv2.circle(GameFrame, (target_x, target_y), 3, (255, 0, 0), -1)
                UpdateTargetDot(cfg.crosshairX + moveX, cfg.crosshairY + moveY)  # update dot position

        else:
            # Reset if NO TARGET
            x1 = y1 = x2 = y2 = 0
            displacementX = displacementY = -1
            moveX = moveY = 9999
            noDetectionIteration += 1
            UpdateTargetDot(-10, -10)

        # === Fire Condition ===
        aim_threshold_x = displacementX * cfg.aim_threshold_x
        aim_threshold_y = displacementY * cfg.aim_threshold_y

        if (
            abs(moveX) <= aim_threshold_x and
            abs(moveY) <= aim_threshold_y and
            noDetectionIteration <= 1 and
            not cfg.is_firing
        ):
            dp(f"main // {cfg.is_firing}")
            noDetectionIteration += 1
            threading.Thread(target=fire).start()  # start fire in new thread


        # FPS
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time


        if cfg.show_fps:
            cv2.putText(GameFrame, f"FPS: {fps:.2f}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                        0.50, (0, 255, 0), 1)

        # ACTIVATE DEBUG WINDOW
        if cfg.show_debug_window:
            update_gui_ai_frame(GameFrame)
        
        #del GameFrame

        # Quit?
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cfg.Running = False
            break

    overlayThread.join()
    cv2.destroyAllWindows()
                 
if __name__ == "__main__":
    main()
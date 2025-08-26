import tkinter as tk
from tkinter import ttk
from config import config
from patterns import load_spray_pattern, save_spray_pattern
from recoil import update_random_range, toggle_recoil_state
from fire import fire

# Global variables for GUI
ai_image_label = None
recoil_var = None
mode_label = None

mode_index = 0
MODES = ["AI_OFF", "AI_ON", "AI/RECOIL_ON"]

def switch_mode():
    global mode_index
    mode_index = (mode_index + 1) % len(MODES)
    mode = MODES[mode_index]
    colors = {"AI_OFF": "red", "AI_ON": "hotpink", "AI/RECOIL_ON": "purple"}

    if mode == "AI_OFF":
        config.AimToggle = False
        config.recoil_control = False
    elif mode == "AI_ON":
        config.AimToggle = True
        config.recoil_control = False
    elif mode == "AI/RECOIL_ON":
        config.AimToggle = True
        config.recoil_control = True

    if mode_label:
        mode_label.config(text=f"[MODE] {mode}", fg=colors[mode])
    if hasattr(config, 'canvas') and hasattr(config, 'fovC'):
        try:
            config.canvas.itemconfig(config.fovC, outline=colors[mode])
        except:
            pass
    if recoil_var:
        recoil_var.set(config.recoil_control)

def CreateOverlay():
    global ai_image_label, recoil_var, mode_label

    root = tk.Tk()
    root.title("Menu")
    root.geometry('250x850')

    # Tabs
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')
    main_tab = tk.Frame(notebook)
    notebook.add(main_tab, text="🎯 Aim Settings")
    recoil_tab = tk.Frame(notebook)
    notebook.add(recoil_tab, text="🌀 Recoil Pattern")

    # AI image
    ai_image_label = tk.Label(root)
    ai_image_label.pack()
    # Recoil checkbox
    recoil_var = tk.IntVar(value=config.recoil_control)
    tk.Checkbutton(main_tab, text="Recoil", variable=recoil_var, command=toggle_recoil_state).pack()

    # Overlay
    overlay = tk.Toplevel(root)
    overlay.geometry(f'150x150+{config.center_x - config.radius}+{config.center_y - config.radius}')
    overlay.overrideredirect(True)
    overlay.attributes('-topmost', True)
    overlay.attributes('-transparentcolor', 'blue')
    canvas = tk.Canvas(overlay, width=150, height=150, bg='blue', bd=0, highlightthickness=0)
    canvas.pack()
    config.canvas = canvas
    config.fovC = canvas.create_oval(0, 0, config.radius*2, config.radius*2, outline='purple')

    root.mainloop()

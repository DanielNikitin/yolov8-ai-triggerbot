from customtkinter import *
import tkinter as tk

def start_gui(config):
    set_appearance_mode("Dark")
    set_default_color_theme("blue")

    root = CTk()
    root.title("New GUI")
    root.geometry("400x500")

    CTkLabel(root, text="GUI v2.0", font=("Helvetica", 16)).pack(pady=10)

    # === Вкладки (TabView) ===
    tabview = CTkTabview(root, width=380, height=400)
    tabview.pack(pady=10)

    tabview.add("Aim Settings")
    tabview.add("Recoil Settings")

    # === Aim Settings tab ===
    aim_tab = tabview.tab("Aim Settings")
    CTkLabel(aim_tab, text="Aim Settings", font=("Helvetica", 14)).pack(pady=10)

    # --- Show AI Window checkbox ---
    ai_var = IntVar(value=int(config.show_debug_window))
    def toggle_ai_window():
        config.show_debug_window = bool(ai_var.get())

    CTkCheckBox(aim_tab, text="Show AI Window", variable=ai_var, command=toggle_ai_window).pack(anchor='w', padx=20)

    # --- Show FPS checkbox ---
    fps_var = IntVar(value=int(config.show_fps))
    def toggle_fps():
        config.show_fps = bool(fps_var.get())

    CTkCheckBox(aim_tab, text="Show FPS", variable=fps_var, command=toggle_fps).pack(anchor='w', padx=20)

    # === Recoil Settings tab ===
    recoil_tab = tabview.tab("Recoil Settings")
    CTkLabel(recoil_tab, text="Recoil Settings", font=("Helvetica", 14)).pack(pady=10)

    # --- Recoil Control checkbox ---
    recoil_var = IntVar(value=int(config.recoil_control))
    def toggle_recoil():
        config.recoil_control = bool(recoil_var.get())

    CTkCheckBox(recoil_tab, text="Enable Recoil Control", variable=recoil_var, command=toggle_recoil).pack(anchor='w', padx=20)

    # === Quit Button ===
    def quit_program():
        config.Running = False
        root.destroy()

    CTkButton(root, text="Выход", command=quit_program).pack(pady=10)

    root.mainloop()

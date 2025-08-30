# gui_main.py
import customtkinter as ctk


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Custom GUI Example")
        self.geometry("900x600")

        # ===== Цветовая схема =====
        self.bg_color = "#1e1e1e"   # фон
        self.panel_color = "#252526"  # боковые панели
        self.line_color = "#3c3c3c"   # разделители

        self.configure(fg_color=self.bg_color)

        # ===== Верхнее меню =====
        self.top_frame = ctk.CTkFrame(self, fg_color=self.panel_color, height=45, corner_radius=0)
        self.top_frame.grid(row=0, column=0, sticky="ew")
        self.top_frame.grid_columnconfigure((0, 1, 2), weight=1)

        btn_style = {"corner_radius": 0, "fg_color": "transparent", "hover_color": "#3c3c3c"}

        self.btn_legit = ctk.CTkButton(self.top_frame, text="Legit", **btn_style, command=self.show_legit)
        self.btn_legit.grid(row=0, column=0, sticky="ew")

        self.btn_visual = ctk.CTkButton(self.top_frame, text="Visual", **btn_style, command=self.show_visual)
        self.btn_visual.grid(row=0, column=1, sticky="ew")

        self.btn_misc = ctk.CTkButton(self.top_frame, text="Misc", **btn_style, command=self.show_misc)
        self.btn_misc.grid(row=0, column=2, sticky="ew")

        # Линия под верхним меню
        self.line_top = ctk.CTkFrame(self, fg_color=self.line_color, height=2, corner_radius=0)
        self.line_top.grid(row=1, column=0, sticky="ew")

        # ===== Основное окно =====
        self.main_frame = ctk.CTkFrame(self, fg_color=self.bg_color, corner_radius=0)
        self.main_frame.grid(row=2, column=0, sticky="nsew")
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Левая панель
        self.left_menu = ctk.CTkFrame(self.main_frame, fg_color=self.panel_color, width=180, corner_radius=0)
        self.left_menu.grid(row=0, column=0, sticky="nsw")

        # Вертикальная линия-разделитель
        self.line_left = ctk.CTkFrame(self.main_frame, fg_color=self.line_color, width=2, corner_radius=0)
        self.line_left.grid(row=0, column=1, sticky="ns")

        # Контент
        self.content = ctk.CTkFrame(self.main_frame, fg_color=self.bg_color, corner_radius=0)
        self.content.grid(row=0, column=2, sticky="nsew")

        # Запускаем с Legit
        self.show_legit()

    def clear_left_menu(self):
        for widget in self.left_menu.winfo_children():
            widget.destroy()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    # ===== Переключение категорий =====
    def show_legit(self):
        self.clear_left_menu()
        self.clear_content()
        add_legit_menu(self)

    def show_visual(self):
        self.clear_left_menu()
        self.clear_content()
        add_visual_menu(self)

    def show_misc(self):
        self.clear_left_menu()
        self.clear_content()
        add_misc_menu(self)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()

import ctypes
from pattern import load_spray_pattern

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
        self.show_gui_menu = 1         # Запуск GUI Меню

        self.recoil_control = False  # Состояние Отдачи
        self.recoil_random_range = 0

        self.selected_weapon = "ak"
        pattern, steps, delay = load_spray_pattern(f"{self.selected_weapon}.txt")
        self.spray_pattern = pattern
        self.recoil_steps = steps
        self.recoil_step_delay = delay

        self.is_firing = False

        self.current_recoil_index = -1  # индексация текущей координаты мыши для рекоила

config = Config()

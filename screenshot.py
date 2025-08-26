import pyautogui
import keyboard
import time
import os
from datetime import datetime

def capture_center_screen(width=800, height=600):
    # Создание папки для сохранения, если её нет
    save_dir = "screenshot_data"
    os.makedirs(save_dir, exist_ok=True)
    
    # Получаем размеры экрана
    screen_width, screen_height = pyautogui.size()
    
    # Вычисляем координаты центра
    left = (screen_width - width) // 2
    top = (screen_height - height) // 2

    # Захват области 800x600
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    
    # Генерация имени файла с отметкой времени
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(save_dir, f"screenshot_{timestamp}.png")
    screenshot.save(filename)
    
    print(f"Скриншот сохранен: {filename}")

print("Нажмите 'S' для создания скриншота (Ctrl+C для выхода)...")

# Бесконечный цикл ожидания нажатия клавиши 'S'
while True:
    if keyboard.is_pressed('s'):
        capture_center_screen()
        time.sleep(1)  # Задержка, чтобы избежать повторного срабатывания

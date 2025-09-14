# Скриншоты всего что на экране

import mss
import keyboard
import time
import os

# Создание папки для сохранения изображений, если ее нет
output_dir = "./CS2DataV1"
os.makedirs(output_dir, exist_ok=True)

print("Скрипт активирован. Нажмите 'Space' для начала записи и 'Q' для выхода.")

keyboard.wait('space')  # Ожидание нажатия пробела для активации

image_counter = 1000

with mss.mss() as sct:
    while not keyboard.is_pressed('q'):
        screenshot_path = os.path.join(output_dir, f"Toadled-{image_counter}.png")
        sct.shot(mon=1, output=screenshot_path)
        print(f"Снимок сохранен: {screenshot_path}")
        image_counter += 1
        time.sleep(0.1)

print("Скрипт завершен.")

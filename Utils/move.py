import random
import time
from pynput.keyboard import Controller
from pynput.mouse import Button, Controller as MouseController

# Инициализация контроллеров для клавиатуры и мыши
keyboard = Controller()
mouse = MouseController()

# Список возможных клавиш
keys = ['w', 'a', 's', 'd']

# Функция для случайного нажатия клавиш и кнопок мыши
def random_key_press():
    # Случайным образом выбираем действие
    action = random.choice(['key', 'mouse'])

    if action == 'key':
        # Случайным образом выбираем клавишу
        key = random.choice(keys)
        print(f"Нажата клавиша: {key}")
        keyboard.press(key)  # Нажимаем клавишу
        time.sleep(random.uniform(0.1, 0.3))  # Удерживаем клавишу на случайное время
        keyboard.release(key)  # Отпускаем клавишу

    elif action == 'mouse':
        # Случайным образом решаем, нажать ли левую кнопку мыши
        if random.choice([True, False]):
            print("Нажата левая кнопка мыши")
            mouse.press(Button.left)  # Нажимаем левую кнопку мыши
            time.sleep(random.uniform(0.1, 0.3))  # Удерживаем кнопку на случайное время
            mouse.release(Button.left)  # Отпускаем левую кнопку мыши

# Запуск случайных нажатий
try:
    while True:
        random_key_press()
        time.sleep(random.uniform(0.5, 2))  # Ждем случайное время между действиями
except KeyboardInterrupt:
    print("Скрипт завершен.")

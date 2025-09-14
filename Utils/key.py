from pynput.keyboard import Key, Controller
import time

keyboard = Controller()

try:
    while True:
        keyboard.press('q')
        time.sleep(0.05)  # Задержка перед отпусканием клавиши
        keyboard.release('q')
        time.sleep(0.05)  # Задержка перед следующим нажатием
except KeyboardInterrupt:
    print("Скрипт остановлен пользователем.")

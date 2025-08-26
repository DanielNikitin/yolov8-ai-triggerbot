import threading
import time
import win32api
import win32con
import pyautogui  # pip install pyautogui
import numpy as np

sqrt3 = np.sqrt(3)
sqrt5 = np.sqrt(5)

def move_mouse(x, y):
    pyautogui.moveTo(x, y)

def wind_mouse(start_x, start_y, dest_x, dest_y, G_0=9, W_0=3, M_0=15, D_0=12, move_mouse=lambda x, y: None):
    current_x, current_y = start_x, start_y
    v_x = v_y = W_x = W_y = 0
    while (dist := np.hypot(dest_x - start_x, dest_y - start_y)) >= 1:
        W_mag = min(W_0, dist)
        if dist >= D_0:
            W_x = W_x / sqrt3 + (2 * np.random.random() - 1) * W_mag / sqrt5
            W_y = W_y / sqrt3 + (2 * np.random.random() - 1) * W_mag / sqrt5
        else:
            W_x /= sqrt3
            W_y /= sqrt3
            if M_0 < 3:
                M_0 = np.random.random() * 3 + 3
            else:
                M_0 /= sqrt5
        v_x += W_x + G_0 * (dest_x - start_x) / dist
        v_y += W_y + G_0 * (dest_y - start_y) / dist
        v_mag = np.hypot(v_x, v_y)
        if v_mag > M_0:
            v_clip = M_0 / 2 + np.random.random() * M_0 / 2
            v_x = (v_x / v_mag) * v_clip
            v_y = (v_y / v_mag) * v_clip
        start_x += v_x
        start_y += v_y
        move_x = int(np.round(start_x))
        move_y = int(np.round(start_y))
        if current_x != move_x or current_y != move_y:
            move_mouse(current_x := move_x, current_y := move_y)
            time.sleep(0.005)  # добавить задержку чтобы не перегружать систему
    return current_x, current_y

# === Основной цикл ===
def mouse_monitor():
    while True:
        lmb_down = win32api.GetAsyncKeyState(win32con.VK_LBUTTON) < 0
        if lmb_down:
            current_x, current_y = pyautogui.position()
            # Укажи сюда координаты, куда хочешь переместить мышь
            target_x = current_x + 50  # например, плавный сдвиг вправо
            target_y = current_y + 30  # и немного вниз
            wind_mouse(current_x, current_y, target_x, target_y, move_mouse=move_mouse)
        else:
            time.sleep(0.01)  # не держим процесс активным зря

# === Запуск потока ===
threading.Thread(target=mouse_monitor, daemon=True).start()

# Простой цикл, чтобы скрипт не завершился
while True:
    time.sleep(1)

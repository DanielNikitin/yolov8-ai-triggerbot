import time
import threading
import win32api
import win32con
import pyautogui
import numpy

sqrt3 = numpy.sqrt(3)
sqrt5 = numpy.sqrt(5)

def wind_mouse(start_x, start_y, dest_x, dest_y, G_0=9, W_0=3, M_0=15, D_0=12, move_mouse=lambda x, y: None):
    current_x, current_y = start_x, start_y
    v_x = v_y = W_x = W_y = 0
    while (dist := numpy.hypot(dest_x - start_x, dest_y - start_y)) >= 1:
        W_mag = min(W_0, dist)
        if dist >= D_0:
            W_x = W_x / sqrt3 + (2 * numpy.random.random() - 1) * W_mag / sqrt5
            W_y = W_y / sqrt3 + (2 * numpy.random.random() - 1) * W_mag / sqrt5
        else:
            W_x /= sqrt3
            W_y /= sqrt3
            if M_0 < 3:
                M_0 = numpy.random.random() * 3 + 3
            else:
                M_0 /= sqrt5
        v_x += W_x + G_0 * (dest_x - start_x) / dist
        v_y += W_y + G_0 * (dest_y - start_y) / dist
        v_mag = numpy.hypot(v_x, v_y)
        if v_mag > M_0:
            v_clip = M_0 / 2 + numpy.random.random() * M_0 / 2
            v_x = (v_x / v_mag) * v_clip
            v_y = (v_y / v_mag) * v_clip
        start_x += v_x
        start_y += v_y
        move_x = int(numpy.round(start_x))
        move_y = int(numpy.round(start_y))
        if current_x != move_x or current_y != move_y:
            move_mouse(current_x := move_x, current_y := move_y)
    return current_x, current_y

def is_left_mouse_pressed():
    return win32api.GetAsyncKeyState(win32con.VK_LBUTTON) < 0

def recoil_control():
    while True:
        if is_left_mouse_pressed():
            x, y = pyautogui.position()
            wind_mouse(x, y, x, y + 60, move_mouse=pyautogui.moveTo)
            time.sleep(0.1)
        else:
            time.sleep(0.01)

# Запуск в фоне
threading.Thread(target=recoil_control, daemon=True).start()

# Основной поток "ждёт"
if __name__ == "__main__":
    while True:
        time.sleep(1)

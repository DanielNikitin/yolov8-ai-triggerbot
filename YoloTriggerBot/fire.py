import win32api, win32con, time
from config import config

is_firing = False

def fire():
    global is_firing
    left_pressed = win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000
    if left_pressed:
        return

    is_firing = True
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.001)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(config.delay)
    is_firing = False

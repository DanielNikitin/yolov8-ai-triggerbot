import win32api, win32con, time, random
from config import config

current_recoil_index = -1

def smooth_mouse_move(dx, dy, steps=None, step_delay=None):
    step_dx = dx / steps
    step_dy = dy / steps
    for _ in range(steps):
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(step_dx), int(step_dy), 0, 0)
        time.sleep(step_delay)

def toggle_recoil_state():
    config.recoil_control = not config.recoil_control
    from gui import recoil_var
    recoil_var.set(config.recoil_control)
    print(f"[RECOIL] {'ENABLED' if config.recoil_control else 'DISABLED'}")

def recoil_loop():
    global current_recoil_index
    last_state = False
    import threading
    print("[RECOIL] Toggle with Num Lock or Checkbox")
    while config.Running:
        key_down = win32api.GetAsyncKeyState(win32con.VK_NUMLOCK) & 1
        if key_down and not last_state:
            toggle_recoil_state()
            time.sleep(0.1)
        last_state = key_down

        if config.recoil_control and win32api.GetKeyState(0x01) < 0:
            for i, (dx, dy) in enumerate(config.spray_pattern):
                current_recoil_index = i
                rand_dx = dx + random.randint(-config.recoil_random_range, config.recoil_random_range)
                rand_dy = dy + random.randint(-config.recoil_random_range, config.recoil_random_range)
                smooth_mouse_move(rand_dx, rand_dy, steps=config.recoil_steps, step_delay=config.recoil_step_delay)
                if win32api.GetKeyState(0x01) >= 0:
                    break
        else:
            current_recoil_index = -1

def update_random_range(val):
    config.recoil_random_range = int(float(val))

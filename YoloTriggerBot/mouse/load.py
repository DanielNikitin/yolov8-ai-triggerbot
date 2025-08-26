import pyautogui
import time
import json

with open("macro.json", "r") as f:
    recorded_positions = json.load(f)

print("Воспроизведение начнется через 3 секунды...")
time.sleep(3)

for pos in recorded_positions:
    pyautogui.moveTo(pos[0], pos[1])
    time.sleep(0.05)

# сохраняет координаты курсора мыши только не в игре

import time
from pynput import mouse

# Store mouse movement data
mouse_data = []
def on_move(x, y):
    timestamp = time.time()
    mouse_data.append((x, y, timestamp))

# Listener for mouse movements
with mouse.Listener(on_move=on_move) as listener:
    time.sleep(5)  # Capture movements for 5 seconds
    listener.stop()
# Save data to a file
with open("mouse_data.txt", "w") as f:
    for entry in mouse_data:
        f.write(f"{entry[0]},{entry[1]},{entry[2]}\n")
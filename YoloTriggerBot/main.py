import threading, time
import numpy as np, mss, ultralytics
import cv2
from config import config
from fire import fire
from recoil import recoil_loop
from gui import CreateOverlay, switch_mode
from ai import update_gui_ai_frame, UpdateTargetDot
import win32api

def main():
    model = ultralytics.YOLO("bestv3.pt")
    screenCapture = mss.mss()

    if config.show_gui_menu:
        threading.Thread(target=CreateOverlay).start()

    threading.Thread(target=recoil_loop, daemon=True).start()

    prev_time = time.time()
    is_firing = False
    x1 = y1 = x2 = y2 = 0
    moveX = moveY = 0
    displacementX = displacementY = -1
    noDetectionIteration = 1

    while config.Running:
        if win32api.GetAsyncKeyState(0x05) & 1:
            switch_mode()
            time.sleep(0.1)

        if not config.AimToggle:
            continue

        GameFrame = np.array(screenCapture.grab(config.region))
        GameFrame = cv2.cvtColor(GameFrame, cv2.COLOR_BGRA2BGR)
        results = model.predict(source=GameFrame, conf=0.5, classes=config.detect_classes,
                                verbose=False, max_det=4, stream=False, imgsz=640)
        boxes = results[0].boxes.xyxy
        if len(boxes) > 0:
            for box in boxes:
                x1, y1, x2, y2 = box.tolist()
                displacementX = x2 - x1
                displacementY = y2 - y1
                target_x = int(x1 + displacementX / 2)
                target_y = int(y1 + displacementY / 3) + config.target_offset_y
                moveX = target_x - config.crosshairX
                moveY = target_y - config.crosshairY
                noDetectionIteration = 0
                cv2.rectangle(GameFrame, (int(x1), int(y1)), (int(x2), int(y2)), (100,100,255), 1)
                cv2.circle(GameFrame, (target_x, target_y), 3, (255,0,0), -1)
                UpdateTargetDot(config.crosshairX + moveX, config.crosshairY + moveY)
        else:
            x1 = y1 = x2 = y2 = 0
            displacementX = displacementY = -1
            moveX = moveY = 9999
            noDetectionIteration += 1
            UpdateTargetDot(-10, -10)

        aim_threshold_x = displacementX * config.aim_threshold_x
        aim_threshold_y = displacementY * config.aim_threshold_y

        if abs(moveX) <= aim_threshold_x and abs(moveY) <= aim_threshold_y and noDetectionIteration <= 1 and not is_firing:
            noDetectionIteration += 1
            threading.Thread(target=fire).start()

        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time

        if config.show_fps:
            cv2.putText(GameFrame, f"FPS: {fps:.2f}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0,255,0), 1)

        if config.show_debug_window:
            update_gui_ai_frame(GameFrame)

        del GameFrame

        if cv2.waitKey(1) & 0xFF == ord('q'):
            config.Running = False
            break

if __name__ == "__main__":
    main()

# захват экрана

import torch
import mss
import numpy as np
import cv2
import time
import os
from ultralytics import YOLO

# Путь к обученной модели YOLOv8
model_path = r'C:/Users/mbyin/PyNeuroVisionScript/TrafoModel_1/exp1/weights/best.pt'
model = YOLO(model_path).cuda()

# Создаем окно с возможностью изменения размера
cv2.namedWindow("YOLOv8 Detection", cv2.WINDOW_NORMAL)
cv2.resizeWindow("YOLOv8 Detection", 800, 600)

prev_time = time.time()

with mss.mss() as sct:
    # Определяем размеры главного экрана
    monitor = sct.monitors[1]  # Первый монитор (основной)

    while True:
        # Захват всего экрана
        screenshot = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        # Запуск модели на кадре
        results = model(frame)

        # Отображение результатов
        annotated_frame = results[0].plot()

        # Вычисление FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time

        # Отображение FPS на изображении
        cv2.putText(annotated_frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Отображение аннотированного изображения
        cv2.imshow("YOLOv8 Detection", annotated_frame)

        # Выход при нажатии клавиши ESC
        if cv2.waitKey(1) & 0xFF == 27:
            break

cv2.destroyAllWindows()

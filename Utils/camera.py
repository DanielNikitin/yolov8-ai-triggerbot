# yolov8 detect при помощи камеры (не тестил)

import cv2
import torch
import time
from ultralytics import YOLO

# Путь к обученной модели YOLOv8
model_path = r'C:/Users/mbyin/PyNeuroVisionScript/TrafoModel_1/exp1/weights/best.pt'
model = YOLO(model_path).cuda()

# Открываем камеру (0 - первая камера)
cap = cv2.VideoCapture(0)

# Проверяем, удалось ли открыть камеру
if not cap.isOpened():
    print("Ошибка: не удалось открыть камеру")
    exit()

# Создаем окно для отображения результатов
cv2.namedWindow("YOLOv8 Camera Detection", cv2.WINDOW_NORMAL)
cv2.resizeWindow("YOLOv8 Camera Detection", 800, 600)

prev_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Ошибка: не удалось получить кадр с камеры")
        break

    # Запускаем модель на кадре
    results = model(frame)

    # Отображаем аннотированный кадр
    annotated_frame = results[0].plot()

    # Вычисляем и отображаем FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time
    cv2.putText(annotated_frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("YOLOv8 Camera Detection", annotated_frame)

    # Нажмите ESC для выхода
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

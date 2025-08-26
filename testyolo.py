import torch
import mss
import numpy as np
import cv2
import time
import os
from ultralytics import YOLO
import pygetwindow as gw

# Путь к обученной модели YOLOv8
model_path = os.path.join(os.getcwd(), "FoxholeModel_4", "exp5", "weights", "best.pt")
model = YOLO(model_path).cuda()

# Функция для нахождения окна игры по процессу "War"
def find_game_window(title_keyword="War"):
    windows = gw.getWindowsWithTitle(title_keyword)
    for window in windows:
        if title_keyword.lower() in window.title.lower():
            print(f"Найдено окно: {window.title}")
            return window
    return None

# Создаем окно с возможностью изменения размера
cv2.namedWindow("YOLOv8 Detection", cv2.WINDOW_NORMAL)
cv2.resizeWindow("YOLOv8 Detection", 800, 600)

# Захват экрана по координатам окна игры и обработка модели
def capture_and_predict(game_window, prev_time):
    # Получаем координаты окна игры
    x, y, width, height = game_window.left, game_window.top, game_window.width, game_window.height

    # Используем mss для захвата экрана по координатам окна игры
    with mss.mss() as sct:
        monitor = {"top": y, "left": x, "width": width, "height": height}
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
    if cv2.waitKey(1) & 0xFF == 27:  # 27 - ESC
        return False, prev_time

    return True, prev_time

# Поиск окна игры и запуск детекции
game_window = find_game_window("War")

if game_window:
    print("Окно найдено, запускаем распознавание...")

    prev_time = time.time()  # Время начала
    is_running = True

    while is_running:
        is_running, prev_time = capture_and_predict(game_window, prev_time)

    cv2.destroyAllWindows()
else:
    print("Не удалось найти окно игры 'War'. Убедитесь, что игра запущена и окно доступно.")

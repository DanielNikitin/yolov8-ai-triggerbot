# проверка подключения камеры через карту захвата

import cv2

# Проверяем камеры с номерами от 0 до 10
for i in range(10):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Камера найдена: {i}")
        cap.release()
    else:
        print(f"Камера {i} недоступна")

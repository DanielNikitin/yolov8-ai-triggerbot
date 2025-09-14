# авто-аннотация по изображениям материала

from ultralytics import YOLO
import cv2
import os

# Путь к обученной модели
model_path = 'C:/Users/mbyin/PyNeuroVisionScript/YoloAimBot/best.pt'
model = YOLO(model_path)

# Папка с кадрами
input_dir = "CS2DataV1/"  # имя папки
output_dir = "CS2DataV1_Annotated"  # аннотированная дата
os.makedirs(output_dir, exist_ok=True)

# Обработка каждого кадра
for img_name in os.listdir(input_dir):
    img_path = os.path.join(input_dir, img_name)
    frame = cv2.imread(img_path)

    # Используем модель для предсказания объектов на кадре
    results = model(frame)

    # Сохранение обработанного кадра с аннотациями
    for i, result in enumerate(results):
        output_path = os.path.join(output_dir, f"{os.path.splitext(img_name)[0]}_annotated_{i}.jpg")
        result.save(output_path)  # Сохранение аннотированного изображения

    print(f"Аннотировано: {img_name}")

print(f"Аннотация завершена. Проверь папку: {output_dir}")

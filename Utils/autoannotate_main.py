from ultralytics import YOLO
import cv2
import os
import torch

# Путь к обученной модели
model_path = 'C:/Users/mbyin/PyNeuroVisionScript/YoloAimBot/best.pt'
model = YOLO(model_path)

# Папка с изображениями
input_dir = "CS2DataV1/raw_images"
output_images_dir = "CS2DataV1_Annotated/images"
output_labels_dir = "CS2DataV1_Annotated/labels"
os.makedirs(output_images_dir, exist_ok=True)
os.makedirs(output_labels_dir, exist_ok=True)

# Обработка каждого изображения
for img_name in os.listdir(input_dir):
    if not img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
        continue  # пропускаем не-изображения

    img_path = os.path.join(input_dir, img_name)
    frame = cv2.imread(img_path)

    results = model(frame)[0]  # берём первый результат

    # Копируем оригинальное изображение
    cv2.imwrite(os.path.join(output_images_dir, img_name), frame)

    # Получение размеров изображения
    h, w, _ = frame.shape

    # Сохранение .txt файла с аннотациями
    txt_path = os.path.join(output_labels_dir, os.path.splitext(img_name)[0] + ".txt")
    with open(txt_path, "w") as f:
        for box in results.boxes:
            cls = int(box.cls[0])  # класс
            device = box.xywh.device
            x_center, y_center, bw, bh = (box.xywh[0] / torch.tensor([w, h, w, h], device=device)).tolist()
            f.write(f"{cls} {x_center:.6f} {y_center:.6f} {bw:.6f} {bh:.6f}\n")

    print(f"Аннотировано: {img_name}")

print(f"\nГотово. Изображения и аннотации находятся в: {output_images_dir} и {output_labels_dir}")

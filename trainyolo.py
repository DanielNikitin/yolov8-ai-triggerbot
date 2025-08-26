#  обучение YOLO модели с нуля

from ultralytics import YOLO

if __name__ == '__main__':
    try:
        # Загружаем модель YOLOv8
        model = YOLO('yolov8n.pt')

        print('creating model FOR CS2 is started :: v8n batch 4, 1024, exp3, yoloAimV3')

        # Обучаем модель на своих данных
        results = model.train(
            data="C:\\Users\\mbyin\\PyNeuroVisionScript\\yoloDataV2\\data.yaml",
            epochs=100,  # Количество эпох
            imgsz=1024,  # Размер входного изображения
            batch=4,  # Размер батча (уменьши, если мало VRAM)
            device=0,  # GPU (0), CPU(1)
            workers=2,  # Количество потоков для загрузки данных
            project="YoloAimBotV3_Model",  # Название проекта
            name="exp3",  # Название эксперимента
            multi_scale=True,  # Включить переменное масштабирование
            exist_ok=True  # Разрешаем перезаписывать результаты
        )

        # Выводим краткую сводку обучения
        print(results)

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        exit(1)  # Завершаем выполнение скрипта с кодом ошибки







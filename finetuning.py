#  до-обучение уже готовой модели

# coal, scrap, sulfure, component
# flatbad, transporter, road, player,
# map-component, map-player, map-road, map-sulfure

# 640
# 1024
# 1280

from ultralytics import YOLO

if __name__ == '__main__':
    try:
        # Загружаем готовую модель на до-обучение
        model = YOLO(r'C:\Users\mbyin\PyNeuroVisionScript\FoxholeModel_4\exp5\weights\best.pt')

        print('fine-tuning is started 1024, batch=4, dataset = ok, FoxholeModel_4, exp5')

        # Обучаем модель на своих данных (дообучение)
        results = model.train(
            data=r"C:\Users\mbyin\PyNeuroVisionScript\FoxholeModel_Dataset_ok\data.yaml",  # Путь к материалу для до-обучения data.yaml
            epochs=30,         # Количество эпох (можно увеличить, если данных много)
            imgsz=1024,         # Размер входного изображения (увеличение может улучшить точность)
            batch=4,          # Размер батча (уменьши, если не хватает VRAM)
            device=0,          # Использование GPU (0), если CPU, то 'cpu'
            workers=2,         # Количество потоков для загрузки данных (SSD = 2)
            project="FoxholeModel_4",  # Название проекта (папка с результатами)
            name="exp5",       # Название эксперимента (чтобы не перезаписать старый)
            exist_ok=True,     # Разрешаем перезаписывать результаты (True, если перезапись нужна)
            resume=False        # Продолжаем обучение с последней эпохи
        )

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        exit(1)  # Завершаем выполнение скрипта с кодом ошибки
# комбинация нескольких датасетов в 1 пакет

import shutil
import os

# Пути к датасетам
dataset1_path = "FoxholeModel_Dataset_ok"
dataset2_path = "FoxholeModel_1_Tuning_ok"
dataset3_path = "FoxholeModel_Dataset2_ok"
merged_dataset_path = "FoxholeModel_Merged"

# Список папок train, valid, test
subdirs = ['train', 'valid', 'test']

def merge_datasets(src_root, dst_root):
    for subdir in subdirs:
        # Пути для изображений и аннотаций с учетом правильной структуры папок
        src_images = os.path.join(src_root, subdir, 'images')
        src_labels = os.path.join(src_root, subdir, 'labels')
        
        dst_images = os.path.join(dst_root, subdir, 'images')
        dst_labels = os.path.join(dst_root, subdir, 'labels')

        # Проверка существования папок источников
        if not os.path.exists(src_images):
            print(f"Папка {src_images} не найдена, пропускаем...")
            continue
        if not os.path.exists(src_labels):
            print(f"Папка {src_labels} не найдена, пропускаем...")
            continue

        # Создание папок назначения
        os.makedirs(dst_images, exist_ok=True)
        os.makedirs(dst_labels, exist_ok=True)

        # Копируем изображения
        for filename in os.listdir(src_images):
            src_file = os.path.join(src_images, filename)
            dst_file = os.path.join(dst_images, filename)
            shutil.copy(src_file, dst_file)

        # Копируем аннотации
        for filename in os.listdir(src_labels):
            src_file = os.path.join(src_labels, filename)
            dst_file = os.path.join(dst_labels, filename)
            shutil.copy(src_file, dst_file)

        print(f"Объединены файлы из {src_root}/{subdir}")

# Объединение данных первого, второго и третьего датасетов
merge_datasets(dataset1_path, merged_dataset_path)
merge_datasets(dataset2_path, merged_dataset_path)
merge_datasets(dataset3_path, merged_dataset_path)

print("Объединение датасетов завершено.")

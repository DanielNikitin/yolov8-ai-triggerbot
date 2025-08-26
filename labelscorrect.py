#  изменение порядка классов в labels аннотациях для соответствия второму датасету

import os

# Пути к аннотациям первого датасета (корневая папка с train/valid/test)
dataset1_labels_path = "FoxholeModel_1_Tuning_ok\\"
print('script is started')

# Словарь для переименования классов {старый индекс: новый индекс}
class_mapping = {
    '0': '10',   # coal -> 1 (второй класс в data.yaml второго датасета)
    '1': '12',  # player -> 10
    '2': '14'   # transporter -> 14

    # 10 - player
    # 14 - transporter
    # 1 - coal
    # 12 - scrap
}

# Функция обновления меток в .txt файлах
def update_labels(folder_path):
    for subdir in ['train', 'valid', 'test']:
        label_subdir_path = os.path.join(folder_path, subdir, 'labels')

        # Проверяем, существует ли папка с аннотациями, иначе пропускаем
        if not os.path.exists(label_subdir_path):
            print(f"Папка {label_subdir_path} не найдена, пропускаем...")
            continue

        for filename in os.listdir(label_subdir_path):
            # Проверяем, является ли объект файлом и имеет ли расширение .txt
            file_path = os.path.join(label_subdir_path, filename)
            if not os.path.isfile(file_path) or not filename.endswith('.txt'):
                continue  # Пропускаем, если не текстовый файл

            # Чтение и обновление файла
            with open(file_path, 'r') as f:
                lines = f.readlines()

            updated_lines = []
            for line in lines:
                parts = line.strip().split()
                if parts and parts[0] in class_mapping:
                    parts[0] = class_mapping[parts[0]]  # Обновляем класс
                updated_lines.append(" ".join(parts))

            # Запись обновленных данных обратно в файл
            with open(file_path, 'w') as f:
                f.write("\n".join(updated_lines))

            print(f"Обновлен файл: {file_path}")

# Запуск обновления аннотаций
update_labels(dataset1_labels_path)
print("Обновление аннотаций завершено.")

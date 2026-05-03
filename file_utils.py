import json


def read_file(file_path):
    """Читает файл в бинарном режиме. Возвращает содержимое в байтах."""
    with open(file_path, 'rb') as f:
        return f.read()


def write_file(file_path, data):
    """Записывает бинарные данные в файл."""
    with open(file_path, 'wb') as f:
        f.write(data)


def read_text_file(file_path):
    """Читает текстовый файл в кодировке UTF-8. Возвращает строку."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_text_file(file_path, data):
    """Записывает текстовые данные в файл в кодировке UTF-8."""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(data)


def load_config(config_path='settings.json'):
    """Загружает конфигурацию из JSON файла. Возвращает словарь."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config, config_path='settings.json'):
    """Сохраняет конфигурацию в JSON файл."""
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
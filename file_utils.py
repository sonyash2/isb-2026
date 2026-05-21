import json


def read_file(file_path):
    """Читает файл в бинарном режиме. Возвращает содержимое в байтах."""
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    except IOError as e:
        raise IOError(f"Ошибка чтения файла {file_path}: {e}")


def write_file(file_path, data):
    """Записывает бинарные данные в файл."""
    try:
        with open(file_path, 'wb') as f:
            f.write(data)
    except IOError as e:
        raise IOError(f"Ошибка записи файла {file_path}: {e}")


def read_text_file(file_path):
    """Читает текстовый файл в кодировке UTF-8. Возвращает строку."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(f"Ошибка декодирования файла {file_path}: {e}")
    except IOError as e:
        raise IOError(f"Ошибка чтения файла {file_path}: {e}")


def write_text_file(file_path, data):
    """Записывает текстовые данные в файл в кодировке UTF-8."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data)
    except IOError as e:
        raise IOError(f"Ошибка записи файла {file_path}: {e}")


def load_config(config_path='settings.json'):
    """Загружает конфигурацию из JSON файла. Возвращает словарь."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Ошибка парсинга JSON: {e}", e.doc, e.pos)


def save_config(config, config_path='settings.json'):
    """Сохраняет конфигурацию в JSON файл."""
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except IOError as e:
        raise IOError(f"Ошибка сохранения конфигурации {config_path}: {e}")

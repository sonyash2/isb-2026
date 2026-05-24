import hashlib
import os
from tqdm import tqdm


def calculate_hash(file_path, algorithm='sha256', progress=True):
    """
    Вычисляет хеш-сумму файла.
    
    Параметры:
        file_path: путь к файлу
        algorithm: алгоритм хеширования (sha256, md5, sha1)
        progress: показывать прогресс-бар
    
    Возвращает:
        str: хеш-сумма в шестнадцатеричном виде
    """
    hash_func = hashlib.new(algorithm)
    file_size = os.path.getsize(file_path)
    
    with open(file_path, 'rb') as f:
        if progress:
            with tqdm(total=file_size, unit='B', unit_scale=True, desc="Вычисление хеша") as pbar:
                while chunk := f.read(8192):
                    hash_func.update(chunk)
                    pbar.update(len(chunk))
        else:
            while chunk := f.read(8192):
                hash_func.update(chunk)
    
    return hash_func.hexdigest()


def save_hash(file_path, hash_value, hash_file=None):
    """
    Сохраняет хеш-сумму в файл.
    
    Параметры:
        file_path: путь к исходному файлу
        hash_value: вычисленная хеш-сумма
        hash_file: путь для сохранения хеша (если None, создается рядом с файлом)
    
    Возвращает:
        str: путь к файлу с хешем
    """
    if hash_file is None:
        hash_file = file_path + '.sha256'
    
    with open(hash_file, 'w') as f:
        f.write(f"{hash_value}  {os.path.basename(file_path)}")
    
    return hash_file


def load_hash(hash_file):
    """
    Загружает хеш-сумму из файла.
    
    Параметры:
        hash_file: путь к файлу с хешем
    
    Возвращает:
        str: хеш-сумма
    """
    with open(hash_file, 'r') as f:
        content = f.read().strip()
        # Формат: "хеш  имя_файла"
        return content.split()[0]


def verify_integrity(file_path, hash_file=None, progress=True):
    """
    Проверяет целостность файла.
    
    Параметры:
        file_path: путь к файлу для проверки
        hash_file: путь к файлу с хешем (если None, ищется рядом)
        progress: показывать прогресс-бар
    
    Возвращает:
        tuple: (is_valid, current_hash, saved_hash)
    """
    if hash_file is None:
        hash_file = file_path + '.sha256'
    
    if not os.path.exists(hash_file):
        raise FileNotFoundError(f"Файл с хешем не найден: {hash_file}")
    
    current_hash = calculate_hash(file_path, progress=progress)
    saved_hash = load_hash(hash_file)
    
    return current_hash == saved_hash, current_hash, saved_hash


def find_collision(algorithm='sha256', max_attempts=100000):
    """
    Демонстрирует поиск коллизии (упрощенная версия для демонстрации).
    
    Параметры:
        algorithm: алгоритм хеширования
        max_attempts: максимальное количество попыток
    
    Возвращает:
        dict: результаты поиска
    """
    import random
    import string
    
    hashes = {}
    
    for i in tqdm(range(max_attempts), desc="Поиск коллизий"):
        # Генерируем случайное сообщение
        length = random.randint(10, 100)
        message = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        
        # Вычисляем хеш
        hash_value = hashlib.new(algorithm, message.encode()).hexdigest()[:16]
        
        # Проверяем, не было ли уже такого хеша
        if hash_value in hashes:
            return {
                'found': True,
                'attempts': i + 1,
                'message1': hashes[hash_value],
                'message2': message,
                'hash': hash_value
            }
        
        hashes[hash_value] = message
    
    return {'found': False, 'attempts': max_attempts}
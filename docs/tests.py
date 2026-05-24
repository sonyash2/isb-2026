import unittest
import os
import tempfile
import hashlib
from hash_utils import calculate_hash, save_hash, load_hash, verify_integrity


class TestHashUtils(unittest.TestCase):
    
    def setUp(self):
        # Создаем временный файл для тестов
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(b"Hello, World!")
        self.temp_file.close()
        self.file_path = self.temp_file.name
    
    def tearDown(self):
        # Удаляем временные файлы
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        if os.path.exists(self.file_path + '.sha256'):
            os.remove(self.file_path + '.sha256')
    
    def test_calculate_hash(self):
        """Тест вычисления хеша."""
        hash_value = calculate_hash(self.file_path, progress=False)
        
        # SHA-256 от "Hello, World!"
        expected = hashlib.sha256(b"Hello, World!").hexdigest()
        
        self.assertEqual(hash_value, expected)
    
    def test_save_and_load_hash(self):
        """Тест сохранения и загрузки хеша."""
        hash_value = calculate_hash(self.file_path, progress=False)
        hash_path = save_hash(self.file_path, hash_value)
        
        self.assertTrue(os.path.exists(hash_path))
        
        loaded_hash = load_hash(hash_path)
        self.assertEqual(loaded_hash, hash_value)
    
    def test_verify_integrity_valid(self):
        """Тест проверки целостности для неизмененного файла."""
        hash_value = calculate_hash(self.file_path, progress=False)
        save_hash(self.file_path, hash_value)
        
        is_valid, current, saved = verify_integrity(self.file_path, progress=False)
        
        self.assertTrue(is_valid)
        self.assertEqual(current, saved)
    
    def test_verify_integrity_invalid(self):
        """Тест проверки целостности для измененного файла."""
        hash_value = calculate_hash(self.file_path, progress=False)
        save_hash(self.file_path, hash_value)
        
        # Изменяем файл
        with open(self.file_path, 'wb') as f:
            f.write(b"Modified content!")
        
        is_valid, current, saved = verify_integrity(self.file_path, progress=False)
        
        self.assertFalse(is_valid)
        self.assertNotEqual(current, saved)
    
    def test_hash_differs_when_file_changes(self):
        """Тест: при изменении файла хеш меняется."""
        hash1 = calculate_hash(self.file_path, progress=False)
        
        # Изменяем файл
        with open(self.file_path, 'wb') as f:
            f.write(b"Different content")
        
        hash2 = calculate_hash(self.file_path, progress=False)
        
        self.assertNotEqual(hash1, hash2)
    
    def test_lavalanche_effect(self):
        """Тест лавинного эффекта: изменение 1 байта сильно меняет хеш."""
        hash1 = calculate_hash(self.file_path, progress=False)
        
        # Изменяем 1 байт
        with open(self.file_path, 'rb') as f:
            content = f.read()
        
        modified = bytearray(content)
        modified[0] = modified[0] ^ 1  # инвертируем первый бит
        
        with open(self.file_path, 'wb') as f:
            f.write(modified)
        
        hash2 = calculate_hash(self.file_path, progress=False)
        
        # Хеши должны отличаться
        self.assertNotEqual(hash1, hash2)
        
        # Подсчитываем количество отличающихся бит
        diff_bits = sum(bin(int(h1, 16) ^ int(h2, 16)).count('1') 
                        for h1, h2 in zip(hash1, hash2))
        
        # Примерно половина бит должна измениться (лавинный эффект)
        self.assertGreater(diff_bits, 100)  # хотя бы 100 бит из 256


if __name__ == '__main__':
    unittest.main()
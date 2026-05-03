import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


class SymmetricCrypto:
    """Класс для симметричного шифрования SM4."""
    
    def __init__(self, key_size=16):
        self.key_size = key_size
        self.block_size = 128
    
    def generate_key(self):
        """Генерирует случайный симметричный ключ. Возвращает ключ в байтах."""
        return os.urandom(self.key_size)
    
    def encrypt(self, data, key):
        """Шифрует данные алгоритмом SM4 в режиме CBC. Возвращает IV + шифротекст."""
        iv = os.urandom(16)
        cipher = Cipher(algorithms.SM4(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(self.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return iv + encrypted_data
    
    def decrypt(self, encrypted_data, key):
        """Расшифровывает данные алгоритмом SM4 в режиме CBC. Возвращает расшифрованные данные."""
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        cipher = Cipher(algorithms.SM4(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(self.block_size).unpadder()
        decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()
        return decrypted_data
    
    def is_valid_key(self, key):
        """Проверяет валидность ключа. Возвращает True если размер ключа правильный."""
        return len(key) == self.key_size
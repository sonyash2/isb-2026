import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend


class AsymmetricCrypto:
    """Класс для асимметричного шифрования RSA."""
    
    def __init__(self, key_size=2048, public_exponent=65537):
        """
        Создает объект для работы с RSA.
        Параметры:
            key_size: размер ключа в битах (по умолчанию 2048)
            public_exponent: открытая экспонента (по умолчанию 65537)
        """
        self.key_size = key_size
        self.public_exponent = public_exponent
    
    def generate_key_pair(self):
        """
        Генерирует пару ключей RSA.
        Возвращает:
            private_key, public_key: объекты закрытого и открытого ключей
        """
        try:
            private_key = rsa.generate_private_key(
                public_exponent=self.public_exponent,
                key_size=self.key_size,
                backend=default_backend()
            )
            public_key = private_key.public_key()
            return private_key, public_key
        except Exception as e:
            raise Exception(f"Ошибка генерации ключей RSA: {e}")
    
    def encrypt_with_public_key(self, data, public_key):
        """
        Шифрует данные открытым ключом RSA с использованием OAEP паддинга.
        Входные параметры:
            data: байтовые данные для шифрования (не более 190 байт для ключа 2048 бит)
            public_key: открытый ключ RSA (объект)
        Возвращает:
            bytes: зашифрованные данные
        """
        try:
            encrypted_data = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return encrypted_data
        except ValueError as e:
            raise ValueError(f"Данные слишком большие для шифрования RSA: {e}")
        except Exception as e:
            raise Exception(f"Ошибка шифрования открытым ключом: {e}")
    
    def decrypt_with_private_key(self, encrypted_data, private_key):
        """
        Расшифровывает данные закрытым ключом RSA. 
        Входные параметры:
            encrypted_data: байтовые зашифрованные данные
            private_key: закрытый ключ RSA (объект)
        Возвращает:
            bytes: расшифрованные данные
        """
        try:
            decrypted_data = private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted_data
        except Exception as e:
            raise Exception(f"Ошибка расшифрования закрытым ключом: {e}")
    
    def serialize_public_key(self, public_key):
        """
        Сериализует открытый ключ в PEM формат для сохранения в файл.
        Входные параметры:
            public_key: открытый ключ RSA (объект)
        Возвращает:
            bytes: сериализованный ключ в PEM формате
        """
        try:
            return public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        except Exception as e:
            raise Exception(f"Ошибка сериализации открытого ключа: {e}")
    
    def serialize_private_key(self, private_key):
        """
        Сериализует закрытый ключ в PEM формат для сохранения в файл.
        Входные параметры:
            private_key: закрытый ключ RSA (объект)
        Возвращает:
            bytes: сериализованный ключ в PEM формате
        """
        try:
            return private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        except Exception as e:
            raise Exception(f"Ошибка сериализации закрытого ключа: {e}")
    
    def deserialize_public_key(self, key_bytes):
        """
        Десериализует открытый ключ из PEM формата (из файла).
        Входные параметры:
            key_bytes: байты сериализованного ключа в PEM формате
        Возвращает:
            public_key: объект открытого ключа RSA
        """
        try:
            return serialization.load_pem_public_key(key_bytes, backend=default_backend())
        except Exception as e:
            raise Exception(f"Ошибка десериализации открытого ключа: {e}")
    
    def deserialize_private_key(self, key_bytes):
        """
        Десериализует закрытый ключ из PEM формата (из файла).
        Входные параметры:
            key_bytes: байты сериализованного ключа в PEM формате
        Возвращает:
            private_key: объект закрытого ключа RSA
        """
        try:
            return serialization.load_pem_private_key(
                key_bytes, 
                password=None, 
                backend=default_backend()
            )
        except Exception as e:
            raise Exception(f"Ошибка десериализации закрытого ключа: {e}")

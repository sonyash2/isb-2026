import sys
import argparse
from file_utils import load_config, read_file, write_file
from asymmetric_crypto import AsymmetricCrypto
from symmetric_crypto import SymmetricCrypto


def generate_keys(config):
    """Режим генерации ключей. Создает RSA ключи и зашифрованный симметричный ключ."""
    print("\n ГЕНЕРАЦИЯ КЛЮЧЕЙ \n")
    
    symmetric = SymmetricCrypto(key_size=config['algorithms']['sm4_key_size'])
    asymmetric = AsymmetricCrypto(key_size=config['algorithms']['key_size'])
    
    print("1. Генерация симметричного ключа SM4...")
    symmetric_key = symmetric.generate_key()
    print(f"   Ключ сгенерирован (размер: {len(symmetric_key)} байт)")
    
    print("2. Генерация асимметричных ключей RSA...")
    private_key, public_key = asymmetric.generate_key_pair()
    print(f"   Ключи RSA сгенерированы (размер: {config['algorithms']['key_size']} бит)")
    
    print("3. Сохранение асимметричных ключей...")
    write_file(config['public_key'], asymmetric.serialize_public_key(public_key))
    write_file(config['private_key'], asymmetric.serialize_private_key(private_key))
    print(f"   Открытый ключ: {config['public_key']}")
    print(f"   Закрытый ключ: {config['private_key']}")
    
    print("4. Шифрование и сохранение симметричного ключа...")
    encrypted_symmetric_key = asymmetric.encrypt_with_public_key(symmetric_key, public_key)
    write_file(config['encrypted_symmetric_key'], encrypted_symmetric_key)
    print(f"   Зашифрованный ключ: {config['encrypted_symmetric_key']}")
    
    print("\n ГЕНЕРАЦИЯ КЛЮЧЕЙ ЗАВЕРШЕНА\n")


def encrypt_file(config):
    """Режим шифрования файла. Загружает ключи и шифрует исходный файл."""
    print("\n ШИФРОВАНИЕ ФАЙЛА \n")
    
    symmetric = SymmetricCrypto(key_size=config['algorithms']['sm4_key_size'])
    asymmetric = AsymmetricCrypto(key_size=config['algorithms']['key_size'])
    
    print("1. Загрузка закрытого ключа RSA...")
    private_key_bytes = read_file(config['private_key'])
    private_key = asymmetric.deserialize_private_key(private_key_bytes)
    print("   Закрытый ключ загружен")
    
    print("2. Расшифровка симметричного ключа...")
    encrypted_symmetric_key = read_file(config['encrypted_symmetric_key'])
    symmetric_key = asymmetric.decrypt_with_private_key(encrypted_symmetric_key, private_key)
    print(f"   Ключ расшифрован (размер: {len(symmetric_key)} байт)")
    
    print(f"3. Загрузка исходного файла: {config['initial_file']}")
    plaintext = read_file(config['initial_file'])
    print(f"   Файл загружен (размер: {len(plaintext)} байт)")
    
    print("4. Шифрование файла SM4-CBC...")
    encrypted_data = symmetric.encrypt(plaintext, symmetric_key)
    write_file(config['encrypted_file'], encrypted_data)
    print(f"   Файл зашифрован: {config['encrypted_file']}")
    print(f"   Размер: {len(encrypted_data)} байт")
    
    print("\n ШИФРОВАНИЕ ЗАВЕРШЕНО\n")


def decrypt_file(config):
    """Режим расшифрования файла. Загружает ключи и расшифровывает файл."""
    print("\n РАСШИФРОВАНИЕ ФАЙЛА \n")
    
    symmetric = SymmetricCrypto(key_size=config['algorithms']['sm4_key_size'])
    asymmetric = AsymmetricCrypto(key_size=config['algorithms']['key_size'])
    
    print("1. Загрузка закрытого ключа RSA...")
    private_key_bytes = read_file(config['private_key'])
    private_key = asymmetric.deserialize_private_key(private_key_bytes)
    print("   Закрытый ключ загружен")
    
    print("2. Расшифровка симметричного ключа...")
    encrypted_symmetric_key = read_file(config['encrypted_symmetric_key'])
    symmetric_key = asymmetric.decrypt_with_private_key(encrypted_symmetric_key, private_key)
    print(f"   Ключ расшифрован (размер: {len(symmetric_key)} байт)")
    
    print(f"3. Загрузка зашифрованного файла: {config['encrypted_file']}")
    encrypted_data = read_file(config['encrypted_file'])
    print(f"   Файл загружен (размер: {len(encrypted_data)} байт)")
    
    print("4. Расшифрование файла SM4-CBC...")
    decrypted_data = symmetric.decrypt(encrypted_data, symmetric_key)
    write_file(config['decrypted_file'], decrypted_data)
    print(f"   Файл расшифрован: {config['decrypted_file']}")
    print(f"   Размер: {len(decrypted_data)} байт")
    
    print("\n РАСШИФРОВАНИЕ ЗАВЕРШЕНО\n")


def main():
    """Главная функция обработки аргументов командной строки."""
    parser = argparse.ArgumentParser(description='Гибридная криптосистема RSA + SM4')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--gen', action='store_true', help='Генерация ключей')
    group.add_argument('--enc', action='store_true', help='Шифрование файла')
    group.add_argument('--dec', action='store_true', help='Расшифрование файла')
    parser.add_argument('--in', dest='input_file', help='Путь к входному файлу')
    parser.add_argument('--out', dest='output_file', help='Путь к выходному файлу')
    parser.add_argument('--config', default='settings.json', help='Путь к файлу конфигурации')
    
    args = parser.parse_args()
    
    try:
        config = load_config(args.config)
        
        if args.input_file:
            config['initial_file'] = args.input_file
        if args.output_file and args.enc:
            config['encrypted_file'] = args.output_file
        if args.output_file and args.dec:
            config['decrypted_file'] = args.output_file
        
        match args:
            case _ if args.gen:
                generate_keys(config)
            case _ if args.enc:
                encrypt_file(config)
            case _ if args.dec:
                decrypt_file(config)
            case _:
                print("Неизвестный режим")
                sys.exit(1)
                
    except FileNotFoundError as e:
        print(f"\n Ошибка: файл не найден - {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n Ошибка: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
import sys
import os
import argparse
from hash_utils import calculate_hash, save_hash, verify_integrity, find_collision


def main():
    parser = argparse.ArgumentParser(description='Контроль целостности файлов с помощью хеш-функций')
    
    subparsers = parser.add_subparsers(dest='command', required=True, help='Доступные команды')
    
    hash_parser = subparsers.add_parser('hash', help='Вычислить хеш файла')
    hash_parser.add_argument('file', help='Путь к файлу')
    hash_parser.add_argument('-a', '--algorithm', default='sha256', help='Алгоритм хеширования')
    hash_parser.add_argument('--no-progress', action='store_true', help='Не показывать прогресс-бар')
    
    save_parser = subparsers.add_parser('save', help='Сохранить хеш в файл')
    save_parser.add_argument('file', help='Путь к файлу')
    save_parser.add_argument('-o', '--output', help='Путь для сохранения хеша')
    save_parser.add_argument('-a', '--algorithm', default='sha256', help='Алгоритм хеширования')
    
    verify_parser = subparsers.add_parser('verify', help='Проверить целостность файла')
    verify_parser.add_argument('file', help='Путь к файлу')
    verify_parser.add_argument('-hf', '--hash-file', help='Путь к файлу с хешем')
    
    collide_parser = subparsers.add_parser('collide', help='Поиск коллизий')
    collide_parser.add_argument('-a', '--algorithm', default='sha256', help='Алгоритм хеширования')
    collide_parser.add_argument('-n', '--attempts', type=int, default=100000, help='Количество попыток')
    
    args = parser.parse_args()
    
    try:
        match args.command:
            case 'hash':
                print(f"Вычисление хеша файла: {args.file}")
                hash_value = calculate_hash(args.file, args.algorithm, not args.no_progress)
                print(f"\n{args.algorithm.upper()} хеш: {hash_value}")
            
            case 'save':
                print(f"Сохранение хеша для файла: {args.file}")
                hash_value = calculate_hash(args.file, args.algorithm, progress=True)
                hash_path = save_hash(args.file, hash_value, args.output)
                print(f"Хеш сохранен в: {hash_path}")
                print(f"Значение: {hash_value}")
            
            case 'verify':
                print(f"Проверка целостности файла: {args.file}")
                is_valid, current_hash, saved_hash = verify_integrity(args.file, args.hash_file)
                
                print(f"\nТекущий хеш:  {current_hash}")
                print(f"Сохраненный хеш: {saved_hash}")
                
                if is_valid:
                    print("\nРЕЗУЛЬТАТ: Файл НЕ ИЗМЕНЕН. Целостность подтверждена.")
                else:
                    print("\nРЕЗУЛЬТАТ: Файл ИЗМЕНЕН. Целостность нарушена!")
            
            case 'collide':
                print(f"Поиск коллизий для {args.algorithm.upper()}...")
                result = find_collision(args.algorithm, args.attempts)
                
                if result['found']:
                    print(f"\nКОЛЛИЗИЯ НАЙДЕНА!")
                    print(f"Попыток: {result['attempts']}")
                    print(f"Хеш: {result['hash']}")
                    print(f"Сообщение 1: {result['message1']}")
                    print(f"Сообщение 2: {result['message2']}")
                else:
                    print(f"\nКоллизия не найдена за {result['attempts']} попыток")
    
    except FileNotFoundError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
"""
Программа для шифрования и дешифрования текста методами Цезаря и Виженера
Поддерживает русский и английский алфавиты, сохраняет регистр и неалфавитные символы

Основные принципы работы:
1. Шифр Цезаря - простой подстановочный шифр с фиксированным сдвигом
2. Шифр Виженера - полиалфавитный шифр с использованием ключевого слова
3. Оба метода сохраняют регистр букв и не изменяют символы не из алфавита
"""

import os
import random


def read_file(filename):
    """Чтение содержимого файла с проверкой его существования"""
    if not os.path.exists(filename):
        print(f"Ошибка: Файл {filename} не найден!")
        return None
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def write_file(filename, text):
    """Запись текста в файл"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


def get_first_lines(text, n=5):
    """Получение первых n строк текста (для предпросмотра)"""
    lines = text.splitlines()
    return "\n".join(lines[:n])






def caesar_encrypt(text, key):
    """Шифрование текста методом Цезаря с заданным ключом-сдвигом"""
    result = []
    # Определение алфавитов для латиницы и кириллицы (с учетом буквы Ё)
    LAT_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    LAT_LOWER = "abcdefghijklmnopqrstuvwxyz"
    RUS_UPPER = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    RUS_LOWER = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"

    for ch in text:
        # Алгоритм шифрования для каждого символа:
        # 1. Находим позицию символа в соответствующем алфавите
        # 2. Добавляем к позиции ключ (сдвиг)
        # 3. Берем результат по модулю длины алфавита (для зацикливания)
        # 4. Заменяем символ на новый из алфавита

        if ch in LAT_UPPER:  # Английские заглавные буквы
            new_index = (LAT_UPPER.index(ch) + key) % len(LAT_UPPER)
            result.append(LAT_UPPER[new_index])
        elif ch in LAT_LOWER:  # Английские строчные буквы
            new_index = (LAT_LOWER.index(ch) + key) % len(LAT_LOWER)
            result.append(LAT_LOWER[new_index])
        elif ch in RUS_UPPER:  # Русские заглавные буквы (включая Ё)
            new_index = (RUS_UPPER.index(ch) + key) % len(RUS_UPPER)
            result.append(RUS_UPPER[new_index])
        elif ch in RUS_LOWER:  # Русские строчные буквы (включая Ё)
            new_index = (RUS_LOWER.index(ch) + key) % len(RUS_LOWER)
            result.append(RUS_LOWER[new_index])
        else:
            result.append(ch)  # Неалфавитные символы остаются без изменений
    return "".join(result)


def caesar_decrypt(text, key):
    """Дешифрование текста методом Цезаря"""
    # Дешифрование - это шифрование с отрицательным ключом
    # Пример: если при шифровании сдвигали на +3, то при дешифровании сдвигаем на -3
    return caesar_encrypt(text, -key)



"""
Принцип работы шифра Виженера:
1. Использует ключевое слово вместо фиксированного сдвига
2. Каждая буква ключа определяет величину сдвига для соответствующей буквы текста
3. По сути, это несколько шифров Цезаря с разными ключами
4. Пример для русского алфавита с ключом "КЛЮЧ":
   Текст: П Р И В Е Т
   Ключ:  К Л Ю Ч К Л
   Шифр:  Щ Р У Ж Ъ Ц
"""

CYRILLIC_ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"


def vigenere_square(alphabet):
    """Генерация квадрата Виженера для заданного алфавита"""
    size = len(alphabet)
    rows = []
    # Квадрат Виженера - это таблица, где каждая строка представляет
    # алфавит, сдвинутый на одну позицию относительно предыдущей
    for i in range(size):
        # Создаем строку: алфавит, начиная с i-й позиции + остаток
        row = alphabet[i:] + alphabet[:i]
        rows.append(row)
    return "\n".join(rows)


def vigenere_encrypt(text, key, alphabet):
    """Шифрование текста методом Виженера"""
    result = []
    key_length = len(key)
    alphabet_upper = alphabet.upper()  # Алфавит в верхнем регистре
    alphabet_lower = alphabet.lower()  # Алфавит в нижнем регистре

    for i, ch in enumerate(text):
        # Алгоритм шифрования для каждого символа:
        # 1. Находим соответствующий символ ключа (ключ повторяется циклически)
        # 2. Определяем индексы символа текста и символа ключа в алфавите
        # 3. Складываем индексы по модулю длины алфавита
        # 4. Заменяем символ на новый из алфавита

        if ch.upper() in alphabet_upper:
            # Обработка с учетом регистра
            if ch.isupper():  # Для заглавных букв
                text_index = alphabet_upper.index(ch)
                key_char = key[i % key_length].upper()
                key_index = alphabet_upper.index(key_char)
                enc_index = (text_index + key_index) % len(alphabet_upper)
                result.append(alphabet_upper[enc_index])
            else:  # Для строчных букв
                text_index = alphabet_lower.index(ch)
                key_char = key[i % key_length].lower()
                key_index = alphabet_lower.index(key_char)
                enc_index = (text_index + key_index) % len(alphabet_lower)
                result.append(alphabet_lower[enc_index])
        else:
            result.append(ch)  # Неалфавитные символы остаются без изменений
    return "".join(result)


def vigenere_decrypt(text, key, alphabet):
    """Дешифрование текста методом Виженера"""
    result = []
    key_length = len(key)
    alphabet_upper = alphabet.upper()
    alphabet_lower = alphabet.lower()

    for i, ch in enumerate(text):
        # Алгоритм дешифрования аналогичен шифрованию, но вместо сложения
        # индексов выполняется вычитание индекса ключевого символа

        if ch.upper() in alphabet_upper:
            if ch.isupper():  # Для заглавных букв
                text_index = alphabet_upper.index(ch)
                key_char = key[i % key_length].upper()
                key_index = alphabet_upper.index(key_char)
                dec_index = (text_index - key_index) % len(alphabet_upper)
                result.append(alphabet_upper[dec_index])
            else:  # Для строчных букв
                text_index = alphabet_lower.index(ch)
                key_char = key[i % key_length].lower()
                key_index = alphabet_lower.index(key_char)
                dec_index = (text_index - key_index) % len(alphabet_lower)
                result.append(alphabet_lower[dec_index])
        else:
            result.append(ch)  # Неалфавитные символы остаются без изменений
    return "".join(result)



def caesar_cli():
    """Интерфейс командной строки для шифра Цезаря"""
    key = input("Введите ключ (целое число): ")
    try:
        key = int(key)
    except ValueError:
        print("Ошибка: Ключ должен быть целым числом!")
        return

    original = read_file("caesar_test.txt")
    if original is None or len(original) < 2000:
        print("Ошибка: Файл caesar_test.txt не найден или содержит менее 2000 символов!")
        return

    # Шифрование и дешифрование
    encrypted = caesar_encrypt(original, key)
    decrypted = caesar_decrypt(encrypted, key)

    # Сохранение результатов
    write_file("en_Cesar.txt", encrypted)
    write_file("de_Cesar.txt", decrypted)

    # Вывод результатов
    print("\nИсходный текст (первые 5 строк):")
    print(get_first_lines(original))
    print("\nЗашифрованный текст (Цезарь):")
    print(get_first_lines(encrypted))
    print("\nРасшифрованный текст (Цезарь):")
    print(get_first_lines(decrypted))


def vigenere_cli():
    """Интерфейс командной строки для шифра Виженера"""
    key = input("Введите ключ (текст): ").strip()
    if not key:
        print("Ошибка: Введите ключ!")
        return

    # Проверка ключа
    if not all(ch.upper() in CYRILLIC_ALPHABET for ch in key):
        print("Ошибка: Ключ должен содержать только кириллические символы!")
        return

    # Выбор алфавита
    alphabet_option = input("Выберите вариант алфавита (1 - по порядку, 2 - случайным образом): ")
    if alphabet_option == "1":
        alphabet = CYRILLIC_ALPHABET
    elif alphabet_option == "2":
        alph_list = list(CYRILLIC_ALPHABET)
        random.shuffle(alph_list)
        alphabet = "".join(alph_list)
        print("Сгенерированный алфавит:", alphabet)
    else:
        print("Ошибка: Неверный выбор алфавита!")
        return

    # Вывод квадрата Виженера
    print("\n----- Квадрат Виженера -----")
    print(vigenere_square(alphabet))

    original = read_file("Vinzher_test.txt")
    if original is None or len(original) < 2000:
        print("Ошибка: Файл Vinzher_test.txt не найден или содержит менее 2000 символов!")
        return

    # Шифрование и дешифрование
    encrypted = vigenere_encrypt(original, key, alphabet)
    decrypted = vigenere_decrypt(encrypted, key, alphabet)

    # Сохранение результатов
    write_file("en_Vishner.txt", encrypted)
    write_file("de_Vishner.txt", decrypted)

    # Вывод результатов
    print("\nИсходный текст (первые 5 строк):")
    print(get_first_lines(original))
    print("\nЗашифрованный текст (Виженер):")
    print(get_first_lines(encrypted))
    print("\nРасшифрованный текст (Виженер):")
    print(get_first_lines(decrypted))


def main():

    while True:
        print("\nВыберите метод шифрования:")
        print("1. Метод Цезаря (простой сдвиг букв)")
        print("2. Метод Виженера (с ключевым словом)")
        print("3. Выход")
        choice = input("Ваш выбор: ")

        if choice == "1":
            caesar_cli()
        elif choice == "2":
            vigenere_cli()
        elif choice == "3":
            break
        else:
            print("Ошибка: Неверный выбор!")


if __name__ == "__main__":
    main()

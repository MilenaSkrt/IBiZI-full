"""
Программа для криптоанализа зашифрованных текстов
Реализует анализ шифров Цезаря и Виженера с визуализацией результатов
"""

import os
import matplotlib.pyplot as plt
from collections import Counter
from itertools import zip_longest  # Для работы с последовательностями разной длины

# Русский алфавит с буквой Ё (33 буквы) в верхнем регистре
RUS_ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

# Версия алфавита в нижнем регистре (для корректной обработки регистра)
RUS_ALPHABET_LOWER = RUS_ALPHABET.lower()

# Эталонные частоты букв русского языка (по данным Национального корпуса русского языка)
# Словарь, где ключи - буквы, значения - их частоты в русских текстах
RUS_LETTER_FREQ = {
    'О': 0.1097,  # Буква О встречается примерно в 10.97% случаев
    'Е': 0.0845,
    'А': 0.0801,
    'И': 0.0735,
    'Н': 0.0670,
    'Т': 0.0626,
    'С': 0.0547,
    'Р': 0.0473,
    'В': 0.0454,
    'Л': 0.0440,
    'К': 0.0349,
    'М': 0.0321,
    'Д': 0.0298,
    'П': 0.0281,
    'У': 0.0262,
    'Я': 0.0201,
    'Ы': 0.0190,
    'Ь': 0.0174,
    'Г': 0.0170,
    'З': 0.0165,
    'Б': 0.0159,
    'Ч': 0.0144,
    'Й': 0.0121,
    'Х': 0.0097,
    'Ж': 0.0094,
    'Ш': 0.0073,
    'Ю': 0.0064,
    'Ц': 0.0048,
    'Щ': 0.0036,
    'Э': 0.0032,
    'Ф': 0.0026,
    'Ъ': 0.0004,
    'Ё': 0.0004
}

# Самые частые биграммы в русском языке, Отсортированы по убыванию частоты встречаемости
COMMON_BIGRAMS = [
    'СТ',
    'НО',
    'ЕН',
    'ТО',
    'НА',
    'ОВ',
    'НИ',
    'РА',
    'ВО',
    'КО'
]


def read_file(filename):

    if not os.path.exists(filename):
        print(f"Ошибка: Файл {filename} не найден!")
        return None

    try:

        with open(filename, "r", encoding="utf-8") as f:

            return f.read()
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return None


def write_file(filename, text):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        print(f"Ошибка при записи файла: {e}")


# ==================== ЧАСТОТНЫЙ АНАЛИЗ ====================

def calculate_letter_frequencies(text):
    """
    Подсчет частоты встречаемости русских букв в тексте

    """
    # Приводим текст к верхнему регистру для единообразия
    text = text.upper()

    # Подсчитываем общее количество русских букв в тексте
    # Используем генератор для фильтрации только русских букв
    total_letters = sum(1 for char in text if char in RUS_ALPHABET)

    # Создаем пустой словарь для хранения частот
    freq = {}

    # Перебираем все буквы русского алфавита
    for letter in RUS_ALPHABET:
        # Считаем количество вхождений текущей буквы в текст
        count = text.count(letter)

        # Вычисляем относительную частоту (доля от общего числа букв)
        if total_letters > 0:  # Проверка чтобы избежать деления на ноль
            # Округляем частоту до 4 знаков после запятой
            freq[letter] = round(count / total_letters, 4)
        else:
            # Если в тексте нет русских букв - устанавливаем частоту 0.0
            freq[letter] = 0.0

    # Возвращаем словарь с частотами
    return freq


def calculate_bigram_frequencies(text, step=1):
    """
    Подсчет частот биграмм (пар букв) в тексте

    """
    # Приводим текст к верхнему регистру
    text = text.upper()

    # Генерируем все возможные биграммы с заданным шагом
    # Используем list comprehension для создания списка биграмм
    bigrams = [text[i:i + 2] for i in range(0, len(text) - 1, step)]

    # Фильтруем биграммы, оставляя только те, что состоят из русских букв
    bigrams = [
        bg for bg in bigrams
        if len(bg) == 2 and all(c in RUS_ALPHABET for c in bg)
    ]

    # Подсчитываем общее количество валидных биграмм
    total_bigrams = len(bigrams)

    # Если биграмм нет - возвращаем пустой список
    if total_bigrams == 0:
        return []

    # Используем Counter для подсчета частот биграмм
    freq = Counter(bigrams)

    # Нормализуем частоты (делим на общее количество) и сортируем по убыванию
    # Возвращаем топ-10 самых частых биграмм
    return [
        (bg, round(cnt / total_bigrams, 4))
        for bg, cnt in freq.most_common(10)
    ]


def plot_frequencies(freq_dict, title):
    """
    Визуализация частотного распределения в виде столбчатой диаграммы

    """
    # Получаем ключи (символы/биграммы) и значения (частоты) из словаря
    labels = list(freq_dict.keys())
    values = list(freq_dict.values())

    plt.figure(figsize=(12, 6))
    bars = plt.bar(labels, values)

    plt.title(title)
    plt.xlabel("Символы")
    plt.ylabel("Частота")


    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.,
            height,
            f'{height:.4f}',
            ha='center',
            va='bottom'
        )

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.show()


# ==================== КРИПТОАНАЛИЗ ШИФРА ЦЕЗАРЯ ====================

def caesar_decrypt(text, key):
    """
    Дешифровка текста, зашифрованного шифром Цезаря

    Параметры:
        text (str): Зашифрованный текст
        key (int): Ключ шифра (сдвиг)

    Возвращает:
        str: Расшифрованный текст
    """
    decrypted = []  # Список для хранения расшифрованных символов

    # Перебираем каждый символ в тексте
    for ch in text:
        # Проверяем, является ли символ русской буквой
        if ch.upper() in RUS_ALPHABET:
            # Вычисляем новый индекс для символа
            idx = (RUS_ALPHABET.index(ch.upper()) - key) % 33

            # Добавляем букву в нужном регистре
            if ch.isupper():
                decrypted.append(RUS_ALPHABET[idx])
            else:
                decrypted.append(RUS_ALPHABET_LOWER[idx])
        else:
            # Не-буквенные символы добавляем без изменений
            decrypted.append(ch)

    # Собираем список символов в строку и возвращаем
    return ''.join(decrypted)


def caesar_cryptanalysis(ciphertext):
    """
    Автоматический криптоанализ шифра Цезаря методом частотного анализа

    Параметры:
        ciphertext (str): Зашифрованный текст

    Возвращает:
        tuple: (найденный ключ, расшифрованный текст)
    """
    # Вычисляем частоты букв в зашифрованном тексте
    freq = calculate_letter_frequencies(ciphertext)

    # Находим букву с максимальной частотой
    most_common = max(freq.items(), key=lambda x: x[1])[0]

    # Вычисляем ключ как разность между позицией самой частой буквы в шифротексте
    # и позицией буквы 'О' (самой частой в русском языке)
    key = (RUS_ALPHABET.index(most_common) - RUS_ALPHABET.index('О')) % 33

    # Дешифруем текст с найденным ключом
    decrypted_text = caesar_decrypt(ciphertext, key)

    # Возвращаем ключ и расшифрованный текст
    return key, decrypted_text


# ==================== КРИПТОАНАЛИЗ ШИФРА ВИЖЕНЕРА ====================

def find_repeated_sequences(text, min_len=3):
    """
    Поиск повторяющихся последовательностей в тексте для метода Казиски

    Параметры:
        text (str): Текст для анализа
        min_len (int): Минимальная длина последовательности (по умолчанию 3)

    Возвращает:
        dict: {последовательность: [позиции_вхождения]}
    """
    sequences = {}  # Словарь для хранения последовательностей

    # Проверяем последовательности длиной от min_len до 5 символов
    for length in range(min_len, 6):
        # Сканируем текст с шагом в 1 символ
        for i in range(len(text) - length + 1):
            # Вырезаем последовательность заданной длины
            seq = text[i:i + length]

            # Проверяем, что последовательность состоит только из русских букв
            if all(c in RUS_ALPHABET for c in seq.upper()):
                # Добавляем последовательность в словарь
                if seq in sequences:
                    sequences[seq].append(i)  # Добавляем позицию если последовательность уже встречалась
                else:
                    sequences[seq] = [i]  # Создаем новую запись

    # Возвращаем только последовательности, встречающиеся более 1 раза
    return {seq: pos for seq, pos in sequences.items() if len(pos) > 1}


def estimate_key_length(ciphertext):
    """
    Оценка длины ключа шифра Виженера методом Казиски

    Параметры:
        ciphertext (str): Зашифрованный текст

    Возвращает:
        int: Предполагаемая длина ключа или None если не удалось определить
    """

    # Вложенная функция для вычисления НОД (алгоритм Евклида)
    def gcd(a, b):
        """Вычисление наибольшего общего делителя"""
        while b:
            a, b = b, a % b
        return a

    # Находим повторяющиеся последовательности в тексте
    repeats = find_repeated_sequences(ciphertext)

    # Вычисляем расстояния между одинаковыми последовательностями
    distances = [y - x for seq in repeats.values() for x, y in zip(seq, seq[1:])]

    # Если не найдено повторений - возвращаем None
    if not distances:
        return None

    # Вычисляем НОД всех расстояний
    current_gcd = distances[0]
    for d in distances[1:]:
        current_gcd = gcd(current_gcd, d)
        # Если НОД стал 1 - дальше можно не проверять
        if current_gcd == 1:
            break

    # Возвращаем НОД если он больше 1, иначе None
    return current_gcd if current_gcd > 1 else None


def try_vigenere_decrypt(ciphertext, key_length):
    """
    Попытка дешифровки шифра Виженера с заданной длиной ключа

    Параметры:
        ciphertext (str): Зашифрованный текст
        key_length (int): Предполагаемая длина ключа

    Возвращает:
        tuple: (предполагаемый ключ, расшифрованный текст)
    """
    # Приводим текст к верхнему регистру для единообразия
    ciphertext_upper = ciphertext.upper()
    key = []  # Список для хранения символов ключа

    # Анализируем каждую группу символов, зашифрованных одним символом ключа
    for i in range(key_length):
        # Собираем подгруппу символов
        subgroup = [
            c for j, c in enumerate(ciphertext_upper)
            if j % key_length == i and c in RUS_ALPHABET
        ]
        subgroup_text = ''.join(subgroup)

        # Анализируем подгруппу как отдельный шифр Цезаря
        subgroup_freq = calculate_letter_frequencies(subgroup_text)

        # Находим самую частую букву в подгруппе
        most_common = max(subgroup_freq.items(), key=lambda x: x[1])[0]

        # Определяем символ ключа для этой подгруппы
        # Предполагаем, что самая частая буква соответствует 'О'
        key_char = RUS_ALPHABET[
            (RUS_ALPHABET.index(most_common) - RUS_ALPHABET.index('О')) % 33
            ]
        key.append(key_char)

    # Собираем символы ключа в строку
    key = ''.join(key)

    # Дешифруем текст с найденным ключом
    decrypted = []
    for i, ch in enumerate(ciphertext):
        if ch.upper() in RUS_ALPHABET:
            # Определяем сдвиг для текущей позиции
            shift = RUS_ALPHABET.index(key[i % key_length].upper())

            # Вычисляем индекс исходной буквы
            idx = (RUS_ALPHABET.index(ch.upper()) - shift) % 33

            # Добавляем букву в нужном регистре
            if ch.isupper():
                decrypted.append(RUS_ALPHABET[idx])
            else:
                decrypted.append(RUS_ALPHABET_LOWER[idx])
        else:
            # Не-буквенные символы оставляем без изменений
            decrypted.append(ch)

    # Возвращаем ключ и расшифрованный текст
    return key, ''.join(decrypted)


def is_likely_correct(text):
    """
    Проверка правдоподобности расшифрованного текста

    Параметры:
        text (str): Текст для проверки

    Возвращает:
        bool: True если текст похож на правильный русский текст
    """
    # Берем первые 200 символов для анализа
    sample = text[:200].upper()

    # Считаем количество самых частых русских букв в тексте
    common_rus_letters = sum(sample.count(c) for c in 'ОЕАИНТ')

    # Эмпирическая проверка: в нормальном тексте таких букв должно быть много
    return common_rus_letters > 50


def vigenere_cryptanalysis(ciphertext, max_key_length=10):
    """
    Полный криптоанализ шифра Виженера

    Параметры:
        ciphertext (str): Зашифрованный текст
        max_key_length (int): Максимальная длина ключа для перебора

    Возвращает:
        tuple: (найденный ключ, расшифрованный текст) или (None, ciphertext) при неудаче
    """
    # Этап 1: Определение длины ключа методом Казиски
    key_length = estimate_key_length(ciphertext)

    # Если метод Казиски не дал результата или ключ слишком длинный
    if key_length is None or key_length > max_key_length:
        print("Метод Казиски не сработал, пробуем перебор...")

        # Перебираем возможные длины ключа от 2 до max_key_length
        for possible_length in range(2, max_key_length + 1):
            print(f"Проверяем длину ключа: {possible_length}")

            # Пробуем дешифровать с текущей длиной ключа
            key, decrypted = try_vigenere_decrypt(ciphertext, possible_length)

            # Проверяем правдоподобность результата
            if is_likely_correct(decrypted):
                return key, decrypted

        # Если ничего не нашли - возвращаем исходный текст
        return None, ciphertext

    # Если длина ключа определена успешно
    print(f"Предполагаемая длина ключа: {key_length}")

    # Этап 2: Определение самого ключа и дешифровка
    return try_vigenere_decrypt(ciphertext, key_length)


def analyze_text_stats(text, title):

    print(f"\nАнализ текста: {title}")

    # Анализ частот букв
    letter_freq = calculate_letter_frequencies(text)
    print("\n10 самых частых букв:")
    for letter, freq in sorted(letter_freq.items(), key=lambda x: -x[1])[:10]:
        print(f"{letter}: {freq:.4f}")

    # Анализ биграмм
    bigrams = calculate_bigram_frequencies(text)
    print("\n10 самых частых биграмм:")
    for bg, freq in bigrams:
        print(f"{bg}: {freq:.4f}")

    # Визуализация частот букв
    plot_frequencies(
        dict(sorted(letter_freq.items(), key=lambda x: -x[1])[:10]),
        f"Частоты букв ({title})"
    )

    # Визуализация частот биграмм
    plot_frequencies(
        dict(bigrams),
        f"Частоты биграмм ({title})"
    )


def handle_caesar():
    """Обработчик для анализа шифра Цезаря"""
    # Запрашиваем имя файла у пользователя
    filename = input("Введите имя файла с зашифрованным текстом: ")

    # Читаем файл
    ciphertext = read_file(filename)
    if ciphertext is None:
        return  # Выходим если файл не прочитан

    # Предупреждаем если текст слишком короткий
    if len(ciphertext) < 2000:
        print("Рекомендуется текст от 2000 символов для точного анализа")

    print("\nАнализ...")
    # Выполняем криптоанализ
    key, decrypted = caesar_cryptanalysis(ciphertext)

    # Выводим результаты
    print(f"\nКлюч: {key}")
    print("\nПервые 200 символов расшифровки:")
    print(decrypted[:200])

    # Предлагаем сохранить результат
    if input("Сохранить результат? (y/n): ").lower() == 'y':
        write_file(f"decrypted_caesar_key{key}.txt", decrypted)
        print("Результат сохранен")


def handle_vigenere():
    """Обработчик для анализа шифра Виженера"""
    # Запрашиваем имя файла у пользователя
    filename = input("Введите имя файла с зашифрованным текстом: ")

    # Читаем файл
    ciphertext = read_file(filename)
    if ciphertext is None:
        return  # Выходим если файл не прочитан

    # Предупреждаем если текст слишком короткий
    if len(ciphertext) < 2000:
        print("Рекомендуется текст от 2000 символов для точного анализа")

    print("\nАнализ...")
    # Выполняем криптоанализ
    key, decrypted = vigenere_cryptanalysis(ciphertext)

    # Выводим результаты если ключ найден
    if key:
        print(f"\nКлюч: {key}")
        print("\nПервые 200 символов расшифровки:")
        print(decrypted[:200])

        # Предлагаем сохранить результат
        if input("Сохранить результат? (y/n): ").lower() == 'y':
            write_file(f"decrypted_vigenere_key{key}.txt", decrypted)
            print("Результат сохранен")
    else:
        print("Не удалось определить ключ")


def handle_frequency_analysis():
    """Обработчик для частотного анализа текста"""
    # Запрашиваем имя файла у пользователя
    filename = input("Введите имя файла для анализа: ")

    # Читаем файл
    text = read_file(filename)
    if text is None:
        return  # Выходим если файл не прочитан

    # Запрашиваем название для анализа
    title = input("Введите название для анализа: ")

    # Выполняем анализ
    analyze_text_stats(text, title)


def main_menu():
    """Главное меню программы"""
    print("Программа криптоанализа")

    while True:
        # Вывод меню
        print("\nМеню:")
        print("1. Анализ Цезаря")
        print("2. Анализ Виженера")
        print("3. Частотный анализ")
        print("4. Выход")


        choice = input("Выберите действие: ").strip()


        if choice == "1":
            handle_caesar()
        elif choice == "2":
            handle_vigenere()
        elif choice == "3":
            handle_frequency_analysis()
        elif choice == "4":
            print("Завершение работы")
            break  # Выход из цикла
        else:
            print("Некорректный ввод")



if __name__ == "__main__":

    main_menu()

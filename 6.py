"""
Программа для криптоанализа зашифрованных текстов (Цезарь и Виженер)
с использованием частотного анализа и анализа k-грамм
"""

import os
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
from itertools import zip_longest

# Русский алфавит с учетом буквы Ё
RUS_ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
RUS_ALPHABET_LOWER = RUS_ALPHABET.lower()

# Частотные характеристики русского языка (примерные)
RUS_LETTER_FREQ = {
    'О': 0.1097, 'Е': 0.0845, 'А': 0.0801, 'И': 0.0735, 'Н': 0.0670,
    'Т': 0.0626, 'С': 0.0547, 'Р': 0.0473, 'В': 0.0454, 'Л': 0.0440,
    'К': 0.0349, 'М': 0.0321, 'Д': 0.0298, 'П': 0.0281, 'У': 0.0262,
    'Я': 0.0201, 'Ы': 0.0190, 'Ь': 0.0174, 'Г': 0.0170, 'З': 0.0165,
    'Б': 0.0159, 'Ч': 0.0144, 'Й': 0.0121, 'Х': 0.0097, 'Ж': 0.0094,
    'Ш': 0.0073, 'Ю': 0.0064, 'Ц': 0.0048, 'Щ': 0.0036, 'Э': 0.0032,
    'Ф': 0.0026, 'Ъ': 0.0004, 'Ё': 0.0004
}

COMMON_BIGRAMS = ['СТ', 'НО', 'ЕН', 'ТО', 'НА', 'ОВ', 'НИ', 'РА', 'ВО', 'КО']


# ==================== Функции для работы с файлами ====================
def read_file(filename):
    """Чтение файла с проверкой его существования"""
    if not os.path.exists(filename):
        print(f"Ошибка: Файл {filename} не найден!")
        return None
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def write_file(filename, text):
    """Запись текста в файл"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


# ==================== Частотный анализ ====================
def calculate_letter_frequencies(text):
    """Подсчет частот букв в тексте"""
    text = text.upper()
    total_letters = sum(1 for char in text if char in RUS_ALPHABET)
    freq = {}

    for letter in RUS_ALPHABET:
        count = text.count(letter)
        if total_letters > 0:
            freq[letter] = count / total_letters
        else:
            freq[letter] = 0.0

    return freq


def calculate_bigram_frequencies(text, step=1):
    """Подсчет частот биграмм в тексте"""
    text = text.upper()
    bigrams = [text[i:i + 2] for i in range(0, len(text) - 1, step)]
    bigrams = [bg for bg in bigrams if len(bg) == 2 and all(c in RUS_ALPHABET for c in bg)]
    total_bigrams = len(bigrams)

    if total_bigrams == 0:
        return {}

    freq = Counter(bigrams)
    for bg in freq:
        freq[bg] /= total_bigrams

    return freq.most_common(10)


def plot_frequencies(freq_dict, title):
    """Построение гистограммы частот"""
    labels = list(freq_dict.keys())
    values = list(freq_dict.values())

    plt.figure(figsize=(12, 6))
    plt.bar(labels, values)
    plt.title(title)
    plt.xlabel("Символы")
    plt.ylabel("Частота")
    plt.show()


# ==================== Криптоанализ Цезаря ====================
def caesar_cryptanalysis(ciphertext):
    """Криптоанализ шифра Цезаря с использованием частотного анализа"""
    cipher_freq = calculate_letter_frequencies(ciphertext)

    # Находим наиболее частую букву в зашифрованном тексте
    most_common_cipher = max(cipher_freq.items(), key=lambda x: x[1])[0]

    # Предполагаем, что она соответствует самой частой букве в русском языке (О)
    most_common_rus = 'О'

    # Вычисляем ключ
    key = (RUS_ALPHABET.index(most_common_cipher) - RUS_ALPHABET.index(most_common_rus)) % len(RUS_ALPHABET)

    # Дешифруем текст
    decrypted = []
    for ch in ciphertext:
        if ch.upper() in RUS_ALPHABET:
            if ch.isupper():
                index = (RUS_ALPHABET.index(ch) - key) % len(RUS_ALPHABET)
                decrypted.append(RUS_ALPHABET[index])
            else:
                index = (RUS_ALPHABET_LOWER.index(ch) - key) % len(RUS_ALPHABET_LOWER)
                decrypted.append(RUS_ALPHABET_LOWER[index])
        else:
            decrypted.append(ch)

    return key, ''.join(decrypted)


# ==================== Криптоанализ Виженера ====================
def find_repeated_sequences(text, min_len=3):
    """Поиск повторяющихся последовательностей в тексте"""
    sequences = {}
    for length in range(min_len, 6):
        for i in range(len(text) - length + 1):
            seq = text[i:i + length]
            if all(c in RUS_ALPHABET for c in seq.upper()):
                if seq in sequences:
                    sequences[seq].append(i)
                else:
                    sequences[seq] = [i]

    # Оставляем только последовательности, встречающиеся несколько раз
    return {seq: pos for seq, pos in sequences.items() if len(pos) > 1}


def estimate_key_length(ciphertext):
    """Оценка длины ключа методом Казиски"""
    repeated_sequences = find_repeated_sequences(ciphertext)
    distances = []

    for seq, positions in repeated_sequences.items():
        for i in range(len(positions) - 1):
            distances.append(positions[i + 1] - positions[i])

    if not distances:
        return None

    # Находим НОД всех расстояний
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    current_gcd = distances[0]
    for d in distances[1:]:
        current_gcd = gcd(current_gcd, d)
        if current_gcd == 1:
            break

    return current_gcd if current_gcd > 1 else None


def vigenere_cryptanalysis(ciphertext, max_key_length=10):
    """Криптоанализ шифра Виженера"""
    # Шаг 1: Определяем длину ключа
    key_length = estimate_key_length(ciphertext)
    if key_length is None or key_length > max_key_length:
        print("Не удалось определить длину ключа, пробуем методом перебора...")
        for possible_length in range(2, max_key_length + 1):
            print(f"Пробуем длину ключа: {possible_length}")
            key, decrypted = try_vigenere_decrypt(ciphertext, possible_length)
            if is_likely_correct(decrypted):
                return key, decrypted
        return None, ciphertext

    print(f"Предполагаемая длина ключа: {key_length}")

    # Шаг 2: Определяем ключ по частотному анализу
    return try_vigenere_decrypt(ciphertext, key_length)


def try_vigenere_decrypt(ciphertext, key_length):
    """Попытка дешифрования с заданной длиной ключа"""
    ciphertext_upper = ciphertext.upper()
    key = []

    for i in range(key_length):
        # Создаем подстроку символов, зашифрованных с одним символом ключа
        subgroup = [c for j, c in enumerate(ciphertext_upper)
                    if j % key_length == i and c in RUS_ALPHABET]
        subgroup_text = ''.join(subgroup)

        # Анализируем подгруппу как шифр Цезаря
        subgroup_freq = calculate_letter_frequencies(subgroup_text)
        most_common = max(subgroup_freq.items(), key=lambda x: x[1])[0]

        # Предполагаем, что самая частая буква соответствует 'О'
        key_char = RUS_ALPHABET[(RUS_ALPHABET.index(most_common) - RUS_ALPHABET.index('О')) % len(RUS_ALPHABET)]
        key.append(key_char)

    key = ''.join(key)
    print(f"Предполагаемый ключ: {key}")

    # Дешифруем текст
    decrypted = []
    for i, ch in enumerate(ciphertext):
        if ch.upper() in RUS_ALPHABET:
            key_char = key[i % key_length]
            shift = RUS_ALPHABET.index(key_char.upper())
            if ch.isupper():
                index = (RUS_ALPHABET.index(ch) - shift) % len(RUS_ALPHABET)
                decrypted.append(RUS_ALPHABET[index])
            else:
                index = (RUS_ALPHABET_LOWER.index(ch) - shift) % len(RUS_ALPHABET_LOWER)
                decrypted.append(RUS_ALPHABET_LOWER[index])
        else:
            decrypted.append(ch)

    return key, ''.join(decrypted)


def is_likely_correct(text):
    """Проверка, выглядит ли текст как правильно расшифрованный"""
    sample = text[:200].upper()
    common_rus_letters = sum(sample.count(c) for c in 'ОЕАИНТ')
    return common_rus_letters > 50  # Эмпирическая проверка


# ==================== Вспомогательные функции ====================
def analyze_text_stats(text, title):
    """Анализ и отображение статистики текста"""
    print(f"\nАнализ текста: {title}")

    # Частоты букв
    letter_freq = calculate_letter_frequencies(text)
    print("\n10 самых частых букв:")
    for letter, freq in sorted(letter_freq.items(), key=lambda x: -x[1])[:10]:
        print(f"{letter}: {freq:.4f}")

    # Биграммы
    bigrams = calculate_bigram_frequencies(text)
    print("\n10 самых частых биграмм:")
    for bg, freq in bigrams:
        print(f"{bg}: {freq:.4f}")

    # Построение графиков
    plot_frequencies(dict(sorted(letter_freq.items(), key=lambda x: -x[1])[:10]),
                     f"Частоты букв ({title})")

    plot_frequencies(dict(bigrams),
                     f"Частоты биграмм ({title})")


# ==================== Основной интерфейс ====================
def main_menu():
    """Главное меню программы"""
    print("Программа криптоанализа зашифрованных текстов")

    while True:
        print("\nВыберите режим работы:")
        print("1. Криптоанализ шифра Цезаря")
        print("2. Криптоанализ шифра Виженера")
        print("3. Анализ частотных характеристик текста")
        print("4. Выход")

        choice = input("Ваш выбор: ")

        if choice == "1":
            caesar_menu()
        elif choice == "2":
            vigenere_menu()
        elif choice == "3":
            analyze_menu()
        elif choice == "4":
            break
        else:
            print("Неверный выбор, попробуйте снова.")


def caesar_menu():
    """Меню криптоанализа Цезаря"""
    filename = input("Введите имя файла с зашифрованным текстом: ")
    ciphertext = read_file(filename)

    if ciphertext is None:
        return

    if len(ciphertext) < 2000:
        print("Предупреждение: для надежного анализа рекомендуется использовать текст длиной не менее 2000 символов.")

    print("\nАнализ шифротекста...")
    key, decrypted = caesar_cryptanalysis(ciphertext)

    print(f"\nПредполагаемый ключ: {key}")
    print("\nПервые 200 символов расшифрованного текста:")
    print(decrypted[:200])

    save = input("\nСохранить результат в файл? (y/n): ")
    if save.lower() == 'y':
        write_file(f"decrypted_caesar_key{key}.txt", decrypted)
        print("Результат сохранен.")


def vigenere_menu():
    """Меню криптоанализа Виженера"""
    filename = input("Введите имя файла с зашифрованным текстом: ")
    ciphertext = read_file(filename)

    if ciphertext is None:
        return

    if len(ciphertext) < 2000:
        print("Предупреждение: для надежного анализа рекомендуется использовать текст длиной не менее 2000 символов.")

    print("\nАнализ шифротекста...")
    key, decrypted = vigenere_cryptanalysis(ciphertext)

    if key:
        print(f"\nПредполагаемый ключ: {key}")
        print("\nПервые 200 символов расшифрованного текста:")
        print(decrypted[:200])

        save = input("\nСохранить результат в файл? (y/n): ")
        if save.lower() == 'y':
            write_file(f"decrypted_vigenere_key{key}.txt", decrypted)
            print("Результат сохранен.")
    else:
        print("Не удалось определить ключ. Попробуйте увеличить длину текста.")


def analyze_menu():
    """Меню анализа частотных характеристик"""
    filename = input("Введите имя файла с текстом для анализа: ")
    text = read_file(filename)

    if text is None:
        return

    title = input("Введите название для анализа (например 'Исходный текст'): ")
    analyze_text_stats(text, title)


if __name__ == "__main__":
    main_menu()

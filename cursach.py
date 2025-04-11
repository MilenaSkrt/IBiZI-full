"""
Курсовая работа по криптоанализу шифра Эль-Гамаля
Автор: [Ваше имя]
Группа: [Ваша группа]
Дата: [Текущая дата]
"""

import random
import math
import time
import matplotlib.pyplot as plt
from sympy import isprime, primerange, gcd, mod_inverse

# =============================================
# 1. Реализация шифра Эль-Гамаля
# =============================================

def generate_keys(p=None, g=None, bit_length=8):
    """
    Генерация ключей для схемы Эль-Гамаля
    
    Параметры:
        p - простое число (если None, генерируется автоматически)
        g - генератор группы (если None, подбирается автоматически)
        bit_length - длина простого числа в битах (по умолчанию 8)
    
    Возвращает:
        (p, g, h) - публичные параметры
        x - секретный ключ
    """
    
    # Генерация простого числа p, если не задано
    if p is None:
        # Диапазон простых чисел для выбранной битовой длины
        lower_bound = 2**(bit_length-1)
        upper_bound = 2**bit_length
        primes = list(primerange(lower_bound, upper_bound))
        p = random.choice(primes)
    
    # Проверка, что p - простое число
    if not isprime(p):
        raise ValueError("p должно быть простым числом")
    
    # Поиск генератора g мультипликативной группы Zp*, если не задан
    if g is None:
        # Факторизация p-1 для нахождения всех простых делителей
        factors = prime_factors(p-1)
        
        # Проверка кандидатов в генераторы
        for g_candidate in range(2, p):
            is_generator = True
            for factor in factors:
                if pow(g_candidate, (p-1)//factor, p) == 1:
                    is_generator = False
                    break
            if is_generator:
                g = g_candidate
                break
    
    # Генерация секретного ключа
    x = random.randint(1, p-2)
    
    # Вычисление публичного ключа
    h = pow(g, x, p)
    
    return (p, g, h), x

def encrypt(p, g, h, m):
    """
    Шифрование сообщения m
    
    Параметры:
        p, g, h - публичные параметры
        m - сообщение (число)
    
    Возвращает:
        (c1, c2) - шифротекст
    """
    # Проверка, что сообщение принадлежит группе
    if m <= 0 or m >= p:
        raise ValueError(f"Сообщение m должно быть в диапазоне (0, {p})")
    
    # Выбор случайного сессионного ключа
    k = random.randint(1, p-2)
    
    # Вычисление компонентов шифротекста
    c1 = pow(g, k, p)
    c2 = (m * pow(h, k, p)) % p
    
    return (c1, c2)

def decrypt(p, x, c1, c2):
    """
    Расшифрование сообщения
    
    Параметры:
        p - простое число
        x - секретный ключ
        c1, c2 - компоненты шифротекста
    
    Возвращает:
        m - расшифрованное сообщение
    """
    # Вычисление общего секрета
    s = pow(c1, x, p)
    
    # Нахождение обратного элемента для s
    s_inv = mod_inverse(s, p)
    if s_inv is None:
        raise ValueError("Ошибка при вычислении обратного элемента")
    
    # Расшифрование сообщения
    m = (c2 * s_inv) % p
    
    return m

# =============================================
# 2. Вспомогательные функции
# =============================================

def prime_factors(n):
    """
    Разложение числа на простые множители
    
    Параметры:
        n - число для факторизации
    
    Возвращает:
        Множество простых делителей
    """
    factors = set()
    # Обработка делителей 2
    while n % 2 == 0:
        factors.add(2)
        n = n // 2
    # Обработка нечетных делителей
    i = 3
    max_factor = math.sqrt(n) + 1
    while i <= max_factor:
        while n % i == 0:
            factors.add(i)
            n = n // i
            max_factor = math.sqrt(n) + 1
        i += 2
    if n > 1:
        factors.add(n)
    return factors

# =============================================
# 3. Методы криптоанализа (решения DLP)
# =============================================

def brute_force(g, h, p):
    """
    Полный перебор для решения задачи дискретного логарифма
    g^x ≡ h mod p
    
    Параметры:
        g, h, p - параметры уравнения
    
    Возвращает:
        x - решение или None, если решение не найдено
    """
    for x in range(p):
        if pow(g, x, p) == h:
            return x
    return None

def baby_step_giant_step(g, h, p):
    """
    Алгоритм Baby-step Giant-step для решения DLP
    
    Параметры:
        g, h, p - параметры уравнения
    
    Возвращает:
        x - решение или None, если решение не найдено
    """
    n = int(math.isqrt(p)) + 1
    
    # Baby-step: построение таблицы {g^j mod p: j}
    table = {}
    curr = 1
    for j in range(n):
        table[curr] = j
        curr = (curr * g) % p
    
    # Giant-step: вычисление g^(-n) mod p
    gn = pow(g, n * (p-2), p)  # По малой теореме Ферма
    
    # Поиск совпадений
    curr = h
    for i in range(n):
        if curr in table:
            return i * n + table[curr]
        curr = (curr * gn) % p
    
    return None

def pollards_rho(g, h, p):
    """
    Алгоритм Полларда (ро) для решения DLP
    
    Параметры:
        g, h, p - параметры уравнения
    
    Возвращает:
        x - решение или None, если решение не найдено
    """
    # Функция итерации
    def next_step(x, a, b):
        if x % 3 == 0:
            return (h * x) % p, a, (b + 1) % (p-1)
        elif x % 3 == 1:
            return (x * x) % p, (2 * a) % (p-1), (2 * b) % (p-1)
        else:
            return (g * x) % p, (a + 1) % (p-1), b
    
    # Инициализация
    x, a, b = 1, 0, 0
    X, A, B = x, a, b
    
    for _ in range(p):
        # Один шаг для медленной последовательности
        x, a, b = next_step(x, a, b)
        
        # Два шага для быстрой последовательности
        X, A, B = next_step(*next_step(X, A, B))
        
        # Проверка на коллизию
        if x == X:
            # Решение уравнения a + x*b ≡ A + x*B mod (p-1)
            denominator = (B - b) % (p-1)
            if denominator == 0:
                return None
            if gcd(denominator, p-1) != 1:
                return None
            x_sol = ((a - A) * mod_inverse(denominator, p-1)) % (p-1)
            return x_sol
    
    return None

# =============================================
# 4. Сравнение производительности методов
# =============================================

def benchmark_methods(max_bits=12):
    """
    Сравнение времени работы методов криптоанализа
    
    Параметры:
        max_bits - максимальная битовая длина для теста
    
    Возвращает:
        Список времен выполнения для каждого метода
    """
    bit_lengths = range(8, max_bits+1, 2)
    results = {'Brute-force': [], 'Baby-step Giant-step': [], 'Pollard\'s Rho': []}
    
    for bits in bit_lengths:
        # Генерация ключей
        (p, g, h), x = generate_keys(bit_length=bits)
        print(f"\nТестирование для p = {p} (битовая длина: {bits})")
        
        # Тестирование Brute-force
        if bits <= 16:  # Для больших длин слишком долго
            start = time.time()
            x_bf = brute_force(g, h, p)
            t_bf = time.time() - start
            results['Brute-force'].append(t_bf)
            print(f"Brute-force: {t_bf:.4f} сек, x = {x_bf}")
        else:
            results['Brute-force'].append(float('nan'))
        
        # Тестирование Baby-step Giant-step
        start = time.time()
        x_bsgs = baby_step_giant_step(g, h, p)
        t_bsgs = time.time() - start
        results['Baby-step Giant-step'].append(t_bsgs)
        print(f"Baby-step Giant-step: {t_bsgs:.4f} сек, x = {x_bsgs}")
        
        # Тестирование Pollard's Rho
        start = time.time()
        x_rho = pollards_rho(g, h, p)
        t_rho = time.time() - start
        results['Pollard\'s Rho'].append(t_rho)
        print(f"Pollard's Rho: {t_rho:.4f} сек, x = {x_rho}")
    
    # Построение графика
    plt.figure(figsize=(10, 6))
    for method in results:
        if method == 'Brute-force':
            # Пропускаем отсутствующие значения для больших длин
            valid_idx = [i for i, t in enumerate(results[method]) if not math.isnan(t)]
            plt.plot([bit_lengths[i] for i in valid_idx], 
                    [results[method][i] for i in valid_idx], 
                    label=method, marker='o')
        else:
            plt.plot(bit_lengths, results[method], label=method, marker='o')
    
    plt.xlabel('Битовая длина p')
    plt.ylabel('Время выполнения (сек)')
    plt.title('Сравнение методов решения DLP')
    plt.legend()
    plt.grid(True)
    plt.savefig('benchmark_results.png')
    plt.show()
    
    return results

# =============================================
# 5. Пример использования
# =============================================

def demo():
    """Демонстрация работы всех компонентов"""
    
    print("="*50)
    print("Демонстрация работы шифра Эль-Гамаля")
    print("="*50)
    
    # 1. Генерация ключей
    print("\n1. Генерация ключей:")
    public, private = generate_keys(bit_length=10)
    p, g, h = public
    x = private
    print(f"Публичные параметры: p = {p}, g = {g}, h = {h}")
    print(f"Секретный ключ: x = {x}")
    
    # 2. Шифрование сообщения
    print("\n2. Шифрование сообщения:")
    message = 42
    print(f"Исходное сообщение: m = {message}")
    c1, c2 = encrypt(p, g, h, message)
    print(f"Шифротекст: (c1 = {c1}, c2 = {c2})")
    
    # 3. Расшифрование сообщения
    print("\n3. Расшифрование сообщения:")
    decrypted = decrypt(p, x, c1, c2)
    print(f"Расшифрованное сообщение: m' = {decrypted}")
    print(f"Совпадение с исходным: {message == decrypted}")
    
    # 4. Криптоанализ
    print("\n4. Криптоанализ (взлом секретного ключа):")
    
    # Brute-force
    print("\nМетод полного перебора (Brute-force):")
    start = time.time()
    x_bf = brute_force(g, h, p)
    t_bf = time.time() - start
    print(f"Найденный ключ: x = {x_bf}")
    print(f"Время выполнения: {t_bf:.6f} сек")
    print(f"Совпадение с настоящим ключом: {x == x_bf}")
    
    # Baby-step Giant-step
    print("\nМетод Baby-step Giant-step:")
    start = time.time()
    x_bsgs = baby_step_giant_step(g, h, p)
    t_bsgs = time.time() - start
    print(f"Найденный ключ: x = {x_bsgs}")
    print(f"Время выполнения: {t_bsgs:.6f} сек")
    print(f"Совпадение с настоящим ключом: {x == x_bsgs}")
    
    # Pollard's Rho
    print("\nМетод Полларда (ро):")
    start = time.time()
    x_rho = pollards_rho(g, h, p)
    t_rho = time.time() - start
    print(f"Найденный ключ: x = {x_rho}")
    print(f"Время выполнения: {t_rho:.6f} сек")
    print(f"Совпадение с настоящим ключом: {x == x_rho}")
    
    # 5. Сравнение производительности
    print("\n5. Запуск теста производительности...")
    benchmark_methods(max_bits=14)

if __name__ == "__main__":
    demo()

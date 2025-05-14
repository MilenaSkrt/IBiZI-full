import random
from time import perf_counter
from sympy import isprime, primitive_root
import matplotlib.pyplot as plt
import os

# --- Быстрая генерация ключей ---
def generate_keys(bits=256):
    attempts = 0
    while True:
        attempts += 1
        candidate = random.getrandbits(bits) | 1  # нечётное число
        if isprime(candidate):
            try:
                g = primitive_root(candidate)
                p = candidate
                break
            except ValueError:
                continue
    x = random.randint(2, p - 2)
    y = pow(g, x, p)
    return (p, g, y), x, attempts

# --- Шифрование ---
def encrypt(message, public_key):
    p, g, y = public_key
    k = random.randint(2, p - 2)
    a = pow(g, k, p)
    s = pow(y, k, p)
    return [(a, (ord(char) * s) % p) for char in message]

# --- Расшифровка ---
def decrypt(cipher, private_key, p):
    result = ''
    for a, b in cipher:
        s = pow(a, private_key, p)
        s_inv = pow(s, -1, p)
        result += chr((b * s_inv) % p)
    return result

# --- Эксперимент ---
def run_experiment(bits_list, plaintext, repeats=3):
    encrypt_times = []
    decrypt_times = []
    keygen_times = []
    avg_attempts_list = []

    os.makedirs("results", exist_ok=True)

    for bits in bits_list:
        print(f"\n=== Тест для {bits} бит ===")
        key_time_sum = 0
        enc_time_sum = 0
        dec_time_sum = 0
        all_attempts = []

        for i in range(repeats):
            print(f"  Повтор {i + 1}/{repeats}...")

            start_key = perf_counter()
            public_key, private_key, attempts = generate_keys(bits)
            key_time = perf_counter() - start_key
            key_time_sum += key_time
            all_attempts.append(attempts)
            print(f"    Генерация ключей: {key_time:.4f} сек (попыток: {attempts})")

            start_encrypt = perf_counter()
            cipher = encrypt(plaintext, public_key)
            encrypt_time = perf_counter() - start_encrypt
            enc_time_sum += encrypt_time
            print(f"    Шифрование: {encrypt_time:.4f} сек")

            start_decrypt = perf_counter()
            decrypted = decrypt(cipher, private_key, public_key[0])
            decrypt_time = perf_counter() - start_decrypt
            dec_time_sum += decrypt_time
            print(f"    Расшифровка: {decrypt_time:.4f} сек")

            # Проверка совпадения
            if decrypted == plaintext:
                print("Расшифрованный текст совпадает с оригиналом.")
            else:
                print("Расшифрованный текст НЕ совпадает с оригиналом.")

            # Сохраняем всё при первом повторе
            if i == 0:
                with open(f"results/keys_{bits}.txt", "w", encoding='utf-8') as f:
                    f.write(f"Public key (p, g, y):\n{public_key}\n")
                    f.write(f"Private key (x):\n{private_key}\n")
                    f.write(f"Attempts to generate key: {attempts}\n")

                with open(f"results/cipher_{bits}.txt", "w", encoding='utf-8') as f:
                    f.write(str(cipher))

                with open(f"results/decrypted_{bits}.txt", "w", encoding='utf-8') as f:
                    f.write(decrypted)

        avg_key = key_time_sum / repeats
        avg_enc = enc_time_sum / repeats
        avg_dec = dec_time_sum / repeats
        avg_attempts = sum(all_attempts) / repeats

        keygen_times.append(avg_key)
        encrypt_times.append(avg_enc)
        decrypt_times.append(avg_dec)
        avg_attempts_list.append(avg_attempts)

    return bits_list, keygen_times, encrypt_times, decrypt_times, avg_attempts_list

# --- Основной запуск ---
if __name__ == '__main__':
    try:
        with open('original.txt', 'r', encoding='utf-8') as f:
            plaintext = f.read()
    except FileNotFoundError:
        print("Файл original.txt не найден. Использую тестовую строку.")
        plaintext = "Тестовое сообщение для проверки алгоритма." * 3

    plaintext = plaintext[:100]

    bits_list = [64, 128, 192, 256]
    bits, key_times, enc_times, dec_times, avg_attempts = run_experiment(bits_list, plaintext, repeats=3)

    # --- График времени ---
    plt.figure(figsize=(10, 6))
    plt.plot(bits, key_times, marker='o', label="Генерация ключей")
    plt.plot(bits, enc_times, marker='s', label="Шифрование")
    plt.plot(bits, dec_times, marker='^', label="Расшифровка")
    plt.xlabel("Длина ключа (бит)")
    plt.ylabel("Время (секунды)")
    plt.title("Среднее время операций ElGamal (3 повтора)")
    plt.yscale('log')
    plt.xticks(bits, [str(b) for b in bits])
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.savefig("results/timings_plot.png")
    plt.show()

    # --- График попыток ---
    plt.figure(figsize=(8, 5))
    plt.plot(bits, avg_attempts, marker='d', color='orange')
    plt.xlabel("Длина ключа (бит)")
    plt.ylabel("Среднее число попыток")
    plt.title("Попытки генерации ключей ElGamal (3 повтора)")
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.xticks(bits, [str(b) for b in bits])
    plt.tight_layout()
    plt.savefig("results/attempts_plot.png")
    plt.show()

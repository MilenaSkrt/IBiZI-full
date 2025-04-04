import string


def get_alphabet_power(password): #мощность алфавита
    power = 0
    if any(c.islower() for c in password):
        power += 26
    if any(c.isupper() for c in password):
        power += 26
    if any(c.isdigit() for c in password):
        power += 10
    if any(c in string.punctuation for c in password):
        power += len(string.punctuation)
    return power


def calculate_combinations(alphabet_power, length): #кол-во возможных комбинаций
    return alphabet_power ** length #мощность умножить на длину


# def calculate_brute_force_time(combinations, speed, attempts, pause):
#     total_attempts = combinations #общее число попыток
#     full_attempt_batches = total_attempts // attempts #полных серий перебора(перед паузой)
#     total_pause_time = full_attempt_batches * pause #общее время пауз
#     total_seconds = (total_attempts / speed) + total_pause_time #общее время перебора
#     minutes, seconds = divmod(total_seconds, 60)
#     hours, minutes = divmod(minutes, 60)
#     days, hours = divmod(hours, 24)
#     years, days = divmod(days, 365)
#     return int(years), int(days), int(hours), int(minutes), int(seconds)

def calculate_brute_force_time(combinations, speed, attempts, pause):
    total_attempts = combinations
    full_attempt_batches = total_attempts // attempts  # Количество полных серий
    remaining_attempts = total_attempts % attempts  # Оставшиеся попытки после последней полной серии

    # общее время пауз  не учитываем паузу, если после последней серии нет оставшихся попыток
    total_pause_time = (full_attempt_batches - (1 if remaining_attempts == 0 else 0)) * pause

    total_seconds = (total_attempts / speed) + total_pause_time

    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    years, days = divmod(days, 365)

    return int(years), int(days), int(hours), int(minutes), int(seconds)

def analyze_password(password, speed, attempts, pause): #анализ пароля, принимает пароль, мощность и вычисляет время перебора
    if not password:
        return None

    alphabet_power = get_alphabet_power(password)
    combinations = calculate_combinations(alphabet_power, len(password))
    brute_force_time = calculate_brute_force_time(combinations, speed, attempts, pause)

    return {
        "password": password,
        "alphabet_power": alphabet_power,
        "combinations": combinations,
        "brute_force_time": brute_force_time
    }


def print_analysis(result):
    if not result:
        print("Ошибка: пустой пароль")
        return

    print(f"Анализ пароля: {result['password']}")
    print(f"Мощность алфавита: {result['alphabet_power']}")
    print(f"Количество возможных комбинаций: {result['combinations']:.2e}")
    years, days, hours, minutes, seconds = result['brute_force_time']
    print(f"Время перебора: {years} лет {days} дней "
          f"{hours} часов {minutes} минут {seconds} секунд")


if __name__ == "__main__":
    password = input("Введите пароль для анализа: ")
    speed = int(input("Введите скорость перебора паролей в секунду: "))
    attempts = int(input("Введите количество неправильных попыток перед паузой: "))
    pause = int(input("Введите длительность паузы (в секундах): "))
    result = analyze_password(password, speed, attempts, pause)
    print_analysis(result)

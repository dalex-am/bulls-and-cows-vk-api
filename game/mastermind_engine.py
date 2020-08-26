import random

_the_number = ''
_result = {'bulls': 0, 'cows': 0}


def start_game():
    global _the_number
    while True:
        _the_number = str(random.randrange(1023, 9876, 1))
        if len(set(_the_number)) == len(_the_number):
            break
    return 'Число сгенерировано. Начинаем! (Всегда можно написать "Сдаюсь" или "Выход")'


def number_from_user_is_ok(user_number):
    if not user_number:
        return False
    user_number = user_number.strip()
    if user_number[0] == '0' or len(user_number) != 4:
        return False
    if user_number.isdigit():
        user_number = set(user_number)
        if len(user_number) == 4:
            return True
    return False


def check_for_bulls_and_cows(user_number):
    global _result
    _result = {'bulls': 0, 'cows': 0}
    user_number = user_number.strip()
    for index, char in enumerate(user_number):
        if char == _the_number[index]:
            _result['bulls'] += 1
        elif char in _the_number:
            _result['cows'] += 1
    return _result


def is_end_game():
    return _result['bulls'] == 4


def user_want_exit():
    return _the_number

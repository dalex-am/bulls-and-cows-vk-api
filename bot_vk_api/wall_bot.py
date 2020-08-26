# -*- coding: utf-8 -*-
from random import randint

import requests
from bot_vk_api._secret import token, group_id
from game.mastermind_engine import start_game, number_from_user_is_ok, check_for_bulls_and_cows, is_end_game, \
    user_want_exit

list_for_end = ['Сдаюсь', 'сдаюсь', 'Хватит', 'хватит', 'Все', 'все', 'Всё', 'всё', 'Выход', 'выход',
                'Exit', 'exit', 'Я так больше не могу', 'ААААААА', 'Узнать число', 'узнать число']
POST_ID = 17530
SESSION_TOTAL_COMMENTS_COUNT = 1
NUMBERS_OF_ERRORS = 0


class Player:
    game_started = False
    counter = 1

    def __init__(self, name):
        self.name = name

    def game_step(self, text, comment_id):

        if not self.game_started and (text == 'Старт' or text == 'старт'):  # Начинаем игру
            self.r_answer(start_game(), comment_id=comment_id)
            self.counter = 1
            self.game_started = True

        elif not self.game_started:  # Просим начать игру
            self.r_answer(f'{self.name}, для начала игры введите "Старт"', comment_id=comment_id)
        else:  # Играем
            input_number = text
            if input_number in list_for_end:
                self.r_answer(f'{self.name}, спасибо за игру! Число: ' + str(user_want_exit()), comment_id=comment_id)
                self.game_started = False

            elif number_from_user_is_ok(input_number):
                result = check_for_bulls_and_cows(input_number)
                self.r_answer('Быков – ' + str(result['bulls']) + ', коров – ' +
                              str(result['cows']) + '\nЭто была попытка № ' + str(self.counter), comment_id=comment_id)
                self.counter += 1
                if is_end_game():
                    self.r_answer('И вы угадали! Для новой игры введите "Старт"', comment_id=comment_id)
                    self.game_started = False
            elif not number_from_user_is_ok(input_number) and self.game_started:
                self.r_answer('Неверный формат! 4 разные цифры, первая – не ноль', comment_id=comment_id)

    def r_answer(self, message, comment_id):
        r_answer = requests.get('https://api.vk.com/method/wall.createComment', params={
            'access_token': token,
            'owner_id': -group_id,
            'post_id': POST_ID,
            'message': message,
            'reply_to_comment': comment_id,
            'v': 5.103,
        })


# Подключаем Bot LongPoll Server
# group_id - id группы
# Токен получать в группе -> Управление -> API -> Создать ключ. Там же включить LongPoll API и выбрать необходимые
# события (комментарии в данном случае).
r = requests.get('https://api.vk.com/method/groups.getLongPollServer', params={'group_id': group_id,
                                                                               'access_token': token,
                                                                               'v': 5.103})
data = r.json()
server = data['response']['server']  # Server и key константа для текущей сессии
key = data['response']['key']
ts_old = data['response']['ts']
list_of_players_id = {}

while True:
    try:
        r = requests.get(f'{server}?act=a_check&key={key}&ts={ts_old}&wait=25')  # Постоянные новые запросы
        data = r.json()
        ts = data['ts']
        from_id = -group_id
        for update in data['updates']:
            if update['object']['from_id'] != -group_id:  # Поиск до первого коммента не от имени группы
                from_id = update['object']['from_id']
                comment_id = update['object']['id']
                text = update['object']['text']
                if 'club' in text and ',' in text:
                    text = text.split(',')[1].strip()
                elif 'club' in text and ',' not in text:
                    text = text.split(']')[1].strip()
                print(f'ID игрока {from_id}, комментарий - "{text}", всего комментариев - '
                      f'{SESSION_TOTAL_COMMENTS_COUNT}, всего игроков - {len(list_of_players_id)}')
                break
        # print(ts_old, ts, from_id, comment_id, text)
        if ts != ts_old and from_id != -group_id:  # если есть комментарий не от имени группы
            ts_old = ts
            SESSION_TOTAL_COMMENTS_COUNT += 1
            if from_id not in list_of_players_id:
                r = requests.get('https://api.vk.com/method/users.get', params={'user_ids': from_id,
                                                                                'access_token': token,
                                                                                'v': 5.103})
                name = r.json()['response'][0]['first_name']
                list_of_players_id[from_id] = Player(name=name)
            list_of_players_id[from_id].game_step(text=text, comment_id=comment_id)
    except:
        print('Ошибка...')
        print(data)
        if NUMBERS_OF_ERRORS == 0:
            r = requests.get('https://api.vk.com/method/messages.send', params={'user_id': 25553631,
                                                                                'peer_id': 25553631,
                                                                                'random_id': randint(1, 2 ** 20),
                                                                                'access_token': token,
                                                                                'message': f'Што-то сломалось',
                                                                                'v': 5.103})
        NUMBERS_OF_ERRORS += 1

        r = requests.get('https://api.vk.com/method/groups.getLongPollServer', params={'group_id': group_id,
                                                                                       'access_token': token,
                                                                                       'v': 5.103})
        data = r.json()
        server = data['response']['server']  # Server и key константа для текущей сессии
        key = data['response']['key']
        ts_old = data['response']['ts']

    # time.sleep(1)

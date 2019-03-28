from vk_handle_bot import VkBot, KeyboardColor
import random
import time

bot = VkBot("b779111702115ac7bf2456c3fb6ae73b32da51de87bec22f101bc0970039f4d0fd9b2d320d30822991795", 180137983)

# Если True, то payload будет возвращаться как словарь, иначе как строка
bot.loading_payload = True

# Можно добавлять собственные атрибуты в класс.
bot.gamers = {}
bot.script_start_time = 0


def before_function(event):
	print("Эта функция выполнится прежде чем будет выполнена функция-хендлер")
	bot.script_start_time = time.time()
	if 1 == 2:

		bot.send_message(text=f"Вы заблокированы", peer_id=event.peer_id)
		# Если сделать
		raise Exception("Тестовое исключение")

		# То работа скрипта будет остановлена.
		# Например, это нужно если вы хотите ограничить доступ для определённых пользователей.
bot.before_function = before_function


def after_function(event):
	print(f"Время выполнения скрипта: {round(time.time() - bot.script_start_time, 3)} секунд")
	print("Эта функция выполнится после того как будет выполнена функция-хендлер")
bot.after_function = after_function


def default_function(event):
	print("Эта функция будет выполнена в том случае, если не нашлось никакого ответа.")
	bot.send_message(text="Неизвестная команда.", peer_id=event.peer_id)
bot.default_function = default_function



def get_variant(event):
	response = bot.gamers[event.from_id]

	if event.payload.get('variant') == response: won = True
	else: won = False

	keyboard = bot.get_keys(
		one_time=True,
		buttons=[
			[
				bot.get_btn(text="Да", color=KeyboardColor.BLUE, payload={"response":True}),
				bot.get_btn(text="Нет", color=KeyboardColor.BLUE, payload={"response":False})
			]
		]
	)

	if won != True: won = "не "
	else: won = ""

	bot.send_message(text=f"Вы {won}угадали) Ответ: {response}. Хочешь сыграть ещё раз?", peer_id=event.peer_id, keyboard=keyboard)
	bot.register_next_step(get_started, event)

def get_started(event):

	reply = ""
	if event.payload.get("response") != None:
		if event.payload.get("response") == False:
			bot.send_message(text="Жаль( Сыграем потом ещё раз. Пиши 'Старт' как захочешь!", peer_id=event.peer_id)
			bot.unset_next_step(event)
			return

	if event.text not in ["Да", "Нет"]:
		reply += f"Отлично, {event.text}.\n\n"

	bot.gamers.update({event.from_id:random.randint(1, 4)})

	buttons = []
	for i in range(1, 5, 1):
		buttons.append(bot.get_btn(text=f"{i}", color=KeyboardColor.BLUE, payload={"variant":i}))
	keyboard = bot.get_keys(one_time=True, buttons=[buttons])

	reply += "Итак. Бросаем кости.. Выбирай вариант:"
	bot.send_message(
		text=reply,
		peer_id=event.peer_id,
		keyboard=keyboard
	)

	bot.register_next_step(get_variant, event)


@bot.message_handler(texts_lower=["старт", "меню", "бот", "эй", "админ", "привет", "начать", "стоп", "чё", "ты"])
def start(event):
	bot.send_message(text="Сыграем?) Напиши своё имя.", peer_id=event.peer_id)
	bot.register_next_step(get_started, event)

bot.polling()
from vk_handle_bot import VkBot

bot = VkBot(token="your token")

def start(e):
	bot.send_message(text=f"Привет, {e.from_id}", peer_id=e.peer_id)
	bot.unset_next_step(e.from_id)

@bot.message_handler(text="тест_текст")
def testText(e):
	bot.send_message(
		text=f"Lorem ipsum dolor sit amel",
		peer_id=e.peer_id
	)
	"""	
	доп параметр для send_message, работает в чат ботах
	keyboard=bot.get_keys(
		one_time=True,
		buttons=[
			[
				bot.get_btn(text="Тест кнопка", color="default")
			]
		]
	)
	"""
	bot.register_next_step(start, e.from_id)

@bot.message_handler(content_type="photo")
def getByPhoto(e):
	bot.send_message(text="Найдено фото", peer_id=e.peer_id)


@bot.message_handler(priveleged_type="text")
def unknownCommand(e):
	bot.send_message(text="Неизвестная команда", peer_id=e.peer_id)

bot.polling(interval=1)
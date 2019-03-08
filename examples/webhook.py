from flask import Flask, request
from vk_handle_bot import VkBot
import json


app = Flask(__name__)
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

@app.route('/vk', methods=['GET', 'POST', 'DELETE'])
def vkontakte():
	data = json.loads(request.data)
	if "type" not in data.keys():
		return "not vk"
	if data['type'] == "confirmation":
		return "e0df84a3"
	elif data['type'] == "message_new":
		bot.process_new_update(data['object'])
		return 'ok'

app.run(host="0.0.0.0", debug=True, port=80)
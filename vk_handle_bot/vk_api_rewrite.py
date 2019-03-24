import json
import random
import re
import threading
import time
from enum import Enum
from collections import namedtuple

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

class KeyboardColor(Enum):
    """
    Возможные цвета кнопок
    """
	PRIMARY = "primary" # синяя
	DEFAULT = "default" # белая
	NEGATIVE = "negative" # красная
	POSITIVE = "positive" # зелёная

class VkBot:
	priveleged_types = {
		"text": r"\w+"
	}
	def __init__(self, token):
		self.decorated = list()
		self.last_update = None
		self.next_steps = dict()
		self.before_function = False
		self.after_function = False

		self.vk_session = self.new_vk_session(token)
		self.vk = self.vk_session.get_api()
		self.long_poll = VkLongPoll(self.vk_session)

	def new_vk_session(self, token):
		return vk_api.VkApi(token=token)

	def register_next_step(self, function, event):
		self.next_steps.update({event.user_id: function})

	def unset_next_step(self, event):
		self.next_steps.update({event.user_id: None})

	def message_handler(self, **kwargs):
		def decorate(function):
			def wrapper(e):
				if self.before_function != False:
					try: self.before_function(e)
					except Exception as s:
						print(f"Остановлена работа скрипта. {s}")
						return
				function(e)
				if self.after_function != False:
					self.after_function(e)
			self.decorated.append(dict(function=wrapper, options=kwargs))
			return wrapper
		return decorate

	def add_handler(self, function, **kwargs):
		self.decorated.append(dict(function=function, options=kwargs))

	def process_new_update(self, update):
		function = None
		if update != self.last_update:
			if self.next_steps.get(update.user_id) == None:
				for executable in self.decorated:
					if function == None:
						if executable['options'].get('commands') != None:
							if function == None:
								for command in executable['options'].get("commands"):
									if command == update.text.split(" ")[0].lower():
										function = executable['function']
										break

						if executable['options'].get('texts') != None:
							if function == None:
								for text in executable['options'].get("texts"):
									if text == update.text:
										function = executable['function']
										break

						if executable['options'].get('priveleged_type') != None:
							if function == None:
								for _type, regexp in self.priveleged_types.items():
									if len(re.findall(regexp, update.text)) > 0:
										function = executable['function']
										break

						if len(update.attachments) != 0:
							if function == None:
								for attachment in update.attachments:
									if 'type' in attachment:
										if update.attachments[attachment] == executable['options'].get('content_type'):
											function = executable['function']
											break
							else:
								break

						for key, option in executable['options'].items() :
							if function == None :
								for key1, option1 in update.__dict__.items() :
									if key1 == key and option1 == option :
										function = executable['function']
										break
							else :
								break
					else:
						break
			else:
				function = self.next_steps[update.user_id]

			if function != None:
				function(update)
				self.last_update = update
		else:
			return "Already processed"

	def polling(self):
		for event in self.long_poll.listen():
			if event.type == VkEventType.MESSAGE_NEW and event.to_me:
				self.process_new_update(event)

	def send_message(self, text, peer_id, attachment=None, keyboard=None):
		return self.vk.messages.send(
			random_id=time.time() + random.randint(0, 12000000),
			peer_id=peer_id,
			attachment=attachment,
			message=text,
			keyboard=keyboard
		)

	def get_keys(self, one_time=False, buttons=[]):
		return json.dumps(dict(
			one_time=one_time,
			buttons=buttons
		), ensure_ascii=False)

	def get_btn(self, text, color, payload=None):
		payload = json.dumps(payload) if payload != None else "{\"none\":\"none\"}"
		return dict(
			action=dict(
				type="text", payload=payload, label=text
			),
			color=color
		)
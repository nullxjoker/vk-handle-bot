from collections import namedtuple
import vk as vk_api
import time
import threading
import random
import re
import json
class VkBot :
	"""Библиотека для быстрого создания бота для вконтакте"""
	priveleged_types = {
		"text" : r"\w+"
	}
	def __init__(self, token, tokens=None, **kwargs):
		self.decorated = []
		self.last_update = None
		self.last_updates = None
		self.next_steps = dict()	
		self.vk = self.new_vk_session(token)
		if tokens != None:
			for arg in tokens:
				self.__dict__[arg['name']] = self.new_vk_session(arg['token'])
		self.before_function = False
		self.after_function = False

	def new_vk_session(self, token):
		return vk_api.API(
			vk_api.Session(access_token=token),
			v="5.92",
			lang="ru",
			timeout=10
		)

	def register_next_step(self, function, from_id):
		self.next_steps.update({from_id:function})

	def unset_next_step(self, from_id):
		self.next_steps.update({from_id:None})

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
		counter = 0
		function = None
		start_time = time.time()
		if update != self.last_update:
			if self.next_steps.get(update['from_id']) == None:
				for executable in self.decorated:
					if function == None :
						if executable['options'].get("commands") != None:
							if function == None :
								for command in executable['options'].get("commands"):
									if command == update['text'].split(" ")[0].lower():
										function = executable['function']
										break

						if executable['options'].get("texts") != None:
							if function == None :
								for text in executable['options'].get("texts"):
									if text == update['text'].lower():
										function = executable['function']
										break

						elif executable['options'].get("priveleged_type") != None :
							if function == None :
								for _type, regexp in self.priveleged_types.items() :
									if len(re.findall(regexp, update["text"])) > 0:
										function = executable['function']
										break

						elif len(update['attachments']) != 0 :
							if function == None :
								for attachment in update['attachments'] :
									if attachment['type'] == executable['options'].get('content_type') :
										function = executable['function']
										break
							else :
								break
						for key, option in executable['options'].items() :
							if function == None :
								for key1, option1 in update.items() :
									if key1 == key and option1 == option :
										function = executable['function']
										break
							else :
								break
					else :
						break
			else:
				function = self.next_steps[update['from_id']]

			if function != None :
				update['splitted'] = update['text'].split(" ")
				
				if "payload" in list(update.keys()):
					update['payload'] = json.loads(update['payload'])
				else:
					update['payload'] = {}

				function(namedtuple("Update", update.keys())(*update.values()))
				self.last_update = update
				print(f"Время выполнения: {time.time() - start_time}")
		else:
			return "Already processed"

	def polling(self, interval=1) :
		last_ts = None

		ts = self.vk.messages.getLongPollServer()['ts']
		try: my_id = self.vk.users.get()[0]['id']
		except: my_id = None
		while True :
			updates = self.vk.messages.getLongPollHistory(
				ts=ts, fields="photo,photo_medium_rec,sex,online,screen_name"
			)['messages']['items']
			try:
				if updates != self.last_updates:
					for update in updates:
						if (ts != last_ts and len(update) > 0
								and "-" not in str(update['from_id'])
								and update['from_id'] != my_id
								) :
							th = threading.Thread(
								target=lambda:self.process_new_update(update)
							)
							th.start()
					last_ts = ts
					self.last_updates = updates
			except IndexError:
				pass

			ts = self.vk.messages.getLongPollServer()['ts']
			time.sleep(interval)
			
	def send_message(self, peer_id, text, attachment=None, keyboard=None) :
		return self.vk.messages.send(
			random_id=random.randint(0, 12000000),
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
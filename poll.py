from vk_handle_bot import VkBot

bot = VkBot("b779111702115ac7bf2456c3fb6ae73b32da51de87bec22f101bc0970039f4d0fd9b2d320d30822991795", 180137983)


@bot.message_handler(texts=['привет'])
def hi(e):
	print(e.from_id)
	bot.send_message(text="Привет", peer_id=e.peer_id)


bot.polling()
import configparser
import json
from datetime import datetime
from telethon.sync import TelegramClient
from telethon import connection


from datetime import date, datetime
import pandas as pd
import os


from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch


from telethon.tl.functions.messages import GetHistoryRequest

# чтение конфига
config = configparser.ConfigParser()
config.read("config.ini")


api_id   = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']



client = TelegramClient(username, api_id, api_hash)

client.start()


async def dump_all_messages(channel):
	"""Записывает json-файл с информацией о всех сообщениях канала/чата"""
	offset_msg = 0    # номер записи, с которой начинается
	limit_msg = 200   # максимальное число записей

	all_messages = []   # список всех сообщений
	total_messages = 0
	total_count_limit = 0  # поменяь значение, если нужны не все сообщения

	class DateTimeEncoder(json.JSONEncoder):

		def default(self, o):
			if isinstance(o, datetime):
				return o.isoformat()
			if isinstance(o, bytes):
				return list(o)
			return json.JSONEncoder.default(self, o)

	word1 = input("Word1 to find: ")
	word2 = input("Word2 to find: ")
	days = int(input("Days: "))
	message_list = []
	id_list = []
	words_list = []
	date_list = []
	while True:
		history = await client(GetHistoryRequest(
			peer=channel,
			offset_id=offset_msg,
			offset_date=None, add_offset=0,
			limit=limit_msg, max_id=0, min_id=0,
			hash=0))
		if not history.messages:
			break
		messages = history.messages

		for message in messages:
			try:
				if word1 and word2 in message.message:

					date_now = datetime.now()
					message_date = message.date
					message_date = message_date.replace(tzinfo=None)
					delta = date_now - message_date
					delta = int(delta.days)
					print(delta, 'days ago')
					if delta <= days:

						print(message.from_id)
						print(message.date)
						words_list.append(word1 + ' ' + word2)

						message_list.append(message.message)

						id = str(message.from_id)
						id_list.append(id)

						date = message.date
						date=date.date()
						print(date)
						date_list.append(date)
			except Exception as e:
				print(e)
				pass

			all_messages.append(message.to_dict())
		offset_msg = messages[len(messages) - 1].id
		total_messages = len(all_messages)
		if total_count_limit != 0 and total_messages >= total_count_limit:
			break
	df = pd.DataFrame({'Message': pd.Series(message_list),
					   'Id': pd.Series(id_list),
					   'words to find': pd.Series(words_list),
					   'datetime': pd.Series(date_list)
					   })
	df.fillna(0)
	try:
		os.makedirs('Telega_parser')
	except:
		pass
	print('Making file...')
	df.to_csv('Telega_parser/' + word1 +'_'+ word2+'.csv', encoding="utf-8-sig")
	df.to_excel('Telega_parser/' + word1 +'_'+ word2+'.xlsx', encoding="utf-8-sig")


async def main():
	url = input("Enter channel (example: https://t.me/textile2077): ")
	channel = await client.get_entity(url)

	await dump_all_messages(channel)



with client:
	client.loop.run_until_complete(main())
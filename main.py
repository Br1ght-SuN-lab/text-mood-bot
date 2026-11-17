from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN
import pickle
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import ExtraTreesClassifier
from nltk.tokenize import TweetTokenizer
from translate import Translator
from engine import everythin_is_fine
from text_messages import error, start_text, depression, send_ask


tokenizer = TweetTokenizer()
translator = Translator(to_lang='en', from_lang='ru')


bot = Bot(TOKEN)
dp = Dispatcher(bot)

async def on_startup(_):
   print("Bot is working!")

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
   await message.answer(text=start_text)
   await message.answer(send_ask)

@dp.message_handler()
async def save_message(message: types.Message):
   if message.text != '/start' and len(message.text) > 0:
      percent = everythin_is_fine(message.text)
      await message.answer(depression.format(percent))
   else:
      await message.answer(error)

if __name__ == "__main__":
   executor.start_polling(dp, on_startup=on_startup, skip_updates=True)

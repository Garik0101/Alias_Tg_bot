from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import sqlite3

import random

import os

TOKEN = os.getenv('TELEGRAM_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect('rate-top.db')
cursor = conn.cursor()

words  = ['եքիդնա', 'Շրի Լանկա', 'բուդդայականություն', 'թեգերան', 'կայծքար', 'հուշարձան', 'վերածննունդ', 'ենթադրական', 'մոլեկուլ', 'կշռաքար', 'սոճի', 'Անանիա Շիրակացի', 'դահուկորդ', 'խլուրդ', 'աստղագետ', 'Վեներա', 'պանրագործ', 'հեքիաթ', 'զինագործ', 'դելֆին', 'գործազուրկ', 'Ամազոն', 'արհեստ', 'սկյուռ', 'խենթ', 'Վաշինգտոն', 'հիշատակ', 'որակ', 'չինացի', 'տիղմ', 'կազդուրվել',]

status = True

def create_table(chat_title):
    cursor.execute('''CREATE TABLE IF NOT EXISTS "{}" (
    user_id INTEGER PRIMARY KEY,
    user_name TEXT,
    guessions INTEGER
);'''.format(chat_title))
    
    conn.commit()

def values_to_table(user_id, user_name, guessions, chat_title):
    cursor.execute('INSERT OR REPLACE INTO "{}" (user_id, user_name, guessions) VALUES (?, ?, ?)'.format(chat_title), (user_id, user_name, guessions)) 
    conn.commit()	
	
@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    create_table(message.chat.title)
    values_to_table(message.from_user.id, message.from_user.first_name, 0, message.chat.title)
    await bot.send_message(message.chat.id, 'Ողջույն, խաղը սկսելու համար ներմուծիր /game հրամանը\n(/start-ը զրոյացնում է բոլոր միավորները)')

@dp.message_handler(commands=['game'])
async def game_start(message: types.Message):
    if status:
        global owner
        owner = message.from_user.id
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text="Ցույց տալ բառը", callback_data='owner')) 
        await bot.send_message(chat_id=message.chat.id, text=f"{message.from_user.mention} դու պետք է բացատրես հետևյալ բառը ↓", reply_markup=keyboard)
    else:
        await bot.send_message(message.chat.id, 'Սպասիր քո հերքին!')

@dp.message_handler(commands=['rate'])
async def show_rating(message: types.Message):
    count = 0
    dictionary_rate  = dict()
    rating_text = ''
    rating_table = cursor.execute('SELECT * FROM "{}"'.format(message.chat.title)).fetchall()
    for row in rating_table:
        count += 1
        rating_text += f'{count}.{row[1]} - {row[2]} միավոր\n'
    await bot.send_message(message.chat.id, rating_text)
    
@dp.callback_query_handler(lambda query: query.data == "owner")
async def answer_text(call: types.CallbackQuery):
    global word
    word = random.choice(words)
    if call.from_user.id == owner:
       	await call.answer(text=word)
    else:
        await call.answer(text='Դու չես բացատրողը')

@dp.message_handler(content_types=['text'])
async def game_function(message: types.Message):
    if word.lower() in message.text.lower():
        guessions = cursor.execute('SELECT guessions FROM "{}" WHERE user_id=?'.format(message.chat.title), (message.from_user.id,))
        guession = guessions.fetchall()[0][0] + 1
        values_to_table(message.from_user.id, message.from_user.first_name, guession, message.chat.title)
        await bot.send_message(message.chat.id, f'{message.from_user.first_name}-ը գուշակեց բառը\nճիշտ բառն էր {word}')
    
if __name__ == '__main__':
    executor.start_polling(dp)

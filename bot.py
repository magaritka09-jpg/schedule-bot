import asyncio
import logging
import os
from datetime import datetime
import pytz
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(**name**)

TELEGRAM_TOKEN = os.environ.get(“TELEGRAM_TOKEN”)
OPENAI_API_KEY = os.environ.get(“OPENAI_API_KEY”)
USER_ID = int(os.environ.get(“USER_ID”, “298630213”))
TIMEZONE = pytz.timezone(“Europe/Istanbul”)

openai_client = OpenAI(api_key=OPENAI_API_KEY)

SCHEDULE = {
0: {  # Понедельник
“morning”: “☀️ Доброе утро! Сегодня понедельник.\n\n📋 Твой день:\n• Душ утром\n• Работа 10:00–19:00\n• 20:00 — английский\n• 20:30 — упражнения на тазовое дно”,
“lang”: “english”,
},
1: {  # Вторник
“morning”: “☀️ Доброе утро! Сегодня вторник.\n\n📋 Твой день:\n• Работа 10:00–19:00\n• 20:00 — турецкий\n• 20:30 — упражнения на тазовое дно”,
“lang”: “turkish”,
},
2: {  # Среда
“morning”: “☀️ Доброе утро! Сегодня среда.\n\n📋 Твой день:\n• 9:00 — пилатес 🧘‍♀️\n• Душ после пилатеса\n• Работа 10:00–19:00\n• Свободный вечер — заслужила!”,
“lang”: None,
},
3: {  # Четверг
“morning”: “☀️ Доброе утро! Сегодня четверг.\n\n📋 Твой день:\n• Работа 10:00–19:00\n• 20:00 — английский\n• 20:30 — упражнения на тазовое дно”,
“lang”: “english”,
},
4: {  # Пятница
“morning”: “☀️ Доброе утро! Сегодня пятница.\n\n📋 Твой день:\n• 9:00 — пилатес 🧘‍♀️\n• Душ после пилатеса\n• Работа 10:00–19:00\n• Свободный вечер — впереди выходные! 🎉”,
“lang”: None,
},
5: {  # Суббота
“morning”: “☀️ Доброе утро! Сегодня суббота.\n\n📋 Твой день:\n• Уборка (кухня + ванная)\n• Если хочется — плавание 🏊‍♀️\n• 20:30 — упражнения на тазовое дно”,
“lang”: “turkish”,
},
6: {  # Воскресенье
“morning”: “☀️ Доброе утро! Сегодня воскресенье.\n\n📋 Твой день:\n• Уборка если осталось\n• 20:00 — турецкий или английский (выбирай сама)\n• Отдых и восстановление 💛”,
“lang”: None,
},
}

LANGUAGE_PROMPTS = {
“english”: “”“Ты преподаватель английского языка. Подготовь короткий урок для студента уровня B1-B2 на сегодня.
Урок должен включать:

1. 1 полезное слово или фразу с примером (что-то из повседневной жизни)
1. 1 короткое упражнение (заполни пропуск или переведи фразу)
1. Ответ на упражнение

Формат — коротко и по делу, как дружеское сообщение. Не более 200 слов. Пиши на русском языке, но английские примеры давай на английском.”””,
"turkish": """Sen bir Türkçe öğretmenisin. Bugün için kısa bir ders hazırla. Öğrenci başlangıç seviyesinde (A1-A2).Ders şunları içermeli:

1. 1 yararlı kelime veya ifade + Rusça açıklama
1. 1 kısa alıştırma
1. Alıştırmanın cevabı

Rusça yaz ama Türkçe örnekleri Türkçe ver. Maksimum 200 kelime. Samimi ve kısa tut.”””
}

async def generate_lesson(language: str) -> str:
try:
prompt = LANGUAGE_PROMPTS.get(language, LANGUAGE_PROMPTS[“english”])
response = openai_client.chat.completions.create(
model=“gpt-4o-mini”,
messages=[{“role”: “user”, “content”: prompt}],
max_tokens=500,
)
return response.choices[0].message.content
except Exception as e:
logger.error(f”OpenAI error: {e}”)
return “Не удалось загрузить урок. Попробуй /lesson чтобы получить его вручную.”

async def send_morning_schedule(bot: Bot):
now = datetime.now(TIMEZONE)
weekday = now.weekday()
schedule = SCHEDULE.get(weekday, {})
message = schedule.get(“morning”, “☀️ Доброе утро! Хорошего дня!”)
await bot.send_message(chat_id=USER_ID, text=message)

async def send_language_reminder(bot: Bot):
now = datetime.now(TIMEZONE)
weekday = now.weekday()
schedule = SCHEDULE.get(weekday, {})
lang = schedule.get(“lang”)
if lang == "english":
    await bot.send_message(chat_id=USER_ID, text="🇬🇧 Через 10 минут — английский! Готовлю урок...")
elif lang == "turkish":
    await bot.send_message(chat_id=USER_ID, text="🇹🇷 Через 10 минут — турецкий! Готовлю урок...")async def send_language_lesson(bot: Bot):
now = datetime.now(TIMEZONE)
weekday = now.weekday()
schedule = SCHEDULE.get(weekday, {})
lang = schedule.get(“lang”)
if lang:
    lesson = await generate_lesson(lang)
    emoji = "🇬🇧" if lang == "english" else "🇹🇷"
    lang_name = "Английский" if lang == "english" else "Турецкий"
    await bot.send_message(
        chat_id=USER_ID,
        text=f"{emoji} *{lang_name} — урок на сегодня*\n\n{lesson}",
        parse_mode="Markdown"
    )async def send_exercise_reminder(bot: Bot):
await bot.send_message(
chat_id=USER_ID,
text=“🌸 Время упражнений на тазовое дно! Не забудь про себя 💛”
)

async def start_command(update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
“Привет! Я твой планировщик 🗓\n\n”
“Команды:\n”
“/today — расписание на сегодня\n”
“/lesson — урок языка прямо сейчас\n”
“/help — помощь”
)

async def today_command(update, context: ContextTypes.DEFAULT_TYPE):
now = datetime.now(TIMEZONE)
weekday = now.weekday()
schedule = SCHEDULE.get(weekday, {})
message = schedule.get(“morning”, “Расписание не найдено”)
await update.message.reply_text(message)

async def lesson_command(update, context: ContextTypes.DEFAULT_TYPE):
now = datetime.now(TIMEZONE)
weekday = now.weekday()
schedule = SCHEDULE.get(weekday, {})
lang = schedule.get(“lang”)
if not lang:
    # Default to english if no language scheduled today
    lang = "english"

await update.message.reply_text("Готовлю урок, секунду... ⏳")
lesson = await generate_lesson(lang)
emoji = "🇬🇧" if lang == "english" else "🇹🇷"
lang_name = "Английский" if lang == "english" else "Турецкий"
await update.message.reply_text(
    f"{emoji} *{lang_name} — урок на сегодня*\n\n{lesson}",
    parse_mode="Markdown"
)async def help_command(update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
“🤖 Я твой личный планировщик!\n\n”
“Каждый день я буду:\n”
“• Утром присылать расписание дня\n”
“• В 19:50 напоминать о языке\n”
“• В 20:00 присылать урок\n”
“• В 20:30 напоминать об упражнениях\n\n”
“Команды:\n”
“/today — расписание на сегодня\n”
“/lesson — урок языка прямо сейчас”
)

def main():
app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("today", today_command))
app.add_handler(CommandHandler("lesson", lesson_command))
app.add_handler(CommandHandler("help", help_command))

scheduler = AsyncIOScheduler(timezone=TIMEZONE)
bot = app.bot

# Утреннее расписание
scheduler.add_job(send_morning_schedule, "cron", hour=9, minute=0, args=[bot])
# В среду и пятницу в 8:00 (пилатес)
scheduler.add_job(send_morning_schedule, "cron", day_of_week="wed,fri", hour=8, minute=0, args=[bot])

# Напоминание о языке в 19:50
scheduler.add_job(send_language_reminder, "cron", hour=19, minute=50, args=[bot])

# Урок языка в 20:00
scheduler.add_job(send_language_lesson, "cron", hour=20, minute=0, args=[bot])

# Упражнения в 20:30
scheduler.add_job(send_exercise_reminder, "cron", hour=20, minute=30, args=[bot])

scheduler.start()

logger.info("Бот запущен!")
app.run_polling()if name == “**main**”:
main()

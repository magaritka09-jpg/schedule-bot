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
logger = logging.getLogger(__name__)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
USER_ID = int(os.environ.get("USER_ID", "298630213"))
TIMEZONE = pytz.timezone("Europe/Istanbul")
openai_client = OpenAI(api_key=OPENAI_API_KEY)
SCHEDULE = {
    0: {  # Понедельник
"morning": " Доброе утро! Сегодня понедельник.\n\n Твой день:\n• Душ утром
      "lang": "english",
},
1: { # Вторник
"morning": " Доброе утро! Сегодня вторник.\n\n "lang": "turkish",
  Твой день:\n• Работа 10:00–
Твой день:\n• 9:00 — пилатес
  Твой день:\n• Работа 10:00–
  Твой день:\n• 9:00 — пилате
  Твой день:\n• Уборка (кухня
  },
2:{ #Среда
"morning": "
    "lang": None,
},
3: {  # Четверг
    "morning": "
Доброе утро! Сегодня среда.\n\n
                   Доброе утро! Сегодня четверг.\n\n
"lang": "english",
},
4: {  # Пятница
"morning": "
    "lang": None,
},
5: {  # Суббота
    "morning": "
Доброе утро! Сегодня пятница.\n\n
                   Доброе утро! Сегодня суббота.\n\n
"lang": "turkish",
\n• Ра
19:00\
\n•
19:00\
с \n
+ ван
  б
n
Д
n
•
н

     },
    6: {  # Воскресенье
"morning": "
        "lang": None,
    },
}
LANGUAGE_PROMPTS = {
    "english": """Ты преподаватель английского языка. Подготовь короткий урок для студ
Урок должен включать:
1. 1 полезное слово или фразу с примером (что-то из повседневной жизни)
2. 1 короткое упражнение (заполни пропуск или переведи фразу)
3. Ответ на упражнение
Формат — коротко и по делу, как дружеское сообщение. Не более 200 слов. Пиши на русско
    "turkish": """Sen bir Türkçe öğretmenisin. Bugün için kısa bir ders hazırla. Öğren
Ders şunları içermeli:
1. 1 yararlı kelime veya ifade + Rusça açıklama
2. 1 kısa alıştırma
3. Alıştırmanın cevabı
Rusça yaz ama Türkçe örnekleri Türkçe ver. Maksimum 200 kelime. Samimi ve kısa tut."""
}
async def generate_lesson(language: str) -> str:
    try:
        prompt = LANGUAGE_PROMPTS.get(language, LANGUAGE_PROMPTS["english"])
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
)
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return "Не удалось загрузить урок. Попробуй /lesson чтобы получить его вручную
async def send_morning_schedule(bot: Bot):
now = datetime.now(TIMEZONE)
weekday = now.weekday()
schedule = SCHEDULE.get(weekday, {})
message = schedule.get("morning", " Доброе утро! Хорошего дня!") await bot.send_message(chat_id=USER_ID, text=message)
  Доброе утро! Сегодня воскресенье.\n\n
Твой день:\n• Уборка ес
 ли ост
ента ур
м языке
ci başl
."
а

 async def send_language_reminder(bot: Bot):
    now = datetime.now(TIMEZONE)
    weekday = now.weekday()
    schedule = SCHEDULE.get(weekday, {})
    lang = schedule.get("lang")
    if lang == "english":
        await bot.send_message(chat_id=USER_ID, text="
    elif lang == "turkish":
        await bot.send_message(chat_id=USER_ID, text="
async def send_language_lesson(bot: Bot):
    now = datetime.now(TIMEZONE)
    weekday = now.weekday()
    schedule = SCHEDULE.get(weekday, {})
    lang = schedule.get("lang")
Через 10 минут — английский!
Через 10 минут — турецкий! Го
  if lang:
lesson = await generate_lesson(lang)
emoji=" "iflang=="english"else" "
lang_name = "Английский" if lang == "english" else "Турецкий" await bot.send_message(
            chat_id=USER_ID,
            text=f"{emoji} *{lang_name} — урок на сегодня*\n\n{lesson}",
            parse_mode="Markdown"
)
async def send_exercise_reminder(bot: Bot):
    await bot.send_message(
        chat_id=USER_ID,
text=" Время упражнений на тазовое дно! Не забудь про себя " )
async def start_command(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
"Привет! Я твой планировщик \n\n" "Команды:\n"
"/today — расписание на сегодня\n" "/lesson — урок языка прямо сейчас\n" "/help — помощь"
)
     Готовл товлю
ю у

 async def today_command(update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(TIMEZONE)
    weekday = now.weekday()
    schedule = SCHEDULE.get(weekday, {})
    message = schedule.get("morning", "Расписание не найдено")
    await update.message.reply_text(message)
async def lesson_command(update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(TIMEZONE)
    weekday = now.weekday()
    schedule = SCHEDULE.get(weekday, {})
    lang = schedule.get("lang")
    if not lang:
        # Default to english if no language scheduled today
        lang = "english"
await update.message.reply_text("Готовлю урок, секунду... ") lesson = await generate_lesson(lang)
emoji=" "iflang=="english"else" "
lang_name = "Английский" if lang == "english" else "Турецкий" await update.message.reply_text(
        f"{emoji} *{lang_name} — урок на сегодня*\n\n{lesson}",
        parse_mode="Markdown"
    )
async def help_command(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
" Я твой личный планировщик!\n\n" "Каждый день я буду:\n"
"• Утром присылать расписание дня\n" "• В 19:50 напоминать о языке\n"
        "• В 20:00 присылать урок\n"
        "• В 20:30 напоминать об упражнениях\n\n"
        "Команды:\n"
        "/today — расписание на сегодня\n"
        "/lesson — урок языка прямо сейчас"
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
    scheduler.add_job(send_morning_schedule, "cron", day_of_week="wed,fri", hour=8, mi
    # Напоминание о языке в 19:50
    scheduler.add_job(send_language_reminder, "cron", hour=19, minute=50, args=[bot])
    # Урок языка в 20:00
    scheduler.add_job(send_language_lesson, "cron", hour=20, minute=0, args=[bot])
    # Упражнения в 20:30
    scheduler.add_job(send_exercise_reminder, "cron", hour=20, minute=30, args=[bot])
    scheduler.start()
    logger.info("Бот запущен!")
    app.run_polling()
if __name__ == "__main__":
    main()
nute=0,

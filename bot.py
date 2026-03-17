import logging
import os
from datetime import datetime
import pytz
from telegram.ext import Application, CommandHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
USER_ID = int(os.environ.get("USER_ID", "298630213"))
TIMEZONE = pytz.timezone("Europe/Istanbul")

SCHEDULE = {
    0: {"morning": "Доброе утро! Понедельник.\n\nСегодня:\n- Душ утром\n- Работа 10:00-19:00\n- 20:00 английский\n- 20:30 упражнения", "lang": "english"},
    1: {"morning": "Доброе утро! Вторник.\n\nСегодня:\n- Работа 10:00-19:00\n- 20:00 турецкий\n- 20:30 упражнения", "lang": "turkish"},
    2: {"morning": "Доброе утро! Среда.\n\nСегодня:\n- 9:00 пилатес\n- Работа 10:00-19:00\n- Свободный вечер!", "lang": None},
    3: {"morning": "Доброе утро! Четверг.\n\nСегодня:\n- Работа 10:00-19:00\n- 20:00 английский\n- 20:30 упражнения", "lang": "english"},
    4: {"morning": "Доброе утро! Пятница.\n\nСегодня:\n- 9:00 пилатес\n- Работа 10:00-19:00\n- Свободный вечер!", "lang": None},
    5: {"morning": "Доброе утро! Суббота.\n\nСегодня:\n- Уборка\n- Плавание если хочется\n- 20:30 упражнения", "lang": "turkish"},
    6: {"morning": "Доброе утро! Воскресенье.\n\nСегодня:\n- Уборка если осталось\n- 20:00 язык на выбор\n- Отдых!", "lang": None},
}

LANGUAGE_PROMPTS = {
    "english": "Ты преподаватель английского языка. Подготовь короткий урок для студента уровня B1-B2. Включи: 1 полезное слово или фразу с примером, 1 короткое упражнение, ответ. Пиши на русском, примеры на английском. Не более 200 слов.",
    "turkish": "Sen Turkce ogretmenisin. A1-A2 seviyesi icin kisa ders: 1 kelime ve Rusca aciklama, 1 alistirma, cevap. Rusca yaz, ornekler Turkce. Maks 200 kelime."
}


async def generate_lesson(language):
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": LANGUAGE_PROMPTS.get(language)}],
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return "Не удалось загрузить урок. Напиши /lesson снова."


async def send_morning_schedule(bot):
    weekday = datetime.now(TIMEZONE).weekday()
    message = SCHEDULE.get(weekday, {}).get("morning", "Доброе утро!")
    await bot.send_message(chat_id=USER_ID, text=message)


async def send_language_reminder(bot):
    weekday = datetime.now(TIMEZONE).weekday()
    lang = SCHEDULE.get(weekday, {}).get("lang")
    if lang == "english":
        await bot.send_message(chat_id=USER_ID, text="Через 10 минут английский! Готовлю урок...")
    elif lang == "turkish":
        await bot.send_message(chat_id=USER_ID, text="Через 10 минут турецкий! Готовлю урок...")


async def send_language_lesson(bot):
    weekday = datetime.now(TIMEZONE).weekday()
    lang = SCHEDULE.get(weekday, {}).get("lang")
    if lang:
        lesson = await generate_lesson(lang)
        lang_name = "Английский" if lang == "english" else "Турецкий"
        await bot.send_message(chat_id=USER_ID, text=f"{lang_name} - урок на сегодня\n\n{lesson}")


async def send_exercise_reminder(bot):
    await bot.send_message(chat_id=USER_ID, text="Время упражнений на тазовое дно! Не забудь про себя")


async def start_command(update, context):
    await update.message.reply_text("Привет! Я твой планировщик\n\n/today - расписание на сегодня\n/lesson - урок языка\n/help - помощь")


async def today_command(update, context):
    weekday = datetime.now(TIMEZONE).weekday()
    message = SCHEDULE.get(weekday, {}).get("morning", "Расписание не найдено")
    await update.message.reply_text(message)


async def lesson_command(update, context):
    weekday = datetime.now(TIMEZONE).weekday()
    lang = SCHEDULE.get(weekday, {}).get("lang") or "english"
    await update.message.reply_text("Готовлю урок, секунду...")lesson = await generate_lesson(lang)
    lang_name = "Английский" if lang == "english" else "Турецкий"
    await update.message.reply_text(f"{lang_name} - урок на сегодня\n\n{lesson}")


async def help_command(update, context):
    await update.message.reply_text("Каждый день:\n- Утром расписание\n- 19:50 напоминание о языке\n- 20:00 урок\n- 20:30 упражнения\n\n/today - расписание\n/lesson - урок")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("today", today_command))
    app.add_handler(CommandHandler("lesson", lesson_command))
    app.add_handler(CommandHandler("help", help_command))

    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    bot = app.bot
    scheduler.add_job(send_morning_schedule, "cron", day_of_week="mon,tue,thu", hour=9, minute=0, args=[bot])
    scheduler.add_job(send_morning_schedule, "cron", day_of_week="wed,fri", hour=8, minute=0, args=[bot])
    scheduler.add_job(send_morning_schedule, "cron", day_of_week="sat,sun", hour=10, minute=0, args=[bot])
    scheduler.add_job(send_language_reminder, "cron", hour=19, minute=50, args=[bot])
    scheduler.add_job(send_language_lesson, "cron", hour=20, minute=0, args=[bot])
    scheduler.add_job(send_exercise_reminder, "cron", hour=20, minute=30, args=[bot])
    scheduler.start()

    logger.info("Бот запущен!")
    app.run_polling()


if name == "__main__":
    main()

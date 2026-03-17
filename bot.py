reply_text("Привет! Я твой планировщик 🗓\n\nКоманды:\n/today - расписание на сегодня\n/lesson - урок языка прямо сейчас\n/help - помощь")


async def today_command(update, context):
    weekday = datetime.now(TIMEZONE).weekday()
    message = SCHEDULE.get(weekday, {}).get("morning", "Расписание не найдено")
    await update.message.reply_text(message)


async def lesson_command(update, context):
    weekday = datetime.now(TIMEZONE).weekday()
    lang = SCHEDULE.get(weekday, {}).get("lang") or "english"
    await update.message.reply_text("Готовлю урок, секунду... ⏳")
    lesson = await generate_lesson(lang)
    emoji = "🇬🇧" if lang == "english" else "🇹🇷"
    lang_name = "Английский" if lang == "english" else "Турецкий"
    await update.message.reply_text(f"{emoji} {lang_name} - урок на сегодня\n\n{lesson}")


async def help_command(update, context):
    await update.message.reply_text("Каждый день:\n• Утром - расписание дня\n• 19:50 - напоминание о языке\n• 20:00 - урок\n• 20:30 - напоминание об упражнениях\n\n/today - расписание\n/lesson - урок прямо сейчас")


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

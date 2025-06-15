import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters
)
from telegram.error import TelegramError
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = 'your_token'
SERVER_URL = 'http://localhost:5001/answer'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        welcome_text = (
            "👋 Привет! Я — ИИ-помощник по адаптивным упражнениям для детей с ОВЗ.\n\n"
            "Я могу подсказать:\n"
            "✅ Какие упражнения подойдут при ДЦП, РАС, нарушениях слуха/зрения, СДВГ и др.\n"
            "✅ Как правильно заниматься с учетом особенностей ребенка\n"
            "✅ Игровые методики для развития моторики, речи и концентрации\n\n"
            "Просто задай вопрос, например:\n"
            "▪ Какие упражнения для ребенка с аутизмом 6 лет?\n"
            "▪ Как улучшить координацию у слабовидящего ребенка?\n"
            "▪ Нужна гимнастика при ДЦП для ног\n\n"
            "Напиши мне, и я постараюсь помочь! 🌟\n"
        )
        await update.message.reply_text(welcome_text)
    except TelegramError as e:
        logger.error(f"Ошибка при отправке приветствия: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        question = update.message.text
        logger.info(f"Получен вопрос: {question}")

        try:
            response = requests.post(SERVER_URL, json={'question': question}, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к серверу: {e}")
            await update.message.reply_text("Сервер временно недоступен, попробуйте позже")
            return

        if 'error' in data:
            logger.error(f"Ошибка сервера: {data['error']}")
            await update.message.reply_text("Произошла ошибка при обработке вопроса")
            return

        answer = data.get('answer', '')
        confidence = data.get('confidence', 0)

        print(confidence)
        
        if not answer:
            response_text = "Затрудняюсь ответить на ваш вопрос. Пожалуйста, обратитесь к специалистам: @rostOk_world"
        elif confidence >= 0.99999:
            response_text = f"{answer}"
        else:
            response_text = f"{answer}\n\nЕсли у вас есть вопросы, обратитесь к специалистам: @rostOk_world"
        
        await update.message.reply_text(response_text)
        
    except TelegramError as e:
        logger.error(f"Ошибка Telegram API: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        await update.message.reply_text("Произошла непредвиденная ошибка")

def main():
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        app.add_error_handler(error_handler)
        
        logger.info("Бот запущен...")
        app.run_polling()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}", exc_info=context.error)
    
    if update and hasattr(update, 'message'):
        try:
            await update.message.reply_text(
                "Произошла ошибка. Пожалуйста, попробуйте позже."
            )
        except TelegramError:
            pass

if __name__ == '__main__':
    main()
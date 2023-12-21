import logging
import os
from datetime import datetime

import django
from asgiref.sync import sync_to_async
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, CallbackContext, MessageHandler, \
    filters

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

TELEGRAM_TOKEN = "6679083154:AAEUXQWGVHtszmBD8xa6_Y98q6gSF864Lls"
TELEGRAM_CHAT_ID = "-4062756263"
AUTHORIZED_CHAT_ID = "409107123"
LANGUAGE, NAME, PHONE, DATE, NUMBER_OF_PEOPLE, BROADCAST_TEXT = range(6)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

user_ids = set()
user_data = {}


def get_language_keyboard():
    keyboard = [['Русский', 'Română']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


async def start(update: Update, context: CallbackContext) -> int:
    user, created = await sync_to_async(User.objects.get_or_create)(chat_id=str(update.effective_chat.id))
    user.full_name = f"{update.effective_user.first_name} {update.effective_user.last_name or ''}"
    await sync_to_async(user.save)()
    reply_markup = get_language_keyboard()
    await update.message.reply_text('Для русского нажмите "Кнопу" / Pentru română apăsați "Button"',
                                    reply_markup=reply_markup)
    return LANGUAGE


async def language_choice(update: Update, context: CallbackContext) -> int:
    context.user_data['language'] = update.message.text
    await update.message.reply_text(
        'Как вас зовут?' if context.user_data['language'] == 'Русский' else 'Cum vă numiți?')
    return NAME


async def name(update: Update, context: CallbackContext) -> int:
    user_name = update.message.text
    context.user_data["name"] = user_name
    user = await sync_to_async(User.objects.get)(chat_id=str(update.effective_chat.id))
    user.full_name = user_name
    await sync_to_async(user.save)()
    await update.message.reply_text("Какой у вас номер телефона?" if context.user_data.get('language',
                                                                                           'Русский') == 'Русский' else "Care este numărul dvs de telefon?")
    return PHONE


async def phone(update: Update, context: CallbackContext) -> int:
    user_phone = update.message.text
    context.user_data["phone"] = user_phone
    user = await sync_to_async(User.objects.get)(chat_id=str(update.effective_chat.id))
    user.phone = user_phone
    await sync_to_async(user.save)()
    await update.message.reply_text("На какую дату вы хотите сделать бронирование?" if context.user_data.get('language',
                                                                                                             'Русский') == 'Русский' else "Pentru ce dată doriți să faceți rezervarea?")
    return DATE


async def date(update: Update, context: CallbackContext) -> int:
    date_text = update.message.text
    try:
        valid_date = datetime.strptime(date_text, "%d.%m.%Y")
        context.user_data["date"] = valid_date
        await update.message.reply_text("Сколько человек будет?" if context.user_data.get('language',
                                                                                          'Русский') == 'Русский' else "Câte persoane veți fi?")
        return NUMBER_OF_PEOPLE
    except ValueError:
        await update.message.reply_text(
            "Введенная дата недействительна. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ (например, 31.12.2021)." if context.user_data.get(
                'language',
                'Русский') == 'Русский' else "Data introdusă este invalidă. Vă rugăm să introduceți data în formatul ZZ.LL.AAAA (de exemplu, 31.12.2021).")
        return DATE


async def number_of_people(update: Update, context: CallbackContext) -> int:
    number_of_people = update.message.text
    context.user_data["number_of_people"] = number_of_people
    user = await sync_to_async(User.objects.get)(chat_id=str(update.effective_chat.id))
    user.person = number_of_people
    user.is_subscribed = True
    await sync_to_async(user.save)()
    await update.message.reply_text(
        f"Ваш запрос на {context.user_data['name']} для {context.user_data['date'].strftime('%d.%m.%Y')} зарегистрирован, мы скоро свяжемся с вами по телефону!" if context.user_data.get(
            'language',
            'Русский') == 'Русский' else f"Solicitarea dvs pentru {context.user_data['name']} pentru {context.user_data['date'].strftime('%d.%m.%Y')} a fost înregistrată, în scurt timp revenim cu confirmarea telefonică!")
    await context.bot.send_message(chat_id=TELEGRAM_CHAT_ID,
                                   text=f"Имя: {context.user_data['name']}, Телефон: {context.user_data['phone']}, Дата: {context.user_data['date'].strftime('%d.%m.%Y')}, Количество человек: {context.user_data['number_of_people']}")
    return ConversationHandler.END


async def cancel(update, context):
    await update.message.reply_text("Anulare. Folosește /start pentru a încerca din nou.")
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [MessageHandler(filters.Regex('^(Русский|Română)$'), language_choice)],
            NAME: [MessageHandler(filters.TEXT, name)],
            PHONE: [MessageHandler(filters.TEXT, phone)],
            DATE: [MessageHandler(filters.TEXT, date)],
            NUMBER_OF_PEOPLE: [MessageHandler(filters.TEXT, number_of_people)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)
    app.run_polling()

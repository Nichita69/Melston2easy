import logging
from datetime import datetime

import environ
from asgiref.sync import sync_to_async
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, CallbackContext, MessageHandler, \
    filters

from users.models import User

environ.Env.read_env(env_file='.env')

env = environ.Env()

TELEGRAM_TOKEN = env("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = env("TELEGRAM_CHAT_ID")
AUTHORIZED_CHAT_ID = env("AUTHORIZED_CHAT_ID")
LANGUAGE, NAME, PHONE, DATE, NUMBER_OF_PEOPLE, BROADCAST_TEXT = range(6)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

user_ids = set()
user_data = {}
BROADCAST_MESSAGE = range(1)


def get_language_keyboard():
    keyboard = [['Русский', 'Română'], ['Fa rezervare']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


def get_start_keyboard():
    keyboard = [['Fa rezervare']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


async def start(update: Update, context: CallbackContext) -> int:
    # Сброс или инициализация данных пользователя
    context.user_data.clear()
    user, created = await sync_to_async(User.objects.get_or_create)(chat_id=str(update.effective_chat.id))
    user.full_name = f"{update.effective_user.first_name} {update.effective_user.last_name or ''}"
    await sync_to_async(user.save)()
    reply_markup = get_language_keyboard()
    await update.message.reply_text('Для русского нажмите "Кнопу" / Pentru română apăsați "Button"',
                                    reply_markup=reply_markup)
    return LANGUAGE


async def handle_reservation_button(update: Update, context: CallbackContext) -> int:
    chat_id = str(update.effective_chat.id)

    # Clear all user data for the specific chat
    if chat_id in user_data:
        user_data.pop(chat_id, None)

    return await start(update, context)


async def language_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    # Clear user data to start fresh
    context.user_data.clear()
    context.user_data['language'] = text
    reply_markup = get_start_keyboard()
    if context.user_data['language'] == 'Русский':
        await update.message.reply_text('Как вас зовут?', reply_markup=reply_markup)
    else:
        await update.message.reply_text('Cum vă numiți?', reply_markup=reply_markup)
    return NAME


async def broadcast_command(update: Update, context: CallbackContext) -> int:
    # Check if the user is authorized
    if str(update.effective_chat.id) == AUTHORIZED_CHAT_ID:
        await update.message.reply_text("Please enter the message to broadcast:")
        return BROADCAST_MESSAGE
    else:
        await update.message.reply_text("You are not authorized to use this command.")
        return ConversationHandler.END


async def broadcast_message(update: Update, context: CallbackContext) -> int:
    broadcast_text = update.message.text
    users = await sync_to_async(list)(User.objects.values_list('chat_id', flat=True))
    for chat_id in users:
        try:
            await context.bot.send_message(chat_id=chat_id, text=broadcast_text)
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
    await update.message.reply_text("Broadcast completed.")
    return ConversationHandler.END


async def name(update: Update, context: CallbackContext) -> int:
    user_name = update.message.text
    context.user_data["name"] = user_name
    user = await sync_to_async(User.objects.get)(chat_id=str(update.effective_chat.id))
    user.full_name = user_name
    await sync_to_async(user.save)()
    reply_markup = get_start_keyboard()
    await update.message.reply_text("Какой у вас номер телефона?" if context.user_data.get('language',
                                                                                           'Русский') == 'Русский' else "Care este numărul dvs de telefon?",
                                    reply_markup=reply_markup)
    return PHONE


async def list_command(update: Update, context: CallbackContext) -> None:
    if str(update.effective_chat.id) == AUTHORIZED_CHAT_ID:
        users = await sync_to_async(list)(User.objects.values_list('chat_id', 'full_name', 'phone', 'is_subscribed'))
        message = '\n'.join([f"Chat ID: {chat_id}, Name: {name}, Phone: {phone}, Subscribed: {is_subscribed}"
                             for chat_id, name, phone, is_subscribed in users])
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("You are not authorized to use this command.")


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

    # Existing conversation handler for the /start command
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("farezervare", handle_reservation_button)],
        states={

            NAME: [MessageHandler(filters.TEXT & ~filters.Regex("^Fa rezervare$"), name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.Regex("^Fa rezervare$"), phone)],
            DATE: [MessageHandler(filters.TEXT & ~filters.Regex("^Fa rezervare$"), date)],
            NUMBER_OF_PEOPLE: [MessageHandler(filters.TEXT & ~filters.Regex("^Fa rezervare$"), number_of_people)],
            LANGUAGE: [MessageHandler(filters.Regex('^(Русский|Română)$'), language_choice)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Handler for the /list command
    list_handler = CommandHandler("list", list_command)

    # Conversation handler for the /broadcast command
    broadcast_handler = ConversationHandler(
        entry_points=[CommandHandler('broadcast', broadcast_command)],
        states={
            BROADCAST_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_message)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Add the new reservation handler
    reservation_handler = MessageHandler(filters.Regex("^Fa rezervare$"), handle_reservation_button)

    # Add all the handlers to the application
    app.add_handler(conv_handler)
    app.add_handler(list_handler)
    app.add_handler(broadcast_handler)
    app.add_handler(reservation_handler)

    app.run_polling()


if __name__ == "__main__":
    main()

import logging
from telegram.ext import Updater, CallbackQueryHandler, CommandHandler, ConversationHandler, Filters, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardRemove
import config
import telegram_utils

TOKEN = config.token
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
INPUT_CUST, DATE_VS, PHOTO_VS, STATE_VS, CONTACT_VS, NOT_CONTACT_VS = range(1, 7)


def date_handler(update, context):
    update.message.reply_text(
        "Masukkan tanggal visit: ",
        reply_markup=telegram_utils.create_calendar()
    )


def fullname(update):
    user = update.callback_query.from_user
    if user.first_name is None and user.last_name:
        return user.last_name
    elif user.last_name is None and user.first_name:
        return user.first_name
    elif user.last_name is None and user.first_name is None:
        return "Anonymous"
    else:
        return user.first_name + " " + user.last_name


def date_callback(update, context):
    selected, date = telegram_utils.process_calendar_selection(update, context)
    if selected:
        context.bot.send_message(
            chat_id=update.callback_query.from_user.id,
            text="Tanggal visit diterima: %s" % (date.strftime("%Y-%m-%d")),
            reply_markup=ReplyKeyboardRemove()
        )
        state_handler(update, context)
        return STATE_VS


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def start(update, context):
    update.message.reply_text(
        "---- Hallo selamat datang di bot visit-ctb telkom ----"
    )
    cust_number(update, context)
    return INPUT_CUST


def cust_number(update, context):
    update.message.reply_text("Masukkan terlebih dahulu Nomor Internet pelanggan: ")


def cust_callback(update, context):
    cust_num = update.message.text
    update.message.reply_text(text="Nomor Internet pelanggan diterima: {}".format(cust_num))
    date_handler(update, context)
    return DATE_VS


def cancel_callback(update, context):
    pass


def photo_handler(update, context):
    pass


def photo_callback(update, context):
    pass


def state_handler(update, context):
    msg = "Silahkan pilih terlebih dahulu status hasil visit"
    keyboard = [[InlineKeyboardButton("Contacted", callback_data="contacted"),
                 InlineKeyboardButton("Not Contacted", callback_data="not_contacted")]]
    keyboard_type_visit = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.callback_query.from_user.id,
        text=msg,
        reply_markup=keyboard_type_visit
    )


def state_callback(update, context):
    query = update.callback_query
    query.edit_message_text(text="Status visit terpilih: {}".format(query.data))


def not_contact_callback(update, context):
    pass


def not_contact_handler(update, context):
    pass


def contact_callback(update, context):
    pass


def contact_handler(update, context):
    pass


if __name__ == "__main__":
    if TOKEN == "":
        print("Token API kosong, tidak dapat menangani bot")
    else:
        up = Updater(TOKEN, use_context=True)
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                INPUT_CUST: [MessageHandler(Filters.regex(r'\d+$'), cust_callback)],
                DATE_VS: [CallbackQueryHandler(date_callback)],
                PHOTO_VS: [MessageHandler(Filters.photo, photo_handler),
                           CommandHandler('photo_input', photo_callback)],
                STATE_VS: [CallbackQueryHandler(state_callback)],
                CONTACT_VS: [MessageHandler(Filters.text, contact_handler),
                             CommandHandler('contact_input', contact_callback)],
                NOT_CONTACT_VS: [MessageHandler(Filters.text, not_contact_handler),
                                 CommandHandler('not_contact_input', not_contact_callback)]
            },
            fallbacks=[CommandHandler('cancel', cancel_callback)]
        )
        up.dispatcher.add_handler(conv_handler)
        up.dispatcher.add_error_handler(error)
        up.start_polling()
        up.idle()

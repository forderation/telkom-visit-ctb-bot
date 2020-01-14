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


def calendar_handler(update, context):
    update.message.reply_text(
        "Masukkan tanggal visit: ",
        reply_markup=telegram_utils.create_calendar()
    )


def calendar_callback(update, context):
    selected, date = telegram_utils.process_calendar_selection(update, context)
    full_name = str(update.callback_query.from_user.first_name) + str(update.callback_query.from_user.last_name)
    if selected:
        context.bot.send_message(
            chat_id=update.callback_query.from_user.id,
            text="Anda %s , Tanggal visit: %s" % (full_name, date.strftime("%Y-%m-%d")),
            reply_markup=ReplyKeyboardRemove()
        )


def choose_type_visit(update, context):
    msg = "Silahkan pilih terlebih dahulu status hasil visit"
    keyboard = [[InlineKeyboardButton("Contacted", callback_data="contacted"),
                 InlineKeyboardButton("Not Contacted", callback_data="not_contacted")]]
    keyboard_type_visit = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(msg, reply_markup=keyboard_type_visit)


def type_visit_keyboard():
    keyboard = [[InlineKeyboardButton("Contacted", callback_data="contacted"),
                 InlineKeyboardButton("Not Contacted", callback_data="not_contacted")]]
    return InlineKeyboardMarkup(keyboard)


def choose_type_visit_callback(update, context):
    query = update.callback_query
    query.edit_message_text(text="Status visit terpilih: {}".format(query.data))


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def start(context, update):
    pass


def cust_number(update, context):
    pass


def input_cust_number(update, context):
    pass


def cancel_callback(update, context):
    pass


def photo_handler(update, context):
    pass


def photo_callback(update, context):
    pass


def state_handler(update, context):
    pass


def state_callback(update, context):
    pass


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
        # up.dispatcher.add_handler(CommandHandler("calendar", calendar_handler))
        # up.dispatcher.add_handler(CallbackQueryHandler(calendar_callback))
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                INPUT_CUST: [MessageHandler(Filters.regex(r'\d+$'), cust_number),
                             CommandHandler('input_cust', input_cust_number)],
                DATE_VS: [MessageHandler(Filters.text, calendar_handler),
                          CommandHandler('date_input', calendar_callback)],
                PHOTO_VS: [MessageHandler(Filters.photo, photo_handler),
                           CommandHandler('photo_input', photo_callback)],
                STATE_VS: [MessageHandler(Filters.text, state_handler),
                           CommandHandler('state_input', state_callback)],
                CONTACT_VS: [MessageHandler(Filters.text, contact_handler),
                             CommandHandler('contact_input', contact_callback)],
                NOT_CONTACT_VS: [MessageHandler(Filters.text, not_contact_handler),
                                 CommandHandler('not_contact_input', not_contact_callback)]
            },
            fallbacks=[CommandHandler('cancel', cancel_callback)]
        )
        up.dispatcher.add_handler(CommandHandler("choose_type_visit", choose_type_visit))
        up.dispatcher.add_handler(CallbackQueryHandler(choose_type_visit_callback))
        up.dispatcher.add_error_handler(error)
        up.start_polling()
        up.idle()

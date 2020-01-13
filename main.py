import logging
from telegram.ext import Updater
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardRemove
import config
import telegramcalendar
TOKEN = config.token
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def calendar_handler(bot, update):
    update.message.reply_text(
        "Masukkan tanggal input: ",
        reply_markup=telegramcalendar.create_calendar()
    )


def calendar_callback(bot, update):
    selected, date = telegramcalendar.process_calendar_selection(bot, update)
    if selected:
        bot.send_message(
            chat_id=update.callback_query.from_user.id,
            text="Tanggal input: %s" % (date.strftime("%d/%m/%Y")),
            reply_markup=ReplyKeyboardRemove()
        )


if __name__ == "__main__":
    if TOKEN == "":
        print("Token API kosong tidak dapat menghandle bot")
    else:
        up = Updater(TOKEN)
        up.dispatcher.add_handler(CommandHandler("calendar", calendar_handler))
        up.dispatcher.add_handler(CallbackQueryHandler(calendar_callback))
        up.start_polling()
        up.idle()

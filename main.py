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
INPUT_CUST, DATE_VS, PHOTO_VS, STATE_VS, CONTACT_VS, NOT_CONTACT_VS, OTHER_DESC, CONFIRM, ADD_CONFIRM = range(1, 10)
option_contacted = ["kemahalan", "tagihan melonjak", "jarang dipakai", "kendala keuangan", "lupa bayar",
                    "pindah ke kompetitor", "sudah ada internet lain", "tidak sempat bayar (sibuk)",
                    "tidak tahu tagihan", "lambat", "putus", "tidak bisa browsing / GGN",
                    "gangguan belum terselesaikan", "internet belum aktif", "tidak merasa pasang"]
data_recap = {
    "nip": "",
    "date": "",
    "state": "",
    "voc": "",
    "other": "",
    "photo": ""
}


def date_handler(update, context):
    update.message.reply_text(
        text="Masukkan tanggal visit: ",
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
        date = date.strftime("%Y-%m-%d")
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Tanggal visit : %s" % date,
            reply_markup=ReplyKeyboardRemove()
        )
        data_recap["date"] = date
        state_handler(update, context)
        return STATE_VS


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
    update.message.reply_text(text="Nomor Internet pelanggan : {}".format(cust_num))
    data_recap["nip"] = cust_num
    date_handler(update, context)
    return DATE_VS


def cancel_callback(update, context):
    update.message.reply_text(text="Sesi input visit CTB Berakhir, Tekan /start untuk mulai kembali")
    return ConversationHandler.END


def photo_handler(update, context):
    pass


def photo_callback(update, context):
    pass


def state_handler(update, context):
    msg = "Silahkan pilih terlebih dahulu status hasil visit :"
    keyboard = [[InlineKeyboardButton("contacted", callback_data="contacted"),
                 InlineKeyboardButton("not contacted", callback_data="not_contacted")]]
    keyboard_type_visit = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.callback_query.from_user.id,
        text=msg,
        reply_markup=keyboard_type_visit
    )


def state_callback(update, context):
    query = update.callback_query
    state = query.data
    query.edit_message_text(text="Status visit : {}".format(state))
    data_recap['state'] = state
    if state == "contacted":
        contact_handler(update, context)
        return CONTACT_VS
    elif state == "not_contacted":
        not_contact_handler(update, context)
        return NOT_CONTACT_VS


def not_contact_callback(update, context):
    pass


def not_contact_handler(update, context):
    pass


def contact_callback(update, context):
    query = update.callback_query
    report_visit = query.data
    query.edit_message_text(text="Hasil laporan visit : {}".format(report_visit))
    data_recap['voc'] = report_visit
    other_handler(update, context)
    return OTHER_DESC


def contact_handler(update, context):
    msg = "Pilih hasil laporan visit :"
    keyboard = [
        [InlineKeyboardButton(value, callback_data=value)] for value in option_contacted
    ]
    keyboard_type_visit = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.callback_query.from_user.id,
        text=msg,
        reply_markup=keyboard_type_visit
    )


def fallback_handler(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    update.message.reply_text(text="Error: Perintah tidak dikenali")


def confirm_handler(update, context):
    recap_data = """
    ----- rekap data input -----
    nomor internet pelanggan : {} 
    tanggal kunjungan : {}
    hasil visit (VOC) ctb : {}
    keterangan lain-lain : {}
    foto kunjungan : {}
    """.format(
        data_recap["nip"],
        data_recap["date"],
        data_recap["voc"],
        data_recap["other"],
        data_recap["photo"]
    )
    msg = "Apakah data yang anda isi sudah benar ? \n{}".format(recap_data)
    keyboard = [[InlineKeyboardButton("salah", callback_data="salah"),
                 InlineKeyboardButton("benar", callback_data="benar")]]
    keyboard_type_visit = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        reply_markup=keyboard_type_visit
    )


def confirm_callback(update, context):
    query = update.callback_query
    state = query.data
    query.edit_message_text(text="Hasil konfirmasi: {}".format(state))
    if state == "benar":
        context.bot.send_message(
            chat_id=update.callback_query.from_user.id,
            text="Data visit berhasil disimpan",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    elif state == "salah":
        # TODO
        pass


def other_handler(update, context):
    msg = "Apakah ada informasi yang ingin ditambahkan (keterangan lain): ?"
    keyboard = [[InlineKeyboardButton("tidak ada", callback_data="tidak ada"),
                 InlineKeyboardButton("ya", callback_data="ya")]]
    keyboard_type_visit = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.callback_query.from_user.id,
        text=msg,
        reply_markup=keyboard_type_visit
    )


def confirm_other_callback(update, context):
    query = update.callback_query
    state = query.data
    query.edit_message_text(text="Keterangan lain-lain : {}".format(state))
    if state == "ya":
        add_other_handler(update, context)
        return ADD_CONFIRM
    elif state == "tidak ada":
        confirm_handler(update, context)
        return CONFIRM


def add_other_handler(update, context):
    msg = "Masukkan keterangan lain-lain: "
    context.bot.send_message(
        chat_id=update.callback_query.from_user.id,
        text=msg
    )


def add_other_callback(update, context):
    other_desc = update.message.text
    update.message.reply_text(text="Keterangan lain-lain : {}".format(other_desc))
    data_recap['other'] = other_desc
    confirm_handler(update, context)
    return CONFIRM


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
                CONTACT_VS: [CallbackQueryHandler(contact_callback)],
                NOT_CONTACT_VS: [CallbackQueryHandler(not_contact_callback)],
                OTHER_DESC: [CallbackQueryHandler(confirm_other_callback)],
                ADD_CONFIRM: [MessageHandler(Filters.text, add_other_callback)],
                CONFIRM: [CallbackQueryHandler(confirm_callback)]
            },
            fallbacks=[CommandHandler('cancel', cancel_callback),
                       MessageHandler(Filters.all, fallback_handler)]
        )
        up.dispatcher.add_handler(conv_handler)
        up.dispatcher.add_error_handler(fallback_handler)
        up.start_polling()
        up.idle()

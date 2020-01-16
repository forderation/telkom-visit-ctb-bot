import logging
from telegram.ext import Updater, CallbackQueryHandler, CommandHandler, ConversationHandler, Filters, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardRemove, ReplyMarkup
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
option_not_contacted = ["alamat tidak ada", "bukan pelanggan yang bersangkutan", "tidak bertemu penghuni",
                        "rumah tidak berpenghuni"]
kode_cn = """<pre>
KODE | KETERANGAN CONTACTED
--------------------------------
A.C.1 | Jarang dipakai
A.C.2 | Kendala Keuangan
A.C.3 | Lupa Bayar
A.C.4 | Pindah ke kompetitor
A.C.5 | Sudah ada internet lain
A.C.6 | Sudah bayar
A.C.7 | Tidak sempat bayar sibuk
A.C.8 | Tidak tahu tagihan
A.PC.1 | Kemahalan
A.PC.2 | Tagihan melonjak
A.PD.1 | Product
A.PD.2 | Putus
A.PD.3 | Tidak bisa browsing/GGN
A.S.1 | Gangguan belum diselesaikan
A.S.1 | Internet belum aktif
A.S.1 | Tidak merasa pasang
</pre>"""
kode_nc = """<pre>
KODE | KETERANGAN NOT CONTACTED
------------------------------------
B.1	 |	Alamat tidak ada
B.2	 |	Bukan pelanggan yang tersedia
B.3	 |	Tidak bertemu penghuni
B.4	 |	Rumah tidak berpenghuni
</pre>
"""
data_recap = {
    "nip": "",
    "date": "",
    "state": "",
    "voc": "",
    "other": "",
    "photo": ""
}


def date_handler(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
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
        query = update.callback_query
        query.edit_message_text(text="Tanggal visit : %s" % date)
        data_recap["date"] = date
        state_handler(update, context)
        return STATE_VS


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=kode_cn,
        reply_markup=ReplyKeyboardRemove()
    )
    cust_number(update, context)
    return INPUT_CUST


def cust_number(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Masukkan terlebih dahulu Nomor Internet pelanggan: "
    )


def cust_callback(update, context):
    cust_num = update.message.text
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Nomor Internet pelanggan : {}".format(cust_num)
    )
    data_recap["nip"] = cust_num
    date_handler(update, context)
    return DATE_VS


def cancel_callback(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sesi input visit CTB Berakhir, Tekan /start untuk mulai kembali"
    )
    return ConversationHandler.END


def photo_handler(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Silahkan upload foto bukti visit : "
    )
    return PHOTO_VS


def photo_callback(update, context):
    photo_file = update.message.photo[-1].get_file()
    # print(update.effective_message)
    photo_file.download('user_photo.jpg')
    photo_id = update.message.photo[-1].file_id
    photo_path = context.bot.get_file(photo_id).file_path
    photo_uri_get = photo_path.split("/")
    data_recap["photo"] = photo_uri_get[-2] + "/" + photo_uri_get[-1]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Upload foto diterima : "
    )
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=photo_id
    )
    confirm_handler(update, context)
    return CONFIRM


def state_handler(update, context):
    msg = "Silahkan pilih terlebih dahulu status hasil visit :"
    keyboard = [[InlineKeyboardButton("not contacted", callback_data="not_contacted"),
                 InlineKeyboardButton("contacted", callback_data="contacted")]]
    keyboard_type_visit = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
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
    msg = "Pilih hasil laporan visit (not contacted):"
    keyboard = [
        [InlineKeyboardButton(value, callback_data=value)] for value in option_contacted
    ]
    keyboard_type_visit = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        reply_markup=keyboard_type_visit
    )


def contact_callback(update, context):
    query = update.callback_query
    report_visit = query.data
    query.edit_message_text(text="Hasil laporan visit : {}".format(report_visit))
    data_recap['voc'] = report_visit
    other_handler(update, context)
    return OTHER_DESC


def contact_handler(update, context):
    msg = "Pilih hasil laporan visit (contacted):"
    keyboard = [
        [InlineKeyboardButton(value, callback_data=value)] for value in option_contacted
    ]
    keyboard_type_visit = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        reply_markup=keyboard_type_visit
    )


def fallback_handler(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Error: Perintah tidak dikenali : %s" % context.error
    )


def confirm_handler(update, context):
    recap_data = "----- rekap data input -----" \
                 "\nnomor internet pelanggan : {}" \
                 "\ntanggal kunjungan : {}" \
                 "\nhasil visit (VOC) ctb : {}" \
                 "\nketerangan lain-lain : {}" \
                 "\nfoto kunjungan : {}".format(data_recap["nip"], data_recap["date"], data_recap["voc"],
                                                data_recap["other"], data_recap["photo"])
    msg = "Apakah data yang anda isi sudah benar ? \n{}".format(recap_data)
    keyboard = [[InlineKeyboardButton("salah (input ulang)", callback_data="salah"),
                 InlineKeyboardButton("benar", callback_data="benar")]]
    keyboard_type_visit = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        reply_markup=keyboard_type_visit
    )


def confirm_callback(update, context):
    query = update.callback_query
    msg_from_bot = update.callback_query.message.text
    state = query.data
    query.edit_message_text(msg_from_bot + "\nKonfirmasi : %s" % query.data)
    if state == "benar":
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Data visit berhasil disimpan" +
                 "\n--- Sesi input data berakhir tekan /start untuk memulai input data kembali ---",
        )
        return ConversationHandler.END
    elif state == "salah":
        start(update, context)
        return INPUT_CUST


def other_handler(update, context):
    msg = "Apakah ada informasi yang ingin ditambahkan (keterangan lain): ?"
    keyboard = [[InlineKeyboardButton("tidak ada", callback_data="tidak ada"),
                 InlineKeyboardButton("ya", callback_data="ya")]]
    keyboard_type_visit = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
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
        chat_id=update.effective_chat.id,
        text=msg
    )


def add_other_callback(update, context):
    other_desc = update.message.text
    data_recap['other'] = other_desc
    photo_handler(update, context)
    return PHOTO_VS


def kode_contact(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=kode_cn,
        parse_mode="HTML"
    )


def kode_not_contact(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=kode_nc,
        parse_mode="HTML"
    )


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
                PHOTO_VS: [MessageHandler(Filters.photo, photo_callback)],
                STATE_VS: [CallbackQueryHandler(state_callback)],
                CONTACT_VS: [CallbackQueryHandler(contact_callback)],
                NOT_CONTACT_VS: [CallbackQueryHandler(not_contact_callback)],
                OTHER_DESC: [CallbackQueryHandler(confirm_other_callback)],
                ADD_CONFIRM: [MessageHandler(Filters.text, add_other_callback)],
                CONFIRM: [CallbackQueryHandler(confirm_callback)]
            },
            fallbacks=[CommandHandler('cancel', cancel_callback),
                       MessageHandler(Filters.all, fallback_handler)],
            allow_reentry=True
        )
        up.dispatcher.add_handler(conv_handler)
        up.dispatcher.add_error_handler(fallback_handler)
        up.dispatcher.add_handler(CommandHandler('code_ct', kode_contact))
        up.dispatcher.add_handler(CommandHandler('code_nct', kode_not_contact))
        up.start_polling()
        up.idle()

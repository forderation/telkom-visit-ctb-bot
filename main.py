import logging
import os

from telegram.ext import Updater, CallbackQueryHandler, CommandHandler, ConversationHandler, Filters, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardRemove
import datetime
import config
import telegram_utils

TOKEN = config.token
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
INPUT_VISIT, PHOTO_VISIT, CONFIRM_VISIT = range(1, 4)
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
A.PD.1 | Lambat
A.PD.2 | Putus
A.PD.3 | Tidak bisa browsing/GGN
A.S.1 | Gangguan belum diselesaikan
A.S.2 | Internet belum aktif
A.S.3 | Tidak merasa pasang
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
    "fullname": "",
    "nip": "",
    "date": "",
    "state": "",
    "voc_code": "",
    "result_voc": "",
    "other": "",
    "photo": []
}


def fullname(update):
    user = update.message.from_user
    if user.first_name is None and user.last_name:
        return user.last_name
    elif user.last_name is None and user.first_name:
        return user.first_name
    elif user.last_name is None and user.first_name is None:
        return "user not defined"
    else:
        return user.first_name + " " + user.last_name


def cancel_callback(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sesi input visit CTB berakhir, tekan /input_visit untuk mengisi data visit kembali"
    )
    return ConversationHandler.END


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


def fallback_handler(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Error: Perintah tidak dikenali : %s" % context.error
    )


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


def start_handler(update, context):
    pass


def submit_photo(update, context):
    user_id = str(update.message.from_user.id)
    cur_dir = os.getcwd()
    user_path = cur_dir + "/res/img/" + user_id
    if not (os.path.exists(user_path)):
        os.makedirs(user_path, 0o777)
    for photo_id in data_recap["photo"]:
        context.bot.get_file(photo_id).download(user_path + "/" + photo_id + ".jpg")
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Submit foto berhasil @" + str(update.message.from_user.username)
    )
    return ConversationHandler.END


def photo_visit_callback(update, context):
    photo_id = update.message.photo[-1].file_id
    data_recap["photo"].append(photo_id)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Upload foto diterima : " + photo_id
    )


def photo_visit_handler(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Silahkan upload bukti foto visit: "
    )


def msg_error(msg, update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg
    )


def input_visit_callback(update, context):
    resp = update.message.text.split(";")
    if len(resp) == 3:
        try:
            ip_cust = int(resp[0])
        except ValueError:
            msgerr = "nomor internet pelanggan tidak kenali pastikan pada kolom awal nilainya angka"
            msg_error(msgerr, update, context)
            return
        visit_code = str(resp[1].strip())
        if not (visit_code in config.option_ct or visit_code in config.option_nct):
            msgerr = "kode visit tidak dikenali. silahkan lihat pada menu /code_ct jika contacted," \
                     " menu /code_nct jika not contacted"
            msg_error(msgerr, update, context)
            return
        if visit_code in config.option_ct:
            state_vs = "contacted"
            mapped_vs = config.map_ct[visit_code]
        else:
            state_vs = "not contacted"
            mapped_vs = config.map_nct[visit_code]
        date_now = datetime.datetime.today()
        date_vs = "{}-{}-{}".format(date_now.day, date_now.month, date_now.year)
        other_vs = resp[2].strip() if resp[2] else "kosong"
        msg_resp = "----- input data diterima -----" \
                   "\nnomor internet pelanggan: {}" \
                   "\ntanggal: {}" \
                   "\nstatus visit: {}" \
                   "\nkode visit: {}" \
                   "\nhasil visit: {}" \
                   "\nketerangan lain-lain: {}".format(ip_cust, date_vs, state_vs, visit_code, mapped_vs, other_vs)
        data_recap["fullname"] = fullname(update)
        data_recap["nip"] = str(ip_cust)
        data_recap["date"] = "{}-{}-{}".format(date_now.year, date_now.month, date_now.day)
        data_recap["voc_code"] = visit_code
        data_recap["state"] = state_vs
        data_recap["result_voc"] = mapped_vs
        data_recap["other"] = other_vs
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg_resp
        )
        photo_visit_handler(update, context)
        return PHOTO_VISIT
    else:
        msg_error("format input salah, pastikan karakter ; berjumlah 2", update, context)


def input_visit(update, context):
    msg = 'Silahkan input dalam bentuk format "nomor internet pelanggan;kode hasil voc;keterangan lain-lain".' \
          'pastikan karakter ; berjumlah 2.'
    exam = "\nContoh: 152504308719; A.PD.3; rumah tutup yns kerja semua cp08191341232"
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg + exam
    )
    return INPUT_VISIT


def confirm_callback(update, context):
    pass


if __name__ == "__main__":
    if TOKEN == "":
        print("Token API kosong, tidak dapat menangani bot")
    else:
        up = Updater(TOKEN, use_context=True)
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('input_visit', input_visit)],
            states={
                INPUT_VISIT: [MessageHandler(Filters.text, input_visit_callback)],
                PHOTO_VISIT: [MessageHandler(Filters.photo, photo_visit_callback),
                              CommandHandler('submit_photo', submit_photo)]
            },
            fallbacks=[CommandHandler('cancel_visit', cancel_callback),
                       CommandHandler('code_ct', kode_contact),
                       CommandHandler('code_nct', kode_not_contact),
                       MessageHandler(Filters.all, fallback_handler)],
            allow_reentry=True
        )
        up.dispatcher.add_handler(conv_handler)
        up.dispatcher.add_error_handler(fallback_handler)
        up.dispatcher.add_handler(CommandHandler('start', start_handler))
        up.dispatcher.add_handler(CommandHandler('code_ct', kode_contact))
        up.dispatcher.add_handler(CommandHandler('code_nct', kode_not_contact))
        up.start_polling()
        up.idle()

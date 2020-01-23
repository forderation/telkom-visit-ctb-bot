import datetime
import logging
import os
import pandas as pd

from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, ConversationHandler
from database import DBHelper
import config
from session_chat import Session

# command list
# input_visit - memulai sesi input data visit
# submit_visit - submit data visit ke bot
# help - lihat contoh penggunaan bot
# cancel - membatalkan sesi input visit
# code_ct - daftar kode untuk status contacted
# code_nct - daftar kode untuk status not contacted
# get_csv - mendapatkan laporan visit dalam bentuk csv
# case conversation handler admin
PASSWD_ADMIN = 1
db = DBHelper()
session = Session()
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
    user_id = str(update.message.from_user.id)
    username = update.message.from_user.username
    if session.is_user_active(user_id):
        msg_resp = "Anda belum pernah menginput data visit"
    else:
        session.remove_user(user_id)
        msg_resp = "Berhasil membatalkan input data visit"
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="@{} {}".format(username, msg_resp)
    )


# def photo_callback(update, context):
#     photo_file = update.message.photo[-1].get_file()
#     # print(update.effective_message)
#     photo_file.download('user_photo.jpg')
#     photo_id = update.message.photo[-1].file_id
#     photo_path = context.bot.get_file(photo_id).file_path
#     photo_uri_get = photo_path.split("/")
#     context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text="Upload foto diterima : "
#     )
#     context.bot.send_photo(
#         chat_id=update.effective_chat.id,
#         photo=photo_id
#     )


def fallback_handler(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


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
    msg = "Silahkan input dalam bentuk format \"/input_visit nomor internet pelanggan;kode hasil voc;keterangan " \
          "lain-lain\"." \
          "pastikan karakter ; berjumlah 2."
    exam = "\nContoh: /input_visit 152504308719; A.PD.3; rumah tutup yns kerja semua cp08191341232"
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg + exam
    )


def photo_visit_callback(update, context):
    user_id = str(update.message.from_user.id)
    if session.is_user_active(user_id):
        if session.is_visited(user_id):
            photo_id = update.message.photo[-1].file_id
            session.add_photo(user_id, photo_id)


def msg_error(msg, update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg
    )


def input_visit_callback(update, context):
    resp = update.message.text.replace('/input_visit', '').replace('@telkom_visit_ctb_bot', '').split(";")
    user_id = str(update.message.from_user.id)
    username = update.message.from_user.username
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
        if session.is_user_active(user_id):
            msg_resp = "@{} sesi input visit anda sudah ada silahkan submit terlebih dahulu".format(username)
        else:
            date = "{}-{}-{}".format(date_now.year, date_now.month, date_now.day)
            other_vs = resp[2].strip() if resp[2] else "kosong"
            session.add_user(user_id, fullname(update), str(ip_cust), date, visit_code, state_vs, mapped_vs, other_vs)
            msg_resp = "@{} input visit diterima:\n{}".format(username, session.get_desc_user(user_id))
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg_resp
        )
    else:
        msg_error("@{} format input salah, pastikan karakter ; \"titik koma\" berjumlah 2".format(username), update,
                  context)


def submit_visit(update, context):
    username = update.message.from_user.username
    user_id = str(update.message.from_user.id)
    if not (session.is_user_active(user_id)):
        msg_resp = "Anda belum menginput data visit"
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="@{} {}".format(username, msg_resp)
        )
        return
    if not (session.is_submitted_photo(user_id)):
        msg_resp = "Anda belum mengupload bukti foto visit"
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="@{} {}".format(username, msg_resp)
        )
        return
    cur_dir = os.getcwd()
    user_path = cur_dir + "/res/img/" + user_id
    if not (os.path.exists(user_path)):
        os.makedirs(user_path, 0o777)
    for photo_id in session.get_photo(user_id):
        context.bot.get_file(photo_id).download(user_path + "/" + photo_id + ".jpg")
    visit_id = db.add_visit(session.get_session(user_id))
    db.add_photo(session.get_photo(user_id), user_id, visit_id)
    session.remove_user(user_id)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Submit data berhasil @" + username
    )
    print(db.get_photo())


def get_csv(update, context):
    visits = db.get_visit()
    df = pd.DataFrame(
        visits,
        columns=["id", "nama visitor", "tanggal visit", "nomor internet pelanggan", "status visit",
                 "hasil visit", "kode visit", "keterangan lain-lain"]
    )
    df.to_csv("report.csv", index=False)
    context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=open("report.csv", 'rb'),
        filename="laporan.csv"
    )


def login_admin(update, context):
    passwd = update.message.text
    respd = db.check_password(passwd)
    if respd is None:
        msg_resp = "Password anda salah"
    else:
        msg_resp = "Login berhasil"
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg_resp
    )


def admin_start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Masukkan password admin : "
    )
    return PASSWD_ADMIN


def admin_logout(update, context):
    pass


if __name__ == "__main__":
    if TOKEN == "":
        print("Token API kosong, tidak dapat menangani bot")
    else:
        print("Doing setup database ...")
        db.setup()
        db.seeder_password()
        print("Setup database done")
        print("Connecting to telegram server ...")
        up = Updater(TOKEN, use_context=True)
        print("Connected to telegram server")
        print("Making conversation ...")
        conv = ConversationHandler(
            entry_points=[CommandHandler('start_adm1n', admin_start)],
            allow_reentry=True,
            fallbacks=[CommandHandler('end_adm1n', admin_logout)],
            states={
                PASSWD_ADMIN: [MessageHandler(Filters.text, login_admin)]
            }
        )
        up.dispatcher.add_handler(conv)
        up.dispatcher.add_error_handler(fallback_handler)
        up.dispatcher.add_handler(CommandHandler('start', start_handler))
        up.dispatcher.add_handler(CommandHandler('help', start_handler))
        up.dispatcher.add_handler(MessageHandler(Filters.photo, photo_visit_callback))
        up.dispatcher.add_handler(CommandHandler('cancel', cancel_callback))
        up.dispatcher.add_handler(CommandHandler('input_visit', input_visit_callback))
        up.dispatcher.add_handler(CommandHandler('submit_visit', submit_visit))
        up.dispatcher.add_handler(CommandHandler('get_csv', get_csv))
        up.dispatcher.add_handler(CommandHandler('code_ct', kode_contact))
        up.dispatcher.add_handler(CommandHandler('code_nct', kode_not_contact))
        print("Making conversation done")
        up.start_polling()
        print("Chatbot already to use")
        up.idle()

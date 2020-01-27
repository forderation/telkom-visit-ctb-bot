import datetime
import logging
import os

import pandas as pd
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, replymarkup
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, ConversationHandler, CallbackQueryHandler

import config
from config import num_keyboard
from database import DBHelper
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
PASSWD_ADMIN, MENU_ADMIN = range(1, 3)
db = DBHelper()
session = Session()
TOKEN = config.token
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
pin_admin = ""
admin_msg_id = 0
admin_chat_id = 0
code_msg_id = 0
code_chat_id = 0


def pin_handler(update, context):
    global pin_admin
    msg_bot = ""
    resp_data = str(update.callback_query.data)
    if resp_data == "cancel":
        context.bot.edit_message_text(
            chat_id=admin_chat_id,
            message_id=admin_msg_id,
            text="Login dibatalkan"
        )
        return ConversationHandler.END
    if resp_data != "clear" and resp_data != "submit":
        pin_admin += resp_data
        msg_bot = len(pin_admin) * "*"
    if resp_data == "clear":
        pin_admin = ""
        msg_bot = "-"
    if resp_data == "submit":
        username = update.callback_query.from_user.username
        resp_pin = db.check_admin_password(pin_admin, username)
        if resp_pin:
            context.bot.edit_message_text(
                chat_id=admin_chat_id,
                message_id=admin_msg_id,
                text="Password benar, anda sudah login"
            )
            return MENU_ADMIN
        else:
            msg_bot = "Password salah"
            pin_admin = ""
    context.bot.edit_message_text(
        chat_id=admin_chat_id,
        message_id=admin_msg_id,
        text=msg_bot,
        reply_markup=InlineKeyboardMarkup(num_keyboard)
    )


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
        session.remove_user(user_id)
        msg_resp = "Berhasil membatalkan input data visit"
    else:
        msg_resp = "Anda belum pernah menginput data visit"
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="@{} {}".format(username, msg_resp)
    )


def fallback_handler(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def report_code(update, context):
    state_menu = []
    for key, value in db.get_state():
        state_menu.append([InlineKeyboardButton(str(value), callback_data=str(key))])
    message = context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Kategori Kode: ",
        reply_markup=InlineKeyboardMarkup(state_menu)
    )
    global admin_msg_id
    global admin_chat_id
    admin_msg_id = message.message_id
    admin_chat_id = message.chat_id


def callback_code(update, context):
    resp_code = update.callback_query.data
    menu_code = "deskripsi - kode visit\n"
    menu_code += len(menu_code) * "-"
    for desc, f, m, r in db.get_detail_code(resp_code):
        menu_code += "\n{} - {}".format(desc, f + m + r)
    context.bot.edit_message_text(
        chat_id=admin_chat_id,
        message_id=admin_msg_id,
        text=menu_code
    )


def start_handler(update, context):
    msg = "Silahkan input dalam bentuk format \"/input_visit nomor internet pelanggan;kode hasil voc;keterangan " \
          "lain-lain\"." \
          "pastikan karakter ; berjumlah 2."
    exam = "\nContoh: /input_visit 152504308719; APD3; rumah tutup yns kerja semua cp08191341232"
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg + exam
    )


def photo_visit_callback(update, context):
    user_id = str(update.message.from_user.id)
    if session.is_user_active(user_id):
        if session.is_visited(user_id):
            photo_id = update.message.photo[-1].file_id
            photo_path = context.bot.get_file(photo_id).file_path
            session.add_photo(user_id, photo_path)


def msg_error(msg, update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg
    )


def input_visit_callback(update, context):
    resp = update.message.text.replace('/input_visit', '').replace('@telkom_visit_ctb_bot', '').split(";")
    user_id = str(update.message.from_user.id)
    username = update.message.from_user.username
    if session.is_user_active(user_id):
        msg_error(
            "@{} sesi input visit anda sudah ada silahkan submit terlebih dahulu".format(username), update, context
        )
        return
    if len(resp) == 3:
        try:
            ip_cust = int(resp[0])
        except ValueError:
            msgerr = "nomor internet pelanggan tidak kenali pastikan pada kolom awal nilainya angka"
            msg_error(msgerr, update, context)
            return
        visit_code = str(resp[1].strip())
        option_code = []
        for f, m, r, idr, ids, idc, state, category, result in db.get_all_code():
            option_code.append([f + m + r] + [[f, m, r]] + [[ids, idc, idr]] + [[state, category, result]])
        menu_code = [x[0] for x in option_code]
        if not (visit_code in menu_code):
            msgerr = "kode visit tidak dikenali. silahkan lihat pada menu /report_code ,"
            msg_error(msgerr, update, context)
            return
        idx_code = menu_code.index(visit_code)
        date_now = datetime.datetime.today()
        idx_visit_code = option_code[idx_code][2]
        caption = option_code[idx_code][3]
        date = "{}-{}-{}".format(date_now.year, date_now.month, date_now.day)
        other_vs = resp[2].strip() if resp[2] else "kosong"
        session.add_user(
            user_id, fullname(update), str(ip_cust), date, visit_code, caption[0], caption[1], caption[2], other_vs,
            idx_visit_code
        )
        msg_resp = "@{} input visit diterima:\n{}".format(username, session.get_desc_user(user_id))
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg_resp
        )
    else:
        msg_error(
            "@{} format input salah, pastikan karakter ; \"titik koma\" berjumlah 2".format(username),
            update,
            context
        )


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
    db.sync_user_input(user_id, fullname(update), username)
    id_visit = db.add_visit(user_id, session.get_session(user_id))
    db.add_photo(user_id, id_visit, session.get_session(user_id)["photo"])
    session.remove_user(user_id)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Submit data berhasil @" + username
    )


def save_photo_local(context, user_id):
    cur_dir = os.getcwd()
    user_path = cur_dir + "/res/img/" + user_id
    if not (os.path.exists(user_path)):
        os.makedirs(user_path, 0o777)
    for photo_id in session.get_photo(user_id):
        context.bot.get_file(photo_id).download(user_path + "/" + photo_id + ".jpg")


def get_report(update, context):
    visits, photos = db.get_report()
    df = pd.DataFrame(
        visits,
        columns=["tanggal visit", "nomor internet pelanggan", "kode visit", "keterangan lain-lain", "nama visitor",
                 "status visit", "kategori visit", "hasil visit"]
    )
    df["bukti foto visit"] = pd.Series(photos)
    df["bukti foto visit"] = df["bukti foto visit"].apply(
        lambda x: str(x).replace("[", "").replace("]", "").replace("'", ""))
    print(df.head(10))
    df.to_excel("report.xlsx", index=False)
    context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=open("report.xlsx", 'rb'),
        filename="laporan visit.xlsx"
    )


def admin_start(update, context):
    global admin_msg_id, admin_chat_id
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Masukkan pin admin : "
    )
    message = context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="-",
        reply_markup=InlineKeyboardMarkup(num_keyboard)
    )
    admin_msg_id = message.message_id
    admin_chat_id = message.chat_id
    return PASSWD_ADMIN


def admin_logout(update, context):
    return ConversationHandler.END


if __name__ == "__main__":
    if TOKEN == "":
        print("Token API kosong, tidak dapat menangani bot")
    else:
        print("Connecting to telegram server ...")
        up = Updater(TOKEN, use_context=True)
        print("Connected to telegram server")
        print("Making conversation ...")
        conv = ConversationHandler(
            entry_points=[CommandHandler('start_adm1n', admin_start)],
            allow_reentry=True,
            fallbacks=[CommandHandler('end_adm1n', admin_logout)],
            states={
                PASSWD_ADMIN: [CallbackQueryHandler(pin_handler)]
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
        up.dispatcher.add_handler(CommandHandler('report_code', report_code))
        up.dispatcher.add_handler(CommandHandler('pin_admin', pin_handler))
        up.dispatcher.add_handler(CallbackQueryHandler(callback_code))
        print("Making conversation done")
        up.start_polling()
        print("Chatbot already to use")
        up.idle()

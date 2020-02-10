import logging
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, InputMediaPhoto, ChatAction
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, ConversationHandler, CallbackQueryHandler
import config
import token_telegram as tk
from config import num_keyboard, sv_header, cr_header, rv_header
from database import DBHelper
from session_chat import Session
from datetime import datetime
import telegram_utils

# command list
# input_visit - memulai sesi input data visit
# submit_visit - submit data visit ke bot
# code_csv - mengunduh list kode visit (file csv)
# todo_list - input list pelanggan yang akan divisit
# help_todo_list - lihat cara penggunaan todo list
# help - lihat contoh penggunaan bot
# cancel - membatalkan sesi input visit
# start_adm1n - masuk ke dalam sesi admin
# start - mulai chat bot
# case conversation handler admin

PASSWD_ADMIN, EDIT_RV_ADMIN, ADD_RV, UDPATE_NAME_RV, UPDATE_CODE_RV, REMOVE_RV, RENAME_RV, RECODE_RV, \
CATEGORY_RESULT_ADMIN, VISIT_RESULT_ADMIN, MENU_ADMIN, PIN_CHANGE, NEW_PIN, LAPORAN_ADMIN, \
EDIT_CR_ADMIN, VISIT_MENU_ADMIN, ADD_CR, RENAME_CR, RECODE_CR, REMOVE_CR, ADD_SV, RENAME_SV, RECODE_SV, \
REMOVE_SV, EDIT_SV_ADMIN, DATE_LAST, DATE_SELECTED, ADMIN_CHOOSE_OPSI, INPUT_USERID = range(1, 30)

db = DBHelper()
session = Session()
TOKEN = tk.token
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
state_rv = -1
state_cv = -1
pin_admin = ""
admin_msg_id = 0
admin_chat_id = 0
code_msg_id = 0
code_chat_id = 0
entry_msg_id = 0
entry_chat_id = 0
lpr_date_start = ""
lpr_date_end = ""
lpr_date_photo = ""
download_option = ""
RIWAYAT_OPT = "LAPORAN_RIWAYAT_SUBMIT_OPT"
VISITOR_OPT = "LIST_VISITOR_OPT"
LVS_OPT = "LAPORAN_VISITOR_SUBMIT_OPT"
VS_PHOTO_OPT = "VISITOR_PHOTO_OPT"
VS_STATISTIK = "STATISTIK_SUBMIT_OPT"


def pin_handler(update, context):
    global pin_admin
    msg_bot = ""
    resp_data = str(update.callback_query.data)
    bot = context.bot
    if resp_data == "cancel":
        bot.edit_message_text(
            chat_id=admin_chat_id,
            message_id=admin_msg_id,
            text="login dibatalkan"
        )
        bot.delete_message(
            chat_id=entry_chat_id,
            message_id=entry_msg_id
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
            bot.edit_message_text(
                chat_id=admin_chat_id,
                message_id=admin_msg_id,
                text="pin benar, anda sudah login"
            )
            bot.delete_message(
                chat_id=entry_chat_id,
                message_id=entry_msg_id
            )
            pin_admin = ""
            admin_menu_handler(update, context)
            return MENU_ADMIN
        else:
            msg_bot = "pin salah"
            pin_admin = ""
    bot.edit_message_text(
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
    for key, value, code in db.get_state():
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


def help_todo_list(update, context):
    msg = "Silahkan input dalam bentuk format /todo_list list nomor internet pelanggan, pastikan dalam bentuk angka semua"
    exam = """\nContoh: /todo_list 152504308719
152504302224
152504303748
152504307600
152504305667
152504303067
    """
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
            msgerr = "kode visit tidak dikenali. silahkan lihat pada menu /code_csv ,"
            msg_error(msgerr, update, context)
            return
        idx_code = menu_code.index(visit_code)
        date_now = datetime.today()
        date = "{}-{}-{}".format(date_now.year, date_now.month, date_now.day)
        idx_visit_code = option_code[idx_code][2]
        caption = option_code[idx_code][3]
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
    # save photo to local data base
    cur_dir = os.getcwd()
    user_path = cur_dir + "/res/img/" + str(datetime.today().strftime('%Y-%m-%d')) + "/" + user_id
    if not (os.path.exists(user_path)):
        os.makedirs(user_path, 0o777)
    photo_paths = []
    for photo_id in session.get_photo(user_id):
        photo_path = user_path + "/" + photo_id + ".jpg"
        context.bot.get_file(photo_id).download(photo_path)
        photo_paths.append(photo_path)
    # add user to total submit if exist else create new user data
    db.increment_submit(user_id, fullname(update), username)
    id_visit = db.insert_visit(user_id, session.get_session(user_id))
    db.insert_photo(user_id, id_visit, photo_paths)
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


def get_report_hist(update, context, ds=None, de=None):
    visits, photos = db.get_report_hist(ds, de)
    df = pd.DataFrame(
        visits,
        columns=["tanggal visit", "nomor internet pelanggan", "kode visit", "keterangan lain-lain", "nama visitor",
                 "status visit", "kategori visit", "hasil visit"]
    )
    df["bukti foto visit"] = pd.Series(photos)
    df["bukti foto visit"] = df["bukti foto visit"].apply(
        lambda x: str(x).replace("[", "").replace("]", "").replace("'", ""))
    df.to_excel("report.xlsx", index=False)
    context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=open("report.xlsx", 'rb'),
        filename="laporan visit.xlsx"
    )


def date_start_handler(update, context):
    context.bot.edit_message_text(
        chat_id=admin_chat_id,
        message_id=admin_msg_id,
        text="masukkan tanggal awal",
        reply_markup=telegram_utils.create_calendar()
    )


def date_end_callback(update, context):
    selected, cancel, date = telegram_utils.process_calendar_selection(update, context)
    if cancel:
        context.bot.edit_message_text(
            chat_id=admin_chat_id,
            message_id=admin_msg_id,
            text="seleksi tanggal laporan dibatalkan"
        )
        admin_laporan_handler(update, context)
        return LAPORAN_ADMIN
    if selected:
        global lpr_date_start
        lpr_date_start = str(date)
        if download_option == VS_PHOTO_OPT:
            context.bot.edit_message_text(
                chat_id=admin_chat_id,
                message_id=admin_msg_id,
                text="masukkan user id: "
            )
            return INPUT_USERID
        elif download_option == VS_STATISTIK:
            result = admin_report_statistik(update, context, lpr_date_start.split(" ")[0], True)
            if result:
                admin_menu_handler(update, context, is_reset=True)
            return MENU_ADMIN
        else:
            context.bot.edit_message_text(
                chat_id=admin_chat_id,
                message_id=admin_msg_id,
                text="masukkan tanggal akhir",
                reply_markup=telegram_utils.create_calendar()
            )
            return DATE_SELECTED


def admin_userid_callback(update, context):
    user_id = update.message.text
    global lpr_date_start
    date = lpr_date_start.split(" ")[0]
    curdir = os.getcwd() + "/res/img/" + date + "/" + user_id + "/"
    error = "foto pada tanggal {} atau user id {} tidak ditemukan".format(date, user_id)
    if os.path.isdir(curdir):
        for file in os.listdir(curdir):
            if file.endswith(".jpg"):
                photo_visit = os.path.join(curdir + "/" + file)
                send_typing_state(update, context)
                context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(photo_visit, 'rb')
                )
        admin_laporan_handler(update, context, True)
        return LAPORAN_ADMIN
    else:
        admin_menu_handler(update, context, error, True)
        return MENU_ADMIN


def send_typing_state(update, context):
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )


def date_selected_callback(update, context):
    selected, cancel, date = telegram_utils.process_calendar_selection(update, context)
    if cancel:
        context.bot.edit_message_text(
            chat_id=admin_chat_id,
            message_id=admin_msg_id,
            text="seleksi tanggal laporan dibatalkan"
        )
        admin_laporan_handler(update, context)
        return LAPORAN_ADMIN
    if selected:
        global lpr_date_start
        global download_option
        if download_option == RIWAYAT_OPT:
            get_report_hist(update, context, lpr_date_start, date)
        if download_option == VISITOR_OPT:
            get_list_visitor(update, context, lpr_date_start, date)
        if download_option == LVS_OPT:
            get_report_todo(update, context, lpr_date_start, date)
        admin_laporan_handler(update, context)
        return LAPORAN_ADMIN


def get_report_todo(update, context, ds, de):
    report_todo = db.get_report_todo(ds, de)
    df = pd.DataFrame(
        report_todo,
        columns=["id", "nama visitor", "username", "tanggal tugas", "terakhir submit", "tugas selesai",
                 "tugas belum selesai",
                 "diluar tugas"]
    )
    df["jumlah tugas"] = df["tugas selesai"] + df["tugas belum selesai"]
    df["jumlah keseluruhan"] = df["jumlah tugas"] + df["diluar tugas"]
    df.to_excel("todo_report.xlsx", index=False)
    context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=open("todo_report.xlsx", 'rb'),
        filename="laporan penugasan.xlsx"
    )


def get_list_visitor(update, context, ds=None, de=None):
    visitors = db.get_list_visitor(ds, de)
    df = pd.DataFrame(
        visitors,
        columns=["id visitor", "nama visitor", "username", "total submit", "terakhir submit"]
    )
    df.to_excel("visitors.xlsx", index=False)
    context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=open("visitors.xlsx", 'rb'),
        filename="list visitor.xlsx"
    )


def admin_start(update, context):
    global admin_msg_id, admin_chat_id, entry_msg_id, entry_chat_id
    entry_msg = context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="masukkan pin admin : "
    )
    entry_msg_id = entry_msg.message_id
    entry_chat_id = entry_msg.chat_id
    message = context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="-",
        reply_markup=InlineKeyboardMarkup(num_keyboard)
    )
    admin_msg_id = message.message_id
    admin_chat_id = message.chat_id
    return PASSWD_ADMIN


def admin_menu_handler(update, context, add_msg="", is_reset=False):
    msg_send = "menu utama admin"
    if len(add_msg) != 0:
        msg_send += "\n*notifikasi: {}*".format(add_msg)
    markup = InlineKeyboardMarkup(config.admin_main_menu)
    parsing = ParseMode.MARKDOWN
    global admin_chat_id, admin_msg_id
    if is_reset:
        message = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg_send,
            reply_markup=markup,
            parse_mode=parsing
        )
        admin_chat_id = message.chat_id
        admin_msg_id = message.message_id
    else:
        context.bot.edit_message_text(
            chat_id=admin_chat_id,
            message_id=admin_msg_id,
            text=msg_send,
            reply_markup=InlineKeyboardMarkup(config.admin_main_menu),
            parse_mode=parsing
        )


def admin_main_menu_callback(update, context):
    data = update.callback_query.data
    global pin_admin
    if data == "logout":
        context.bot.delete_message(
            chat_id=admin_chat_id,
            message_id=admin_msg_id
        )
        return ConversationHandler.END
    if data == "sbhi":
        date_now = datetime.today()
        date = "{}-{:02d}-{:02d}".format(date_now.year, date_now.month, date_now.day)
        admin_report_statistik(update, context, date)
        return MENU_ADMIN
    if data == "gp":
        context.bot.edit_message_text(
            chat_id=admin_chat_id,
            message_id=admin_msg_id,
            text="masukkan pin admin saat ini: ",
            reply_markup=InlineKeyboardMarkup(num_keyboard)
        )
        pin_admin = ""
        return PIN_CHANGE
    if data == "laporan":
        admin_laporan_handler(update, context)
        return LAPORAN_ADMIN
    if data == "pv":
        admin_vm_handler(update, context)
        return VISIT_MENU_ADMIN


def admin_laporan_handler(update, context, is_reset=False):
    markup = InlineKeyboardMarkup(config.admin_laporan_menu)
    msg = "menu laporan : "
    global admin_chat_id, admin_msg_id
    if is_reset:
        message = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg,
            reply_markup=markup
        )
        admin_chat_id = message.chat_id
        admin_msg_id = message.message_id
    else:
        context.bot.edit_message_text(
            chat_id=admin_chat_id,
            message_id=admin_msg_id,
            text=msg,
            reply_markup=markup
        )


def admin_change_pin(update, context):
    global pin_admin
    msg_bot = ""
    resp_data = str(update.callback_query.data)
    if resp_data == "cancel":
        admin_menu_handler(update, context)
        return MENU_ADMIN
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
                text="masukkan pin baru:",
                reply_markup=InlineKeyboardMarkup(num_keyboard)
            )
            pin_admin = ""
            return NEW_PIN
        else:
            msg_bot = "pin salah"
            pin_admin = ""
    context.bot.edit_message_text(
        chat_id=admin_chat_id,
        message_id=admin_msg_id,
        text=msg_bot,
        reply_markup=InlineKeyboardMarkup(num_keyboard)
    )


def todo_submit(update, context):
    todolist = update.message.text.replace("/todo_list", "").strip().split("\n")
    username = update.message.from_user.username
    user_id = str(update.message.from_user.id)
    todo_list_validated = []
    if todolist == ['']:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="@{} sertakan list nomor internet pelanggan, lihat penggunaan /help_todo_list".format(username)
        )
        return
    for todo in todolist:
        todo = todo.strip()
        if re.search('[A-Za-z,./?\';[\\]!@#$%^&*()<>:"{}]+', todo):
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="@{} input harus berupa angka, lihat penggunaan /help_todo_list".format(username)
            )
            return
        else:
            if len(todo) != 0:
                todo_list_validated.append(todo.strip())
    db.insert_todo_list(todo_list_validated, user_id, fullname(update), username)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="@{} input todo list diterima".format(username)
    )


def admin_new_pin(update, context):
    global pin_admin
    msg_bot = ""
    resp_data = str(update.callback_query.data)
    if resp_data == "cancel":
        admin_menu_handler(update, context)
        return MENU_ADMIN
    if resp_data != "clear" and resp_data != "submit":
        pin_admin += resp_data
        msg_bot = len(pin_admin) * "*"
    if resp_data == "clear":
        pin_admin = ""
        msg_bot = "-"
    if resp_data == "submit":
        db.seeder_admin(pin_admin)
        pin_admin = ""
        admin_menu_handler(update, context, "update pin berhasil")
        return MENU_ADMIN
    context.bot.edit_message_text(
        chat_id=admin_chat_id,
        message_id=admin_msg_id,
        text=msg_bot,
        reply_markup=InlineKeyboardMarkup(num_keyboard)
    )


def admin_laporan_callback(update, context):
    data = update.callback_query.data
    global download_option
    if data == "lv":
        download_option = VISITOR_OPT
        admin_choose_opsi_handler(update, context)
        return ADMIN_CHOOSE_OPSI
    if data == "sbdt":
        date_start_handler(update, context)
        download_option = VS_STATISTIK
        return DATE_LAST
    if data == "rws":
        download_option = RIWAYAT_OPT
        admin_choose_opsi_handler(update, context)
        return ADMIN_CHOOSE_OPSI
    if data == "lvs":
        download_option = LVS_OPT
        date_start_handler(update, context)
        return DATE_LAST
    if data == "fbv":
        date_start_handler(update, context)
        download_option = VS_PHOTO_OPT
        return DATE_LAST
    if data == "kmu":
        admin_menu_handler(update, context)
        return MENU_ADMIN


def admin_vm_callback(update, context):
    data = update.callback_query.data
    keyboard = config.admin_back_menu.copy()
    if data == "kmu":
        admin_menu_handler(update, context)
        return MENU_ADMIN
    if data == "rs_menu":
        num_key = 1
        for id_key, category, state in db.get_category_visit():
            caption = f"{category} : {state}"
            if num_key == 1:
                keyboard.append([InlineKeyboardButton(caption, callback_data=id_key)])
                num_key += 1
                continue
            if num_key == 2:
                keyboard[len(keyboard) - 1].append(InlineKeyboardButton(caption, callback_data=id_key))
                num_key = 1
        context.bot.edit_message_text(
            chat_id=admin_chat_id,
            message_id=admin_msg_id,
            text="pilih kategori visit terlebih dahulu",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return VISIT_RESULT_ADMIN
    if data == "ct_menu":
        num_key = 1
        for id_, state, code in db.get_state():
            if num_key == 1:
                keyboard.append([InlineKeyboardButton(state, callback_data=id_)])
                num_key += 1
                continue
            if num_key == 2:
                keyboard[len(keyboard) - 1].append(InlineKeyboardButton(state, callback_data=id_))
                num_key = 1
        context.bot.edit_message_text(
            chat_id=admin_chat_id,
            message_id=admin_msg_id,
            text="pilih kategori state terlebih dahulu",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CATEGORY_RESULT_ADMIN
    if data == "sv_menu":
        admin_edit_sv_handler(update, context)
        return EDIT_SV_ADMIN


def admin_edit_sv_handler(update, context):
    msg = "daftar state visit: \nid - nama - kode"
    for _id, name, code in db.get_state():
        msg += f"\n{_id} - {name} - {code}"
    context.bot.edit_message_text(
        chat_id=admin_chat_id,
        message_id=admin_msg_id,
        text=msg,
        reply_markup=InlineKeyboardMarkup(config.admin_state_menu)
    )


def admin_vm_handler(update, context):
    context.bot.edit_message_text(
        chat_id=admin_chat_id,
        message_id=admin_msg_id,
        text="menu pengaturan penamaan dan kode visit",
        reply_markup=InlineKeyboardMarkup(config.admin_kv_menu)
    )


def admin_edit_sv_callback(update, context):
    data = update.callback_query.data
    if data == "kmu":
        admin_menu_handler(update, context)
        return MENU_ADMIN
    if data == "tss":
        admin_crud_handler(update, context, sv_header["ADD"])
        return ADD_SV
    if data == "pnss":
        admin_crud_handler(update, context, sv_header["RENAME"])
        return RENAME_SV
    if data == "pkss":
        admin_crud_handler(update, context, sv_header["RECODE"])
        return RECODE_SV
    if data == "hss":
        admin_crud_handler(update, context, sv_header["REMOVE"])
        return REMOVE_SV


def admin_edit_rv_callback(update, context):
    data = update.callback_query.data
    if data == "kmu":
        admin_menu_handler(update, context)
        return MENU_ADMIN
    if data == "ths":
        admin_crud_handler(update, context, rv_header["ADD"])
        return ADD_RV
    if data == "pnhs":
        admin_crud_handler(update, context, rv_header["RENAME"])
        return RENAME_RV
    if data == "pkhs":
        admin_crud_handler(update, context, rv_header["RECODE"])
        return RECODE_RV
    if data == "hhs":
        admin_crud_handler(update, context, rv_header["REMOVE"])
        return REMOVE_RV


def admin_choose_rv_callback(update, context):
    category_id = update.callback_query.data
    if category_id == "kmu":
        admin_menu_handler(update, context)
        return MENU_ADMIN
    category = db.get_category_name(category_id)
    msg = "daftar hasil visit kategori: {}\nid - nama - kode".format(category)
    for _id, name, code in db.get_visit_result(category_id):
        msg += f"\n{_id} - {name} - {code}"
    global state_rv
    state_rv = category_id
    state_rv = category_id
    context.bot.edit_message_text(
        chat_id=admin_chat_id,
        message_id=admin_msg_id,
        text=msg,
        reply_markup=InlineKeyboardMarkup(config.admin_result_menu)
    )
    return EDIT_RV_ADMIN


def admin_back_menu_callback(update, context):
    global state_rv
    data = update.callback_query.data
    if data == "kmu":
        admin_menu_handler(update, context)
        return MENU_ADMIN


def admin_add_rv_callback(update, context):
    resp = update.message.text.split("\n")
    global state_rv
    # validasi data
    for row in resp:
        split = row.split("-")
        if len(split) != 2:
            admin_crud_handler(update, context, rv_header["ADD"], "gagal, terdapat kesalahan format penulisan")
            return ADD_RV
        if db.check_exist_code_rv(state_rv, split[1].strip()):
            admin_crud_handler(update, context, rv_header["ADD"],
                               'gagal, kode pada "' + split[0].strip() + '" sudah dipakai')
            return ADD_RV
    # memasukkan data
    for row in resp:
        name, code = row.split("-")
        db.add_result_visit(state_rv, code.strip(), name.strip())
    admin_crud_handler(update, context, rv_header["ADD"], "berhasil menambahkan data")
    return ADD_RV


def admin_rename_rv_callback(update, context):
    resp = update.message.text.split("\n")
    # validasi data
    for row in resp:
        split = row.split("-")
        if len(split) != 2:
            admin_crud_handler(update, context, rv_header["RENAME"], "gagal, terdapat kesalahan format penulisan")
            return RENAME_RV
        if not (db.check_exist_id_rv(split[0].strip(), state_rv)):
            admin_crud_handler(update, context, rv_header["RENAME"],
                               'gagal, id pada "' + split[1].strip() + '" tidak ditemukan')
            return RENAME_RV
    for row in resp:
        id_, new_name = row.split("-")
        db.rename_result_visit(id_.strip(), new_name.strip())
    admin_crud_handler(update, context, rv_header["RENAME"], "berhasil mengganti data nama visit")
    return RENAME_RV


def admin_recode_rv_callback(update, context):
    resp = update.message.text.split("\n")
    global state_rv
    # validasi data
    for row in resp:
        split = row.split("-")
        if len(split) != 2:
            admin_crud_handler(update, context, rv_header["RECODE"], "gagal, terdapat kesalahan format penulisan")
            return RECODE_RV
        if not (db.check_exist_id_rv(split[0].strip(), state_rv)):
            admin_crud_handler(update, context, rv_header["RECODE"],
                               'gagal, id pada kode "' + split[1].strip() + '" tidak ditemukan')
            return RECODE_RV
        if db.check_exist_code_rv(state_rv, split[1].strip()):
            admin_crud_handler(update, context, rv_header["RECODE"],
                               'gagal, kode "' + split[1].strip() + '" sudah dipakai oleh data lainnya')
            return RECODE_RV
    for row in resp:
        id_, new_code = row.split("-")
        db.recode_result_visit(id_.strip(), new_code.strip())
    admin_crud_handler(update, context, rv_header["RECODE"], "berhasil mengganti kode hasil visit")
    return RECODE_RV


def admin_remove_rv_callback(update, context):
    resp = update.message.text.split("\n")
    global state_rv
    # validasi data
    for id_ in resp:
        if not (db.check_exist_id_rv(id_, state_rv)):
            admin_crud_handler(update, context, rv_header["REMOVE"],
                               'gagal, id pada kode "' + id_ + '" tidak ditemukan')
            return REMOVE_RV
    for id_ in resp:
        db.remove_result_visit(id_.strip())
    admin_crud_handler(update, context, rv_header["REMOVE"], "berhasil menghapus opsi data hasil visit")
    return REMOVE_RV


def admin_choose_cr_callback(update, context):
    state_id = update.callback_query.data
    if state_id == "kmu":
        admin_menu_handler(update, context)
        return MENU_ADMIN
    state = db.get_state_with_id(state_id)
    msg = "daftar kategori visit pada state: {}\nid - nama - kode".format(state)
    for _id, name, code in db.get_category_visit_with_state_id(state_id):
        msg += f"\n{_id} - {name} - {code}"
    global state_cv
    state_cv = state_id
    context.bot.edit_message_text(
        chat_id=admin_chat_id,
        message_id=admin_msg_id,
        text=msg,
        reply_markup=InlineKeyboardMarkup(config.admin_category_menu)
    )
    return EDIT_CR_ADMIN


def admin_edit_cr_callback(update, context):
    data = update.callback_query.data
    if data == "kmu":
        admin_menu_handler(update, context)
        return MENU_ADMIN
    if data == "tks":
        admin_crud_handler(update, context, header=cr_header["ADD"])
        return ADD_CR
    if data == "pnks":
        admin_crud_handler(update, context, header=cr_header["RENAME"])
        return RENAME_CR
    if data == "pkks":
        admin_crud_handler(update, context, header=cr_header["RECODE"])
        return RECODE_CR
    if data == "hks":
        admin_crud_handler(update, context, header=cr_header["REMOVE"])
        return REMOVE_CR


def admin_add_cr_callback(update, context):
    resp = update.message.text.split("\n")
    global state_cv
    # validasi data
    for row in resp:
        split = row.split("-")
        if len(split) != 2:
            admin_crud_handler(update, context, cr_header["ADD"], "gagal, terdapat kesalahan format penulisan")
            return ADD_CR
        if db.check_exist_code_cr(state_cv, split[1].strip()):
            admin_crud_handler(update, context, cr_header["ADD"],
                               'gagal, kode pada "' + split[0].strip() + '" sudah dipakai')
            return ADD_CR
    # memasukkan data
    for row in resp:
        name, code = row.split("-")
        db.add_category(state_cv, name.strip(), code.strip())
    admin_crud_handler(update, context, cr_header["ADD"], "berhasil menambahkan data")
    return ADD_CR


def admin_crud_handler(update, context, header="", notif=""):
    msg = header
    if len(notif) != 0:
        msg += "\n*notifikasi: {}*".format(notif)
    global admin_msg_id, admin_chat_id
    msg = context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        reply_markup=InlineKeyboardMarkup(config.admin_back_menu),
        parse_mode=ParseMode.MARKDOWN
    )
    admin_msg_id = msg.message_id
    admin_chat_id = msg.chat_id


def admin_rename_cr_callback(update, context):
    resp = update.message.text.split("\n")
    # validasi data
    for row in resp:
        split = row.split("-")
        if len(split) != 2:
            admin_crud_handler(update, context, cr_header["RENAME"], "gagal, terdapat kesalahan format penulisan")
            return RENAME_CR
        if not (db.check_exist_id_cr(split[0].strip(), state_cv)):
            admin_crud_handler(update, context, cr_header["RENAME"],
                               'gagal, id pada "' + split[1].strip() + '" tidak ditemukan')
            return RENAME_CR
    for row in resp:
        id_, new_name = row.split("-")
        db.rename_category_visit(id_.strip(), new_name.strip())
    admin_crud_handler(update, context, cr_header["RENAME"], "berhasil mengganti nama kategori visit")
    return RENAME_CR


def admin_recode_cr_callback(update, context):
    resp = update.message.text.split("\n")
    # validasi data
    for row in resp:
        split = row.split("-")
        if len(split) != 2:
            admin_crud_handler(update, context, cr_header["RECODE"], "gagal, terdapat kesalahan format penulisan")
            return RECODE_CR
        if not (db.check_exist_id_cr(split[0].strip(), state_cv)):
            admin_crud_handler(update, context, cr_header["RECODE"],
                               'gagal, id pada kode "' + split[1].strip() + '" tidak ditemukan')
            return RECODE_CR
        if db.check_exist_code_cr(state_cv, split[1].strip()):
            admin_crud_handler(update, context, cr_header["RECODE"],
                               'gagal, kode "' + split[1].strip() + '" sudah dipakai oleh data lainnya')
            return RECODE_CR
    for row in resp:
        id_, new_code = row.split("-")
        db.recode_category_visit(id_.strip(), new_code.strip())
    admin_crud_handler(update, context, cr_header["RECODE"], "berhasil mengganti kode kategori visit")
    return RECODE_CR


def admin_remove_cr_callback(update, context):
    resp = update.message.text.split("\n")
    # validasi data
    for id_ in resp:
        if not (db.check_exist_id_cr(id_, state_cv)):
            admin_crud_handler(update, context, cr_header["REMOVE"],
                               'gagal, id pada kode "' + id_ + '" tidak ditemukan')
            return REMOVE_CR
    for id_ in resp:
        db.remove_category_visit(id_.strip())
    admin_crud_handler(update, context, cr_header["REMOVE"], "berhasil menghapus opsi data hasil visit")
    return REMOVE_CR


def admin_add_sv_callback(update, context):
    resp = update.message.text.split("\n")
    for row in resp:
        split = row.split("-")
        if len(split) != 2:
            admin_crud_handler(update, context, sv_header["ADD"], "gagal, terdapat kesalahan format penulisan")
            return ADD_SV
        if db.check_exist_code_sv(split[1]):
            admin_crud_handler(update, context, sv_header["ADD"],
                               'gagal, kode pada "' + split[0].strip() + '" sudah dipakai')
            return ADD_SV
    # memasukkan data
    for row in resp:
        name, code = row.split("-")
        db.add_state(name.strip(), code.strip())
    admin_crud_handler(update, context, sv_header["ADD"], "berhasil menambahkan data")
    return ADD_SV


def admin_rename_sv_callback(update, context):
    resp = update.message.text.split("\n")
    # validasi data
    for row in resp:
        split = row.split("-")
        if len(split) != 2:
            admin_crud_handler(update, context, sv_header["RENAME"], "gagal, terdapat kesalahan format penulisan")
            return RENAME_SV
        if not (db.check_exist_id_sv(split[0].strip())):
            admin_crud_handler(update, context, sv_header["RENAME"],
                               'gagal, id pada "' + split[1].strip() + '" tidak ditemukan')
            return RENAME_SV
    for row in resp:
        id_, new_name = row.split("-")
        db.rename_state_visit(id_.strip(), new_name.strip())
    admin_crud_handler(update, context, sv_header["RENAME"], "berhasil mengganti nama state visit")
    return RENAME_SV


def admin_recode_sv_callback(update, context):
    resp = update.message.text.split("\n")
    # validasi data
    for row in resp:
        split = row.split("-")
        if len(split) != 2:
            admin_crud_handler(update, context, sv_header["RECODE"], "gagal, terdapat kesalahan format penulisan")
            return RECODE_SV
        if not (db.check_exist_id_sv(split[0].strip())):
            admin_crud_handler(update, context, sv_header["RECODE"],
                               'gagal, id pada kode "' + split[1].strip() + '" tidak ditemukan')
            return RECODE_SV
        if db.check_exist_code_sv(split[1].strip()):
            admin_crud_handler(update, context, sv_header["RECODE"],
                               'gagal, kode "' + split[1].strip() + '" sudah dipakai oleh data lainnya')
            return RECODE_SV
    for row in resp:
        id_, new_code = row.split("-")
        db.recode_state_visit(id_.strip(), new_code.strip())
    admin_crud_handler(update, context, sv_header["RECODE"], "berhasil mengganti kode state visit")
    return RECODE_SV


def admin_remove_sv_callback(update, context):
    resp = update.message.text.split("\n")
    # validasi data
    for id_ in resp:
        if not (db.check_exist_id_sv(id_)):
            admin_crud_handler(update, context, sv_header["REMOVE"],
                               'gagal, id pada kode "' + id_ + '" tidak ditemukan')
            return REMOVE_SV
    for id_ in resp:
        db.remove_state_visit(id_.strip())
    admin_crud_handler(update, context, sv_header["REMOVE"], "berhasil menghapus opsi data state visit")
    return REMOVE_SV


def admin_choose_opsi_handler(update, context):
    context.bot.edit_message_text(
        chat_id=admin_chat_id,
        message_id=admin_msg_id,
        text="pilih opsi pengunduhan",
        reply_markup=InlineKeyboardMarkup(config.date_choose)
    )


def code_csv(update, context):
    all_code = db.get_all_code()
    df = pd.DataFrame(
        all_code,
        columns=["code state", "code category", "code result", "id result", "id state",
                 "id category", "name state", "name category", "name result"]
    )
    df = df.drop(["id result", "id state", "id category"], axis=1)
    df["kode input"] = df.apply(
        lambda row: "{}{}{}".format(row["code state"], row["code category"], row["code result"]), axis=1)
    df.sort_values(by=['kode input'], inplace=True)
    df.to_excel("code list.xlsx", index=False)
    context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=open("code list.xlsx", 'rb'),
        filename="list kode.xlsx"
    )


def admin_choose_opsi_callback(update, context):
    data = update.callback_query.data
    global download_option
    if data == "kmu":
        admin_menu_handler(update, context)
        return MENU_ADMIN
    if data == "sd":
        if download_option == RIWAYAT_OPT:
            get_report_hist(update, context)
        elif download_option == VISITOR_OPT:
            get_list_visitor(update, context)
        admin_laporan_handler(update, context)
        return LAPORAN_ADMIN
    if data == "brt":
        date_start_handler(update, context)
        return DATE_LAST


def admin_report_statistik(update, context, date, reset_menu=False):
    send_typing_state(update, context)
    report_todo = db.get_report_todo(date)
    if len(report_todo) == 0:
        admin_menu_handler(update, context, "data submit masih kosong " + date, reset_menu)
        return False
    else:
        todo_done = [person[5] for person in report_todo]
        todo_wait = [person[6] for person in report_todo]
        outer_submit = [person[7] for person in report_todo]
        size = len(report_todo)
        fig, ax = plt.subplots()
        ind = np.arange(size)
        width = 0.15
        p1 = ax.bar(ind, todo_done, width, align='center')
        p2 = ax.bar(ind + width, todo_wait, width, align='center')
        p3 = ax.bar(ind + width + width, outer_submit, width, align='center')
        ax.set_xticks(ind + width * 3 / 3)
        ax.set_xticklabels([person[2] for person in report_todo])
        ax.autoscale_view()
        ax.set_title('Statistik submit Visit pada tanggal ' + date)
        ax.legend((p1[0], p2[0], p3[0]), ('todo done', 'todo wait', 'outer submit'))
        plt.ylabel("Total submit")
        plt.xlabel("Pengunjung")

        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width() / 2., 1.0 * height, '%d' % int(height), ha='center',
                        va='bottom')

        autolabel(p1)
        autolabel(p2)
        autolabel(p3)
        plt.savefig('report.png')
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open('report.png', 'rb')
        )
        return True


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
            fallbacks=[
                CommandHandler('code_csv', code_csv)
            ],
            states={
                PASSWD_ADMIN: [CallbackQueryHandler(pin_handler)],
                MENU_ADMIN: [CallbackQueryHandler(admin_main_menu_callback)],
                PIN_CHANGE: [CallbackQueryHandler(admin_change_pin)],
                NEW_PIN: [CallbackQueryHandler(admin_new_pin)],
                LAPORAN_ADMIN: [CallbackQueryHandler(admin_laporan_callback)],
                DATE_LAST: [CallbackQueryHandler(date_end_callback)],
                DATE_SELECTED: [CallbackQueryHandler(date_selected_callback)],
                VISIT_MENU_ADMIN: [CallbackQueryHandler(admin_vm_callback)],
                VISIT_RESULT_ADMIN: [CallbackQueryHandler(admin_choose_rv_callback)],
                CATEGORY_RESULT_ADMIN: [CallbackQueryHandler(admin_choose_cr_callback)],
                EDIT_RV_ADMIN: [CallbackQueryHandler(admin_edit_rv_callback)],
                EDIT_CR_ADMIN: [CallbackQueryHandler(admin_edit_cr_callback)],
                INPUT_USERID: [MessageHandler(Filters.regex(r'\d+$'), admin_userid_callback)],
                ADMIN_CHOOSE_OPSI: [CallbackQueryHandler(admin_choose_opsi_callback)],
                ADD_RV: [
                    CallbackQueryHandler(admin_back_menu_callback),
                    MessageHandler(Filters.text, admin_add_rv_callback)
                ],
                RENAME_RV: [
                    CallbackQueryHandler(admin_back_menu_callback),
                    MessageHandler(Filters.text, admin_rename_rv_callback)
                ],
                RECODE_RV: [
                    CallbackQueryHandler(admin_back_menu_callback),
                    MessageHandler(Filters.text, admin_recode_rv_callback)
                ],
                REMOVE_RV: [
                    CallbackQueryHandler(admin_back_menu_callback),
                    MessageHandler(Filters.regex(r'\d+$'), admin_remove_rv_callback)
                ],
                ADD_CR: [
                    CallbackQueryHandler(admin_back_menu_callback),
                    MessageHandler(Filters.text, admin_add_cr_callback)
                ],
                RENAME_CR: [
                    CallbackQueryHandler(admin_back_menu_callback),
                    MessageHandler(Filters.text, admin_rename_cr_callback)
                ],
                RECODE_CR: [
                    CallbackQueryHandler(admin_back_menu_callback),
                    MessageHandler(Filters.text, admin_recode_cr_callback)
                ],
                REMOVE_CR: [
                    CallbackQueryHandler(admin_back_menu_callback),
                    MessageHandler(Filters.regex(r'\d+$'), admin_remove_cr_callback)
                ],
                EDIT_SV_ADMIN: [CallbackQueryHandler(admin_edit_sv_callback)],
                ADD_SV: [
                    CallbackQueryHandler(admin_back_menu_callback),
                    MessageHandler(Filters.text, admin_add_sv_callback)
                ],
                RENAME_SV: [
                    CallbackQueryHandler(admin_back_menu_callback),
                    MessageHandler(Filters.text, admin_rename_sv_callback)
                ],
                RECODE_SV: [
                    CallbackQueryHandler(admin_back_menu_callback),
                    MessageHandler(Filters.text, admin_recode_sv_callback)
                ],
                REMOVE_SV: [
                    CallbackQueryHandler(admin_back_menu_callback),
                    MessageHandler(Filters.regex(r'\d+$'), admin_remove_sv_callback)
                ]
            }
        )
        up.dispatcher.add_handler(conv)
        up.dispatcher.add_error_handler(fallback_handler)
        up.dispatcher.add_handler(CommandHandler('start', start_handler))
        up.dispatcher.add_handler(CommandHandler('help', start_handler))
        up.dispatcher.add_handler(MessageHandler(Filters.photo, photo_visit_callback))
        up.dispatcher.add_handler(CommandHandler('cancel', cancel_callback))
        up.dispatcher.add_handler(CommandHandler('input_visit', input_visit_callback))
        up.dispatcher.add_handler(CommandHandler('todo_list', todo_submit))
        up.dispatcher.add_handler(CommandHandler('submit_visit', submit_visit))
        up.dispatcher.add_handler(CommandHandler('help_todo_list', help_todo_list))
        # up.dispatcher.add_handler(CommandHandler('report_code', report_code))
        up.dispatcher.add_handler(CommandHandler('code_csv', code_csv))
        # up.dispatcher.add_handler(CallbackQueryHandler(callback_code))
        print("Making conversation done")
        up.start_polling()
        print("Chatbot already to use")
        up.idle()

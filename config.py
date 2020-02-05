from telegram import InlineKeyboardButton
from emoji import emojize

plus = emojize(":heavy_plus_sign:", use_aliases=True)
pen = emojize(":pencil2:", use_aliases=True)
code = emojize(":1234:", use_aliases=True)
remove = emojize(":negative_squared_cross_mark:", use_aliases=True)
gear = emojize(":gear:", use_aliases=True)
book = emojize(":closed_book:", use_aliases=True)
key = emojize(":key:", use_aliases=True)
arrow_back = emojize(":arrow_backward:", use_aliases=True)
arrow_up = emojize(":arrow_up_small:", use_aliases=True)

num_keyboard = [
    [
        InlineKeyboardButton("1", callback_data='1'),
        InlineKeyboardButton("2", callback_data='2'),
        InlineKeyboardButton("3", callback_data='3')
    ],
    [
        InlineKeyboardButton("4", callback_data='4'),
        InlineKeyboardButton("5", callback_data='5'),
        InlineKeyboardButton("6", callback_data='6')
    ],
    [
        InlineKeyboardButton("7", callback_data='7'),
        InlineKeyboardButton("8", callback_data='8'),
        InlineKeyboardButton("9", callback_data='9')
    ],
    [
        InlineKeyboardButton("clear", callback_data='clear'),
        InlineKeyboardButton("0", callback_data='0'),
        InlineKeyboardButton("cancel", callback_data='cancel')
    ],
    [
        InlineKeyboardButton("submit", callback_data='submit')
    ]
]

admin_main_menu = [
    [InlineKeyboardButton("pengaturan visit " + gear, callback_data="pv"),
     InlineKeyboardButton("laporan " + book, callback_data="laporan")],
    [InlineKeyboardButton("ganti pin " + key, callback_data="gp"),
     InlineKeyboardButton("keluar " + arrow_back, callback_data="logout")],
]

admin_laporan_menu = [
    [InlineKeyboardButton("kembali ke menu utama " + arrow_up, callback_data="kmu")],
    [InlineKeyboardButton("list visitor", callback_data="lv")],
    [InlineKeyboardButton("laporan riwayat submit", callback_data="rws")],
    [InlineKeyboardButton("laporan penugasan", callback_data="lvs")]
]

admin_kv_menu = [
    [InlineKeyboardButton("kembali ke menu utama " + arrow_up, callback_data="kmu")],
    [InlineKeyboardButton("state visit", callback_data="sv_menu")],
    [InlineKeyboardButton("kategori visit", callback_data="ct_menu")],
    [InlineKeyboardButton("hasil visit", callback_data="rs_menu")],
]

admin_back_menu = [
    [
        InlineKeyboardButton("kembali ke menu utama " + arrow_up, callback_data="kmu")
    ],
]

admin_state_menu = [
    [InlineKeyboardButton("kembali ke menu utama " + arrow_up, callback_data="kmu")],
    [InlineKeyboardButton("tambah state visit " + plus, callback_data="tss")],
    [InlineKeyboardButton("perbarui nama state visit " + pen, callback_data="pnss")],
    [InlineKeyboardButton("perbarui kode state visit " + code, callback_data="pkss")],
    [InlineKeyboardButton("hapus state visit " + remove, callback_data="hss")],
]

admin_category_menu = [
    [InlineKeyboardButton("kembali ke menu utama " + arrow_up, callback_data="kmu")],
    [InlineKeyboardButton("tambah kategori visit " + plus, callback_data="tks")],
    [InlineKeyboardButton("perbarui nama kategori visit " + pen, callback_data="pnks")],
    [InlineKeyboardButton("perbarui kode kategori visit " + code, callback_data="pkks")],
    [InlineKeyboardButton("hapus kategori visit " + remove, callback_data="hks")],
]

date_choose = [
    [InlineKeyboardButton("kembali ke menu utama " + arrow_up, callback_data="kmu")],
    [InlineKeyboardButton("semua data", callback_data="sd")],
    [InlineKeyboardButton("berdasarkan rentang tanggal", callback_data="brt")],
]

rv_header = {
    "ADD": "menambahkan hasil visit"
           "\nformat penambahan : nama hasil visit - kode hasil visit"
           "\ncontoh: \njarang digunakan - 1"
           "\nrouter bermasalah - 2",
    "RENAME": "mengganti nama hasil visit"
              "\nformat penggantian nama : id - nama baru hasil visit"
              "\ncontoh: \n1 - jarang digunakan"
              "\n2 - router bermasalah",
    "RECODE": "mengganti kode hasil visit"
              "\nformat penggantian nama : id - kode baru hasil visit"
              "\ncontoh: \n1 - 10"
              "\n2 - 11",
    "REMOVE": "menghapus data opsi hasil visit"
              "\nformat penghapusan data opsi : id"
              "\ncontoh: \n1"
              "\n2"
}

cr_header = {
    "ADD": "menambahkan kategori visit"
           "\nformat penambahan : nama kategori - kode kategori"
           "\ncontoh: \nservice - S"
           "\nproduct - PD",
    "RENAME": "mengganti nama kategori visit"
              "\nformat penggantian nama : id - nama baru kategori visit"
              "\ncontoh: \n1 - price"
              "\n2 - product",
    "RECODE": "mengganti kode kategori visit"
              "\nformat penggantian kode : id - kode kategori visit"
              "\ncontoh: \n1 - C"
              "\n2 - PD",
    "REMOVE": "menghapus data opsi kategori visit"
              "\nformat penghapusan data opsi : id"
              "\ncontoh: \n1"
              "\n2"
}

sv_header = {
    "ADD": "menambahkan state visit"
           "\nformat penambahan : nama state - kode state"
           "\ncontoh: \ncontacted - A"
           "\nnot contacted - B",
    "RENAME": "mengganti nama state visit"
              "\nformat penggantian nama : id - nama baru state visit"
              "\ncontoh: \n1 - terkontak"
              "\n2 - tidak ditemukan",
    "RECODE": "mengganti kode state visit"
              "\nformat penggantian kode : id - kode state visit"
              "\ncontoh: \n1 - CT"
              "\n2 - NCT",
    "REMOVE": "menghapus data opsi state visit"
              "\nformat penghapusan data opsi : id"
              "\ncontoh: \n1"
              "\n2"
}

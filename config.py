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
    [
        InlineKeyboardButton("perbarui nama state", callback_data="pns"),
        InlineKeyboardButton("perbarui kode state", callback_data="pks"),
        InlineKeyboardButton("hapus state", callback_data="hs"),
        InlineKeyboardButton("kembali ke menu utama", callback_data="kmu")
    ],
]

admin_category_menu = [
    [
        InlineKeyboardButton("perbarui nama kategori", callback_data="pnk"),
        InlineKeyboardButton("perbarui kode kategori", callback_data="pkk"),
        InlineKeyboardButton("hapus kategori", callback_data="hk"),
        InlineKeyboardButton("kembali ke menu utama", callback_data="kmu")
    ]
]

admin_result_menu = [
    [InlineKeyboardButton("kembali ke menu utama " + arrow_up, callback_data="kmu")],
    [InlineKeyboardButton("tambah hasil visit " + plus, callback_data="ths")],
    [InlineKeyboardButton("perbarui nama hasil visit " + pen, callback_data="pnhs")],
    [InlineKeyboardButton("perbarui kode hasil visit " + code, callback_data="pkhs")],
    [InlineKeyboardButton("hapus hasil visit " + remove, callback_data="hhs")],
]

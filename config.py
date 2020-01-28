from telegram import InlineKeyboardButton

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
    [InlineKeyboardButton("kode visit", callback_data="kv"),
     InlineKeyboardButton("laporan", callback_data="laporan")],
    [InlineKeyboardButton("ganti pin", callback_data="gp"),
     InlineKeyboardButton("keluar", callback_data="logout")],
]

admin_laporan_menu = [
    [InlineKeyboardButton("list visitor", callback_data="lv")],
    [InlineKeyboardButton("laporan riwayat submit", callback_data="rws")],
    [InlineKeyboardButton("kembali ke menu utama", callback_data="kmu")]
]

admin_kv_menu = [
    [InlineKeyboardButton("state visit", callback_data="sv_menu")],
    [InlineKeyboardButton("kategori visit", callback_data="ct_menu")],
    [InlineKeyboardButton("hasil visit", callback_data="rs_menu")],
    [InlineKeyboardButton("kembali ke menu utama", callback_data="kmu")]
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
    [
        InlineKeyboardButton("perbarui nama hasil visit", callback_data="pnhs"),
        InlineKeyboardButton("perbarui kode hasil visit", callback_data="pkhs"),
        InlineKeyboardButton("hapus hasil visit", callback_data="hhs"),
        InlineKeyboardButton("kembali ke menu utama", callback_data="kmu")
    ]
]

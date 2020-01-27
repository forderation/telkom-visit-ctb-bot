from telegram import InlineKeyboardButton
num_keyboard = [
    [
        InlineKeyboardButton("1", callback_data='1'), InlineKeyboardButton("2", callback_data='2'),
        InlineKeyboardButton("3", callback_data='3')
    ],
    [
        InlineKeyboardButton("4", callback_data='4'), InlineKeyboardButton("5", callback_data='5'),
        InlineKeyboardButton("6", callback_data='6')
    ],
    [
        InlineKeyboardButton("7", callback_data='7'), InlineKeyboardButton("8", callback_data='8'),
        InlineKeyboardButton("9", callback_data='9')
    ],
    [
        InlineKeyboardButton("clear", callback_data='clear'), InlineKeyboardButton("0", callback_data='0'),
        InlineKeyboardButton("cancel", callback_data='cancel')
    ],
    [
        InlineKeyboardButton("submit", callback_data='submit')
    ]
]

admin_main_menu = [
        [InlineKeyboardButton("kode visit", callback_data="kv")],
        [InlineKeyboardButton("laporan", callback_data="laporan")],
        [InlineKeyboardButton("keluar", callback_data="logout")]
]

admin_laporan_menu = [
    [InlineKeyboardButton("laporan visitor", callback_data="lv")],
    [InlineKeyboardButton("history laporan", callback_data="hl")],
    [InlineKeyboardButton("kembali ke menu utama", callback_data="kmu")]
]
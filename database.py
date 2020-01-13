import sqlite3


class DBHelper:

    def __init__(self, dbname="visit_ctb.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        self.TABLE_NAME = "VISIT_CTB"

    # noinspection SpellCheckingInspection
    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS " + \
               self.TABLE_NAME + \
               " (id_visit integer primary key," + \
               "visitor text not null," + \
               "tanggal_kunjungan text not null," + \
               "nomor_pelanggan text not null," + \
               "opsi_hasil text," + \
               "hasil_visit text," + \
               "visit_gagal text," + \
               "bukti_visit text not null," + \
               "keterangan_lain text)"
        self.conn.execute(stmt)
        self.conn.commit()
    #
    # def add_item(self, item_text):
    #     stmt = "INSERT INTO items (description) VALUES (?)"
    #     args = (item_text,)
    #     self.conn.execute(stmt, args)
    #     self.conn.commit()
    #
    # def delete_items(self, item_text):
    #     stmt = "DELETE FROM items where description = (?)"
    #     args = (item_text,)
    #     self.conn.execute(stmt, args)
    #     self.conn.commit()
    #
    # def get_items(self):
    #     stmt = "SELECT description FROM items"
    #     return [x[0] for x in self.conn.execute(stmt)]

import sqlite3


class DBHelper:

    def __init__(self, dbname="visit_ctb.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.TABLE_VISIT = "TABLE_VISIT"
        self.TABLE_PHOTO = "TABLE_PHOTO"

    def setup(self):
        stmt_table_visit = "CREATE TABLE IF NOT EXISTS " + \
                           self.TABLE_VISIT + \
                           " (visit_id integer primary key," + \
                           "visitor_name text not null," + \
                           "date_visit date not null," + \
                           "nip text not null," + \
                           "state_visit text not null," + \
                           "result_visit text not null," + \
                           "code_visit text not null," + \
                           "other_desc text)"
        stmt_table_photo = "CREATE TABLE IF NOT EXISTS " + \
                           self.TABLE_PHOTO + \
                           " (photo_id integer primary key," + \
                           "tele_photo_id text not null," + \
                           "visitor_id integer not null," + \
                           "visit_id integer not null," \
                           "FOREIGN KEY(visit_id) REFERENCES " + \
                           self.TABLE_VISIT + \
                           "(visit_id)" + \
                           ")"
        self.conn.execute(stmt_table_visit)
        self.conn.execute(stmt_table_photo)
        self.conn.commit()

    def add_visit(self, user_session):
        cursor = self.conn.cursor()
        stmt = "INSERT INTO " + \
               self.TABLE_VISIT + \
               " (visitor_name, date_visit, nip, state_visit, result_visit, code_visit, other_desc)" + \
               "VALUES (?,?,?,?,?,?,?)"
        args = (
            user_session["fullname"], user_session["date"], user_session["nip"],
            user_session["voc_state"], user_session["result_voc"], user_session["voc_code"],
            user_session["other_desc"],
        )
        cursor.execute(stmt, args)
        return cursor.lastrowid

    def add_photo(self, photos, visitor_id, visit_id):
        cursor = self.conn.cursor()
        for photo_id in photos:
            stmt = "INSERT INTO  " + \
                   self.TABLE_PHOTO + \
                   " (tele_photo_id, visitor_id, visit_id) values (?,?,?)"
            args = (photo_id, visitor_id, visit_id)
            cursor.execute(stmt, args)
        self.conn.commit()

    def get_photo(self):
        ts = self.TABLE_VISIT
        tp = self.TABLE_PHOTO
        cursor = self.conn.cursor()
        stmt = "SELECT " + tp + ".tele_photo_id," + tp + ".visitor_id," + ts + ".visitor_name," + \
               ts + ".date_visit," + \
               ts + ".code_visit" + " FROM " + \
               tp + \
               " JOIN " + \
               ts + \
               " ON " + \
               tp + ".visit_id=" + \
               ts + ".visit_id"
        cursor.execute(stmt)
        return cursor.fetchall()

    def get_visit(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM " + self.TABLE_VISIT)
        return cursor.fetchall()


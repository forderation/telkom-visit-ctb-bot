import sqlite3
from ddl import ddl


class DBHelper:

    def __init__(self, dbname="visit_ctb2.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.VISIT = "VISIT_HIST"
        self.PHOTO = "PHOTO_VISIT"
        self.ADMIN = "ADMIN"
        self.CATEGORY = "CATEGORY_RESULT"
        self.STATE = "STATE_VISIT"
        self.RESULT = "VISIT_RESULT"
        self.VISITOR = "VISITOR"
        self.cursor = self.conn.cursor()

    def setup(self):
        self.conn.executescript(ddl)
        self.conn.commit()

    def seeder_password(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO " + self.TB_ADMIN + "(password, last_login) VALUES ('admin',date('now'))"
        )
        self.conn.commit()

    def seeder_visit(self):
        cursor = self.conn.cursor()

    def check_password(self, passwd):
        cursor = self.conn.cursor()
        stmt_check_pass = "SELECT * FROM " + self.TB_ADMIN + " WHERE password = '" + passwd + "'"
        cursor.execute(stmt_check_pass)
        return cursor.fetchone()

    def add_visit(self, user_session):
        cursor = self.conn.cursor()
        stmt = "INSERT INTO " + \
               self.TB_VISIT + \
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
                   self.TB_PHOTO + \
                   " (tele_photo_id, visitor_id, visit_id) values (?,?,?)"
            args = (photo_id, visitor_id, visit_id)
            cursor.execute(stmt, args)
        self.conn.commit()

    def get_photo(self):
        ts = self.TB_VISIT
        tp = self.TB_PHOTO
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
        cursor.execute("SELECT * FROM " + self.TB_VISIT)
        return cursor.fetchall()


db = DBHelper()
db.setup()

import sqlite3


class DBHelper:

    def __init__(self, dbname="visit_ctb.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.TB_VISIT = "TABLE_VISIT"
        self.TB_PHOTO = "TABLE_PHOTO"
        self.TB_ADMIN = "TABLE_ADMIN"
        self.TB_OPTION = "TABLE_OPTION"
        self.TB_SEED = "TABLE_SEEDER"

    def setup(self):
        stmt_table_option = "CREATE TABLE IF NOT EXISTS " + self.TB_OPTION + \
                            " (id interger primary key, state_visit text not " \
                            "null, front_code text not null, mid_code text not null, rear_code text not null, " \
                            "result_visit text not null) "
        stmt_table_visit = "CREATE TABLE IF NOT EXISTS " + \
                           self.TB_VISIT + \
                           "(visit_id integer primary key, visitor_name text not null, date_visit date not null, " \
                           "nip text not null, option_id integer not null," \
                           "other_desc text, FOREIGN KEY(option_id) REFERENCES " + self.TB_OPTION + "(id))"
        stmt_table_photo = "CREATE TABLE IF NOT EXISTS " + \
                           self.TB_PHOTO + \
                           " (photo_id integer primary key," \
                           "tele_photo_id text not null," \
                           "visitor_id integer not null," \
                           "visit_id integer not null," \
                           "FOREIGN KEY(visit_id) REFERENCES " + \
                           self.TB_VISIT + \
                           "(visit_id)" \
                           ")"
        stmt_table_admin = "CREATE TABLE IF NOT EXISTS " + self.TB_ADMIN + \
                           " (id integer primary key, password text " \
                           "not null, last_login date, " \
                           "username text) "
        stmt_table_seed = "CREATE TABLE IF NOT EXISTS " + self.TB_SEED + \
                          "(id integer primary key, name_seeder text " \
                          "not null, date_seeding date not null, " \
                          "state_seed integer not null) "
        self.conn.execute(stmt_table_option)
        self.conn.execute(stmt_table_visit)
        self.conn.execute(stmt_table_photo)
        self.conn.execute(stmt_table_admin)
        self.conn.execute(stmt_table_seed)
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

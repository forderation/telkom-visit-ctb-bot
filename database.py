import sqlite3
from ddl import ddl
import hashlib


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

    def check_admin_password(self, pin, username):
        cursor = self.conn.cursor()
        hashed_pin = hashlib.md5(str(pin).encode('utf-8')).hexdigest()
        query_check_pass = "SELECT * FROM " + self.ADMIN + " WHERE password = '" + hashed_pin + "' AND id = 1"
        cursor.execute(query_check_pass)
        admin = cursor.fetchone()
        if admin is None:
            return False
        else:
            query_update = "UPDATE " + self.ADMIN + " SET username = '" + username + \
                           "', last_login = (select " \
                           "datetime('now','localtime')) WHERE id = 1 "
            cursor.execute(query_update)
            self.conn.commit()
            return True

    def add_visit(self, user_id, user_session):
        cursor = self.conn.cursor()
        query = "INSERT INTO " + \
                self.VISIT + \
                " (date_submit, nip, other_desc, id_state, id_category, id_result, id_visitor)" + \
                "VALUES ((SELECT datetime('now','localtime')),?,?,?,?,?,?)"
        state, category, result = user_session["idx_visit_code"]
        args = (
            user_session["nip"], user_session["other_desc"], state, category, result, user_id
        )
        cursor.execute(query, args)
        id_visit = cursor.lastrowid
        self.conn.commit()
        return id_visit

    def add_photo(self, user_id, id_visit, photo_paths):
        cursor = self.conn.cursor()
        for photo_path in photo_paths:
            query = "INSERT INTO " + self.PHOTO + \
                    " (photo_path, id_visitor, id_visit, date_submit) VALUES (?,?,?,(SELECT " + \
                    "datetime('now', 'localtime'))) "
            args = (photo_path, user_id, id_visit)
            cursor.execute(query, args)
        self.conn.commit()

    def get_photo(self):
        ts = self.TB_VISIT
        tp = self.TB_PHOTO
        cursor = self.conn.cursor()
        query = "SELECT " + tp + ".tele_photo_id," + tp + ".visitor_id," + ts + ".visitor_name," + \
                ts + ".date_visit," + \
                ts + ".code_visit" + " FROM " + \
                tp + \
                " JOIN " + \
                ts + \
                " ON " + \
                tp + ".visit_id=" + \
                ts + ".visit_id"
        cursor.execute(query)
        return cursor.fetchall()

    def get_visit(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM " + self.TB_VISIT)
        return cursor.fetchall()

    def get_state(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name_state FROM " + self.STATE)
        return cursor.fetchall()

    def get_detail_code(self, id_state):
        cursor = self.conn.cursor()
        query = "SELECT name_result,{}.code_state, {}.code_category, code_result FROM ".format(self.STATE,
                                                                                               self.CATEGORY) \
                + self.RESULT + " JOIN " + self.STATE + \
                " ON {}.id_state={}.id JOIN ".format(self.RESULT, self.STATE) + self.CATEGORY + \
                " ON {}.id_category={}.id ".format(self.RESULT, self.CATEGORY) + \
                " WHERE {}.id_state = '{}'".format(self.RESULT, id_state)
        cursor.execute(query)
        return cursor.fetchall()

    def get_all_code(self):
        cursor = self.conn.cursor()
        query = "SELECT {}.code_state, {}.code_category, code_result, {}.id, {}.id_state, {}.id_category, " \
                "{}.name_state, {}.name_category ,{}.name_result FROM ".format(self.STATE, self.CATEGORY, self.RESULT,
                                                                               self.RESULT, self.RESULT, self.STATE,
                                                                               self.CATEGORY, self.RESULT) + \
                self.RESULT + " JOIN " + self.STATE + " ON {}.id_state={}.id JOIN ".format(self.RESULT, self.STATE) + \
                self.CATEGORY + " ON {}.id_category={}.id ".format(self.RESULT, self.CATEGORY)
        cursor.execute(query)
        return cursor.fetchall()

    def sync_user_input(self, user_id, fullname, username):
        cursor = self.conn.cursor()
        query = "SELECT * FROM " + self.VISITOR + " WHERE id_visitor='" + user_id + "'"
        print(query)
        cursor.execute(query)
        if not cursor.fetchall():
            query = "INSERT INTO " + self.VISITOR + \
                    " (id_visitor, name_visitor, username, total_submit, last_submit) " + \
                    "VALUES (?,?,?,1,(SELECT datetime('now','localtime')))"
            print(query)
            cursor.execute(query, (user_id, fullname, username))
        else:
            query = "UPDATE " + self.VISITOR + \
                    " SET name_visitor = '" + fullname + "', username = '" + username + \
                    "', total_submit = " \
                    "total_submit+1, last_submit " \
                    "= (SELECT datetime('now','localtime')) WHERE id_visitor = {}".format(user_id)
            print(query)
            cursor.execute(query)
        self.conn.commit()


db = DBHelper()
print(db.get_all_code())

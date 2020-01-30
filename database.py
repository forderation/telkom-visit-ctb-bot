import sqlite3
from ddl import ddl
import hashlib


class DBHelper:

    def __init__(self, dbname="visit_ctb2.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.VISIT_HIST = "VISIT_HIST"
        self.PHOTO = "PHOTO_VISIT"
        self.ADMIN = "ADMIN"
        self.CATEGORY = "CATEGORY_RESULT"
        self.STATE = "STATE_VISIT"
        self.RESULT = "VISIT_RESULT"
        self.VISITOR = "VISITOR"

    def setup(self):
        self.conn.executescript(ddl)
        self.conn.commit()

    def seeder_admin(self, pin):
        cursor = self.conn.cursor()
        hashed_pin = hashlib.md5(str(pin).encode('utf-8')).hexdigest()
        query_delete = "DELETE FROM " + self.ADMIN + " WHERE id = 1"
        cursor.execute(query_delete)
        cursor.execute(
            "INSERT INTO " + self.ADMIN + " (id,password) VALUES (1,'{}')".format(hashed_pin)
        )
        self.conn.commit()

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
                self.VISIT_HIST + \
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

    def get_state(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name_state FROM " + self.STATE)
        return cursor.fetchall()

    def get_state_with_id(self, id_):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name_state FROM " + self.STATE + " WHERE id = " + id_)
        return cursor.fetchone()[0]

    def get_category_visit_with_state_id(self, state_id):
        cursor = self.conn.cursor()
        query = "SELECT id, name_category, code_category FROM " + self.CATEGORY + " WHERE id_state = " + state_id
        cursor.execute(query)
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
        cursor.execute(query)
        if not cursor.fetchall():
            query = "INSERT INTO " + self.VISITOR + \
                    " (id_visitor, name_visitor, username, total_submit, last_submit) " + \
                    "VALUES (?,?,?,1,(SELECT datetime('now','localtime')))"
            cursor.execute(query, (user_id, fullname, username))
        else:
            query = "UPDATE " + self.VISITOR + \
                    " SET name_visitor = '" + fullname + "', username = '" + username + \
                    "', total_submit = " \
                    "total_submit+1, last_submit " \
                    "= (SELECT datetime('now','localtime')) WHERE id_visitor = {}".format(user_id)
            cursor.execute(query)
        self.conn.commit()

    def get_report_hist(self):
        vh = self.VISIT_HIST
        query = "SELECT * FROM " + vh + " JOIN " + self.VISITOR + \
                " ON {}.id_visitor = {}.id_visitor JOIN ".format(vh, self.VISITOR) + self.STATE + \
                " ON {}.id_state = {}.id JOIN ".format(vh, self.STATE) + \
                self.CATEGORY + " ON {}.id_category = {}.id JOIN ".format(vh, self.CATEGORY) + \
                self.RESULT + " ON {}.id_result = {}.id".format(vh, self.RESULT)
        cursor = self.conn.cursor()
        cursor_ph = self.conn.cursor()
        cursor.execute(query)
        result = []
        res_photos = []
        for row in cursor.fetchall():
            id_hist = row[0]
            query = "SELECT photo_path FROM " + self.PHOTO + " WHERE id_visit = '" + str(id_hist) + "'"
            cursor_ph.execute(query)
            photos = cursor_ph.fetchall()
            date = row[1].split(" ")[0]
            nip = row[2]
            other_desc = row[3]
            name_visitor = row[10]
            state_visit = row[15]
            category_visit = row[18]
            result_visit = row[22]
            visit_code = row[16] + row[19] + row[23]
            result.append(
                [date, nip, visit_code, other_desc, name_visitor, state_visit,
                 category_visit, result_visit]
            )
            res_photos.append([ph[0] for ph in photos])
        return result, res_photos

    def get_list_visitor(self):
        query = "SELECT id_visitor, name_visitor, username, total_submit, last_submit FROM " + self.VISITOR
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def get_category_visit(self):
        query = "SELECT {}.id, name_category, {}.name_state FROM ".format(self.CATEGORY, self.STATE) + \
                self.CATEGORY + " JOIN " + self.STATE + " ON {}.id_state = {}.id".format(self.CATEGORY, self.STATE)
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def get_category_name(self, category_id):
        query = "SELECT name_category FROM " + self.CATEGORY + " WHERE id = " + str(category_id)
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor.fetchone()[0]

    def get_visit_result(self, category_id):
        query = "SELECT id, name_result, code_result FROM " + self.RESULT + " WHERE id_category = " + str(category_id)
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def check_exist_code_rv(self, category_id, result_code):
        cursor = self.conn.cursor()
        query = "SELECT * FROM " + self.RESULT + " WHERE id_category = " + str(category_id) + \
                " AND code_result = '" + str(result_code) + "'"
        cursor.execute(query)
        if not (cursor.fetchone() is None):
            return True
        return False

    def check_exist_code_cr(self, state_id, category_code):
        cursor = self.conn.cursor()
        query = "SELECT * FROM " + self.CATEGORY + " WHERE code_category = '" + str(category_code) + "' AND id_state = " + state_id
        cursor.execute(query)
        if cursor.fetchone() is None:
            return False
        return True

    def add_result_visit(self, category_id, code_vs, name_vs):
        cursor = self.conn.cursor()
        query = "SELECT id_state FROM " + self.CATEGORY + " WHERE id = " + str(category_id)
        id_state = cursor.execute(query).fetchone()[0]
        query = "INSERT INTO " + self.RESULT + " (name_result, code_result, id_category, id_state) VALUES (?,?,?,?)"
        cursor.execute(query, (name_vs, code_vs, category_id, id_state))
        self.conn.commit()

    def add_category(self, state_id, name_category, code_category):
        cursor = self.conn.cursor()
        query = "INSERT INTO " + self.CATEGORY + " (name_category, code_category, id_state) VALUES (?,?,?)"
        cursor.execute(query, (name_category, code_category, state_id))
        self.conn.commit()

    def check_exist_id_rv(self, id_, category_id):
        cursor = self.conn.cursor()
        query = "SELECT * FROM " + self.RESULT + " WHERE id = " + id_ + " AND id_category = " + category_id
        cursor.execute(query)
        if cursor.fetchone() is None:
            return False
        return True

    def rename_result_visit(self, id_, new_name):
        cursor = self.conn.cursor()
        query = "UPDATE " + self.RESULT + " SET name_result = '" + new_name + "' WHERE id = " + id_
        cursor.execute(query)
        self.conn.commit()

    def recode_result_visit(self, id_, new_code):
        cursor = self.conn.cursor()
        query = "UPDATE " + self.RESULT + " SET code_result = '" + new_code + "' WHERE id = " + id_
        cursor.execute(query)
        self.conn.commit()

    def remove_result_visit(self, id_):
        cursor = self.conn.cursor()
        query = "DELETE FROM " + self.RESULT + " WHERE id = " + id_
        cursor.execute(query)
        self.conn.commit()


db = DBHelper()
# print(db.get_list_visitor())
# db.seeder_admin(1)
# id_, name = zip(*db.get_category_visit())
# print(f"{id_}: {name}")
# print(db.get_category_visit())
# print(db.check_exist_code_rv(1, 12))
# db.add_result_vist(1)

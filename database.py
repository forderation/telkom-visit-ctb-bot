from ddl import ddl
import hashlib
import mysql.connector as connector


class DBHelper:
    def __init__(self, dbname="telkom-visit-ctb-2"):
        self.dbname = dbname
        self.db = None
        self.VISIT_HIST = "VISIT_HIST"
        self.PHOTO = "PHOTO_VISIT"
        self.ADMIN = "ADMIN"
        self.CATEGORY = "CATEGORY_RESULT"
        self.STATE = "STATE_VISIT"
        self.RESULT = "VISIT_RESULT"
        self.VISITOR = "VISITOR"
        self.TODO_LIST = "TODO_LIST"
        self.VISITOR_TODO = "VISITOR_TODO"
        self.buid_connection()

    def buid_connection(self):
        while True:
            try:
                self.db = connector.connect(
                    host="localhost",
                    user="root",
                    passwd="",
                    database=self.dbname
                )
                print("Connected with database")
                break
            except connector.errors.InterfaceError:
                print("Connection error, try to connecting again")

    def setup(self):
        cursor = self.db.cursor(buffered=True)
        cursor.executemany(ddl)
        self.db.commit()

    def seeder_admin(self, pin):
        cursor = self.db.cursor(buffered=True)
        hashed_pin = hashlib.md5(str(pin).encode('utf-8')).hexdigest()
        query_delete = "DELETE FROM " + self.ADMIN + " WHERE id = 1"
        cursor.execute(query_delete)
        cursor.execute(
            "INSERT INTO " + self.ADMIN + " (id,password) VALUES (1,'{}')".format(hashed_pin)
        )
        self.db.commit()

    def check_admin_password(self, pin, username):
        cursor = self.db.cursor(buffered=True)
        hashed_pin = hashlib.md5(str(pin).encode('utf-8')).hexdigest()
        query_check_pass = "SELECT * FROM " + self.ADMIN + " WHERE password = '" + hashed_pin + "' AND id = 1"
        cursor.execute(query_check_pass)
        admin = cursor.fetchone()
        if admin is None:
            return False
        else:
            query_update = "UPDATE " + self.ADMIN + " SET username = '" + username + \
                           "', last_login = (SELECT CURRENT_TIMESTAMP()) WHERE id = 1 "
            cursor.execute(query_update)
            self.db.commit()
            return True

    def get_token(self):
        cursor = self.db.cursor(buffered=True)
        query = "SELECT token FROM bot_token WHERE id = 1"
        cursor.execute(query)
        return cursor.fetchone()

    def change_token(self, token):
        cursor = self.db.cursor(buffered=True)
        query = "UPDATE bot_token SET token = '" + token + "' WHERE id = 1"
        cursor.execute(query)
        self.db.commit()

    def insert_visit(self, user_id, user_session):
        cursor = self.db.cursor(buffered=True)
        nip = user_session["nip"]
        query = "SELECT * FROM " + self.VISITOR_TODO + " WHERE id_visitor = '{}' ".format(user_id) + \
                "AND date=(SELECT CURRENT_DATE())"
        cursor.execute(query)
        if len(cursor.fetchall()) == 0:
            query = "INSERT INTO " + self.VISITOR_TODO + \
                    " (id_visitor, date, vtd_last_submit) VALUES ('{}',(SELECT CURRENT_DATE()),".format(user_id) + \
                    "(SELECT CURRENT_TIME()))"
            cursor.execute(query)
            self.db.commit()
        query = "SELECT nip FROM " + self.TODO_LIST + " WHERE id_visitor = '{}' ".format(user_id) + \
                "AND is_submit = 0 AND nip = '{}'".format(nip)
        cursor.execute(query)
        if len(cursor.fetchall()) != 0:
            update = "UPDATE " + self.VISITOR_TODO + " SET todo_done = todo_done + 1, vtd_last_submit = " + \
                     "(SELECT CURRENT_TIME()) WHERE DATE = (SELECT CURRENT_DATE())" + \
                     " AND id_visitor = '{}'".format(user_id)
            cursor.execute(update)
            self.db.commit()
            update_todo = "UPDATE " + self.TODO_LIST + " SET is_submit = 1 WHERE TD_DATE = " + \
                          "(SELECT CURRENT_DATE()) AND nip = '{}' ".format(nip) + \
                          "AND id_visitor = '{}'".format(user_id)
            cursor.execute(update_todo)
            self.db.commit()
            get_wait_todo = "SELECT COUNT(id_todo) FROM {} WHERE id_visitor ".format(self.TODO_LIST) + \
                            "= '{}' AND is_submit = 0 AND TD_DATE = (SELECT CURRENT_DATE())".format(user_id)
            cursor.execute(get_wait_todo)
            wait_todo = cursor.fetchone()[0]
            update = "UPDATE " + self.VISITOR_TODO + " SET todo_wait = {} ".format(wait_todo) + \
                     "WHERE DATE = (SELECT CURRENT_DATE())" + \
                     " AND id_visitor = '{}'".format(user_id)
            cursor.execute(update)
            self.db.commit()
        else:
            update = "UPDATE " + self.VISITOR_TODO + " SET outer_submit = outer_submit + 1, vtd_last_submit = " + \
                     "(SELECT CURRENT_TIME()) WHERE DATE = (SELECT CURRENT_DATE())" + \
                     " AND id_visitor = '{}'".format(user_id)
            cursor.execute(update)
            self.db.commit()
        query = "INSERT INTO " + \
                self.VISIT_HIST + \
                " (hs_date_submit, nip, other_desc, id_state, id_category, id_result, id_visitor)" + \
                "VALUES ((SELECT CURRENT_TIMESTAMP()),%s,%s,%s,%s,%s,%s)"
        state, category, result = user_session["idx_visit_code"]
        args = (
            nip, user_session["other_desc"], state, category, result, user_id
        )
        cursor.execute(query, args)
        id_visit = cursor.lastrowid
        self.db.commit()
        return id_visit

    def insert_photo(self, user_id, id_visit, photo_paths):
        cursor = self.db.cursor(buffered=True)
        for photo_path in photo_paths:
            query = "INSERT INTO " + self.PHOTO + \
                    " (photo_path, id_visitor, id_hist, ph_date_submit) VALUES (%s,%s,%s,(SELECT CURRENT_TIMESTAMP())) "
            args = (photo_path, user_id, id_visit)
            cursor.execute(query, args)
        self.db.commit()

    def get_state(self):
        cursor = self.db.cursor(buffered=True)
        cursor.execute("SELECT id_state, name_state, code_state FROM " + self.STATE)
        return cursor.fetchall()

    def get_state_with_id(self, id_):
        cursor = self.db.cursor(buffered=True)
        cursor.execute("SELECT name_state FROM " + self.STATE + " WHERE id_state = " + id_)
        return cursor.fetchone()[0]

    def get_category_visit_with_state_id(self, state_id):
        cursor = self.db.cursor(buffered=True)
        query = "SELECT id_category, name_category, code_category FROM " + self.CATEGORY + " WHERE id_state = " + state_id
        cursor.execute(query)
        return cursor.fetchall()

    def get_detail_code(self, id_state):
        cursor = self.db.cursor(buffered=True)
        query = "SELECT name_result,{}.code_state, {}.code_category, code_result FROM ".format(self.STATE,
                                                                                               self.CATEGORY) \
                + self.RESULT + " JOIN " + self.STATE + \
                " ON {}.id_state={}.id_state JOIN ".format(self.RESULT, self.STATE) + self.CATEGORY + \
                " ON {}.id_category={}.id_category ".format(self.RESULT, self.CATEGORY) + \
                " WHERE {}.id_state = '{}'".format(self.RESULT, id_state)
        cursor.execute(query)
        return cursor.fetchall()

    def get_all_code(self):
        cursor = self.db.cursor(buffered=True)
        query = "SELECT {}.code_state, {}.code_category, code_result, {}.id_result, {}.id_state, {}.id_category, " \
                "{}.name_state, {}.name_category ,{}.name_result FROM ".format(self.STATE, self.CATEGORY, self.RESULT,
                                                                               self.RESULT, self.RESULT, self.STATE,
                                                                               self.CATEGORY, self.RESULT) + \
                self.RESULT + " JOIN " + self.STATE + " ON {}.id_state={}.id_state JOIN ".format(self.RESULT,
                                                                                                 self.STATE) + \
                self.CATEGORY + " ON {}.id_category={}.id_category ".format(self.RESULT, self.CATEGORY)
        cursor.execute(query)
        return cursor.fetchall()

    def sync_user_input(self, user_id, fullname, username):
        cursor = self.db.cursor(buffered=True)
        query = "SELECT * FROM " + self.VISITOR + " WHERE id_visitor='" + user_id + "'"
        cursor.execute(query)
        if not cursor.fetchall():
            query = "INSERT INTO " + self.VISITOR + \
                    " (id_visitor, name_visitor, username, total_submit, vs_last_submit) " + \
                    "VALUES (%s,%s,%s,0,(SELECT CURRENT_TIMESTAMP()))"
            cursor.execute(query, (user_id, fullname, username))
            self.db.commit()

    def increment_submit(self, user_id, fullname, username):
        cursor = self.db.cursor(buffered=True)
        self.sync_user_input(user_id, fullname, username)
        query = "UPDATE " + self.VISITOR + \
                " SET name_visitor = '" + fullname + "', username = '" + username + \
                "', total_submit = " \
                "total_submit+1, vs_last_submit " \
                "= (SELECT CURRENT_TIMESTAMP()) WHERE id_visitor = {}".format(user_id)
        cursor.execute(query)
        self.db.commit()

    def get_report_hist(self, date_start=None, date_end=None):
        vh = self.VISIT_HIST
        query = "SELECT id_hist, hs_date_submit, nip, other_desc, name_visitor, name_state, name_category, name_result, code_state, code_category, code_result FROM " + vh + " JOIN " + self.VISITOR + \
                " ON {}.id_visitor = {}.id_visitor JOIN ".format(vh, self.VISITOR) + self.STATE + \
                " ON {}.id_state = {}.id_state JOIN ".format(vh, self.STATE) + \
                self.CATEGORY + " ON {}.id_category = {}.id_category JOIN ".format(vh, self.CATEGORY) + \
                self.RESULT + " ON {}.id_result = {}.id_result ".format(vh, self.RESULT)
        if not (date_start is None) and not (date_end is None):
            query += "WHERE {}.hs_date_submit BETWEEN '{}' AND '{}'".format(self.VISIT_HIST, date_start, date_end)
        cursor = self.db.cursor(buffered=True)
        cursor_ph = self.db.cursor(buffered=True)
        cursor.execute(query)
        result = []
        res_photos = []
        for row in cursor.fetchall():
            id_hist = row[0]
            query = "SELECT photo_path FROM " + self.PHOTO + " WHERE id_hist = '{}'".format(id_hist)
            cursor_ph.execute(query)
            photos = cursor_ph.fetchall()
            date = row[1]
            nip = row[2]
            other_desc = row[3]
            name_visitor = row[4]
            state_visit = row[5]
            category_visit = row[6]
            result_visit = row[7]
            visit_code = str(row[8]) + str(row[9]) + str(row[10])
            result.append(
                [date, nip, visit_code, other_desc, name_visitor, state_visit,
                 category_visit, result_visit]
            )
            res_photos.append([ph[0] for ph in photos])
        return result, res_photos

    def get_list_visitor(self, date_start=None, date_end=None):
        query = "SELECT id_visitor, name_visitor, username, total_submit, vs_last_submit FROM " + self.VISITOR
        if not (date_start is None) and not (date_end is None):
            query += " WHERE vs_last_submit BETWEEN '{}' AND '{}'".format(date_start, date_end)
        cursor = self.db.cursor(buffered=True)
        cursor.execute(query)
        return cursor.fetchall()

    def get_category_visit(self):
        query = "SELECT {}.id_category, name_category, {}.name_state FROM ".format(self.CATEGORY, self.STATE) + \
                self.CATEGORY + " JOIN " + self.STATE + " ON {}.id_state = {}.id_state".format(self.CATEGORY,
                                                                                               self.STATE)
        cursor = self.db.cursor(buffered=True)
        cursor.execute(query)
        return cursor.fetchall()

    def get_category_name(self, category_id):
        query = "SELECT name_category FROM " + self.CATEGORY + " WHERE id_category = " + str(category_id)
        cursor = self.db.cursor(buffered=True)
        cursor.execute(query)
        return cursor.fetchone()[0]

    def get_visit_result(self, category_id):
        query = "SELECT id_result, name_result, code_result FROM " + self.RESULT + " WHERE id_category = " + str(
            category_id)
        cursor = self.db.cursor(buffered=True)
        cursor.execute(query)
        return cursor.fetchall()

    def check_exist_code_rv(self, category_id, result_code):
        cursor = self.db.cursor(buffered=True)
        query = "SELECT * FROM " + self.RESULT + " WHERE id_category = " + str(category_id) + \
                " AND code_result = '" + str(result_code) + "'"
        cursor.execute(query)
        if not (cursor.fetchone() is None):
            return True
        return False

    def check_exist_code_cr(self, state_id, category_code):
        cursor = self.db.cursor(buffered=True)
        query = "SELECT * FROM " + self.CATEGORY + " WHERE code_category = '" + str(
            category_code) + "' AND id_state = " + state_id
        cursor.execute(query)
        if cursor.fetchone() is None:
            return False
        return True

    def check_exist_code_sv(self, state_code):
        cursor = self.db.cursor(buffered=True)
        query = "SELECT * FROM " + self.STATE + " WHERE code_state = '" + str(state_code) + "'"
        cursor.execute(query)
        if cursor.fetchone() is None:
            return False
        return True

    def add_result_visit(self, category_id, code_vs, name_vs):
        cursor = self.db.cursor(buffered=True)
        query = "SELECT id_state FROM " + self.CATEGORY + " WHERE id_category = " + str(category_id)
        cursor.execute(query)
        id_state = cursor.fetchone()[0]
        query = "INSERT INTO " + self.RESULT + " (name_result, code_result, id_category, id_state) VALUES (%s,%s,%s,%s)"
        cursor.execute(query, (name_vs, code_vs, category_id, id_state))
        self.db.commit()

    def add_category(self, state_id, name_category, code_category):
        cursor = self.db.cursor(buffered=True)
        query = "INSERT INTO " + self.CATEGORY + " (name_category, code_category, id_state) VALUES (%s,%s,%s)"
        cursor.execute(query, (name_category, code_category, state_id))
        self.db.commit()

    def add_state(self, name_state, code_state):
        cursor = self.db.cursor(buffered=True)
        query = "INSERT INTO " + self.STATE + " (name_state, code_state) VALUES (%s,%s)"
        cursor.execute(query, (name_state, code_state))
        self.db.commit()

    def check_exist_id_rv(self, id_, category_id):
        cursor = self.db.cursor(buffered=True)
        query = "SELECT * FROM " + self.RESULT + " WHERE id_result = " + id_ + " AND id_category = " + category_id
        cursor.execute(query)
        if cursor.fetchone() is None:
            return False
        return True

    def check_exist_id_cr(self, id_, state_id):
        cursor = self.db.cursor(buffered=True)
        query = "SELECT * FROM " + self.CATEGORY + " WHERE id_category = " + str(id_) + " AND id_state = " + str(
            state_id)
        cursor.execute(query)
        if cursor.fetchone() is None:
            return False
        return True

    def check_exist_id_sv(self, state_id):
        cursor = self.db.cursor(buffered=True)
        query = "SELECT * FROM " + self.STATE + " WHERE id_state = " + str(state_id)
        cursor.execute(query)
        if cursor.fetchone() is None:
            return False
        return True

    def rename_result_visit(self, id_, new_name):
        cursor = self.db.cursor(buffered=True)
        query = "UPDATE " + self.RESULT + " SET name_result = '" + new_name + "' WHERE id_result = " + id_
        cursor.execute(query)
        self.db.commit()

    def rename_category_visit(self, id_, new_name):
        cursor = self.db.cursor(buffered=True)
        query = "UPDATE " + self.CATEGORY + " SET name_category = '" + new_name + "' WHERE id_category = " + str(id_)
        cursor.execute(query)
        self.db.commit()

    def rename_state_visit(self, id_, new_name):
        cursor = self.db.cursor(buffered=True)
        query = "UPDATE " + self.STATE + " SET name_state = '" + new_name + "' WHERE id_state = " + str(id_)
        cursor.execute(query)
        self.db.commit()

    def recode_category_visit(self, id_, new_code):
        cursor = self.db.cursor(buffered=True)
        query = "UPDATE " + self.CATEGORY + " SET code_category = '" + new_code + "' WHERE id_category = " + str(id_)
        cursor.execute(query)
        self.db.commit()

    def recode_state_visit(self, id_, new_code):
        cursor = self.db.cursor(buffered=True)
        query = "UPDATE " + self.STATE + " SET code_state = '" + new_code + "' WHERE id_state = " + str(id_)
        cursor.execute(query)
        self.db.commit()

    def recode_result_visit(self, id_, new_code):
        cursor = self.db.cursor(buffered=True)
        query = "UPDATE " + self.RESULT + " SET code_result = '" + new_code + "' WHERE id_result = " + id_
        cursor.execute(query)
        self.db.commit()

    def remove_result_visit(self, id_):
        cursor = self.db.cursor(buffered=True)
        query = "DELETE FROM " + self.RESULT + " WHERE id_result = " + id_
        cursor.execute(query)
        self.db.commit()

    def remove_category_visit(self, id_):
        cursor = self.db.cursor(buffered=True)
        query = "DELETE FROM " + self.CATEGORY + " WHERE id_category = " + id_
        cursor.execute(query)
        self.db.commit()

    def remove_state_visit(self, id_):
        cursor = self.db.cursor(buffered=True)
        query = "DELETE FROM " + self.STATE + " WHERE id_state = " + id_
        cursor.execute(query)
        self.db.commit()

    def insert_todo_list(self, list_todo, user_id, fullname, username):
        cursor = self.db.cursor(buffered=True)
        self.sync_user_input(user_id, fullname, username)
        for nip in list_todo:
            check_query = "SELECT * FROM " + self.TODO_LIST + " WHERE nip = '{}' ".format(nip) + \
                          "AND id_visitor = '{}' AND td_date = (SELECT CURRENT_DATE())".format(user_id)
            cursor.execute(check_query)
            if len(cursor.fetchall()):
                continue
            query = "INSERT INTO " + self.TODO_LIST + " (nip, td_date, id_visitor, is_submit) " + \
                    "VALUES (%s,(SELECT CURRENT_DATE()),%s, 0)"
            cursor.execute(query, (nip, user_id))
            self.db.commit()

    def get_report_todo(self, date_start, date_end=None):
        cursor = self.db.cursor(buffered=True)
        query = "SELECT {}.id_visitor, {}.name_visitor, ".format(self.VISITOR, self.VISITOR) + \
                "{}.username, date, {}.vtd_last_submit, ".format(self.VISITOR, self.VISITOR_TODO) + \
                "todo_done, todo_wait, outer_submit FROM {} JOIN {} ON ".format(self.VISITOR_TODO, self.VISITOR) + \
                "{}.id_visitor = {}.id_visitor ".format(self.VISITOR_TODO, self.VISITOR)
        if date_end is None:
            query += "WHERE date = '{}'".format(date_start)
        else:
            query += "WHERE date BETWEEN '{}' AND '{}'".format(date_start, date_end)
        cursor.execute(query)
        return cursor.fetchall()
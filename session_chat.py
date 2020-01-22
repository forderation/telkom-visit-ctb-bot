class Session:
    """
    isi session adalah berupa dictionary (tipe key : value)
    contoh _session = {
    "muzaki" : {
        "is_visit_input": True,
        "is_photo_input": False,
        "fullname": fullname,
        "nip": nip,
        "date": date,
        "voc_code": voc_code,
        "voc_state": voc_state,
        "result_voc": result_voc,
        "other_desc": other_desc,
        "photo": []
    }
    }
    """

    def __init__(self):
        self._session = {}
        self.input_vs = "input_visit"

    def is_user_active(self, user_id):
        return True if user_id in self._session else False

    def remove_user(self, user_id):
        if self.is_user_active(user_id):
            del self._session[user_id]
            return True
        return False

    def add_user(self, user_id, fullname, nip, date, voc_code, voc_state, result_voc, other_desc):
        self._session[user_id] = {
            "is_visit_input": True,
            "is_photo_input": False,
            "fullname": fullname,
            "nip": nip,
            "date": date,
            "voc_code": voc_code,
            "voc_state": voc_state,
            "result_voc": result_voc,
            "other_desc": other_desc,
            "photo": []
        }

    def add_photo(self, user_id, photo_id):
        self._session[user_id]["photo"].append(photo_id)
        self._session[user_id]["is_photo_input"] = True
        return True

    def is_visited(self, user_id):
        return self._session[user_id]["is_visit_input"]

    def get_desc_user(self, user_id):
        user = self._session[user_id]
        fullname = user["fullname"]
        nip = user["nip"]
        date = user["date"]
        voc_code = user["voc_code"]
        voc_state = user["voc_state"]
        result_voc = user["result_voc"]
        other_desc = user["other_desc"]
        msg = "nama penginput : {}" \
              "\nnomor internet pelanggan : {}" \
              "\ntanggal input : {}" \
              "\nkode visit : {}" \
              "\nstatus visit : {}" \
              "\nhasil visit : {}" \
              "\nketerangan lain : {}" \
              "\njangan lupa untuk mengupload foto visit dan melakukan /submit_visit".format(fullname, nip, date,
                                                                                             voc_code, voc_state,
                                                                                             result_voc, other_desc)
        return msg

    def get_photo(self, user_id):
        """
        :param user_id:
        :return list [] : List of photo url from user
        """
        return self._session[user_id]["photo"]

    def is_submitted_photo(self, user_id):
        return self._session[user_id]["is_photo_input"]

    def get_session(self, user_id):
        return self._session[user_id]

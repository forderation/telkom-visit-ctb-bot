ddl = """--
-- File generated with SQLiteStudio v3.2.1 on Thu Jan 23 11:45:29 2020
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: ADMIN
DROP TABLE IF EXISTS ADMIN;

CREATE TABLE ADMIN (
    id         INTEGER PRIMARY KEY,
    password   TEXT    NOT NULL,
    last_login DATE,
    username   TEXT
);


-- Table: CATEGORY_RESULT
DROP TABLE IF EXISTS CATEGORY_RESULT;

CREATE TABLE CATEGORY_RESULT (
    id            INTEGER PRIMARY KEY AUTOINCREMENT
                          NOT NULL,
    name_category TEXT    NOT NULL,
    code_category TEXT    NOT NULL
                          UNIQUE,
    id_state      INTEGER REFERENCES STATE_VISIT (id) ON DELETE CASCADE
                                                      ON UPDATE CASCADE
                          NOT NULL
);


-- Table: PHOTO_VISIT
DROP TABLE IF EXISTS PHOTO_VISIT;

CREATE TABLE PHOTO_VISIT (
    id            INTEGER PRIMARY KEY,
    tele_photo_id TEXT    NOT NULL,
    id_visitor    INTEGER NOT NULL
                          REFERENCES VISITOR (id),
    id_visit      INTEGER NOT NULL
                          REFERENCES VISIT_HIST (id) ON DELETE RESTRICT
                                                     ON UPDATE RESTRICT,
    date_submit   DATE,
    FOREIGN KEY (
        id_visit
    )
    REFERENCES TABLE_VISIT (visit_id) 
);

-- Table: STATE_VISIT
DROP TABLE IF EXISTS STATE_VISIT;

CREATE TABLE STATE_VISIT (
    id         INTEGER PRIMARY KEY AUTOINCREMENT
                       NOT NULL,
    name_state TEXT    NOT NULL,
    code_state INTEGER UNIQUE
                       NOT NULL
);

-- Table: VISIT_HIST
DROP TABLE IF EXISTS VISIT_HIST;

CREATE TABLE VISIT_HIST (
    id          INTEGER PRIMARY KEY
                        NOT NULL,
    date_submit DATE    NOT NULL,
    nip         TEXT    NOT NULL,
    other_desc  TEXT,
    id_state    INTEGER REFERENCES STATE_VISIT (id) ON DELETE RESTRICT
                                                    ON UPDATE RESTRICT,
    id_category INTEGER REFERENCES CATEGORY_RESULT (id),
    id_result   INTEGER REFERENCES VISIT_RESULT (id),
    id_visitor  INTEGER REFERENCES VISITOR (id) ON DELETE RESTRICT
                                                ON UPDATE RESTRICT
);

-- Table: VISIT_RESULT
DROP TABLE IF EXISTS VISIT_RESULT;

CREATE TABLE VISIT_RESULT (
    id          INTEGER PRIMARY KEY AUTOINCREMENT
                        NOT NULL,
    name_result TEXT    NOT NULL,
    code_result TEXT    NOT NULL
                        UNIQUE,
    id_category INTEGER REFERENCES CATEGORY_RESULT (id) ON DELETE RESTRICT
                                                        ON UPDATE RESTRICT
                        NOT NULL,
    id_state    INTEGER REFERENCES STATE_VISIT (id) ON DELETE RESTRICT
                                                    ON UPDATE RESTRICT
                        NOT NULL
);

-- Table: VISITOR
DROP TABLE IF EXISTS VISITOR;

CREATE TABLE VISITOR (
    id           INTEGER PRIMARY KEY AUTOINCREMENT
                         NOT NULL,
    id_visitor   BIGINT  UNIQUE
                         NOT NULL,
    name_visitor TEXT    NOT NULL,
    username     TEXT    NOT NULL,
    total_submit INTEGER DEFAULT (0),
    last_submit  DATE    NOT NULL
);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
"""

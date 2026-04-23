import sqlite3
from datetime import datetime
import logging

def connect_db():
    db = sqlite3.connect("flsite.db")
    db.row_factory = sqlite3.Row
    return db

def create_db():
    db = connect_db()
    with open("sq_db.sql", "r") as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

class FDataBase:
    def __init__(self, db: sqlite3.Connection):
        self.__db = db
        self.__cur = self.__db.cursor()
    
    def createUser(self, name, email, password):
        sql = """INSERT INTO users (name, email, pwd) VALUES (?, ?, ?)"""
        sql2 = f"""SELECT id FROM users WHERE email = '{email}'"""
        try:
            self.__cur.execute(sql, (name, email, password))
            self.__db.commit()
            self.__cur.execute(sql2)
            res = self.__cur.fetchone()
            if res: return res["id"]
        except Exception as e:
            logging.error("Cannot create user: " + str(e))
        return -1

    def getUserByID(self, id):
        sql = f"""SELECT * FROM users WHERE id = {id}"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if res: return res
        except Exception as e:
            logging.error("Can't get user by id: " + str(e))
        return None

    def getUserByEmail(self, email):
        sql = f"""SELECT * FROM users WHERE email = '{email}'"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if res: return res
        except Exception as e:
            logging.error("Can't get user by email: " + str(e))
        return None

    def isParentFor(self, userID, parentID) -> bool:
        sql = f"""SELECT COUNT(*) AS cnt FROM parentStudents WHERE studentID = '{userID}' AND parentID = '{parentID}'"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if res: return res["cnt"] > 0
        except Exception as e:
            logging.error("Cannot check if user is a parent: " + str(e))
        return False

    def isTeacherFor(self, userID, teacherID) -> bool:
        sql = f"""SELECT COUNT(*) AS cnt FROM teacherStudents WHERE studentID = '{userID}' AND teacherID = '{teacherID}'"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if res: return res["cnt"] > 0
        except Exception as e:
            logging.error("Cannot check if user is a teacher: " + str(e))
        return False

    def addTask(self, desc, deadline: datetime, userID, createdByID, priority: 0) -> bool:
        """priority: 0 - default; 1 - medium; 2 - high"""
        sql = f"""INSERT INTO tasks (task, priority, deadline, ownerID, createdByID, isDone) VALUES (?, ?, ?, ?, ?, ?)"""
        try:
            self.__cur.execute(sql, (desc, priority, deadline.strftime("%Y:%m:%d %H:%M:%S"), userID, createdByID, 0))
            self.__db.commit()
            return True
        except Exception as e:
            logging.error("Can't create task: " + str(e))
        return False

    def getTasksOnDate(self, date: datetime):
        dateAfter = datetime(date.year, date.month, date.day, 23, 59, 59)
        format = "%Y:%m:%d %H:%M:%S"
        sql = f"""SELECT id, task, priority, deadline, ownerID, createdByID, isDone FROM tasks 
        WHERE deadline >= '{date.strftime(format)}' AND deadline <= '{dateAfter.strftime(format)}' 
        ORDER BY deadline ASC, priority DESC"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except Exception as e:
            logging.error("Cannot get user tasks: " + str(e))
        return []

    def getTaskByID(self, id):
        # TODO make protection from direct access (only user who created may access their personal tasks)
        sql = f"""SELECT * FROM tasks WHERE id = '{id}'"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if res: return res
        except Exception as e:
            logging.error("Cannot get task by id: " + str(e))
        return None

    def undoTask(self, id):
        # TODO make protection from direct access (only user who created may access their personal tasks)
        sql = f"""UPDATE tasks SET isDone = '0' WHERE id = '{id}'"""
        try:
            self.__cur.execute(sql)
            self.__db.commit()
            return True
        except Exception as e:
            logging.error("Cannot undo task: " + str(e))
        return False

    def markDoneTask(self, id):
        # TODO make protection from direct access (only user who created may access their personal tasks)
        sql = f"""UPDATE tasks SET isDone = '1' WHERE id = '{id}'"""
        try:
            self.__cur.execute(sql)
            self.__db.commit()
            return True
        except Exception as e:
            logging.error("Cannot mark done task: " + str(e))
        return False


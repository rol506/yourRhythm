import sqlite3
from datetime import datetime
import logging

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def connect_db():
    db = sqlite3.connect("flsite.db")
    db.row_factory = dict_factory
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
        self.__dateFormat = "%Y-%m-%d %H:%M:%S";
    
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
            self.__cur.execute(sql, (desc, priority, deadline.strftime(self.__dateFormat), userID, createdByID, 0))
            self.__db.commit()
            return True
        except Exception as e:
            logging.error("Can't create task: " + str(e))
        return False

    def addTaskClass(self, desc, deadline: datetime, classID, createdByID, priority: 0) -> bool:
        """priority: 0 - default; 1 - medium; 2 - high"""
        sql = f"""SELECT studentID from teacherStudents WHERE classID = {classID}"""
        sql2 = f"""INSERT INTO tasks (task, priority, deadline, ownerID, createdByID, isDone) VALUES (?, ?, ?, ?, ?, ?)"""
        try:
            self.__cur.execute(sql)
            l = self.__cur.fetchall()
            if len(l) == 0: return True
            for stud in l:
                self.__cur.execute(sql2, (desc, priority, deadline.strftime(self.__dateFormat), stud["studentID"], createdByID, 0))
            self.__db.commit()
            return True
        except Exception as e:
            logging.error("Can't create task: " + str(e))
        return False    

    def getTasksOnDate(self, date: datetime, userID):
        dateAfter = datetime(date.year, date.month, date.day, 23, 59, 00)
        date = datetime(date.year, date.month, date.day, 00, 00, 00)
        sql = f"""SELECT id, task, priority, deadline, ownerID, createdByID, isDone FROM tasks 
        WHERE deadline >= '{date.strftime(self.__dateFormat)}' AND deadline <= '{dateAfter.strftime(self.__dateFormat)}' AND ownerID = {userID} 
        ORDER BY deadline ASC, priority DESC"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except Exception as e:
            logging.error("Cannot get user tasks: " + str(e))
        return []

    def getTasksOnWeek(self, date, userID):
        dateAfter = datetime(date.year, date.month, date.day+6, 23, 59, 00)
        date = datetime(date.year, date.month, date.day, 23, 59, 00)
        sql = f"""SELECT id, task, priority, deadline, ownerID, createdByID, isDone FROM tasks 
        WHERE deadline >= '{date.strftime(self.__dateFormat)}' AND deadline <= '{dateAfter.strftime(self.__dateFormat)}' AND ownerID = {userID} 
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
        sql = f"""UPDATE tasks SET isDone = '1', completionDate = datetime() WHERE id = '{id}'"""
        try:
            self.__cur.execute(sql)
            self.__db.commit()
            return True
        except Exception as e:
            logging.error("Cannot mark done task: " + str(e))
        return False

    def getCompletedTasks(self, userID):
        sql = f"""SELECT COUNT(*) as cnt FROM tasks WHERE ownerID = '{userID}' AND isDone > 0"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if res: return res["cnt"]
        except Exception as e:
            logging.error("Cannot fetch completed task count: " + str(e))
        return 0

    def getTaskCount(self, userID):
        sql = f"""SELECT COUNT(*) as cnt FROM tasks WHERE ownerID = '{userID}'"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if res: return res["cnt"]
        except Exception as e:
            logging.error("Cannot fetch task count: " + str(e))
        return 0

    def getCompletionStats(self, userID, date:datetime):
        endDate = datetime(date.year, date.month, date.day+6, 23, 59)
        sql = f"""SELECT * FROM tasks WHERE ownerID = '{userID}' AND completionDate >= '{date.strftime(self.__dateFormat)}'
        AND completionDate <= '{endDate.strftime(self.__dateFormat)}' AND isDone > 0 ORDER BY completionDate ASC"""
        print(sql)
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except Exception as e:
            logging.error("Cannot get task completion stats: " + str(e))
        return []

    def getStudents(self, teacherID):
        sql = f"""SELECT users.name as name, users.email as email, users.id as id, teacherStudents.className as className, teacherStudents.classID as classID
        FROM users LEFT JOIN teacherStudents ON teacherStudents.studentID = users.id WHERE teacherID = {teacherID} ORDER BY className"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except Exception as e:
            logging.error("Cannot fetch students: " + str(e))
        return []


from math import log
from flask import Flask, abort, g, jsonify, redirect, render_template, flash, request, session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from dotenv import load_dotenv
from defs import AddTaskAIForm, AddTaskForChild, AddTaskForm, AddTaskForChildAI, LoginForm, RegisterForm, User
from werkzeug.security import check_password_hash, generate_password_hash
from FDataBase import FDataBase
from datetime import datetime
from urllib.parse import unquote, quote
import os
import sqlite3
import logging
import sys
import json
import requests

load_dotenv()

app = Flask("calendar-web", static_folder="static/", template_folder="templates/")
loginManager = LoginManager()
loginManager.init_app(app)

app.config["SECRET_KEY"] = os.environ.get("WEB_SECRET_KEY", "")
app.config["WEB_PORT"] = int(os.environ.get("WEB_PORT", 4221))
app.config["DEBUG"] = True
app.config["AI_HOST"] = os.environ.get("AI_HOST", "127.0.0.1")
app.config["AI_PORT"] = os.environ.get("AI_PORT", "4222")

sqlFormat = "%Y%m%d%H%M%S"

logging.basicConfig(encoding="utf-8", level=logging.INFO, 
                    format="%(levelname)s %(asctime)s %(message)s",
                    handlers=[logging.FileHandler("log.txt", ("w" if app.config["DEBUG"] else "w+")), logging.StreamHandler(sys.stdout)])

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

def get_db():
    if not hasattr(g, "link_db"):
        g.link_db = connect_db()
    return g.link_db

@loginManager.user_loader
def load_user(user_id):
    return User(user_id)

@app.teardown_appcontext
def close_db(_):
    if hasattr(g, "link_db"):
        g.link_db.close()

@app.route("/index", methods=["POST", "GET"])
@app.route("/home", methods=["POST", "GET"])
@app.route("/", methods=["POST", "GET"])
@login_required
def index():
    dbase = FDataBase(get_db())
    usr = dbase.getUserByID(current_user.get_id())
    form = AddTaskForm()
    aiForm = AddTaskAIForm()
    if usr is None:
        logout_user()
        if request.method == "POST":
            return abort(401)
        else:
            session["next"] = request.path
            return redirect("/login")

    if request.method == "POST" and form.validate_on_submit():
        dbase.addTask(form.task.data.strip(), datetime.combine(form.deadlineDate.data, form.deadlineTime.data), current_user.get_id(), current_user.get_id(), form.priority.data)
        return redirect("/")

    return render_template("index.html", user=usr, form=form, aiForm=aiForm)

@app.route("/calendar/<id>")
@login_required
def calendar(id):
    dbase = FDataBase(get_db())
    usr = dbase.getUserByID(current_user.get_id())
    if usr is None:
        logout_user()
        if request.method == "POST":
            return abort(401)
        else:
            session["next"] = request.path
            return redirect("/login")

    usr2 = dbase.getUserByID(id)
    if usr2 is None:
        return abort(404)

    return render_template("calendar.html", user=usr)

@app.route("/addAI", methods=["POST"])
@login_required
def addAITask():
    dbase = FDataBase(get_db())
    usr = dbase.getUserByID(current_user.get_id())
    if usr is None:
        logout_user()
        if request.method == "POST":
            return abort(401)

    form = AddTaskAIForm()
    if form.validate_on_submit():
        print("got ai request:", form.task.data)
        res = requests.get("http://" + app.config["AI_HOST"] + ":" + str(app.config["AI_PORT"]) + "/process/" + quote(form.task.data.strip())).content
        print("got ai answer:",res)
        res = json.loads(unquote(res))
        for t in res:
            dbase.addTask(t["task"], datetime.strptime(t["date"] + " " + t["time"], "%d/%m/%Y %H:%M"), current_user.get_id(), current_user.get_id(), form.priority.data)

        return redirect("/")

    return redirect("/")
    

@app.route("/getTasks/<date>")
@login_required
def getTasks(date):
    dbase = FDataBase(get_db())
    usr = dbase.getUserByID(current_user.get_id())
    if usr is None:
        # Do not redirect and chenge session["next"] on API-like routes
        logout_user()
        return abort(401)

    res = []
    tasks = dbase.getTasksOnDate(datetime.strptime(date, "%d-%m-%Y"), current_user.get_id())
    if len(tasks) == 0:
        return jsonify([]);
    for t in tasks:
        res.append(dict(t))
    return jsonify(res)

@app.route("/getTasksWeek/<date>")
@login_required
def getTasksWeek(date):
    dbase = FDataBase(get_db())
    usr = dbase.getUserByID(current_user.get_id())
    if usr is None:
        # Do not redirect and chenge session["next"] on API-like routes
        logout_user()
        return abort(401)

    res = []
    tasks = dbase.getTasksOnWeek(datetime.strptime(date, "%d-%m-%Y"), current_user.get_id())
    if len(tasks) == 0:
        return jsonify([]);
    for t in tasks:
        res.append(dict(t))
    return jsonify(res)

@app.route("/getTasks/<date>/<id>")
@login_required
def getTasksFor(date, id):
    dbase = FDataBase(get_db())
    usr = dbase.getUserByID(current_user.get_id())
    if usr is None:
        # Do not redirect and chenge session["next"] on API-like routes
        logout_user()
        return abort(401)

    usr2 = dbase.getUserByID(id)
    if usr2 is None:
        return abort(404)

    res = []
    tasks = dbase.getTasksOnDate(datetime.strptime(date, "%d-%m-%Y"))
    #TODO
    if len(tasks) == 0:
        return "";
    for t in tasks:
        res.append(dict(t))
    return jsonify(res)

@app.route("/getTask/<id>")
@login_required
def getTask(id):
    dbase = FDataBase(get_db())
    usr = dbase.getUserByID(current_user.get_id())
    if usr is None:
        # Do not redirect and chenge session["next"] on API-like routes
        logout_user()
        return abort(401)

    task = dbase.getTaskByID(id)
    if task is None:
        return jsonify([])
    else:
        return jsonify(dict(task))

@app.route("/undoTask/<id>")
@login_required
def undoTask(id):
    dbase = FDataBase(get_db())
    usr = dbase.getUserByID(current_user.get_id())
    if usr is None:
        # Do not redirect and chenge session["next"] on API-like routes
        logout_user()
        return abort(401)

    dbase.undoTask(id)
    return ""

@app.route("/markDoneTask/<id>")
@login_required
def markDoneTask(id):
    dbase = FDataBase(get_db())
    usr = dbase.getUserByID(current_user.get_id())
    if usr is None:
        # Do not redirect and chenge session["next"] on API-like routes
        logout_user()
        return abort(401)

    dbase.markDoneTask(id)
    return ""

@app.route("/profile/getTasksCompleted")
@login_required
def completedTasks():
    dbase = FDataBase(get_db())
    id = current_user.get_id()
    usr = dbase.getUserByID(id)
    if usr is None:
        # Do not redirect and chenge session["next"] on API-like routes
        logout_user()
        return abort(401)

    res = dbase.getCompletedTasks(id)
    return jsonify({"completedCount": res})

@app.route("/profile/getTaskCount")
@login_required
def taskCount():
    dbase = FDataBase(get_db())
    usr = dbase.getUserByID(current_user.get_id())
    if usr is None:
        # Do not redirect and chenge session["next"] on API-like routes
        logout_user()
        return abort(401)

    res = dbase.getTaskCount(current_user.get_id())
    return jsonify({"taskCount": res})

@app.route("/getCompletionStats/<date>")
@login_required
def completionStats(date):
    dbase = FDataBase(get_db())
    usr = dbase.getUserByID(current_user.get_id())
    if usr is None:
        # Do not redirect and chenge session["next"] on API-like routes
        logout_user()
        return abort(401)

    date = datetime.strptime(date, "%d-%m-%Y")
    r = dbase.getCompletionStats(current_user.get_id(), date)
    res = []
    for t in r:
        r = dict(t)
        r["deadline"] = datetime.strptime(r["deadline"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S.000%:z")
        r["completionDate"] = datetime.strptime(r["completionDate"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S.000%:z")
        res.append(r)
    return jsonify({"tasks": res})

@app.route("/login", methods=["POST", "GET"])
def login():
    if (current_user.is_authenticated):
        return redirect("/")
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        dbase = FDataBase(get_db())
        usr = dbase.getUserByEmail(form.email.data)
        if usr is not None and check_password_hash(usr["pwd"], form.pwd.data):
            user = User(usr["id"])
            login_user(user, form.remember.data)
            return redirect(session.pop("next", "/"))
        else:
            flash("Неверная почта или пароль!", "info")
    return render_template("login.html", form=form)

@app.route("/register", methods=["POST", "GET"])
def register():
    if (current_user.is_authenticated):
        return redirect("/")

    form = RegisterForm()
    if request.method == "POST":
        if not form.validate_on_submit():
            return render_template("register.html", form=form)
        dbase = FDataBase(get_db())
        hash = generate_password_hash(form.pwd.data)
        usr = dbase.getUserByEmail(form.email.data)
        if usr is not None:
            flash("Такой адрес электронной почты уже зарегистрирован!", "info")
            return render_template("register.html", form=form)
        id = dbase.createUser(form.name.data, form.email.data, hash)
        if id < 0:
            print("[ERROR] Can't create user:", form.email.data)
            return render_template("register.html", form=form)
        user = User(id)
        login_user(user, remember=form.remember.data)
        return redirect(session.pop("next", "/"))

    return render_template("register.html", form=form)

@app.route("/profile")
@login_required
def profile():
    id = current_user.get_id()
    dbase = FDataBase(get_db())
    usr = dbase.getUserByID(int(id))
    if usr is None:
        print("[ERROR] user ID is invalid!")
        logout_user()
        return redirect("/login")

    form = AddTaskForm()
    aiForm = AddTaskAIForm()
    uid = current_user.get_id()
    completed=dbase.getCompletedTasks(uid)
    all=dbase.getTaskCount(uid)
    return render_template("profile.html", user=usr, form=form, aiForm=aiForm, all=all, completed=completed, percent=int(completed/(all if all != 0 else 1)*100))

@app.route("/classes")
@login_required
def classes(): 
    dbase = FDataBase(get_db())
    usr = dbase.getUserByID(current_user.get_id())
    form = AddTaskForChild()
    form.id.data = current_user.get_id()
    aiForm = AddTaskAIForm()
    if usr is None:
        logout_user()
        if request.method == "POST":
            return abort(401)
        else:
            session["next"] = request.path
            return redirect("/login") 

    cl = dbase.getStudents(current_user.get_id())
    res = {}
    for s in cl:
        print
        all = dbase.getTaskCount(s["id"])
        completed = dbase.getCompletedTasks(s["id"])
        s["all"] = all
        s["completed"] = completed
        s["percent"] = int(completed/all*100) if all > 0 else 0
        res[s["className"]] = res.get(s["className"], [])
        res[s["className"]].append(dict(s))

    return render_template("class.html", form=form, aiForm=aiForm, user=usr, classes=res)

@app.route("/addTaskChild", methods=["POST"])
@login_required
def addTaskForChild():
    dbase = FDataBase(get_db())
    usr = dbase.getUserByID(current_user.get_id())
    if usr is None:
        # Do not redirect and chenge session["next"] on API-like routes
        logout_user()
        return abort(401)

    form = AddTaskForChild()
    print(form.id.data)
    if form.validate_on_submit():
        if int(form.id.data) < 0:
            classID = int(form.id.data) * -1
            dbase.addTaskClass(form.task.data.strip(), datetime.combine(form.deadlineDate.data, form.deadlineTime.data), 
                          classID, current_user.get_id(), form.priority.data)
        else:
            dbase.addTask(form.task.data.strip(), datetime.combine(form.deadlineDate.data, form.deadlineTime.data), 
                          form.id.data, current_user.get_id(), form.priority.data)

    return redirect("/classes")

@app.route("/addTaskChildAI", methods=["POST"])
@login_required
def addTaskForChildAI():
    dbase = FDataBase(get_db())
    usr = dbase.getUserByID(current_user.get_id())
    if usr is None:
        logout_user()
        if request.method == "POST":
            return abort(401)

    form = AddTaskForChildAI()
    if form.validate_on_submit():
        print("got ai request:", form.task.data)
        res = requests.get("http://" + app.config["AI_HOST"] + ":" + str(app.config["AI_PORT"]) + "/process/" + quote(form.task.data.strip())).content
        print("got ai answer:",res)
        res = json.loads(unquote(res))
        for t in res:
            dbase.addTask(t["task"], datetime.strptime(t["date"] + " " + t["time"], "%d/%m/%Y %H:%M"), form.id.hidden, current_user.get_id(), form.priority.data)

        return redirect("/classes")

    return redirect("/classes")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route("/healthcheck")
def healthcheck():
    return "", 200

@loginManager.unauthorized_handler
def unauthorized():
    session["next"] = request.path
    return redirect("/login")

if __name__ == "__main__":
    create_db()
    app.run("0.0.0.0", app.config.get("WEB_PORT", 4221), debug=app.config["DEBUG"])

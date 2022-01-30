import sqlite3, builtins, random, datetime, os, requests
from flask import Flask, redirect, url_for, request, session
from etc import database
from etc.utils import render, admin_only, userchk, limiter
from views.userauth import userauth_view
from views.board import board_view
from views.thread import thread_view
from views.error import error_view
from views.user import user_view
from views.api import *

database.connect()
app = Flask(__name__)
app.secret_key = str(os.urandom(24))
limiter.init_app(app)

app.register_blueprint(userauth_view)
app.register_blueprint(board_view)
app.register_blueprint(thread_view)
app.register_blueprint(error_view)
app.register_blueprint(user_view)
app.register_blueprint(v1.api)
r = 2

@app.route("/")
@userchk
def index():
    try:
        boards = dict(requests.get(f"http://jake.chiyo.org/api/v1/board").json())
        return render("index.html", boards=boards)
    except sqlite3.ProgrammingError:
        return "this is not working"

@app.route("/beta")
@userchk
def beta():
    try:    
        session.pop("beta")
    except KeyError:
        session["beta"] = 1

    return redirect(url_for("index"))

@app.route("/help")
@userchk
def help():
    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]

    return render("help.html")

@app.route("/p/<post>")
@userchk
def goto_post(post):
    session["flashCommentHeader"] = ["False", 0]
    postInfo = cursor.execute("SELECT * FROM posts WHERE msg_id = ?", (post,)).fetchone()
    
    if not postInfo:
        return redirect(url_for("index"))
    
    session["flashCommentHeader"] = [postInfo[1], 0]
    return redirect(url_for("thread_view.thread", board=postInfo[2], thread=postInfo[3]) + f"#{postInfo[1]}")

@app.route("/newnews", methods=["GET", "POST"])
@userchk
@admin_only
def new_news():
    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]

    if request.method == "GET":
        return render("newnews.html", dumbname=False, dumbpass=False)
    else:
        cursor.execute("INSERT INTO news(subject, content, date) VALUES(?,?,?)", (request.form["news_subject"], request.form["news_content"], datetime.datetime.now().strftime("%d %B %Y, %H:%M:%S (%I:%M:%S%p)"),))
        sql.commit()
        return redirect(url_for("index"))

@app.route("/users")
@userchk
def user_list():
    return render("userlist.html")

@app.route("/rules")
@userchk
def rules():
    return render("rules.html")

@app.route("/test", methods=["GET", "POST"])
def test():
    if request.method == "GET":
        try: 
            userinfo = [f"{session['username']}", f"{session['id']}", f"{session['type']}"]
        except KeyError: 
            userinfo = ["not logged in", "not logged in", "not logged in"]

        try: 
            betainfo = f'''beta: {session['beta']}'''
        except KeyError: 
            betainfo = "beta: not in beta"

        return render("tagger.html", userinfo=userinfo, betainfo=betainfo)
    else:
        return redirect(url_for("index"))

@app.route("/rats")
@userchk
def rats():
    randomMusic = ["sad", "mexican", "balloon", "epic"]
    randomMusic = random.choice(randomMusic)
    return render("comedy.html", randomMusic=randomMusic)

if __name__ == "__main__":
    while True:
        app.run(debug=True, host="0.0.0.0")
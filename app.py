import json, sqlite3, builtins, random, jinja2, werkzeug.security, datetime
from functools import wraps
from flask import Flask, redirect, url_for, render_template, request, session, abort
from etc import database

database.connect()
app = Flask(__name__)
app.secret_key = "iamakey"

r = 2
builtins.randomAdFoot = [["Do you like spaghetti? I sure do!", "Check out Marisa Space for some spaghetti!", "http://chiyo.org/"], ["The best content platform around!","VidLii!", "https://vili.co/"], ["Miss the days of realism in art? Worry no more!", "Hyper-realistic Sonic is here to save us!", "https://c.tenor.com/9z3rpvYfoDIAAAAM/sonic-and-mario-kiss.gif"]] # Turn this into JSON file

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kws):
            try:
                if session["type"] == 1:
                    pass
                else:
                    abort(401)
            except KeyError:
                abort(401)
            return f(*args, **kws)            
    return decorated_function

def render(temp=None, **kwargs):
    if not temp: return "What the hell am i gonna render without a temlate!"

    agent = request.headers.get('User-Agent')
    phones = ["iphone", "android", "blackberry"]
    
    try:
        if session["beta"]:
            return render_template("cosmic/" + temp, **kwargs)
    except KeyError:
        pass
    except jinja2.exceptions.TemplateNotFound:
        return render_template("pc/" + temp, **kwargs)

    try:
        if any(phone in agent.lower() for phone in phones):
            return render_template("ph/" + temp, **kwargs)
        else:
            return render_template("pc/" + temp, **kwargs)
    except jinja2.exceptions.TemplateNotFound:
        abort(404)

@app.route("/", methods=["GET", "POST"])
def index():
    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]
    if request.method == "POST":
        print(request.form["submit"])
    try:
        boards = cursor.execute("SELECT * FROM `boards`").fetchall()
        users = cursor.execute("SELECT * FROM users").fetchall()
        return render("index.html", boards=boards, users=users, adFoot=randomAdFoot, session=session)
    except sqlite3.ProgrammingError:
        return "this is not working"

@app.route("/beta")
def beta():
    try:    
        session.pop("beta")
    except KeyError:
        session["beta"] = 1

    return redirect(url_for("index"))

#    return render("tagger.html", content=name, r=r, list=["rattim","ratjohnson","ratjunior"])

@app.route("/logout")
def logout():
    try:
        if session["username"]:
            [session.pop(key) for key in list(session.keys())]
    except KeyError:
        pass

    return redirect(url_for("index"))

@app.route("/login", methods=["GET", "POST"])
def login():
    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]

    try:
        if session["username"]:
            return redirect(url_for("index"))
    except KeyError:
        pass

    if request.method == "GET":
        return render("login.html", dumbname=False, dumbpass=False, adFoot=randomAdFoot)
    else:
        userInfo = cursor.execute("SELECT * from `users` WHERE username = ?", (request.form["username"],)).fetchone()
        if not userInfo: 
            return render("login.html", dumbname=True, dumbpass=False, adFoot=randomAdFoot)

        hash_check = werkzeug.security.check_password_hash(userInfo[1], request.form["password"])
        if not hash_check or userInfo[1] != request.form["password"]:
            return render("login.html", dumbname=False, dumbpass=True, adFoot=randomAdFoot)
        else:
            session["username"] = userInfo[0]
            session["id"] = userInfo[2]
            session["type"] = userInfo[3]

    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]

    try:
        if session["username"]:
            return redirect(url_for("index"))
    except KeyError:
        pass

    if request.method == "GET":
        return render("register.html", dumbname=False, dumbpass=False, adFoot=randomAdFoot)
    else:

        userInfo = cursor.execute("SELECT * from `users` WHERE username = ?", (request.form["username"],)).fetchone()
        if userInfo: 
            return render("register.html", dumbname=True, dumbpass=False, adFoot=randomAdFoot)
        
        if len(request.form["password"].split()) == 0:
            return render("register.html", dumbname=False, dumbpass=True, adFoot=randomAdFoot)


        userID = cursor.execute("SELECT MAX(id) FROM `users`").fetchone()[0]
        if not userID:
            if userID == 0:
                pass
            else:
                userID = -1
        
        if not request.form.get("nohash"):
            password = werkzeug.security.generate_password_hash(request.form["password"])
        else:
            password = request.form["password"]

        cursor.execute("INSERT INTO users(username, password, id, type, date) VALUES(?,?,?,?,?)", (request.form["username"], password, userID + 1, 0, datetime.datetime.now().strftime("%d %B %Y, %H:%M:%S (%I:%M:%S%p)"),))
        sql.commit()

        userInfo = cursor.execute("SELECT * from `users` WHERE username = ?", (request.form["username"],)).fetchone()

        session["username"] = userInfo[0]
        session["id"] = userInfo[2]
        session["type"] = userInfo[3]
    return redirect(url_for("index"))

@app.route("/delboard/<board>/", methods=["GET", "POST"])
@admin_only
def delete_board(board):
    userCheck = cursor.execute("SELECT `type` FROM `users` WHERE username = ?", (session["username"],)).fetchone()
    if not userCheck: return "bad"

    print(userCheck[0])
    if userCheck[0] == 1:
        cursor.execute("DELETE FROM `boards` WHERE board_id = ?", (board,)).fetchone()
        cursor.execute("DELETE FROM `threads` WHERE board_id = ?", (board,)).fetchone()
        cursor.execute("DELETE FROM `posts` WHERE board_id = ?", (board,)).fetchone()
    sql.commit()

    return redirect(url_for("index"))

@app.route("/newboard", methods=["GET", "POST"])
@admin_only
def new_board():
    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]

    if request.method == "GET":
        return render("newboard.html", adFoot=randomAdFoot)
    else:
        boardID = cursor.execute("SELECT MAX(board_id) FROM `boards`").fetchone()[0]
        if not boardID:
            if boardID == 0:
                pass
            else:
                boardID = -1
        cursor.execute("INSERT INTO boards(name, info, board_id) VALUES(?,?,?)", (request.form["board_name"], request.form["board_info"], boardID + 1,))
        sql.commit()
    return redirect(url_for("board", board=boardID + 1))

@app.route("/help")
def help():
    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]

    return render("help.html", adFoot=randomAdFoot)

@app.route("/p/<post>")
def goto_post(post):
    session["flashCommentHeader"] = ["False", 0]
    postInfo = cursor.execute("SELECT * FROM posts WHERE msg_id = ?", (post,)).fetchone()
    
    if not postInfo:
        return redirect(url_for("index"))
    
    session["flashCommentHeader"] = [postInfo[1], 0]
    return redirect(url_for("thread", board=postInfo[2], thread=postInfo[3]) + f"#{postInfo[1]}")

@app.route("/b/<board>/")
def board(board):

    try:
        print(session["boardPostFailed"])
        if session["boardPostFailed"][1] != 0:
            session["boardPostFailed"] = [False, 0]

        if session["boardPostFailed"][0] != False:
            print("nigger")
            session["boardPostFailed"] = [session["boardPostFailed"][0], 1]

    except KeyError:
        session["boardPostFailed"] = [False, 0]

    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]

    boards = cursor.execute("SELECT * FROM boards WHERE board_id = ?", (board,)).fetchone()
    threads = cursor.execute("SELECT * FROM threads WHERE board_id = ?", (board,)).fetchall()
    users = cursor.execute("SELECT * FROM users").fetchall()

    if not boards:
        abort(404)

    return render("board.html", thread=threads, board=boards, users=users, adFoot=randomAdFoot, boardPostFailed=session["boardPostFailed"][0])

@app.route("/b/<board>/<thread>")
def thread(board, thread):

    try:
        if session["threadPostFailed"][1] != 0:
            session["threadPostFailed"] = [False, 0]

        if session["threadPostFailed"][0] != False:
            session["threadPostFailed"] = [session["threadPostFailed"][0], 1]

    except KeyError:
        session["threadPostFailed"] = [False, 0]

    try:
        if session["flashCommentHeader"][1] != 0:
            session["flashCommentHeader"] = ["False", 0]

        if session["flashCommentHeader"][0] != "False":
            session["flashCommentHeader"] = [session["flashCommentHeader"][0], 1]

    except KeyError:
        session["flashCommentHeader"] = ["False", 0]

    print(session["flashCommentHeader"])

    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]
    
    boards = cursor.execute("SELECT * FROM boards WHERE board_id = ?", (board,)).fetchone()
    threads = cursor.execute("SELECT * FROM threads WHERE thread_id = ?", (thread,)).fetchone()
    posts = cursor.execute("SELECT * FROM posts WHERE thread_id = ?", (thread,)).fetchall()
    users = cursor.execute("SELECT * FROM users").fetchall()

    if not threads:
        abort(404)

    return render("thread.html", thread=threads, board=boards, post=posts, users=users, threadPostFailed=session["threadPostFailed"][0], flashCommentHeader=session["flashCommentHeader"][0], adFoot=randomAdFoot)

@app.route("/b/<board>/<thread>/post", methods=["GET", "POST"])
def new_thread_comment(board, thread):
    session["threadPostFailed"] = [False, 0]
    
    if len(request.form["thread_content"].split()) < 1:
        session["threadPostFailed"] = ["Cannot send an empty message!", 0]
        return redirect(url_for("thread", board=board, thread=thread))

    postsID = cursor.execute("SELECT MAX(msg_id) FROM `posts`").fetchone()[0]
    if not postsID:
        if postsID == 0:
            pass
        else:
            postsID = -1

    cursor.execute("INSERT INTO posts(content, msg_id, thread_id, board_id, date) VALUES(?,?,?,?,?)", (request.form["thread_content"], postsID + 1, thread, board, datetime.datetime.now().strftime("%b %d, %Y, %I:%M:%S %p"),))
    sql.commit()

    return redirect(url_for("thread", board=board, thread=thread))

@app.route("/b/<board>/post", methods=["GET", "POST"])
def new_thread(board):
    session["boardPostFailed"] = [False, 0]
    
    if len(request.form["board_content"].split()) < 1:
        session["boardPostFailed"] = ["Cannot create a board with an empty name!", 0]
        return redirect(url_for("board", board=board))

    threadID = cursor.execute("SELECT MAX(thread_id) FROM `threads`").fetchone()[0]
    if not threadID:
        if threadID == 0:
            pass
        else:
            threadID = -1

    cursor.execute("INSERT INTO threads(info, thread_id, board_id) VALUES(?,?,?)", (request.form["board_content"], threadID + 1, board,))
    sql.commit()

    return redirect(url_for("board", board=board))

@app.route("/users")
def user_list():
    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]
    users = cursor.execute("SELECT * FROM users").fetchall()

    return render("userlist.html", users=users, adFoot=randomAdFoot)

@app.route("/random")
def randomBoard():
    boardID = cursor.execute("SELECT MAX(board_id) FROM `boards`").fetchone()[0]
    if not boardID: return abort(404)
    randomBoardID = random.randint(0, boardID)
    return redirect(url_for("board", board=randomBoardID))

@app.route("/test", methods=["GET", "POST"])
def test():
    if request.method == "GET":
        return render("tagger.html")
    else:
        print(request.form.get("test"))
        return redirect(url_for("index"))

@app.errorhandler(404)
def page_not_found(a):
    return render_template("errors/404.html")
    #return redirect(url_for("index"))

@app.errorhandler(500)
def internal_server_error(a):
    return render_template("errors/500.html")
    #return redirect(url_for("index"))

@app.errorhandler(401)
def forbidden(e):
    return render_template("errors/401.html")

if __name__ == "__main__":
    while True:
        app.run(debug=True, host="0.0.0.0")
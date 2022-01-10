import sqlite3, builtins, random, jinja2, werkzeug.security, datetime, os
from functools import wraps
from flask import Flask, redirect, url_for, render_template, request, session, abort
from etc import database

database.connect()
app = Flask(__name__)
app.secret_key = str(os.urandom(24))

r = 2
builtins.randomAdFoot = [["Zombo!", "WELCOME TO ZOMBO COM", "https://www.zombo.com/"], ["404.","Give it to me, now!", "/thisisnotreal"], ["Sonic The Hedgehog and Mayo the Plumber!", "Anything is possible.", "https://c.tenor.com/9z3rpvYfoDIAAAAM/sonic-and-mario-kiss.gif"]] # Turn this into JSON file

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
    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]
    news = cursor.execute("SELECT * FROM news").fetchall()

    try:
        if session["beta"]:
            return render_template("pc/" + temp, news=news, session=session, adFoot=randomAdFoot, **kwargs)
    except KeyError:
        pass
    except jinja2.exceptions.TemplateNotFound:
        return render_template("cosmic/" + temp, news=news, session=session, adFoot=randomAdFoot, **kwargs)

    try:
        if any(phone in agent.lower() for phone in phones):
            return render_template("ph/" + temp, news=news, session=session, adFoot=randomAdFoot, **kwargs)
        else:
            return render_template("cosmic/" + temp, news=news, session=session, adFoot=randomAdFoot, **kwargs)
    except jinja2.exceptions.TemplateNotFound:
        try:
            return render_template("pc/" + temp, news=news, session=session, adFoot=randomAdFoot, **kwargs)
        except jinja2.exceptions.TemplateNotFound:
            abort(404)

@app.route("/")
def index():
    try:
        boards = cursor.execute("SELECT * FROM `boards`").fetchall()
        users = cursor.execute("SELECT * FROM users").fetchall()
        return render("index.html", boards=boards, users=users)
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
    try:
        if session["username"]:
            return redirect(url_for("index"))
    except KeyError:
        pass

    if request.method == "GET":
        return render("login.html", dumbname=False, dumbpass=False)
    else:
        userInfo = cursor.execute("SELECT * from `users` WHERE username = ?", (request.form["username"],)).fetchone()
        if not userInfo: 
            return render("login.html", dumbname=True, dumbpass=False)

        hash_check = werkzeug.security.check_password_hash(userInfo[1], request.form["password"])
        
        if hash_check or userInfo[1] == request.form["password"]:
            session["username"] = userInfo[0]
            session["id"] = userInfo[2]
            session["type"] = userInfo[3]
        else:
            return render("login.html", dumbname=False, dumbpass=True)

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
        return render("register.html", dumbname=False, dumbpass=False)
    else:

        userInfo = cursor.execute("SELECT * from `users` WHERE username = ?", (request.form["username"],)).fetchone()
        if userInfo: 
            return render("register.html", dumbname=True, dumbpass=False)
        
        if len(request.form["password"].split()) == 0:
            return render("register.html", dumbname=False, dumbpass=True)


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
    if not userCheck: 
        return abort(401)

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
        return render("newboard.html")
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

    return render("help.html")

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
        if session["boardPostFailed"][1] != 0:
            session["boardPostFailed"] = [False, 0]

        if session["boardPostFailed"][0] != False:
            session["boardPostFailed"] = [session["boardPostFailed"][0], 1]

    except KeyError:
        session["boardPostFailed"] = [False, 0]

    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]

    boards = cursor.execute("SELECT * FROM boards WHERE board_id = ?", (board,)).fetchone()
    threads = cursor.execute("SELECT * FROM threads WHERE board_id = ?", (board,)).fetchall()
    users = cursor.execute("SELECT * FROM users").fetchall()

    if not boards:
        abort(404)

    return render("board.html", thread=threads, board=boards, users=users, boardPostFailed=session["boardPostFailed"][0])

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

    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]

    boards = cursor.execute("SELECT * FROM boards WHERE board_id = ?", (board,)).fetchone()
    threads = cursor.execute("SELECT * FROM threads WHERE thread_id = ?", (thread,)).fetchone()
    posts = cursor.execute("SELECT * FROM posts WHERE thread_id = ?", (thread,)).fetchall()
    users = cursor.execute("SELECT * FROM users").fetchall()

    if not cursor.execute("SELECT * FROM threads WHERE board_id = ? and thread_id = ?", (board, thread,)).fetchone():
        abort(404)

    return render("thread.html", thread=threads, board=boards, post=posts, users=users, threadPostFailed=session["threadPostFailed"][0], flashCommentHeader=session["flashCommentHeader"][0])

@app.route("/b/<board>/<thread>/post", methods=["GET", "POST"])
def new_thread_comment(board, thread):
    session["threadPostFailed"] = [False, 0]
    
    if len(request.form["thread_content"].split()) < 1:
        session["threadPostFailed"] = ["Cannot send an empty message!", 0]
        return redirect(url_for("thread", board=board, thread=thread))

    postsID = cursor.execute("SELECT MAX(msg_id) FROM `posts`").fetchone()[0]

    doesBoardExist = cursor.execute("SELECT `board_id` FROM `threads` WHERE `board_id` = ?", (board,)).fetchone()
    doesThreadExist = cursor.execute("SELECT `thread_id` FROM `threads` WHERE `thread_id` = ?", (thread,)).fetchone()
    if doesBoardExist and doesThreadExist:
        if not postsID:
            if postsID == 0:
                pass
            else:
                postsID = -1

        try:
            username = session["username"]
            userid = session["id"]
        except KeyError:
            username = "Anon"
            userid = 0

        cursor.execute("INSERT INTO posts(content, msg_id, thread_id, board_id, date, userid, username) VALUES(?,?,?,?,?,?,?)", (request.form["thread_content"], postsID + 1, thread, board, datetime.datetime.now().strftime("%b %d, %Y, %I:%M:%S %p"), userid, username,))
        sql.commit()

    return redirect(url_for("thread", board=board, thread=thread))

@app.route("/newnews", methods=["GET", "POST"])
def new_news():
    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]

    if request.method == "GET":
        return render("newnews.html", dumbname=False, dumbpass=False)
    else:
        cursor.execute("INSERT INTO news(subject, content, date) VALUES(?,?,?)", (request.form["news_subject"], request.form["news_content"], datetime.datetime.now().strftime("%d %B %Y, %H:%M:%S (%I:%M:%S%p)"),))
        sql.commit()
        return redirect(url_for("index"))


@app.route("/b/<board>/post", methods=["GET", "POST"])
def new_thread(board):
    session["boardPostFailed"] = [False, 0]
    
    if len(request.form["board_content"].split()) < 1:
        session["boardPostFailed"] = ["Cannot create a board with an empty name!", 0]
        return redirect(url_for("board", board=board))

    maxThreadID = cursor.execute("SELECT MAX(thread_id) FROM `threads`").fetchone()[0]
    
    doesBoardExist = cursor.execute("SELECT `board_id` FROM `boards` WHERE `board_id` = ?", (board,)).fetchone()
    if doesBoardExist:
        if not maxThreadID:
            if maxThreadID == 0:
                pass
            else:
                maxThreadID = -1


        cursor.execute("INSERT INTO threads(info, thread_id, board_id) VALUES(?,?,?)", (request.form["board_content"], maxThreadID + 1, board,))
        sql.commit()

    return redirect(url_for("board", board=board))

@app.route("/users")
def user_list():
    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]
    users = cursor.execute("SELECT * FROM users").fetchall()

    return render("userlist.html", users=users)

@app.route("/random")
def randomBoard():
    maxPostID = cursor.execute("SELECT MAX(msg_id) FROM `posts`").fetchone()[0]

    same = True
    while same:
        postID = cursor.execute("SELECT * FROM `posts` WHERE msg_id = ?", (random.randint(0, maxPostID),)).fetchone()
        if f"{postID[2]}{postID[3]}" != f"{request.referrer[-1]}{request.referrer[-3]}":
            break

    return redirect(url_for("thread", board=postID[2], thread=postID[3]))

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
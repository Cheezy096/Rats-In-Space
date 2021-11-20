import json, sqlite3, builtins, random
from flask import Flask, redirect, url_for, render_template, request, session, abort
from datetime import timedelta
from etc import database

database.connect()
print("no connect why")
app = Flask(__name__)
app.secret_key = "iamakey"

r = 2
builtins.randomAdFoot = [["Do you like spaghetti? I sure do!", "Check out Marisa Space for some spaghetti!", "http://chiyo.org/"], ["The best content platform around!","VidLii!", "https://vili.co/"], ["Miss the days of realism in art? Worry no more!", "Hyper-realistic Sonic is here to save us!", "https://c.tenor.com/9z3rpvYfoDIAAAAM/sonic-and-mario-kiss.gif"]] # Turn this into JSON file

@app.route("/")
def index():
    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]
    boards = cursor.execute("SELECT * FROM `boards`").fetchall()
    return render_template("index.html", boards=boards, adFoot=randomAdFoot)

@app.route("/test/<name>") # Test me world! <h1>tagger</h1>
def home(name):
    return render_template("tagger.html", content=name, r=r, list=["rattim","ratjohnson","ratjunior"])

@app.route("/newboard", methods=["GET", "POST"])
def new_board():
    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]
    print("newboard")

    if request.method == "GET":
        return render_template("newboard.html", adFoot=randomAdFoot)
        print("newboard")
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

@app.route("/b/<board>/")
def board(board):
    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]

    boards = cursor.execute("SELECT * FROM boards WHERE board_id = ?", (board,)).fetchone()
    threads = cursor.execute("SELECT * FROM threads WHERE board_id = ?", (board,)).fetchall()

    return render_template("board.html", thread=threads, board=boards, adFoot=randomAdFoot)



@app.route("/b/<board>/<thread>")
def thread(board, thread):
    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]
    boards = cursor.execute("SELECT * FROM boards WHERE board_id = ?", (board,)).fetchone()
    threads = cursor.execute("SELECT * FROM threads WHERE thread_id = ?", (thread,)).fetchone()
    posts = cursor.execute("SELECT * FROM posts WHERE thread_id = ?", (thread,)).fetchall()

    return render_template("thread.html", thread=threads, board=boards, post=posts, adFoot=randomAdFoot)



@app.route("/b/<board>/<thread>/post", methods=["GET", "POST"])
def new_thread_comment(board, thread):
    postsID = cursor.execute("SELECT MAX(msg_id) FROM `posts`").fetchone()[0]
    if not postsID:
        if postsID == 0:
            pass
        else:
            postsID = -1

    cursor.execute("INSERT INTO posts(content, msg_id, thread_id, board_id) VALUES(?,?,?,?)", (request.form["thread_content"], postsID + 1, thread, board))
    sql.commit()

    return redirect(url_for("thread", board=board, thread=thread))



@app.route("/b/<board>/post", methods=["GET", "POST"])
def new_thread(board):
    threadID = cursor.execute("SELECT MAX(thread_id) FROM `threads`").fetchone()[0]
    if not threadID:
        if threadID == 0:
            pass
        else:
            threadID = -1

    cursor.execute("INSERT INTO threads(info, thread_id, board_id) VALUES(?,?,?)", (request.form["board_content"], threadID + 1, board,))
    sql.commit()

    return redirect(url_for("board", board=board))


@app.route("/allposts")
def allposts():
    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]
    boards = cursor.execute("SELECT * FROM boards").fetchall()
    threads = cursor.execute("SELECT * FROM threads").fetchall()

    return render_template("allthreads.html", posts=threads, boards=boards, adFoot=randomAdFoot)


@app.route("/random")
def randomBoard():
    boardID = cursor.execute("SELECT MAX(board_id) FROM `boards`").fetchone()[0]
    if not boardID: return abort(404)
    randomBoardID = random.randint(0, boardID)
    return redirect(url_for("board", board=randomBoardID))

@app.errorhandler(404)
def page_not_found(a):
    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]
    return render_template('index.html',adFoot=randomAdFoot), 404

if __name__ == "__main__":
    app.run()
import datetime
from flask import Blueprint
from etc.utils import *

thread_view = Blueprint('thread_view', __name__)

@thread_view.route("/b/<board>/post", methods=["GET", "POST"])
def new_thread(board):
    session["boardPostFailed"] = [False, 0]
    
    if len(request.form["board_content"].split()) < 1:
        session["boardPostFailed"] = ["Cannot create a board with an empty name!", 0]
        return redirect(url_for("board_view.board", board=board))

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

    return redirect(url_for("board_view.board", board=board))

@thread_view.route("/b/<board>/<thread>")
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


    boards = cursor.execute("SELECT * FROM boards WHERE board_id = ?", (board,)).fetchone()
    threads = cursor.execute("SELECT * FROM threads WHERE thread_id = ?", (thread,)).fetchone()
    posts = cursor.execute("SELECT * FROM posts WHERE thread_id = ?", (thread,)).fetchall()

    if not cursor.execute("SELECT * FROM threads WHERE board_id = ? and thread_id = ?", (board, thread,)).fetchone():
        abort(404)

    return render("thread.html", thread=threads, board=boards, post=posts, threadPostFailed=session["threadPostFailed"][0], flashCommentHeader=session["flashCommentHeader"][0])

@thread_view.route("/b/<board>/<thread>/post", methods=["GET", "POST"])
def new_thread_comment(board, thread):
    session["threadPostFailed"] = [False, 0]
    
    if len(request.form["thread_content"].split()) < 1:
        session["threadPostFailed"] = ["Cannot send an empty message!", 0]
        return redirect(url_for("thread_view.thread", board=board, thread=thread))

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
            userid = None

        cursor.execute("INSERT INTO posts(content, msg_id, thread_id, board_id, date, userid, username) VALUES(?,?,?,?,?,?,?)", (request.form["thread_content"], postsID + 1, thread, board, datetime.datetime.now().strftime("%b %d, %Y, %I:%M:%S %p"), userid, username,))
        sql.commit()

    return redirect(url_for("thread_view.thread", board=board, thread=thread))
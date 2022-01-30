from flask import Blueprint
from etc.utils import *

board_view = Blueprint('board_view', __name__)

@board_view.route("/b/<board>/")
@userchk
def board(board):

    try:
        if session["boardPostFailed"][1] != 0:
            session["boardPostFailed"] = [False, 0]

        if session["boardPostFailed"][0] != False:
            session["boardPostFailed"] = [session["boardPostFailed"][0], 1]

    except KeyError:
        session["boardPostFailed"] = [False, 0]

    try:
        userAnon = cursor.execute("SELECT `anon` FROM `users` WHERE id = ?", (session["id"],)).fetchone()[0]
    except KeyError:
        userAnon = None
        
    boards = cursor.execute("SELECT * FROM boards WHERE board_id = ?", (board,)).fetchone()
    threads = cursor.execute("SELECT * FROM threads WHERE board_id = ?", (board,)).fetchall()

    if not boards:
        abort(404)

    return render("board.html", thread=threads, board=boards, anon=userAnon, boardPostFailed=session["boardPostFailed"][0])

@board_view.route("/delboard/<board>/", methods=["GET", "POST"])
@userchk
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

@board_view.route("/newboard", methods=["GET", "POST"])
@userchk
@admin_only
def new_board():
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
    return redirect(url_for("board_view.board", board=boardID + 1))

@board_view.route("/random")
@userchk
def randomBoard():
    maxPostID = cursor.execute("SELECT MAX(msg_id) FROM `posts`").fetchone()[0]

    same = True
    while same:
        postID = cursor.execute("SELECT * FROM `posts` WHERE msg_id = ?", (random.randint(0, maxPostID),)).fetchone()
        if f"{postID[2]}{postID[3]}" != f"{request.referrer[-1]}{request.referrer[-3]}":
            break

    return redirect(url_for("thread_view.thread", board=postID[2], thread=postID[3]))
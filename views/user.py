from flask import Blueprint
from etc.utils import *

user_view = Blueprint('user_view', __name__)

@user_view.route("/u/<user>")
@userchk
def profile(user):
    userCheck = cursor.execute("SELECT * FROM `users` WHERE id = ?", (user,)).fetchone()
    userPosts = cursor.execute("SELECT * FROM `posts` WHERE userid = ? ORDER BY msg_id DESC LIMIT 10", (user,)).fetchall()
    return render("user.html", user=userCheck, posts=userPosts)

@user_view.route("/u/preferences", methods=["GET", "POST"])
@userchk
def preferences():
    try:
        userCheck = cursor.execute("SELECT * FROM `users` WHERE id = ?", (session["id"],)).fetchone()
    except KeyError:
        return redirect(url_for("index"))
    
    if request.method == "GET":
        return render("preferences.html", user=userCheck, errorMessage=None)
    else:
        if len(str(request.form.get("userinfo")).split()) < 1:
            userinfo = None
        else:
            userinfo = str(request.form.get("userinfo"))

        if len(str(request.form.get("username")).split()) < 1:
            return render("preferences.html", user=userCheck, errorMessage="Can't use an empty name!")

        cursor.execute("UPDATE `users` SET username = ?, info = ?, avatar = ?, beta = ?, anon = ? WHERE id = ?", (str(request.form.get("username")), userinfo, str(request.form.get("avatarselection")), request.form.get("beta"), request.form.get("nouser"), userCheck[2],)).fetchone()
        sql.commit()
        
        session["username"] = str(request.form.get("username"))
        userCheck = cursor.execute("SELECT * FROM `users` WHERE id = ?", (session["id"],)).fetchone()
        return render("preferences.html", user=userCheck, errorMessage=None)

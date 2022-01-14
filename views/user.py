from flask import Blueprint
from etc.utils import *

user_view = Blueprint('user_view', __name__)

@user_view.route("/u/<user>")
def profile(user):
    userCheck = cursor.execute("SELECT * FROM `users` WHERE id = ?", (user,)).fetchone()
    userPosts = cursor.execute("SELECT * FROM `posts` WHERE userid = ?", (user,)).fetchall()
    print(userPosts)
    return render("user.html", user=userCheck, posts=userPosts)
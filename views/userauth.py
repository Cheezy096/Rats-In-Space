import werkzeug.security
from flask import Blueprint
from etc.utils import *

userauth_view = Blueprint('userauth_view', __name__)

@userauth_view.route("/login", methods=["GET", "POST"])
def login():
    try:
        if session["username"]:
            return redirect(url_for("index"))
    except KeyError:
        pass

    if request.method == "GET":
        session["loginLastPage"] = request.referrer
        return render("login.html", dumbname=False, dumbpass=False)
    else:
        
        if len(request.form["username"].split()) < 1:
            return render("login.html", dumbname=False, dumbpass=False)

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

    return redirect(session["loginLastPage"])

@userauth_view.route("/register", methods=["GET", "POST"])
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

        if len(request.form["username"].split()) < 1:
            return render("register.html", dumbname=False, dumbpass=False)

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

@userauth_view.route("/logout")
def logout():
    try:
        if session["username"]:
            [session.pop(key) for key in list(session.keys())]
    except KeyError:
        pass

    return redirect(request.referrer)
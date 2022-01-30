import werkzeug.security, base64, string
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
        return render("login.html", errorMessage=None)
    else:
        
        if len(request.form["username"].split()) < 1:
            return render("login.html", errorMessage=None)

        userInfo = cursor.execute("SELECT * from `users` WHERE username = ?", (request.form["username"],)).fetchone()
        if not userInfo: 
            return render("login.html", errorMessage="User doesn't exist!")

        hash_check = werkzeug.security.check_password_hash(userInfo[1], request.form["password"])
        
        if hash_check or userInfo[1] == request.form["password"]:
            session["username"] = userInfo[0]
            session["id"] = userInfo[2]
            session["type"] = userInfo[3]
        else:
            return render("login.html", errorMessage="Incorrect password!")

    try:
        return redirect(session["loginLastPage"])
    except KeyError:
        return redirect(url_for("index"))
        
@userauth_view.route("/register", methods=["GET", "POST"])
def register():
    try:
        if session["username"]:
            return redirect(url_for("index"))
    except KeyError:
        pass

    if request.method == "GET":
        session["loginLastPage"] = request.referrer
        return render("register.html", errorMessage=None)
    else:

        if len(request.form["username"].split()) < 1:
            return render("register.html", errorMessage="Can't set an empty username!")

        userInfo = cursor.execute("SELECT * from `users` WHERE username = ?", (request.form["username"],)).fetchone()
        if userInfo: 
            return render("register.html", errorMessage="User already exists!")
        
        if len(request.form["password"].split()) == 0:
            return render("register.html", errorMessage="Can't set an empty password!")


        userID = cursor.execute("SELECT MAX(id) FROM `users`").fetchone()[0]
        if not userID:
            if userID == 0: # Check if previous user ID was zero and ignore since database addition will add by one
                print(userID)
                pass
            else: # Check if previous user ID doesnt exist and make userID -1 so when database addition will add one userID will be zero
                print(userID)
                userID = -1
        
        if not request.form.get("nohash"):
            password = werkzeug.security.generate_password_hash(request.form["password"])
        else:
            password = request.form["password"]

        date = datetime.datetime.now().strftime("%d %B %Y, %H:%M:%S (%I:%M:%S%p)")
        randomText = ''.join(random.choices(string.ascii_letters,k=25))
        key = f"{str(base64.b64encode(bytes(request.form['username'], encoding='UTF-8')), 'UTF-8')}.{str(base64.b64encode(bytes(date, encoding='UTF-8')), 'UTF-8')}.{str(base64.b64encode(bytes(str(userID + 1), encoding='UTF-8')), 'UTF-8')}.{str(base64.b64encode(bytes(randomText, encoding='UTF-8')), 'UTF-8')}"

        cursor.execute("INSERT INTO users(username, password, id, type, date, banned, key, avatar, anon, beta) VALUES(?,?,?,?,?,?,?,?,?,?)", (request.form["username"], password, userID + 1, 0, date,0,key,"rat1", None, None,))
        sql.commit()

        userInfo = cursor.execute("SELECT * from `users` WHERE username = ?", (request.form["username"],)).fetchone()

        session["username"] = userInfo[0]
        session["id"] = userInfo[2]
        session["type"] = userInfo[3]
        session["token"] = userInfo[7]
    try:
        return redirect(session["loginLastPage"])
    except KeyError:
        return redirect(url_for("index"))


@userauth_view.route("/logout")
def logout():
    try:
        if session["username"]:
            [session.pop(key) for key in list(session.keys())]
    except KeyError:
        pass

    return redirect(request.referrer)

@userauth_view.route("/u/<user>/ban")
@admin_only
def ban(user):
    userExists = cursor.execute("SELECT * from `users` WHERE id = ?", (user,)).fetchone()
    if not userExists:
        return redirect(url_for("index"))
    elif userExists[6] == 0:
        cursor.execute("UPDATE `users` SET banned = ? WHERE id = ?", (1, user,)).fetchone()
        cursor.execute("UPDATE `threads` SET userid = ?, username = ? WHERE userid = ?", (None, "Anon", userExists[2],)).fetchall()
        cursor.execute("UPDATE `posts` SET userid = ?, username = ? WHERE userid = ?", (None, "Anon", userExists[2],)).fetchall()

        sql.commit()

    return redirect(url_for("index"))
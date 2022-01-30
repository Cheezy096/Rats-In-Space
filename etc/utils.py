from flask import redirect, url_for, render_template, request, session, abort
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import random, jinja2, datetime, os, requests

def cock():
    return get_remote_address

limiter = Limiter(key_func=cock)

def render(temp=None, **kwargs):
    randomAdFoot = [["Zombo!", "WELCOME TO ZOMBO COM", "https://www.zombo.com/"], ["404.","Give it to me, now!", "/thisisnotreal"], ["Sonic The Hedgehog and Mayo the Plumber!", "Anything is possible.", "https://c.tenor.com/9z3rpvYfoDIAAAAM/sonic-and-mario-kiss.gif"]] # Turn this into JSON file
    randomAdHead = random.choice(os.listdir("./static/images/GIFS/headad"))

    if not temp: 
        return "What the hell am i gonna render without a template!"

    agent = request.headers.get('User-Agent')
    phones = ["iphone", "android"]
    randomAdFoot = randomAdFoot[random.randint(0, len(randomAdFoot) - 1)]
    news = cursor.execute("SELECT * FROM news").fetchall()
    users = dict(requests.get(f"http://jake.chiyo.org/api/v1/user").json())

    try:
        if any(phone in agent.lower() for phone in phones):
            print(agent.lower())
            return render_template("ph/" + temp, users=users, news=news, session=session, datetoday=datetime.datetime.now(), adFoot=randomAdFoot, adHead=randomAdHead, **kwargs)
        else:
            return render_template("cosmic/" + temp, users=users, news=news, session=session, datetoday=datetime.datetime.now(), adFoot=randomAdFoot, adHead=randomAdHead, **kwargs)
    except jinja2.exceptions.TemplateNotFound:
        abort(404)

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kws):
            print(request.headers)
            try:
                if session["type"] == 1:
                    pass
                else:
                    abort(401)
            except KeyError:
                abort(401)
            return f(*args, **kws)            
    return decorated_function

def userchk(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        try:
            session["username"]
        except KeyError:
            return f(*args, **kws)            

        userExists = cursor.execute("SELECT * from `users` WHERE username = ?", (session["username"],)).fetchone()
        if not userExists:
            return redirect(url_for("userauth_view.logout"))
        elif userExists[6] == 1:
            return render("banned.html")
        return f(*args, **kws)            
    return decorated_function
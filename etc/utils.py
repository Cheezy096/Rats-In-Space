from flask import Flask, redirect, url_for, render_template, request, session, abort
from functools import wraps
import builtins, random, jinja2, datetime

builtins.randomAdFoot = [["Zombo!", "WELCOME TO ZOMBO COM", "https://www.zombo.com/"], ["404.","Give it to me, now!", "/thisisnotreal"], ["Sonic The Hedgehog and Mayo the Plumber!", "Anything is possible.", "https://c.tenor.com/9z3rpvYfoDIAAAAM/sonic-and-mario-kiss.gif"]] # Turn this into JSON file

def render(temp=None, **kwargs):
    if not temp: 
        return "What the hell am i gonna render without a temlate!"

    agent = request.headers.get('User-Agent')
    phones = ["iphone", "android", "blackberry"]

    randomAdFoot = builtins.randomAdFoot[random.randint(0, len(builtins.randomAdFoot) - 1)]
    news = cursor.execute("SELECT * FROM news").fetchall()
    users = cursor.execute("SELECT * FROM users").fetchall()

    try:
        if session["beta"]:
            return render_template("pc/" + temp, users=users, news=news, session=session, datetoday=datetime.datetime.now(), adFoot=randomAdFoot, **kwargs)
    except KeyError:
        pass
    except jinja2.exceptions.TemplateNotFound:
        return render_template("cosmic/" + temp, users=users, news=news, session=session, datetoday=datetime.datetime.now(), adFoot=randomAdFoot, **kwargs)

    try:
        if any(phone in agent.lower() for phone in phones):
            return render_template("ph/" + temp, users=users, news=news, session=session, datetoday=datetime.datetime.now(), adFoot=randomAdFoot, **kwargs)
        else:
            return render_template("cosmic/" + temp, users=users, news=news, session=session, datetoday=datetime.datetime.now(), adFoot=randomAdFoot, **kwargs)
    except jinja2.exceptions.TemplateNotFound:
        try:
            return render_template("pc/" + temp, users=users, news=news, session=session, datetoday=datetime.datetime.now(), adFoot=randomAdFoot, **kwargs)
        except jinja2.exceptions.TemplateNotFound:
            abort(404)

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
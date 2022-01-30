from flask import Blueprint, jsonify
from etc.utils import *

error_view = Blueprint('error_view', __name__)

@error_view.app_errorhandler(404)
def page_not_found(a):
    return render_template("errors/404.html"), 404

@error_view.app_errorhandler(500)
def internal_server_error(a):
    return render_template("errors/500.html"), 500

@error_view.app_errorhandler(401)
def forbidden(e):
    return render_template("errors/401.html"), 401

@error_view.app_errorhandler(429)
def forbidden(e):
    return jsonify({"error":"rate limited"})
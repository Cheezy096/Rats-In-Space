import json, werkzeug.security, base64, string
from flask import Blueprint, jsonify
from etc.utils import *
from etc.database import *

class v1(object):
    api = Blueprint('api_v1', __name__, url_prefix="/api/v1/")

    def api_auth(admin=None):
        try:
            userInfo = cursor.execute("SELECT * from `users` WHERE key = ?", (request.headers["authentication"],)).fetchone()

            if not userInfo:
                return jsonify({"error":"You are not authorized to perform this task."})

            if admin and not userInfo[3]:
                return jsonify({"error":"You are not authorized to perform this task."})

            return True

        except KeyError as key:
            return jsonify({"error":f"Missing key: `{key}`"})


    @api.route("status", methods=["GET"])
    def status():
        return jsonify({"success":"i am alive (v1)"})

    @api.route("board", methods=["GET","POST"])
    @limiter.limit("10/5 seconds")
    def board():
        if request.method == "GET":

            if request.args.get("board_id"):
                try:
                    board_id = int(request.args.get("board_id"))
                except ValueError:
                    return jsonify({"error": "Could not convert board_id to `int` type."})
                    
                boards = cursor.execute("SELECT * FROM boards WHERE board_id = ?",(board_id,)).fetchone()
                if not boards:
                    return jsonify({"error": "This board does not exist."})

                return jsonify({"success": {"id":boards[2],"description":boards[1],"name":boards[0]}})

            else:
                boards = cursor.execute("SELECT * FROM boards").fetchall()

                output = {"status code": None}
                i = 0
                for x in boards:
                    output.update({str(i): {"id":x[2],"description":x[1],"name":x[0]}})
                    i += 1

                if i == 0:
                    output["status code"] = {"error": "No boards found."}
                else:
                    output["status code"] = "success"

                return jsonify(output)
        else:
            if v1.api_auth() == True:
                data = json.loads(request.data)
            
                boardID = cursor.execute("SELECT MAX(board_id) FROM `boards`").fetchone()[0]
                if not boardID:
                    if boardID == 0:
                        pass
                    else:
                        boardID = -1
            
                try:
                    cursor.execute("INSERT INTO boards(name, info, board_id) VALUES(?,?,?)", (data["name"], data["info"], boardID + 1,))
                    sql.commit()
                except KeyError as key:
                    return jsonify({"error": f"Could not find {key} (Did you misspell it?)"})

                return jsonify({"status code": "success", "0": {"name":data["name"], "info":data["info"], "id":str(boardID + 1)}})
            else:
                return jsonify({"error":"could not get it fag"})

    @api.route("user", methods=["GET", "POST"])
    @limiter.limit("10/5 seconds")
    def user():
        if request.method == "GET":

            if request.args.get("user_id"):
                try:
                    user_id = int(request.args.get("user_id"))
                except ValueError:
                    return jsonify({"error": "Could not convert user_id to `int` type."})
                    
                users = cursor.execute("SELECT * FROM users WHERE id = ?",(user_id,)).fetchone()
                if not users:
                    return jsonify({"error": "This user does not exist."})

                return jsonify({"status code": "success", "0": {"name":users[0],"id":users[2],"type":users[3],"creation_date":users[4],"custom_info":users[5],"banned":users[6]}})

            else:
                users = cursor.execute("SELECT * FROM users").fetchall()

                output = {"status code": None}
                i = 0
                for x in users:
                    output.update({str(i): {"name":x[0],"id":x[2],"type":x[3],"creation_date":x[4],"custom_info":x[5],"banned":x[6]}})
                    i += 1

                if i == 0:
                    output["status code"] = {"error": "No users found."}
                else:
                    output["status code"] = "success"

                return jsonify(output)
        else:
            if v1.api_auth() == True:
                data = json.loads(request.data)

                if len(data["name"].split()) < 1:
                    return jsonify({"error":"Cannot use an empty username."})

                if len(data["password"].split()) < 1:
                    return jsonify({"error":"Cannot use an empty password."})

                userInfo = cursor.execute("SELECT * from `users` WHERE username = ?", (data["name"],)).fetchone()
                if userInfo: 
                    return jsonify({"error":"This username already exists."})    

                userID = cursor.execute("SELECT MAX(id) FROM `users`").fetchone()[0]
                if not userID:
                    if userID == 0: # Check if previous user ID was zero and ignore since database addition will add by one
                        pass
                    else: # Check if previous user ID doesnt exist and make userID -1 so when database addition will add one userID will be zero
                        userID = -1
                
                try:
                    if data["hashed"]:
                        password = werkzeug.security.generate_password_hash(data["password"])
                except KeyError:
                    password = data["password"]

                date = datetime.datetime.now().strftime("%d %B %Y, %H:%M:%S (%I:%M:%S%p)")
                randomText = ''.join(random.choices(string.ascii_letters,k=25))
                key = f"{str(base64.b64encode(bytes(data['name'], encoding='UTF-8')), 'UTF-8')}.{str(base64.b64encode(bytes(date, encoding='UTF-8')), 'UTF-8')}.{str(base64.b64encode(bytes(str(userID + 1), encoding='UTF-8')), 'UTF-8')}.{str(base64.b64encode(bytes(randomText, encoding='UTF-8')), 'UTF-8')}"

                cursor.execute("INSERT INTO users(username, password, id, type, date, banned, key, info) VALUES(?,?,?,?,?,?,?,?)", (data["name"], password, userID + 1, 0, date,0,key,data["info"],))
                sql.commit()

                return jsonify({"status code": "success", "0": {"name":data["name"], "id":userID+1, "password":password,"created_at":date,"key":key,"hashed":"not in yet",}})
            else:
                return jsonify({"error":"could not get it fag"})
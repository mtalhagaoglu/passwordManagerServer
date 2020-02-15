from flask import (
    Flask,
    request,
    jsonify,
    abort
)
import sqlite3
from flask_cors import CORS

import app as application

app = Flask(__name__)
CORS(app)


def tokenCheck(token):
    db = sqlite3.connect("users.db")
    c = db.cursor()
    c.execute("SELECT id,key FROM users WHERE token = ?",(token,))
    try:
        id,key = list(c.fetchall()[0])
        db.commit()
        db.close()
    except:
        db.commit()
        db.close()
        return {"status": False}
    return {"status": True,"id": id,"key": key}

@app.route("/")
def hello():
    return("passwordManager")

@app.route("/signIn",methods = ["POST"])
def signInFunc():
    if request.method == "POST":
        data = request.get_json()
        email = data["email"]
        password = data["password"]
        response = application.signIn(email,password)
        return jsonify(response)
    else:
        return jsonify({"status": "wrong request"})

@app.route("/login",methods = ["POST"])
def loginFunc():
    if request.method == "POST":
        data = request.get_json()
        email = data["email"]
        password = data["password"]
        response = application.login(email,password)
        return jsonify(response)
    else:
        return jsonify({"status": "wrong request"})

@app.route("/saveAccount",methods = ["POST"])
def saveFunc():
    if request.method == "POST":
        data = request.get_json()
        token = data["token"]
        accountName = data["accountName"]
        username = data["username"]
        password = data["password"] #Encrypted with user's master key
        answer = tokenCheck(token)
        if answer["status"]:
            id = answer["id"]
            key = answer["key"] 
            response = application.saveAccount(id,accountName,password,key,username)
            return jsonify(response)
        else:
            return jsonify({"status": "wrong token"})
    else:
        return jsonify({"status": "wrong request"})

@app.route("/deleteAccount",methods = ["POST"])
def deleteFunc():
    if request.method == "POST":
        data = request.get_json()
        token = data["token"]
        accountName = data["accountName"]
        answer = tokenCheck(token)
        if answer["status"]:
            id = answer["id"]
            key = answer["key"] 
            response = application.deleteAccount(id,accountName)
            return jsonify(response)
        else:
            return jsonify({"status": "wrong token"})
    else:
        return jsonify({"status": "wrong request"})

@app.route("/getData",methods = ["POST"])
def getFunc():
    if request.method == "POST":
        data = request.get_json()
        token = data["token"]
        answer = tokenCheck(token)
        if answer["status"]:
            id = answer["id"]
            response = application.getAccounts(id)
            return jsonify(response)
        else:
            return jsonify({"status": "wrong token"})
    else:
        return jsonify({"status": "wrong request"})



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0",port = 5001)
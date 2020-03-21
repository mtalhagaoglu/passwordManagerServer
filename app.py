import sqlite3
from datetime import date
from random import randint
from uuid import uuid4
import ast

import security

def getKey(id):
    db = sqlite3.connect("users.db")
    c = db.cursor()
    c.execute("SELECT key FROM users WHERE id = ?",(id,))
    key = list(c.fetchall()[0])[0]
    db.commit()
    db.close()
    return key


def passworddb(id):
    db = sqlite3.connect("passwords.db")
    c = db.cursor()
    c.execute("INSERT INTO accounts (id,accounts,last_active) VALUES (?,?,?)",
            (id,str([]),date.today()))
    db.commit()
    db.close()
    

def lastOnlineUpdateID(id,database):
    db = sqlite3.connect(f"{database}.db")
    c = db.cursor()
    c.execute("UPDATE accounts SET last_active = ? WHERE id = ?",(date.today(),id,))
    db.commit()
    db.close()

def lastOnlineUpdateEmail(email,database):
    db = sqlite3.connect(f"{database}.db")
    c = db.cursor()
    c.execute("UPDATE users SET last_active = ? WHERE email = ?",(date.today(),email,))
    db.commit()
    db.close()

def signIn(email,password):
    db  = sqlite3.connect("users.db")
    c = db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id int, email text, password text, token text,last_active text,key text)")
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    data=c.fetchall()
    if len(data)==0:
        id = randint(pow(10,8),pow(10,9)-1)
        token = uuid4()
        key = uuid4() 
        c.execute("INSERT INTO users (id,email,password,token,last_active,key) VALUES (?,?,?,?,?,?)",
            (id,email,password,str(token),date.today(),str(key)))
        db.commit()
        db.close()
        passworddb(id)
        return {"status": "created","token": token,"id": id}
    else:
        db.commit()
        db.close()
        return {"status": "exist"}

def login(email,password):
    db = sqlite3.connect("users.db")
    c = db.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    data= c.fetchall()
    if len(data)==0:
        db.commit()
        db.close()
        return {"status": "not exist"}
    else:
        c.execute("SELECT password,key FROM users WHERE email = ?",(email,))
        data = list(c.fetchall()[0])
        if (password == data[0]):
            key = data[1]
            print(f"{email} login succesfully")
            token = uuid4()
            c.execute("UPDATE users SET token = ? WHERE email = ?",(str(token),email,))
            db.commit()
            db.close()
            lastOnlineUpdateEmail(email,"users")
            print(f"Login is successful. Token is {token} and key is {key}")
            return {"status": "successful","token": str(token)}
        else:
            db.commit()
            db.close()
            print(f"{email} nice try")
            return {"status": "password wrong"}


def saveAccount(id,account,password,key,username,folder):
    db  = sqlite3.connect("passwords.db")
    c = db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS accounts (id int,accounts text,last_active)")
    c.execute("SELECT accounts FROM accounts WHERE id = ?", (id,))
    password = security.encrypt(key,password)
    username = security.encrypt(key,username)
    print(f"my new password is {password}")
    print(f"my real password is {security.decrypt(key,password)}")
    print(f"my new username is {username}")
    print(f"my real username is {security.decrypt(key,username)}")
    try:
        data = ast.literal_eval(list(c.fetchall()[0])[0])
        print(data)
    except:
        data = []
    newData = []
    for i in data:
        if (i["name"] == account):
            i["username"] = username
            i["password"] = password
            i["folder"] = folder
            newData.append(i)
        else:
            newData.append(i)
    lock = 1
    for i in newData:
        if i["name"] == account:
            lock = 0
            break
        else:
            pass
    if lock == 1:
        newData.append({"name": account,"password": password,"username": username,"folder": folder})

    print(f"newData is {newData}")
    print(len(newData))
    c.execute("UPDATE accounts SET accounts = ? WHERE id = ?",(str(newData),id,))
    db.commit()
    db.close()
    return {"status": "saved"}

def deleteAccount(id,account):
    db = sqlite3.connect("passwords.db")
    c = db.cursor()
    c.execute("SELECT accounts FROM accounts WHERE id = ?", (id,))
    try:
        data = ast.literal_eval(list(c.fetchall()[0])[0])
    except:
        data = []
    newData = []
    for i in data:
        if i["name"] == account:
            pass
        else:
            newData.append(i)
    print(f"newData is {newData}")
    c.execute("UPDATE accounts SET accounts = ? WHERE id = ?",(str(newData),id,))
    db.commit()
    db.close()
    return {"status": "deleted"}

def getAccounts(id):
    try:
        db = sqlite3.connect("passwords.db")
        c = db.cursor()
        c.execute("SELECT accounts FROM accounts WHERE id = ?", (id,))
        try:
            data = ast.literal_eval(list(c.fetchall()[0])[0])
            print(data)
            newData = []
            key = getKey(id)
            for i in data:
                i["password"] = security.decrypt(key,i["password"])
                i["username"] = security.decrypt(key,i["username"])
                newData.append(i)
            data = newData
        except:
            data = []
            print("crash")
        return {"status": "succesfully", "data": data}
    except:
        return {"status": "succesfully", "data": []}
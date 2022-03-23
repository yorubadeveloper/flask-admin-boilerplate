from app import app
from flask import request, session
from helpers.database import *
from helpers.hashpass import *
from helpers.mailer import *
from bson import json_util, ObjectId
import json
from helpers.gcloud.service_incidents.mod_gcloud import *


def load_gsheet(gsheet_name, gsheet_tab):
    return get_gsheet_data(gsheet_name, gsheet_tab)


def checkloginusername():
    username = request.form["username"]
    check = db.users.find_one({"username": username})
    if check is None:
        return "No User"
    else:
        return "User exists"

def checkloginpassword():
    username = request.form["username"]
    check = db.users.find_one({"username": username})
    password = request.form["password"]
    hashpassword = getHashed(password)
    if hashpassword == check["password"]:
        # sendmail(subject="Login on Flask Admin Boilerplate", sender="Flask Admin Boilerplate", recipient=check["email"], body="You successfully logged in on Flask Admin Boilerplate")
        session["username"] = username
        return "correct"
    else:
        return "wrong"
    

def checkusername():
    username = request.form["username"]
    check = db.users.find_one({"username": username})
    if check is None:
        return "Available"
    else:
        return "Username taken"

def registerUser():
    fields = [k for k in request.form]                                      
    values = [request.form[k] for k in request.form]
    data = dict(zip(fields, values))
    user_data = json.loads(json_util.dumps(data))
    user_data["password"] = getHashed(user_data["password"])
    user_data["confirmpassword"] = getHashed(user_data["confirmpassword"])
    db.users.insert(user_data)
    # sendmail(subject="Registration for Flask Admin Boilerplate", sender="Flask Admin Boilerplate", recipient=user_data["email"], body="You successfully registered on Flask Admin Boilerplate")
    print("Done")

def load_data_to_db(sheet_name, tab_name, collection_name, key):
    data = load_gsheet(sheet_name, tab_name)
    if not data.empty:
        data_records = data.to_dict("records")
        for record in data_records:
            print(record)
            try:
                db[collection_name].find_one_and_update({"uuid":record.get("uuid")}, {"$set": record}, upsert=True)
            except Exception as e:
                print(e)
                pass
    return pd.DataFrame(db[collection_name].find({}))


def load_data_from_dataframe_to_db(datarecords, collection_name, key=[]):
    query = {}
    for k in key:
       query[k] = ''
    for record in datarecords:
        print(record)
        try:
            db[collection_name].find_one_and_update(query, {"$set": record}, upsert=True)
        except Exception as e:
            print(e)
            pass
    return pd.DataFrame(db[collection_name].find({}))


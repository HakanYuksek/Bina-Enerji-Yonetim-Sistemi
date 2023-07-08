from flask import Flask, flash, redirect, render_template, request, session, abort
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import json
from passlib.hash import sha256_crypt
import os
from flask_session import Session
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import threading
from datetime import datetime
import random
import jsonify
import json

app = Flask(__name__)


#SESSION AYARLARI
SESSION_TYPE = 'filesystem'
SESSION_FILE_DIR = os.path.join(app.root_path,"session_files")
app.config.from_object(__name__)
Session(app)

D = [1,1,1]
H = [1,1,1]

@app.route("/")
def index():
    if not session.get('logged_in'):
        return render_template("index.html",username = "not")
    else:
        return render_template("index.html",username = session["username"])
    
@app.route("/login",methods=["POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
    
        con = sqlite3.connect('DB.db')

        cur = con.cursor()


        query = "select * from Users where Username=?"
        
        cur.execute(query,(username,))

        rows = cur.fetchone()
        
        if rows is not None:
            if sha256_crypt.verify(password,str(rows[1])):
                con.close()
                session['logged_in'] = True
                session["username"] = username
                return render_template("index.html",username=username)
            else:
                print('wrong password!')
        else:
                print('wrong username!')
        con.close()
        return render_template("index.html",username = "WrongUser")

    
@app.route("/calculateCarbon")
def calculateCarbon():
    if not session.get('logged_in'):
        return render_template("karbon.html",username = "not")
    else:
        return render_template("karbon.html",username = session["username"])

@app.route("/result",methods=["POST"])
def result():
    kisi_sayisi=float(request.form["kisiSayisi"])
    elektrik_tuketimi=float(request.form["ElektrikTuketimi"])
    dogalgaz_tuketimi=float(request.form["DogalgazTuketimi"])
    return render_template("result.html",sum_result=(0.67*elektrik_tuketimi+56.1*dogalgaz_tuketimi)/10000,kisi_basi=((0.67*elektrik_tuketimi+56.1*dogalgaz_tuketimi)/kisi_sayisi)/10000,x=kisi_sayisi,y=elektrik_tuketimi,z=dogalgaz_tuketimi)

@app.route("/logout")
def logout():
    session['logged_in'] = False
    session.pop("username",None)
    session.pop("password",None)
    return index()


@app.route("/loadConsumes")
def loadPage():
    # The user should be login to the system to use this method
    if not session.get('logged_in'):
        return render_template("index.html",username = "not")
    else:
        return render_template("loads.html",username = session["username"])


@app.route("/showLoads",methods=["POST","GET"])
def showLoadsOfTheUser():
    # The user should be login to the system to use this method
    if not session.get('logged_in'):
        return render_template("index.html",username = "not")
    else:
        if request.method =="POST":
            selectedUser = request.form["sel1"]
            day = request.form["sel2"]

            if selectedUser == "Daire-1":
                userID = 1
            elif selectedUser == "Daire-2":
                userID = 2
            else:
                userID = 3

            if day == "Pazartesi":
                day = 1
            elif day == "Sali":
                day = 2
            elif day == "Carsamba":
                day = 3
            elif day == "Persembe":
                day = 4
            elif day == "Cuma":
                day = 5
            elif day == "Cumartesi":
                day = 6
            else:
                day = 7
            

            conn = sqlite3.connect("DB.db")

            query = "select * from Loads where userID="+str(userID)+" and day="+str(day)

            loads = pd.read_sql(query,conn)

            if userID != 3:
                loads.drop(columns=["Elektrikli_Arac_Sarzi"],axis=1,inplace=True)

            #loads.drop(columns=["userID"],axis=1,inplace=True)

            conn.close()

            figName = "static/Ev"+str(userID)+"/"+str(day)+".png"
            figName += "?dummy="+str(random.randint(0,1000000000000))

            return render_template("loadsHome.html",username = session["username"],column_names=loads.columns.values, row_data=list(loads.values.tolist()),figName = figName,link_column="day", zip=zip,userID = userID,day = day)
        else:
            return render_template("loads.html",username=session["username"])

@app.route("/updateLoads")
def update():
    # The user should be login to the system to use this method
    if not session.get('logged_in'):
        return render_template("index.html",username = "not")
    else:
        userID = request.args.get("userID")
        day = request.args.get("day")
        hour = request.args.get("hour")

        days = {"1":"Pazartesi","2":"Sali","3":"Carsamba","4":"Persembe","5":"Cuma","6":"Cumartesi","7":"Pazar"}

        hour = int(hour) + 1

        conn = sqlite3.connect("DB.db")

        query = "select * from Loads where userID="+str(userID)+" and day="+str(day)+" and hour = "+str(hour)

        loads = pd.read_sql(query,conn)

        if int(userID) !=3:
            loads.drop(columns=["Elektrikli_Arac_Sarzi"],axis=1,inplace=True)

        conn.close()

        dayText = days[day]

        loads.drop(columns=["hour"],axis=1,inplace=True)
        loads.drop(columns=["userID"],axis=1,inplace=True)
        loads.drop(columns=["day"],axis=1,inplace=True)

        return render_template("updateLoadPage.html",username = session["username"],column_names=loads.columns.values, zip=zip,row_data=list(loads.values.tolist()),dayText=dayText,userID = userID,day = day,hour=hour)

@app.route("/updateAtDB",methods=["POST","GET"])
def updateDB():
    # The user should be login to the system to use this method
    if not session.get('logged_in'):
        return render_template("index.html",username = "not")
    else:
        if request.method =="POST":
            userID = int(request.form["userID"])
            day = int(request.form["day"])
            hour = request.form["hour"]
            dayText = request.form["dayText"]
            
            conn = sqlite3.connect("DB.db")

            cursor = conn.cursor()

            query = "select * from Loads where userID="+str(userID)+" and day="+str(day)+" and hour = "+str(hour)
            loads = pd.read_sql(query,conn)

            if userID !=3:
                loads.drop(columns=["Elektrikli_Arac_Sarzi"],axis=1,inplace=True)
            

            query = "update Loads set "
            sum = 0
            for col in loads.columns.values:
                if col != "day" and col!= "hour" and col!= "userID" and col!="Toplam" and col!="olcekli":
                    sum += float(request.form[col])
                    query = query + col +" = "+request.form[col]+ ","
            query += "Toplam="+str(sum)+",olcekli="+str((float(sum)/1000))
            
            query += " where userID="+str(userID)+" and day="+str(day)+" and hour="+str(hour)

            cursor.execute(query)

            conn.commit()

            time = []

            for i in range(24):
                time.append(i+1)

            query = "select * from Loads where userID="+str(userID)+" and day="+str(day)
            loads = pd.read_sql(query,conn)

            draw = loads["Toplam"]
            loadData = []
            for i in draw:
                loadData.append(i)

            figName = "static/Ev"+str(userID)+"/"+str(day)+".png"
            conn.close()

            x = threading.Thread(target=updateFigure, args=(figName,time,loadData,dayText,))
            x.start()
            x.join()

            updateFigure(figName,time,loadData,dayText)
            figName += "?dummy="+str(random.randint(0,1000000000000))
            print(figName)
            print("Day---->",day)            
            return render_template("loadsHome.html",username = session["username"],column_names=loads.columns.values, row_data=list(loads.values.tolist()),figName = figName,link_column="day", zip=zip,userID = userID,day = day)
        else:
            return render_template("loads.html",username=session["username"])

def updateFigure(figName,time,loadData,dayText):
    plt.figure(random.randint(0,10000000000000))
    plt.plot(time,loadData,color="b")
    plt.xlabel("Zaman")
    plt.ylabel("Tüketilen Toplam Yük Miktarı")
    plt.title(dayText)
    plt.savefig(figName)


@app.route("/prices")
def showPrices():
    # The user should be login to the system to use this method
    if not session.get('logged_in'):
        return render_template("index.html",username = "not")
    else:
        conn = sqlite3.connect("DB.db")

        # Firstly, we should find consumes of the each userID
        query = "select * from Loads"
        loads = pd.read_sql(query,conn)

        sums = {1:0,2:0,3:0}
        for id1,sum1 in zip(loads["userID"],loads["Toplam"]):
            sums[id1] += sum1

        # We hold consuming data in the sums dict

        prices = []
        prices.append(round(float((sums[1])/10000),2))
        prices.append(round(float((sums[2])/10000),2))
        prices.append(round(float((sums[3])/10000),2))

        sums[1] = round(sums[1],2)
        sums[2] = round(sums[2],2)
        sums[3] = round(sums[3],2)
        
        return render_template("prices.html",username=session["username"],zip = zip,prices=prices,sums=sums)
        
        query = ""


# This method provides to update loads according to the circuit, ESP8266 can send data to this method with HTTP GET, Of course the format should be suitable
# for the system
@app.route("/getData",methods = ["GET"])
def dataFromCircuit():
    if request.method == "GET":
        userID = request.args.get("userID")
        day = request.args.get("day")
        hour = request.args.get("hour")
        toplam = request.args.get("Toplam")
        if str(day) == "1":
            dayText = "Pazartesi"
        elif str(day) == "2":
            dayText = "Sali"
        elif str(day) == "3":
            dayText = "Carsamba"
        elif str(day) == "4":
            dayText = "Persembe"
        elif str(day) == "5":
            dayText = "Cuma"
        elif str(day) == "6":
            dayText = "Cumartesi"
        else:
            dayText = "Pazar"

        day = D[int(userID)-1]
        hour = H[int(userID)-1]
        
        conn = sqlite3.connect("DB.db")

        cursor = conn.cursor()

        query = "select userID,day,hour,Toplam from loads where userID="+str(userID)+" and day="+str(day)+" and hour = "+str(hour)
        loads = pd.read_sql(query,conn)

        query = "update loads set Toplam = "+str(toplam)+",olcekli = "+str((float(toplam)/1000))

        query += " where userID="+str(userID)+" and day="+str(day)+" and hour="+str(hour)

        cursor.execute(query)

        conn.commit()

        time = []

        for i in range(24):
            time.append(i+1)

        query = "select Toplam from loads where userID="+str(userID)+" and day="+str(day)
        loads = pd.read_sql(query,conn)

        draw = loads["Toplam"]
        loadData = []
        for i in draw:
            loadData.append(i)

        figName = "static/Ev"+str(userID)+"/"+str(day)+".png"
        cursor.close()
        conn.close()

        x = threading.Thread(target=updateFigure, args=(figName,time,loadData,dayText,))
        x.start()
        x.join()

        updateFigure(figName,time,loadData,dayText)

        H[int(userID)-1] += 1
        if H[int(userID)-1] == 25:
            H[int(userID)-1] = 1
            D[int(userID)-1] += 1
            if D[int(userID)-1] == 7:
                D[int(userID)-1] = 1

# This method provides to update loads according to the circuit, ESP8266 can send data to this method with HTTP GET, Of course the format should be suitable
# for the system
@app.route("/postData",methods = ["POST"])
def dataFromCircuit2():
    if request.method == "POST":
        userID = request.form.get("userID")
        day = request.form.get("day")
        hour = request.form.get("hour")
        toplam = request.form.get("Toplam")
        if str(day) == "1":
            dayText = "Pazartesi"
        elif str(day) == "2":
            dayText = "Sali"
        elif str(day) == "3":
            dayText = "Carsamba"
        elif str(day) == "4":
            dayText = "Persembe"
        elif str(day) == "5":
            dayText = "Cuma"
        elif str(day) == "6":
            dayText = "Cumartesi"
        else:
            dayText = "Pazar"

        conn = sqlite3.connect("DB.db")

        cursor = conn.cursor()
        query = "select userID,day,hour,Toplam from loads where userID="+str(userID)+" and day="+str(day)+" and hour = "+str(hour)
        loads = pd.read_sql(query,conn)

        query = "update loads set Toplam = "+str(toplam)+",olcekli = "+str((float(toplam)/1000))

        query += " where userID="+str(userID)+" and day="+str(day)+" and hour="+str(hour)

        cursor.execute(query)

        conn.commit()

        time = []

        for i in range(24):
            time.append(i+1)

        query = "select Toplam from loads where userID="+str(userID)+" and day="+str(day)
        loads = pd.read_sql(query,mydb)

        draw = loads["Toplam"]
        loadData = []
        for i in draw:
            loadData.append(i)

        figName = "static/Ev"+str(userID)+"/"+str(day)+".png"
        cursor.close()
        conn.close()

        x = threading.Thread(target=updateFigure, args=(figName,time,loadData,dayText,))
        x.start()
        x.join()

        updateFigure(figName,time,loadData,dayText)


@app.route("/webservice")
def my_web_service():
    
    conn = sqlite3.connect("DB.db")
    cursor = conn.cursor()
    
    userID = request.args.get("userID")
    day = request.args.get("day")

    if H[int(userID)-1] != 1:
        updated =H[int(userID)-1]-1
    else:
        updated = 1
        
    query = "select Toplam,olcekli from loads where userID="+str(userID)+" and day="+str(day)+" and hour="+str(updated)
    loads = pd.read_sql(query,conn)

    cursor.close()
    conn.close()

    appDict = {
      'hour': updated,
      "Toplam": loads["Toplam"][0],
      "olcekli":loads["olcekli"][0]
    }
    
    app_json = json.dumps(appDict)
    return app_json    
    
if __name__ == "__main__":
    app.run(debug = True)


from flask import Flask, render_template, request, redirect, url_for,session, flash, logging
from wtforms import validators
from wtforms.form import Form
from wtforms.validators import *
from flask_mysqldb import MySQL
import mysql.connector

from wtforms.fields import *
from credentials import *
from passlib.hash import sha256_crypt
app = Flask(__name__)

mySql = MySQL(app)

mydb = mysql.connector.connect(
host="localhost",
user="root",
password= "",  
database = "gymdatabase"
)

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods = ["POST","GET"])
def login():

    if request.method == "POST":
        username = request.form['username']
        password_candidate = request.form['password']
        cur = mydb.cursor()
        cur.execute('SELECT * FROM info WHERE username = %s', [username])
        result = cur.fetchone()
        print(result,"-----line 52")
        
        

        # data = cur.fetchone()
        admin_name = result[0]
        password = result[1]
        # hash = sha256_crypt.hash(password)
        # print(password, "---------",  hash) #store hash in data base inspite of original password

        print(password,"--line 56")

        if username == admin_name and sha256_crypt.verify(password_candidate, password):
            session['logged_in'] = True
            session['username']=username
            session['prof']=result[3] #profession
            cur.close()
            flash('You are logged in', 'success')
            if session['prof'] == 1:
                return redirect(url_for('admin'))

            return ("Admin logged in")

        else:
            error = "Invalid Login"
            return error

    return render_template("login.html")

@app.route('/admin')
def admin():
    return render_template('adminDash.html')

values =[]

cur = mydb.cursor()
cur.execute("SELECT username FROM info")
result = cur.fetchall()

for i in result:
    values.append(i)
cur.close()

#same form for everyone
class AddTrainerForm(Form):
    print(values,"------line 80")
    name = StringField('Name',[Length(min=1, max=100)])
    username = StringField('Username',[InputRequired(),NoneOf(values=values, message="Username already taken, Please try another")])
    password = PasswordField('Password',[DataRequired(),EqualTo('confirm',message='Passwords must match')])
    confirm = PasswordField('Confirm Password')
    street = StringField('Street',[Length(min=1, max=100)])
    city = StringField('City',[Length(min=1, max=100)])
    phone = StringField('Phone',[Length(min=1, max=100)])

    
@app.route('/addTrainer/', methods = ['GET','POST'])
def addTrainer(): 
    values.clear() #removes all usernames from list if present
    form = AddTrainerForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        street = form.street.data
        city = form.city.data
        phone = form.phone.data
        cur = mydb.cursor(buffered=True)
        val = (name,username,password,street,city, 2, phone)
        cur.execute("INSERT INTO info(name, username, password, street, city, prof, phone) VALUES(%s, %s, %s, %s, %s, %s, %s)", val)
        #first create table for trainer
        cur.execute("INSERT INTO trainers(username) VALUES(%s)", [username])
        mydb.commit()
      
        
        cur.close()
        mydb.close()
        flash('You recruited a new Trainer!!', 'success')
        return redirect(url_for('admin'))
        # return "Trainer added"
    # else:
    #     flash("Username already taken !!! Change it", 'alert')
    return render_template('addTrainer.html',form=form)

	
@app.route('/addReceptionalist/', methods = ['GET','POST'])
def addReceptionalist(): 
    values.clear() #removes all usernames from list if present
    form = AddTrainerForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        street = form.street.data
        city = form.city.data
        phone = form.phone.data
        cur = mydb.cursor(buffered=True)
        val = (name,username,password,street,city, 3, phone)
        cur.execute("INSERT INTO info(name, username, password, street, city, prof, phone) VALUES(%s, %s, %s, %s, %s, %s, %s)", val)
        #first create table for trainer
        cur.execute("INSERT INTO receptionalist(username) VALUES(%s)", [username])
        mydb.commit()
      
        
        cur.close()
        mydb.close()
        flash('You recruited a new Receptionalist!!', 'success')
        return redirect(url_for('admin'))
        # return "Receptionalist added"
    # else:
    #     flash("Username already taken !!! Change it", 'alert')
    return render_template('addTrainer.html',form=form)

	

print(values, "line --- 150")
Trainerchoices =[]
i = 1
while i < len(values):
    tup = values[i][0]
    if tup.startswith("t"): #for trainer
        print(tup)
        Trainerchoices.append(tup)
    i+=1




class deleteForm(Form):
    username= SelectField(u'Choose trainer which you want to delete', choices=Trainerchoices)


@app.route('/deleteTrainer/', methods=['POST','GET'])
def deleteTrainer():
    form = deleteForm(request.form)
    if request.method == 'POST':
        username = form.username.data
        cur = mydb.cursor()
        cur.execute("DELETE FROM trainers WHERE username = %s", [username])
        cur.execute("DELETE FROM info WHERE username = %s", [username])
        mydb.commit()
        cur.close()
        Trainerchoices.clear()
        return " {} removed".format(username)


    return render_template("deleteTrainer.html", form=form)    




Recepchoices =[]
i = 1
while i < len(values):
    tup = values[i][0]
    if tup.startswith("r"): #for receptionalist
        print(tup)
        Recepchoices.append(tup)
    i+=1




class deleteRecepForm(Form):
    username= SelectField(u'Choose trainer which you want to delete', choices=Recepchoices)


@app.route('/deleteReceptionalist/', methods=['POST','GET'])
def deleteReceptionalist():
    form = deleteRecepForm(request.form)
    if request.method == 'POST':
        username = form.username.data
        cur = mydb.cursor()
        cur.execute("DELETE FROM receptionalist WHERE username = %s", [username])
        cur.execute("DELETE FROM info WHERE username = %s", [username])
        mydb.commit()
        cur.close()
        Trainerchoices.clear()
        return " {} removed".format(username)


    return render_template("deleteTrainer.html", form=form)    


class addEquipForm(Form):
    name = StringField('Name',[Length(min=1, max=100)])
    count = IntegerField('Count',[NumberRange(min=1, max=25)])

@app.route('/addEquipment/',methods = ["POST","GET"])
def addEquipment():
    form = addEquipForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        count = form.count.data
        cur = mydb.cursor()
        cur.execute("SELECT name FROM equipments")
        equips = []
        result = cur.fetchall()
        print(result,"-------line 235")
        i = 0
        while i < len(result):
            tup = result[i][0]
            equips.append(tup)
            i+=1
        print(equips,"----------241")
        if name in equips:
            cur.execute("UPDATE equipments SET count = count+%s WHERE name = %s", (count, name))
        else:
            cur.execute("INSERT INTO equipments(name, count) VALUES(%s, %s)",(name, count))
        mydb.commit()
        cur.close()
        flash('You added a new Equipment!!', 'success')
        return redirect(url_for('admin'))


    return render_template('addEquip.html', form = form)


Equipchoices=[]
cur = mydb.cursor()
cur.execute("SELECT name FROM equipments")
res = cur.fetchall()
i = 0
while i < len(res):
    tup = res[i][0]
    Equipchoices.append(tup)
    i+=1
print(Equipchoices,"--------263")
cur.close()
class removeEquipForm(Form):
    name = RadioField('Name', choices=Equipchoices)
    count = IntegerField('Count',[NumberRange(min=1, max=25), InputRequired()])

@app.route('/removeEquipments')
def removeEquipments(): 
    form = removeEquipForm(request.form)
    if request.method == "POST" and form.validate():
        cur = mydb.cursor()
        cur.execute("SELECT * FROM equipments WHERE name = %s", [form.name.data])
        data = cur.fetchone()
        app.logger.info(data['count'])
        print(data, "---------277")
        name = form.name.data
        count = form.count.data
        cur.execute("UPDATE equip SET count = count-%s WHERE name = %s", (count, name))

    

    return render_template('removeEquip.html', form=form)










@app.route("/logout/")
def logout():
    session["username"] = None
    return redirect("/")

if __name__ == "__main__":
    app.secret_key = "232422"
    app.run(debug=True)

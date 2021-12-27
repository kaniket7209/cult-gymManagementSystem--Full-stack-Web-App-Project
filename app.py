
from flask import Flask, config, render_template, request, redirect, url_for,session, flash, logging
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
port = 3306,
user="root",
password= "",  
database = "gymdatabase", 

)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods = ["POST","GET"])
def login():

    if request.method == "POST":
        username = request.form['username']
        password_candidate = request.form['password']
        mydb.reconnect()
        cur = mydb.cursor()
        cur.execute('SELECT * FROM info WHERE username = %s', [username])
        result = cur.fetchone()
        # print(result,"-----line 52")
        # result = cur.fetchall()
        
        

        # data = cur.fetchone()
        # admin_name = result[0]
        password = result[1]
        # hash = sha256_crypt.hash(password)
        # print(password, "---------",  hash) #store hash in data base inspite of original password

        # print(password,"--line 56")

        if sha256_crypt.verify(password_candidate, password):
            session['logged_in'] = True
            session['username']=username
            session['prof']=result[3] #profession
            cur.close()
            flash('You are logged in')
            if session['prof'] == 1:
                return redirect(url_for('admin'))
            elif session['prof'] == 2:
                return redirect(url_for('trainerdash'))

        else:
            error = "Invalid Login"
            return error

    return render_template("login.html")

@app.route('/admin')
def admin():
    return render_template('adminDash.html')

@app.route('/trainerDashboard')
def trainerdash():
    return render_template('trainerdash.html')

def trainChoice():

    Trainerchoices =[]
    
    mydb.reconnect()
    cur = mydb.cursor(buffered=True)
    cur.execute('SELECT username FROM trainers')
    res = cur.fetchall()
    # print("158",res)
    cur.close()
    i = 0
    while i < len(res):
        tup = res[i][0]
        Trainerchoices.append(tup)
        i+=1
    return Trainerchoices

#same form for receptionalist and trainer
class AddTrainerForm(Form):
    # print(values,"------line 80")
    trainerhoices = trainChoice()
    name = StringField('Name',[Length(min=1, max=100)])
    username = StringField('Username',[InputRequired(),NoneOf(values=trainerhoices, message="Username already taken, Please try another")])
    password = PasswordField('Password',[DataRequired(),EqualTo('confirm',message='Passwords must match')])
    confirm = PasswordField('Confirm Password')
    street = StringField('Street',[Length(min=1, max=100)])
    city = StringField('City',[Length(min=1, max=100)])
    phone = StringField('Phone',[Length(min=1, max=100)])

    
@app.route('/addTrainer/', methods = ['GET','POST'])
def addTrainer(): 
    
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
        if session['prof'] == 1:
            return redirect(url_for('admin'))
        elif session['prof'] == 2:
            return redirect(url_for('trainerdash'))
    else:
        flash("Username already taken !!! Change it")
    return render_template('addTrainer.html',form=form)


def recep():
    Recepchoices =[]
    mydb.reconnect()
    cur = mydb.cursor()
    cur.execute('SELECT username FROM receptionalist')
    res = cur.fetchall()
    cur.close()
    i = 0
    while i < len(res):
        tup = res[i][0]
        Recepchoices.append(tup)
        i+=1
    return Recepchoices


class AddRecepForm(Form):
    # print(values,"------line 80")
    Recepchoices = recep()
    name = StringField('Name',[Length(min=1, max=100)])
    username = StringField('Username',[InputRequired(),NoneOf(values=Recepchoices, message="Username already taken, Please try another")])
    password = PasswordField('Password',[DataRequired(),EqualTo('confirm',message='Passwords must match')])
    confirm = PasswordField('Confirm Password')
    street = StringField('Street',[Length(min=1, max=100)])
    city = StringField('City',[Length(min=1, max=100)])
    phone = StringField('Phone',[Length(min=1, max=100)])


@app.route('/addReceptionalist/', methods = ['GET','POST'])
def addReceptionalist(): 
   
    form = AddRecepForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        street = form.street.data
        city = form.city.data
        phone = form.phone.data
        mydb.reconnect()
        cur = mydb.cursor(buffered=True)
        val = (name,username,password,street,city, 3, phone)
        cur.execute("INSERT INTO info(name, username, password, street, city, prof, phone) VALUES(%s, %s, %s, %s, %s, %s, %s)", val)
        #first create table for trainer
        cur.execute("INSERT INTO receptionalist(username) VALUES(%s)", [username])
        mydb.commit()
      
        
        cur.close()
        mydb.close()
        flash('You recruited a new Receptionalist!!', 'success')
        if session['prof'] == 1:
            return redirect(url_for('admin'))
        elif session['prof'] == 2:
            return redirect(url_for('trainerdash'))
    else:
        flash("Username already taken !!! Change it", 'alert')
    return render_template('addTrainer.html',form=form)




class deleteForm(Form):
    Trainerchoices=trainChoice()
    if Trainerchoices:
        username= SelectField(u'Trainer List', choices=Trainerchoices)
    else:
        username= RadioField(u'Sorry Trainer list is empty', choices=['No Trainers'])



@app.route('/deleteTrainer/', methods=['POST','GET'])
def deleteTrainer():    
    form = deleteForm(request.form)
    if request.method == 'POST':
        username = form.username.data
        mydb.reconnect()
        cur = mydb.cursor()
        Trainerchoices=trainChoice()
        if not username in Trainerchoices:
            return """Sorry {} this trainer doesn't exist anymore.. Kindly <a href="/addTrainer">add</a> Trainer first""".format(session['username'])
        else:
            cur.execute("DELETE FROM trainers WHERE username = %s", [username])
            cur.execute("DELETE FROM info WHERE username = %s", [username])
            mydb.commit()
            cur.close()
            flash(' {} deleted from the list'.format(username))
        if session['prof'] == 1:
            return redirect(url_for('admin'))
        elif session['prof'] == 2:
            return redirect(url_for('trainerdash'))

    return render_template("deleteTrainer.html", form=form)    





class deleteRecepForm(Form):
    Recepchoices= recep()
    if Recepchoices:
        username= SelectField(u'Receptionalists List', choices=Recepchoices)
    else:
        username= RadioField(u'Sorry no Receptionalists available', choices=[''])



@app.route('/deleteReceptionalist/', methods=['POST','GET'])
def deleteReceptionalist():
    form = deleteRecepForm(request.form)
    if request.method == 'POST':
        username = form.username.data
        mydb.reconnect()
        cur = mydb.cursor()
    
        Recepchoices= recep()
        if not username in Recepchoices:
            return  """Sorry {} Receptionalists list is empty.. Kindly <a href="/addReceptionalist">add</a> Receptionalist first""".format(session['username'])
        else:
            cur.execute("DELETE FROM receptionalist WHERE username = %s", [username])
            cur.execute("DELETE FROM info WHERE username = %s", [username])
            mydb.commit()
            cur.close()
            flash("{} removed from receptionalists list".format(username))
        # return ' {} removed <a href="/admin">Go back </a>'.format(username) 


    return render_template("deleteTrainer.html", form=form)    


class addEquipForm(Form):
    name = StringField('Name',[Length(min=1, max=100)])
    count = IntegerField('Count',[NumberRange(min=1, max=25)])

@app.route('/addEquipment/',methods = ["POST","GET"])
def addEquipment():
    Equipchoices, countChoice = equipments() 
    list = [Equipchoices, countChoice]

    form = addEquipForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        count = form.count.data
        cur = mydb.cursor()
        cur.execute("SELECT name FROM equipments")
        equips = []
        result = cur.fetchall()
        # print(result,"-------line 235")
        i = 0
        while i < len(result):
            tup = result[i][0]
            equips.append(tup)
            i+=1
        # print(equips,"----------241")
        if name in equips:
            cur.execute("UPDATE equipments SET count = count+%s WHERE name = %s", (count, name))
            flash('Updated')
        else:
            cur.execute("INSERT INTO equipments(name, count) VALUES(%s, %s)",(name, count))
            flash('You added a new Equipment!!')
        mydb.commit()
        cur.close()
       
        if session['prof'] == 1:
            return redirect(url_for('admin'))
        elif session['prof'] == 2:
            return redirect(url_for('trainerdash'))


    return render_template('addEquip.html', form = form, list = list)

def equipments():
    Equipchoices=[]
    countChoice=[]
    cur = mydb.cursor()
    cur.execute("SELECT name , count FROM equipments")
    res = cur.fetchall()
    print(res,"-281")
    i = 0
    while i < len(res):
        tup = res[i][0]
        tupc = res[i][1]
        Equipchoices.append(tup)
        countChoice.append(tupc)
        i+=1
    # print(Equipchoices,"--------263")
    cur.close()
    return Equipchoices, countChoice

class removeEquipForm(Form):
    Equipchoices, countchoices = equipments() 
    if Equipchoices:
        name = RadioField(u'Select equipment which you want to remove', choices=Equipchoices)
        count = IntegerField('Count',[NumberRange(min=1, max=25)])
    else:
        name = RadioField(u'Sorry Equipment list is empty', choices=['0'])
        count = IntegerField(' ')


@app.route('/removeEquipments/',methods = ["POST","GET"])
def removeEquipments():
    form = removeEquipForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        count = form.count.data
 
        cur = mydb.cursor()
        cur.execute("SELECT name FROM equipments")
        equips = []
        result = cur.fetchall()
        # print(result,"-------line 235")
        i = 0
        while i < len(result):
            tup = result[i][0]
            equips.append(tup)
            i+=1
        # print(equips,"----------241")
        if name in equips:
            cur.execute("UPDATE equipments SET count = count-%s WHERE name = %s", (count, name))
            flash('{} {} deleted'.format(count, name))

        else:
            return ("""Sorry {} No more equipments left <a href="/addEquipment">Add</a> it first""".format(session['username']))
        mydb.commit()
        cur.close()
        if session['prof'] == 1:
            return redirect(url_for('admin'))
        elif session['prof'] == 2:
            return redirect(url_for('trainerdash'))


    return render_template('removeEquip.html', form = form)

@app.route('/viewEquipments')
def viewEquip():
    mydb.reconnect()
    cur = mydb.cursor()
    cur.execute("SELECT * FROM equipments")
    res = cur.fetchall()
    print(res, "-----------377")
    cur.close()
    return render_template('viewEquip.html', res = res)

def planChoices():
    planChoices = []
    cur= mydb.cursor()
    cur.execute("SELECT DISTINCT name FROM plans")
    res = cur.fetchall()
    print(res, "----------line 308")
    cur.close()
    i = 0
    while i < len(res): 
        tup= res[i][0]
        planChoices.append(tup)
        i+=1
    return planChoices


class addPlanForm(Form):
    name = StringField('Plan name',[Length(min=1, max=50)])
    exercise = StringField('Exercise',[Length(min=1, max=50)])
    sets = IntegerField('Number of Sets',[NumberRange(min=1, max=100)])
    reps = IntegerField('Repetitions',[NumberRange(min=1, max=500)])

@app.route('/addPlans/', methods = ['POST', 'GET'])
def addPlans():
    form = addPlanForm(request.form)
    if request.method == "POST":
        name = form.name.data
        exercise = form.exercise.data
        sets = form.sets.data
        reps = form.reps.data
        cur = mydb.cursor()
        planChoice= planChoices()
        if name.lower() in planChoice:
            return """Hey {} 
            Sorry😢 this plan already exists ..Create a <a href="/addPlans">new</a> one""".format(session['username'])
            
        else:
            cur.execute("INSERT INTO plans(name, exercise, sets, reps) VALUES(%s, %s, %s, %s)", (name, exercise, sets, reps))
        mydb.commit()
        cur.close()
        flash('{} added'.format(name))
        if session['prof'] == 1:
            return redirect(url_for('admin'))
        elif session['prof'] == 2:
            return redirect(url_for('trainerdash'))
	

    return render_template('addplans.html', form = form)



def member():
    memberchoices = []
    mydb.reconnect()
    cur = mydb.cursor()
    cur.execute("SELECT DISTINCT username FROM members")
    res = cur.fetchall()
    i = 0
    while i < len(res):
        tup = res[i][0]
        memberchoices.append(tup)
        i += 1

    return memberchoices



class addMemberForm(Form):
    planChoices = planChoices() 
    memberchoices = member()
    TrainerChoices = trainChoice()
    name = StringField('Name',[Length(min=1, max=50)])
    username = StringField('Username',[InputRequired(),NoneOf(values=memberchoices, message="Username already taken, Please try another")])
    password = PasswordField('Password',[DataRequired(),EqualTo('confirm',message='Passwords must match')])
    confirm = PasswordField('Confirm Password')
    street = StringField('Street',[Length(min=1, max=100)])
    city = StringField('City',[Length(min=1, max=100)])
    phone = StringField('Phone',[Length(min=1, max=100)])
    plan = RadioField(u'Select Plan', choices = planChoices)
    trainer = SelectField(u'Select Trainer', choices=TrainerChoices)



@app.route('/addMember/', methods = ['GET','POST'])
def addMember():
    form =  addMemberForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        street = form.street.data
        city = form.city.data
        phone= form.city.data
        plan = form.plan.data
        trainer = form.trainer.data
        mydb.reconnect()
        cur = mydb.cursor()
        val = (name,username,password,street,city, 4, phone) # member profession = 4
        cur.execute("INSERT INTO info(name, username, password, street, city, prof, phone) VALUES(%s, %s, %s, %s, %s, %s, %s)", val)
        cur.execute("INSERT INTO members(username, plan, trainer) VALUES(%s, %s, %s)", (username, plan, trainer))
        mydb.commit()
        cur.close()
        flash('{} added'.format(name))
        if session['prof'] == 1:
            return redirect(url_for('admin'))
        elif session['prof'] == 2:
            return redirect(url_for('trainerdash'))
        else:
            return redirect(url_for('login'))


    return render_template('addMember.html', form=form)




class deleteMemberform(Form):
    memberchoices = member()
    if memberchoices:
        name = RadioField(u'Members Present', choices=memberchoices)
    else:
        name = RadioField(u'Members list is empty', choices=['NO member present'])
        


@app.route('/deleteMember', methods = ['GET', 'POST'])
def deleteMember():
    form = deleteMemberform(request.form)
    if request.method == "POST" and form.validate():
        name  = form.name.data
        mydb.reconnect()
        cur = mydb.cursor()
        memberchoices = member()
        if not name in memberchoices:
            return """Sorry {} member list is empty.. Kindly <a href="/addMember">add</a> first""".format(session['username'])
        else:
            cur.execute("DELETE FROM members WHERE username = %s", [name])
            cur.execute("DELETE FROM info WHERE username = %s", [name])
        mydb.commit()
        cur.close()
        flash('{} deleted'.format(name))
        if session['prof'] == 1:
            return redirect(url_for('admin'))
        elif session['prof'] == 2:
            return redirect(url_for('trainerdash'))


    return render_template('deleteMember.html', form=form)
# print(values, "-------329")


@app.route('/viewdetails')
def details():
    
    mydb.reconnect()
    cur = mydb.cursor(buffered=True)
    cur.execute("SELECT * FROM info WHERE username != %s", [session['username']])
    result = cur.fetchall()
    # for row in result:
    #     print("username ", row[0])
    #     print("name ", row[2])
    #     print("Profession ", row[3])
    #     print("street ", row[4])
    #     print("city ", row[5])
    #     print("phone ", row[6])

      
    cur.close()
    return render_template('details.html', result = result)


@app.route('/viewplans/')
def viewplans():
    mydb.reconnect()
    cur= mydb.cursor()
    cur.execute("SELECT * FROM plans")
    result = cur.fetchall()

    cur.close()
    return render_template('viewplans.html', result = result)



class delplanForm(Form):
    planChoices = planChoices()
    name = RadioField(u'Plans list',choices=planChoices)
 
@app.route('/delplans/', methods = ['POST', 'GET'])
def delplans():
    form = delplanForm(request.form)
    if request.method == "POST":
        name = form.name.data
        planChoice= planChoices()
       
        if not name in planChoice:
            flash('Sorry this plan is not available')
            # return """Sorry {} plan list is empty.. Kindly <a href="/addPlans">add</a> first""".format(session['username'])
        else:
            mydb.reconnect()
            cur = mydb.cursor()
            cur.execute("DELETE FROM plans WHERE name = %s", [name])
            mydb.commit()
            cur.close()
            flash('{} deleted'.format(name))
    
       
        if session['prof'] == 1:
            return redirect(url_for('admin'))
        elif session['prof'] == 2:
            return redirect(url_for('trainerdash'))
	

    return render_template('delplans.html', form = form)


class editprofileForm(Form):

    Recepchoices = recep()
    name = StringField('Name',[Length(min=1, max=100)])
    username = StringField('Username',[InputRequired(),NoneOf(values=Recepchoices, message="Username already taken, Please try another")])
    street = StringField('Street',[Length(min=1, max=100)])
    city = StringField('City',[Length(min=1, max=100)])
    phone = StringField('Phone',[Length(min=1, max=100)])

#edit profile not working

@app.route('/editprofile/', methods = ['POST','GET'])
def editprofile():
    form = editprofileForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        street = form.street.data
        city = form.street.data
        phone = form.phone.data
        mydb.reconnect()
        cur = mydb.cursor()
        cur.execute("UPDATE info SET name = %s ,street = %s ,city = %s ,phone = %s WHERE username = %s", (name,street,city,phone, username))
        mydb.commit()
        cur.close()
        flash('Profile Updated')
        if session['prof'] == 1:
            return redirect(url_for('admin'))
        elif session['prof'] == 2:
            return redirect(url_for('trainerdash'))

    
    return render_template('editprofile.html', form = form)

class changepasswordForm(Form):
    password = PasswordField('Password',[DataRequired(),EqualTo('confirm',message='Passwords must match')])
    confirm = PasswordField('Confirm Password')
   

@app.route('/changepass/', methods = ['POST','GET'])
def changepass():
    form = changepasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        password = sha256_crypt.encrypt(str(form.password.data))
        mydb.reconnect()
        cur = mydb.cursor()
        cur.execute("UPDATE info SET password = %s WHERE username = %s ",(password,session['username']))
        mydb.commit()
        cur.close()
        if session['prof'] == 1:
            return redirect(url_for('admin'))
        elif session['prof'] == 2:
            return redirect(url_for('trainerdash'))
        
    return render_template('changepassword.html', form= form)


@app.route("/logout/")
def logout():
    session["username"] = None
    return redirect("/login")

if __name__ == "__main__":
    app.secret_key = "232422"
    app.run(debug=True)

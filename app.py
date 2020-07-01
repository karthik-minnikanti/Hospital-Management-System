from flask import Flask, render_template, url_for, request, session, redirect
import mysql.connector
from datetime import datetime
from flask_login import logout_user, LoginManager

app = Flask(__name__)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="hospital"
)
mycursor = mydb.cursor()

@lm.user_loader
def load_user(user):
    # return User.get(user)
    return ("hi")

def verifyPatient(id1):
    mycursor.execute('SELECT * FROM patient WHERE id = %s', (id1,))
    patient = mycursor.fetchone()
    if patient:
        if patient[6] == 1:
            return True
        return False
    return False

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html')
    return render_template('login.html',message='')

@app.route('/Welcome', methods= ['POST', 'GET'])
def home():
    if 'username' in session:
        return render_template('index.html')
    return render_template('login.html',message='')

@app.route('/login', methods = ['POST','GET'])
def login():
    if 'username' in session:
        return render_template('index.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        mycursor.execute('SELECT * From employee WHERE employeename = %s and password = %s',(username,password,))
        employee = mycursor.fetchone()
        session['role'] = employee[2]
        if employee:
            session['username'] = username
            return render_template('welcome.html')
        return render_template('login.html',message='Username and password do not match')
    return render_template('login.html')

@app.route('/registration',methods = ['POST','GET'])
def registration():
    if 'username' not in session:
        return render_template('login.html',message='Please login')
    if session['role'] == 'dia' or session['role'] == 'pharm':
        return render_template('access.html')
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        type1 = request.form['type'] 
        add = request.form['address']
        mycursor.execute('SELECT * FROM patid')
        id1 = mycursor.fetchone()
        id2 = id1[0] + 1
        mycursor.execute('UPDATE patid SET id = %s WHERE id = %s',(id2, id1[0]))
        mydb.commit()
        mycursor.execute('SELECT * FROM patient WHERE id = %s',(id1[0],))
        ex = mycursor.fetchone()
        if ex:
            return render_template('registration.html',message='This patient is already existed')
        mycursor.execute('INSERT INTO patient (id, name, age, type, address) VALUES(%s, %s, %s, %s, %s)',(id1[0], name, age, type1, add))
        mydb.commit()
        return render_template('registration.html',message='Successfully Registered and Registration id is '+ str(id1[0]) )
    return render_template('registration.html',message='')

@app.route('/update', methods= ['POST','GET'])
def update():
    if 'username' not in session:
        return render_template('login.html',message='Please login')
    if session['role'] == 'dia' or session['role'] == 'pharm':
        return render_template('access.html')
    if request.method == 'POST':
        id1 = request.form['id']
        if verifyPatient(id1):
            mycursor.execute('SELECT * FROM patient WHERE id = %s', (id1,))
            patient = mycursor.fetchone()
            session['id'] = id1
            return render_template('update1.html', id = patient[0], name = patient[1], age = patient[2], date = patient[3], address = patient[4], type = patient[5],message='' )
        return render_template('update.html',message='Patient Record Not found')
    return render_template('update.html',message='')

@app.route('/updating', methods=['POST','GET'])
def updating():
    
    if 'username' not in session:
        return render_template('login.html',message='Please login')
    if session['role'] == 'dia' or session['role'] == 'pharm':
        return render_template('access.html')
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        type1 = request.form['type'] 
        add = request.form['address']
        mycursor.execute('UPDATE patient SET name = %s, age = %s, type = %s, address = %s WHERE id = %s',(name, age, type1, add, session['id']))
        mydb.commit()
        return render_template('update.html', message= 'Successfully Updated')

@app.route('/delete',methods = ['POST','GET'])
def delete():
    
    if 'username' not in session:
        return render_template('login.html',message='Please login')
    if session['role'] == 'dia' or session['role'] == 'pharm':
        return render_template('access.html')
    if request.method == 'POST':
        id1 = request.form['id']
        if verifyPatient(id1):
            mycursor.execute('SELECT * FROM patient WHERE id = %s', (id1,))
            patient = mycursor.fetchone()
            session['id'] = id1
            return render_template('delete1.html', id = patient[0], name = patient[1], age = patient[2], date = patient[3], address = patient[4], type = patient[5],message='' )
        return render_template('delete.html',message ='Patient Record Not Found')
    return render_template('delete.html',message='')

@app.route('/deleting', methods = ['POST','GET'])
def deleting():
    if session['role'] == 'dia' or session['role'] == 'pharm':
        return render_template('access.html')
    if request.method == 'POST':
        status = 0
        mycursor.execute('UPDATE patient SET status = %s WHERE id = %s',(status,session['id']))
        mydb.commit()
        return render_template('delete.html', message= 'Successfully deleted')
    return render_template('delete.html')

@app.route('/viewall', methods = ['POST','GET'])
def viewall():
    if session['role'] == 'dia' or session['role'] == 'pharm':
        return render_template('access.html')
    mycursor.execute('SELECT * FROM patient')
    patients = mycursor.fetchall()
    return render_template('viewall.html', patients = patients)

@app.route('/search', methods = ['POST','GET'])
def search():
   
    if 'username' not in session:
        return render_template('login.html',message='Please login')
    if session['role'] == 'dia' or session['role'] == 'pharm':
        return render_template('access.html')
    if request.method == 'POST':
        id1 = request.form['id']
        mycursor.execute('SELECT * FROM patient WHERE id = %s', (id1,))
        patient = mycursor.fetchone()
        session['id'] = id1
        if patient:
            if patient[6] == 0:
                status = 'Discharged'
            else:
                status = 'Active'
            return render_template('search.html', id = patient[0], name = patient[1], age = patient[2], date = patient[3], address = patient[4], type = patient[5],message='',status=status )
        return render_template('search1.html',message='No Patient Found')
    return render_template('search1.html',message='')

@app.route('/issuemedicine', methods = ['POST','GET'])
def issuemedicine():
    
    if 'username' not in session:
        return render_template('login.html',message='Please login')
    if session['role'] == 'register' or session['role'] == 'dia':
        return render_template('access.html')
    if request.method == 'GET':
        return render_template('searchformedicine.html',message='')
    if request.method == 'POST':
        id1 = request.form['id']
        session['id'] = id1
        mycursor.execute('SELECT * FROM patient WHERE id =%s',(id1,))
        patient = mycursor.fetchone()
        if patient:
            if patient[6] == 0:
                return render_template('searchformedicine.html',message='Patient is discharged')
            else:
                mycursor.execute('SELECT *FROM medicine WHERE id = %s',(id1,))
                medicine = mycursor.fetchall()
                return render_template('issuemedicine.html',patient = patient, medicine = medicine)
        return render_template('searchformedicine.html',message='No Patient Found')
                             
@app.route('/addmedicine',methods=['POST','GET'])
def addmedicine():
    
    if 'username' not in session:
        return render_template('login.html',message='Please login')
    if session['role'] == 'register' or session['role'] == 'dia':
        return render_template('access.html')
    if request.method=="POST":
        medicinename=request.form['medicinename']
        quantity=request.form['q']
        rate=request.form['rate']
        amount=int(quantity)*int(rate)
        mycursor.execute('INSERT INTO medicine(id,medicinename,quantity,rate,amount) VALUES (%s,%s,%s,%s,%s)',(session['id'],medicinename,quantity,rate,amount))
        mydb.commit()
        return render_template('searchformedicine.html',message='Successfully added')
    return render_template('addmedicine.html', id = session['id'])

@app.route('/test',methods=['POST','GET'])
def test():
    
    if 'username' not in session:
        return render_template('login.html',message='Please login')
    if session['role'] == 'register' or session['role'] == 'pharm':
        return render_template('access.html')
    if request.method=='GET':
        return render_template('test.html',message='')
    if request.method=="POST":
        id1=request.form['id']
        session['id']=id1
        mycursor.execute('SELECT *FROM patient WHERE id= %s',(id1,))
        patient=mycursor.fetchone()
        if patient:
            if patient[6] == 0:
                return render_template('test.html',message='Patient is discharged')
            else:
                mycursor.execute('SELECT * FROM test WHERE id=%s',(id1,))
                tests = mycursor.fetchall()
                return render_template('test1.html',patient = patient,tests = tests)
        return render_template('test.html',message='No Patient Found')

@app.route('/addtest', methods = ['POST','GET'])
def addtest():
    
    if 'username' not in session:
        return render_template('login.html',message='Please login')
    if session['role'] == 'register' or session['role'] == 'pharm':
        return render_template('access.html')
    if request.method == 'POST':
        testname = request.form['testname']
        price = request.form['rate']
        mycursor.execute('INSERT INTO test (id,testname,testprice) VALUES (%s,%s,%s)',(session['id'],testname,price))
        mydb.commit()
        return render_template('test.html',message='Successfully Added')
    return render_template('addtest.html',id = session['id'])

@app.route('/billing', methods = ['POST','GET'])
def billing():
    
    if 'username' not in session:
        return render_template('login.html',message='Please login')
    if session['role'] == 'dia' or session['role'] == 'pharm':
        return render_template('access.html')
    if request.method == 'GET':
        return render_template('billing.html', message="")
    if request.method == 'POST':
        id1 = request.form['id']
        session['id'] = id1
        mycursor.execute('SELECT * FROM patient WHERE id = %s ',(id1,))
        patient = mycursor.fetchone()
        if patient:
            if patient[6] == 0:
                return render_template("billing.html", message="Patient discharged")
            if verifyPatient(id1):
                mycursor.execute('SELECT * FROM patient WHERE id = %s ',(id1,))
                patient = mycursor.fetchone()
                dateTimeObj = datetime.utcnow()
                noofdays = dateTimeObj- patient[3]
                noofdays = noofdays.days + 1
                if patient[5] == "General" :
                    roomrent = 2000 * noofdays
                elif patient[5] == "semisharin":
                    roomrent = 4000 * noofdays
                else:
                    roomrent = 8000 * noofdays
                mycursor.execute('SELECT * FROM medicine WHERE id = %s ',(id1,))
                medicines = mycursor.fetchall()
                medbill = 0
                if medicines:
                    for ele in medicines:
                        medbill += ele[4]
                mycursor.execute('SELECT * FROM test WHERE id = %s ',(id1,))
                tests = mycursor.fetchall()
                testbill = 0
                if tests:
                    for ele in tests:
                        testbill += ele[2]
                total = roomrent+medbill+testbill
                return render_template('bill.html',medicines = medicines, tests = tests,patient =patient, noofdays = noofdays, roomrent = roomrent, medbill = medbill, testbill = testbill ,total = total)
        return render_template('billing.html', message = "No patient found")

@app.route('/discharge')
def dis():
    if 'username' not in session:
        return render_template('login.html',message='Please login')
    status =0
    mycursor.execute('UPDATE patient SET status = %s WHERE id = %s',(status,session['id']))
    mydb.commit()
    return render_template('billing.html',message='Discharged')

@app.route('/logout')
def logout():
    if 'username' not in session:
        return render_template('login.html', message= "")
    logout_user()
    session.pop('username',None)
    return render_template('login.html', message= "successfully logged out")

if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'the random string'
    app.run(debug = True)

from flask import Flask,render_template,url_for,flash,redirect,request,jsonify,session,send_file
from datetime import date
from datetime import datetime
import mysql.connector,schedule
import base64 
from  base64 import b64encode
from PIL import Image
import os
from os.path import expanduser, join
from flask_login import login_required
from flask_mail import Mail, Message
import pandas as pd
import time
import threading
import io
import imghdr
import json

app = Flask(__name__)

app.config['SECRET_KEY'] = '595cb35b0ead18a9447fa848035471fe'

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'dbmsassignment19@gmail.com'
app.config['MAIL_PASSWORD'] = 'plxrmzyejopmpais'
mail = Mail(app)


# function to connect to mysql server
def connect_mysql(user, password, host, database):
    try:
        conn = mysql.connector.connect(user=user, password=password, host=host, database=database)
        return conn
    except mysql.connector.Error as error:
        print("Error while connecting to MySQL:", error)
        raise

# execute the query
def execute_query(conn, query, params=None,multi=False):
    cursor = conn.cursor()
    if not conn.is_connected():
        conn.ping(reconnect=True)
    try:
        if multi:
            # Split the query into individual statements
            statements = filter(None, query.split(';'))
            # Execute each statement separately
            for statement in statements:
                cursor.execute(statement, params)
                while cursor.nextset():
                    pass
            result = None
        else:
            cursor.execute(query, params)
            result = cursor.fetchall()
        return result
    except mysql.connector.Error as error:
        print("Error while executing query:", error)
        raise
    finally:
        conn.commit()
        cursor.close()

def execute_query_commit(conn, query, params=None):
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as error:
        print("Error while executing query:", error)
        raise
    finally:
        cursor.close()

#connect to mysql server
conn = connect_mysql("root", "sudeeksha@23", "localhost", "hms")

query = '''CREATE TABLE IF NOT EXISTS frontdeskop(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) NOT NULL,phone_number VARCHAR(10) NOT NULL,password VARCHAR(50) NOT NULL);'''
result = execute_query(conn, query)

query = '''CREATE TABLE IF NOT EXISTS dataentryop(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) NOT NULL,phone_number VARCHAR(10) NOT NULL,password VARCHAR(50) NOT NULL);'''
result = execute_query(conn, query)

query = '''CREATE TABLE IF NOT EXISTS  medication(id INT NOT NULL PRIMARY KEY,name VARCHAR(50) NOT NULL);'''
result = execute_query(conn, query)

query = '''CREATE TABLE IF NOT EXISTS tests_available(id INT NOT NULL PRIMARY KEY,name VARCHAR(50) NOT NULL);'''
result = execute_query(conn, query)

query = '''CREATE TABLE IF NOT EXISTS treatments_available(id INT NOT NULL PRIMARY KEY,name VARCHAR(50) NOT NULL,cost INT NOT NULL);'''
result = execute_query(conn, query)

query='''CREATE TABLE IF NOT EXISTS department (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,name VARCHAR(50)) AUTO_INCREMENT=1;'''
result = execute_query(conn, query)

query = '''CREATE TABLE IF NOT EXISTS doctor (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,name VARCHAR(50),department INT,password VARCHAR(50),phone_number VARCHAR(10),email_id VARCHAR(50),FOREIGN KEY (department) REFERENCES department(id))AUTO_INCREMENT=1000;'''
result = execute_query(conn, query)

query = '''CREATE TABLE IF NOT EXISTS patient (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,name VARCHAR(50) NOT NULL,age INT NOT NULL,address VARCHAR(50) NOT NULL,gender VARCHAR(10) NOT NULL,phone_number VARCHAR(15),insurance_id VARCHAR(15)) AUTO_INCREMENT = 1;'''
result = execute_query(conn, query)

query = '''CREATE TABLE IF NOT EXISTS appointment (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,patient_id INT NOT NULL,doctor_id INT,date DATETIME NOT NULL,time_slot VARCHAR(25) NOT NULL,emergency INT NOT NULL,symptoms VARCHAR(255),token INT,FOREIGN KEY (patient_id) REFERENCES patient(id),FOREIGN KEY (doctor_id) REFERENCES doctor(id))AUTO_INCREMENT=1;'''
result = execute_query(conn, query)

query = '''CREATE TABLE IF NOT EXISTS unread_notification(id INT PRIMARY KEY,FOREIGN KEY (id) REFERENCES appointment(id));'''
result = execute_query(conn, query)

query = '''CREATE TABLE IF NOT EXISTS prescribes (patient_id INT NOT NULL,doctor_id INT NOT NULL,date_prescribed DATETIME NOT NULL,dose VARCHAR(50),appointment_id INT,medication_id INT NOT NULL,FOREIGN KEY (patient_id) REFERENCES patient(id),FOREIGN KEY (doctor_id) REFERENCES doctor(id),FOREIGN KEY (appointment_id) REFERENCES appointment(id),FOREIGN KEY (medication_id) REFERENCES medication(id),PRIMARY KEY (patient_id, doctor_id,medication_id, date_prescribed));'''
result = execute_query(conn, query)

query = '''CREATE TABLE IF NOT EXISTS test(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,patient_id INT NOT NULL,date DATETIME,result VARCHAR(50),time_slot VARCHAR(50),test_report LONGBLOB,token INT,test_id INT NOT NULL,FOREIGN KEY (test_id) REFERENCES tests_available(id),FOREIGN KEY (patient_id) REFERENCES patient(id))AUTO_INCREMENT=1;'''
result = execute_query(conn, query)

query = '''CREATE TABLE IF NOT EXISTS room (id VARCHAR(50) NOT NULL PRIMARY KEY,type VARCHAR(50) NOT NULL,count INT NOT NULL);'''
result = execute_query(conn, query)

query = '''CREATE TABLE IF NOT EXISTS stay (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,patient_id INT NOT NULL,room_id VARCHAR(50),start_date DATETIME NOT NULL,end_date DATETIME,FOREIGN KEY (patient_id) REFERENCES patient(id),FOREIGN KEY (room_id) REFERENCES room(id));'''
result = execute_query(conn, query)

query = '''CREATE TABLE IF NOT EXISTS treatment (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,patient_id INT NOT NULL,doctor_id INT,date DATETIME ,time_slot VARCHAR(50),cost VARCHAR(50),stay_id INT,description VARCHAR(255),Side_Effects VARCHAR(255),token INT,treatment_id INT NOT NULL,FOREIGN KEY (patient_id) REFERENCES patient(id),FOREIGN KEY (doctor_id) REFERENCES doctor(id),FOREIGN KEY (stay_id) REFERENCES stay(id),FOREIGN KEY (treatment_id) REFERENCES treatments_available(id))AUTO_INCREMENT=1;'''
result = execute_query(conn, query)

@app.route("/")
@app.route("/home")
def home():
	return render_template('home.html')
@app.route("/frontdesk")
def frontdesk():
	return render_template('frontdesk_login.html',title='FrontDeskOperator | Login')
@app.route("/dataentry")
def dataentry():
	return render_template('dataentry_login.html',title='DataEntryOperator | Login')
@app.route("/administrator")
def administrator():
	return render_template('admin_login.html',title='Database Administrator')
@app.route('/auth_frontdesk', methods=['POST'])
def frontdesk_authenticate():
    id = request.form['id']
    password = request.form['password']
    query = "SELECT * FROM frontdeskop WHERE id = %s AND password = %s"
    params = (id, password)
    result = execute_query(conn, query, params)
    if result:
        frontdesk_operator_id = result[0][0] 
        return redirect(url_for('frontdesk_user', frontdesk_operator_id=frontdesk_operator_id))
    else:
        error = "Invalid id or password. Please try again."
        return render_template('frontdesk_login.html', error=error)

@app.route('/frontdesk/<string:frontdesk_operator_id>')
def frontdesk_user(frontdesk_operator_id):
    return render_template('frontdesk.html')

@app.route('/auth_dataentry', methods=['POST'])
def dataentryop_authenticate():
    id = request.form['id']
    password = request.form['password']
    query = "SELECT * FROM dataentryop WHERE id = %s AND password = %s"
    params = (id, password)
    result = execute_query(conn, query, params)
    if result:
        dataentry_operator_id = result[0][0] 
        return redirect(url_for('dataentry_user', dataentry_operator_id=dataentry_operator_id))
    else:
        error = "Invalid id or password. Please try again."
        return render_template('dataentry_login.html', error=error)

@app.route('/dataentry/<string:dataentry_operator_id>')
def dataentry_user(dataentry_operator_id):
    return render_template('data_entry.html')

@app.route('/auth_admin',methods=['POST'])
def admin_authenticate():
    password = request.form['password']
    if password == "hms@123":
        return render_template('administrator.html')
    else:
        error = "Invalid password. Please try again."
        return render_template('admin_login.html',error=error)

@app.route('/admin_main',methods=['POST','GET'])    
def administrator_mainpage():
    return render_template('administrator.html')

@app.route('/AddingUser',methods=['POST','GET'])
def add_user():
    return render_template('add_user.html')

@app.route('/AddingFrontdeskOp',methods=['POST','GET'])
def add_frontdesk_op():
    return render_template('Add frontDeskop.html')

@app.route("/FrontdeskOpInsert",methods=['POST','GET'])
def frontdeskop_insert():
    name = request.form['FrontDeskoperatorName']
    phone_number = request.form['Number']
    password = request.form['password']
    query = '''INSERT INTO frontdeskop(username,phone_number,password) VALUES(%s,%s,%s)'''
    params = (name,phone_number,password)
    result = execute_query_commit(conn,query,params)
    status = "Registered FrontDeskOperator successfully"
    return render_template('Add frontDeskop.html',status=status)

@app.route('/AddingDataEntryOp',methods=['POST','GET'])
def add_dataentry_op():
    return render_template('Add dataEntryop.html')

@app.route("/DataEntryOpInsert",methods=['POST','GET'])
def dataentryop_insert():
    name = request.form['DataEntryoperatorName']
    phone_number = request.form['Number']
    password = request.form['password']
    query = '''INSERT INTO dataentryop(username,phone_number,password) VALUES(%s,%s,%s)'''
    params = (name,phone_number,password)
    result = execute_query_commit(conn,query,params)
    status = "Registered DataEntryOperator successfully"
    return render_template('Add dataEntryop.html',status=status)

@app.route('/AddingDoctor',methods=['POST','GET'])
def add_doctor():
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT name FROM department')
    data = cursor.fetchall()
    return render_template('Add Doctor.html',departments=data)

@app.route("/DoctorInsert",methods=['POST','GET'])
def doctor_insert():
    name = request.form['DoctorName']
    phone_number = request.form['Number']
    department_name = request.form['Department']
    query = "SELECT id FROM department WHERE name = %s"
    params=(department_name,)
    data = execute_query(conn,query,params)
    department_id = data[0][0]
    email_id = request.form['email']
    password = request.form['password']
    query = '''INSERT INTO doctor(name,department,password,phone_number,email_id) VALUES(%s,%s,%s,%s,%s)'''
    params = (name,department_id,password,phone_number,email_id)
    result = execute_query_commit(conn,query,params)
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT name FROM department')
    data = cursor.fetchall()
    status = "Registered Doctor successfully"
    return render_template('Add Doctor.html',departments=data,status=status)

@app.route('/DeleteUser',methods=['POST','GET'])
def delete_user():
    return render_template('delete_user.html')

@app.route('/DeletingFrontdeskOp',methods=['POST','GET'])
def delete_frontdesk_op():
    return render_template('Delete FrontDeskop.html')

@app.route('/RemoveFrontdeskOp',methods=['POST','GET'])
def remove_frontdesk_op():
    id = request.form['FrontDeskoperatorid']
    query = "SELECT * FROM frontdeskop WHERE id = %s"
    params = (id,)
    result = execute_query(conn, query, params)
    if result:
        query = "DELETE FROM frontdeskop WHERE id = %s"
        params = (id,)
        data = execute_query_commit(conn, query, params)
        status = "User deleted successfully!"
        return render_template('Delete FrontDeskop.html', status=status)
    else:
        error = "ID not found! Please try again"
        return render_template('Delete FrontDeskop.html',error=error)

@app.route('/DeletingDataEntryOp',methods=['POST','GET'])
def delete_dataentry_op():
    return render_template('Delete Dataentryop.html')

@app.route('/RemoveDataEntryOp',methods=['POST','GET'])
def remove_dataentry_op():
    id = request.form['DataEntryoperatorid']
    query = "SELECT * FROM dataentryop WHERE id = %s"
    params = (id,)
    result = execute_query(conn, query, params)
    if result:
        query = "DELETE FROM dataentryop WHERE id = %s"
        params = (id,)
        data = execute_query_commit(conn, query, params)
        status = "User deleted successfully!"
        return render_template('Delete Dataentryop.html', status=status)
    else:
        error = "ID not found! Please try again"
        return render_template('Delete Dataentryop.html',error=error)

@app.route('/DeletingDoctor',methods=['POST','GET'])
def delete_doctor():
    return render_template('Delete Doctor.html')

@app.route('/RemoveDoctor',methods=['POST','GET'])
def remove_doctor():
    id = request.form['Doctorid']
    query = "SELECT * FROM doctor WHERE id = %s"
    params = (id,)
    result = execute_query(conn, query, params)
    if result:
        query = "UPDATE doctor SET password=NULL WHERE id = %s"
        params = (id,)
        data = execute_query_commit(conn, query, params)
        status = "User deleted successfully!"
        return render_template('Delete Doctor.html', status=status)
    else:
        error = "ID not found! Please try again"
        return render_template('Delete Doctor.html',error=error)

@app.route("/PatientRegistration")
def patient_registration():
    return render_template('Patient Registration.html')

@app.route("/PatientInsert",methods=['POST'])
def patient_insert():
    name = request.form['PatientName']
    age = request.form['Age']
    address = request.form['Address']
    gender = request.form['Gender'] 
    phone_number = request.form['Number']
    insurance_id = request.form['Insurance id']
    query = '''INSERT INTO patient(name,age,address,gender,phone_number,insurance_id) VALUES(%s,%s,%s,%s,%s,%s)'''
    params = (name,age,address,gender,phone_number,insurance_id)
    result = execute_query_commit(conn,query,params)
    status = "Registered patient successfully"
    return render_template('Patient Registration.html',status=status)

@app.route('/Appointment', methods=['GET', 'POST'])
def book_appointment():
    # Connect to the database
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT name FROM department')
    data = cursor.fetchall()

    # Pass the data to the HTML template
    return render_template('ind.html', specialisations=data)

@app.route('/get_doctors/<specialisation>',methods=['GET'])
def get_doctors(specialisation):
    # Connect to the database and retrieve data for the second drop-down
    # print(specialisation)
    cursor = conn.cursor()
    cursor.execute('SELECT doctor.id,doctor.name FROM doctor,department WHERE doctor.department=department.id AND department.name=%s', (specialisation,))
    data = cursor.fetchall()
    # print(data)
     # Filter the doctors based on availability on the selected date and time slot
    selected_date = request.args.get('date')
    selected_time_slot = request.args.get('time_slot')
    available_doctors = []
    for doctor in data:
        cursor.execute('SELECT * FROM appointment WHERE doctor_id=%s AND DATE(date)=%s AND time_slot=%s', (doctor[0], selected_date, selected_time_slot))
        appointments = cursor.fetchall()
        if len(appointments) < 10 :
            available_doctors.append(doctor)
    # Return the data as a JSON object
    return jsonify(doctors=available_doctors)

@app.route('/auth_pat', methods=['POST'])
def authenticate_patient():
    # print(1)
    patient_id = request.form['Patientid']
    emergency = request.form['emergency']
    query = "SELECT * FROM patient WHERE id = %s"
    params = (patient_id,)
    result = execute_query(conn, query, params)
    if result:
        if emergency=='1':
            # print(date)
            doctor_id = None
            time_slot = ""
            query = '''INSERT INTO appointment(patient_id,doctor_id,date,time_slot,emergency) VALUES(%s,%s,NOW(),%s,%s)'''
            params = (patient_id,doctor_id,time_slot,emergency)
            status = "Appointment booked successfully!"
        else:
            doctor_name = request.form['DoctorName']
            date = request.form['Date']
            time_slot = request.form['TimeSlot']
            if doctor_name == "" or date == "" or time_slot == "":
                error = "Enter all the details!"
                cursor = conn.cursor()
                cursor.execute('SELECT DISTINCT name FROM department')
                data = cursor.fetchall()
                return render_template('ind.html', error=error, specialisations=data)
            else: 
                query = "SELECT id FROM doctor WHERE name = %s"
                params=(doctor_name,)
                data = execute_query(conn,query,params)
                doctor_id = data[0][0]
                query = "SELECT * FROM appointment WHERE doctor_id=%s AND DATE(date)=%s AND time_slot=%s"
                params = (doctor_id, date, time_slot)
                appointments = execute_query(conn,query,params)
                token = 1 + len(appointments)
                query = '''INSERT INTO appointment(patient_id,doctor_id,date,time_slot,emergency,token) VALUES(%s,%s,%s,%s,%s,%s)'''
                params = (patient_id,doctor_id,date,time_slot,emergency,token)
                status = "Appointment booked successfully! Your token no is " + str(token)
        data = execute_query_commit(conn,query,params)
        query = '''SELECT MAX(id) FROM appointment'''
        appointment_id = execute_query(conn,query)
        query = '''INSERT INTO unread_notification(id) VALUES(%s)'''
        params=(appointment_id[0][0],)
        notif_data = execute_query_commit(conn,query,params)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT name FROM department')
        data = cursor.fetchall()
        return render_template('ind.html', status=status, specialisations=data)
    else:
        error = "PatientID not found. Please try again."
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT name FROM department')
        data = cursor.fetchall()
        return render_template('ind.html', error=error, specialisations=data)

@app.route('/TestSchedule')
def test_schedule():
    return render_template('test.html')

@app.route('/get_slots/<date>',methods=['GET'])
def get_slots(date):
    # Connect to the database and retrieve data for the second drop-down
    cursor = conn.cursor()
    data = ['9-12','2-5','6-10']
    available_slots = []
    for slot in data:
        cursor.execute('SELECT * FROM test WHERE DATE(date)=%s AND time_slot=%s', (date,slot))
        tests = cursor.fetchall()
        if len(tests) < 10 :
            available_slots.append(slot)
    return jsonify(slots=available_slots)

@app.route('/TestInsert', methods=['POST'])
def test_insert():
    Test_id = request.form['Testid']
    query = "SELECT * FROM test WHERE id = %s"
    params = (Test_id,)
    result = execute_query(conn, query, params)
    if result:
        Date=request.form['date']
        timeSlot=request.form['timeSlot']
        query = "SELECT test_id FROM test WHERE id = %s"
        params=(Test_id,)
        data = execute_query(conn,query,params)
        test_name = data[0][0]

        query = "SELECT * FROM test WHERE test_id=%s AND DATE(date)=%s AND time_slot=%s"
        params = (test_name, Date, timeSlot)
        # print(params)
        tests = execute_query(conn,query,params)
        token = len(tests) +1 
        query = '''UPDATE test SET date = %s, time_slot = %s, token = %s WHERE id = %s '''
        params = (Date,timeSlot,token,Test_id)
        result = execute_query_commit(conn,query,params)
        status="Test Scheduled sucessfully! Your token no is " + str(token)
        return render_template('test.html',status=status)
    else:
        error = "Invalid test_id. Please enter correct test_id."
        return render_template('test.html', error=error)

@app.route('/TreatmentSchedule', methods=['GET','POST'])
def treatment():
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT name FROM department')
    data = cursor.fetchall()
    return render_template('treatment.html',specialisations=data)

@app.route('/get_doctors_treatment/<specialisation>',methods=['GET'])
def get_doctors_treatment(specialisation):
    # Connect to the database and retrieve data for the second drop-down
    cursor = conn.cursor()
    cursor.execute('SELECT doctor.id,doctor.name FROM doctor,department WHERE doctor.department=department.id AND department.name=%s', (specialisation,))
    data = cursor.fetchall()

     # Filter the doctors based on availability on the selected date and time slot
    selected_date = request.args.get('date')
    selected_time_slot = request.args.get('time_slot')
    available_doctors = []
    for doctor in data:
        cursor.execute('SELECT * FROM treatment WHERE doctor_id=%s AND DATE(date)=%s AND time_slot=%s', (doctor[0], selected_date, selected_time_slot))
        treatments = cursor.fetchall()
        if len(treatments)<5 :
            available_doctors.append(doctor)
    # Return the data as a JSON object
    return jsonify(doctors=available_doctors)


@app.route('/auth_treat', methods=['POST'])
def authenticate_treatment():
    print("here in the code")
    Treatment_id = request.form['Treatmentid']
    query = "SELECT * FROM treatment WHERE id = %s"
    params = (Treatment_id,)
    result = execute_query(conn, query, params)
    if result:
        doctor_name = request.form['DoctorName']
        query = "SELECT id FROM doctor WHERE name = %s"
        params=(doctor_name,)
        data = execute_query(conn,query,params)
        doctor_id = data[0][0]
        # treatmenttype=request.form['Treatmenttype']
        Date=request.form['date']
        timeSlot=request.form['timeSlot']
        query = "SELECT * FROM treatment WHERE doctor_id=%s AND DATE(date)=%s AND time_slot=%s"
        params = (doctor_id, Date, timeSlot)
        treatments = execute_query(conn,query,params)
        token = 1 + len(treatments)
        query = '''UPDATE treatment SET doctor_id = %s, date = %s, time_slot = %s, token = %s WHERE id = %s '''
        params = (doctor_id,Date,timeSlot,token,Treatment_id)
        data = execute_query_commit(conn,query,params)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT name FROM department')
        data = cursor.fetchall()
        status="Treatment Scheduled sucessfully! Your token no is " + str(token)
        return render_template('treatment.html',status=status,specialisations=data)
    else:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT name FROM department')
        data = cursor.fetchall()

        error = "TreatmentID not found. Please try again."
        return render_template('treatment.html', error=error,specialisations=data)

@app.route('/AdmitPatient')
def admit():
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT type FROM room')
    data = cursor.fetchall()
    return render_template('admit.html',Roomtype=data)

@app.route('/get_rooms/<Roomtype>',methods=['GET'])
def get_room(Roomtype):
    # Connect to the database and retrieve data for the second drop-down
    cursor = conn.cursor()
    cursor.execute('SELECT id,type FROM room WHERE type=%s', (Roomtype,))
    data = cursor.fetchall()

     # Filter the doctors based on availability on the selected date and time slot
    available_rooms = []
    # print(data)
    for roomnum in data:
        cursor.execute('SELECT DISTINCT id FROM room WHERE id=%s AND count!=0 ', (roomnum[0],))
        rooms = cursor.fetchall()
        # print(rooms)
        if rooms:
            available_rooms.append(rooms)
    # Return the data as a JSON object
    return jsonify(room=available_rooms)

@app.route('/auth_admit', methods=['POST'])
def authenticate_admit():
    # print("here in the code")
    Treatment_id = request.form['Treatmentid']
    query = "SELECT * FROM treatment WHERE id = %s"
    params = (Treatment_id,)
    result = execute_query(conn, query, params)
    if result:
        query = "SELECT patient_id FROM treatment WHERE id = %s"
        params=(Treatment_id,)
        data = execute_query(conn,query,params)
        patient_id = data[0][0]
        room_id = request.form['RoomNumber']
        start_date = request.form['date']
        query = '''INSERT INTO stay(patient_id,room_id,start_date) VALUES(%s,%s,%s)'''
        params = (patient_id,room_id,start_date)
        data = execute_query_commit(conn,query,params)
        query = '''UPDATE treatment SET stay_id = (SELECT MAX(id) FROM stay) WHERE id=%s'''
        params=(Treatment_id,)
        data = execute_query_commit(conn,query,params)
        query = '''UPDATE room SET count = count-1 WHERE id = %s'''
        params=(room_id,)
        data = execute_query_commit(conn,query,params)
        status="Patient Admitted Successfully!"
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT type FROM room')
        data = cursor.fetchall()
        return render_template('admit.html',status=status, Roomtype=data)
    else:
        error = "Invalid Treatment_id. Enter correct Treatment id!"
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT type FROM room')
        data = cursor.fetchall()
        return render_template('admit.html',error=error, Roomtype=data)

@app.route('/Discharge', methods=['GET','POST'])
def Discharge():
    return render_template('discharge.html')

@app.route('/auth_discharge', methods=['POST'])
def authenticate_Discharge():
    Treatment_id = request.form['Treatmentid']
    query = "SELECT * FROM treatment WHERE id = %s"
    params = (Treatment_id,)
    result = execute_query(conn, query, params)

    if result:
        end_date = request.form['date']
        query = "UPDATE stay SET end_date=%s WHERE id=(SELECT stay_id FROM treatment WHERE id = %s)"
        params = (end_date,Treatment_id)
        data = execute_query_commit(conn,query,params)
        query = "UPDATE room SET count=count+1 WHERE id = (SELECT stay.room_id FROM stay,treatment WHERE treatment.stay_id=stay.id AND treatment.id=%s)"
        params = (Treatment_id,)
        data = execute_query_commit(conn,query,params)
        status="Discharged sucessfully!"
        return render_template('discharge.html',status=status)
    else:
        error = "Invalid Treatment_id. Please enter correct Treatment_id."
        return render_template('discharge.html',error=error)

# route to display all patient records
@app.route("/show_patient_details")
def show_all_patients():
    # execute SQL query to retrieve all records from patient table
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patient")
    # fetch all records
    records = cursor.fetchall()
    # render template and pass records to HTML for display
    return render_template('show_all.html', records=records)

# route to edit a patient record
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_patient_details(id):
    # execute SQL query to retrieve record with given id
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patient WHERE id=%s", (id,))
    # fetch the record
    record = cursor.fetchone()
    
    if request.method == 'POST':
        # get updated values from form
        name = request.form['name']
        age = request.form['age']
        address = request.form['address']
        gender = request.form['gender']
        phone_number = request.form['phone_number']
        insurance_id = request.form['insurance_id']
        
        # execute SQL query to update the record with the new values
        sql = "UPDATE patient SET name=%s, age=%s, address=%s, gender=%s, phone_number=%s, insurance_id=%s WHERE id=%s"
        val = (name, age, address, gender, phone_number, insurance_id, id)
        cursor.execute(sql, val)
        conn.commit()
        
        # redirect to the show_all route to display updated records
        return redirect('/show_patient_details')
        
    # render template and pass record to HTML for display in edit form
    return render_template('edit.html', record=record)

@app.route('/dataentry/test_details', methods=['GET', 'POST'])
def test_details():
    if  request.method == 'POST':
        patient_id = request.form['patient_id']
        test_id = request.form['test_id']
        test_result = request.form['test_result']
        test_report = request.files['test_report']
        #file_path = os.path.abspath('/Downloads/' + test_report.filename)
        #test_report.save(file_path)
        #with open(file_path, 'rb')as f:
            #file_data = f.read()
        
        if patient_id == '' or test_id == '' or test_result == '' or test_report == '':
            return render_template('test_details.html', error='Please fill all the fields.')

        # Check if patient ID and test ID exists in the database
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patient WHERE id=%s", (patient_id,))
        patient = cursor.fetchone()
        if not patient:
            return render_template('test_details.html', error='Patient ID not found. Please enter correct ID.')

        cursor.execute("SELECT * FROM test WHERE patient_id=%s AND id=%s", (patient_id, test_id))
        test = cursor.fetchone()
        if not test:
            return render_template('test_details.html', error='Invalid ID. Please enter correct ID.')

        cursor.execute("UPDATE test SET result=%s WHERE patient_id=%s AND id=%s",
                       (test_result, patient_id, test_id))
        if not test_report:
           return render_template('test_details.html', error='Please fill all the fields')
        if test_report:
            # file_path = os.path.abspath('/Downloads/' + test_report.filename)
            home = expanduser("~")
            downloads_folder = join(home, "Downloads")
            file_path = join(downloads_folder, test_report.filename)
            test_report.save(file_path)
            with open(file_path, 'rb') as f:
                file_data = f.read()
            cursor.execute("UPDATE test SET test_report=%s WHERE patient_id=%s AND id=%s",
                       (file_data, patient_id, test_id))
        conn.commit()
        
        success = 'Test details updated successfully!'
        return render_template('test_details.html', success=success)
        
    else:
        
        return render_template('test_details.html')


@app.route('/search_treatment_description',methods=['POST','GET'])
def search_treatment_description():
    treatment_id = request.form['search']
    cursor = conn.cursor()
    cursor.execute('SELECT description FROM treatment WHERE id = %s', (treatment_id,))
    row = cursor.fetchone()
    cursor.close()
    if row is not None:
        session['treatment_id'] = treatment_id
        return render_template('treatment_details.html', treatment_id=treatment_id, treatment_description=row[0])
    else:
        return render_template('treatment_details.html', error='Treatment ID not found')


@app.route('/dataentry/treatment_details', methods=['GET', 'POST'])
def treatment_details():
    if request.method == 'POST':
        treatment_id = session['treatment_id']
        print(treatment_id)
        treatment_description = request.form['treatment_description']
        side_effects = request.form['side_effects']
        cost = request.form['cost']
        
        if not all([treatment_id, treatment_description, side_effects, cost]):
            return render_template('treatment_details.html', error='Please fill all the fields.')
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM treatment WHERE id=%s", (treatment_id,))
        treatment = cursor.fetchone()
        if not treatment:
            return render_template('treatment_details.html', error='Invalid Treatment ID. Please enter correct ID.')
       
        cursor.execute("UPDATE treatment SET description=%s, side_effects=%s, cost=%s WHERE id=%s",
                       (treatment_description, side_effects, cost, treatment_id))
        
        conn.commit()

        success = 'Treatment details updated successfully!'
        return render_template('treatment_details.html', success=success)

    else:
        return render_template('treatment_details.html')






@app.route('/dataentry/medication_details', methods=['GET', 'POST'])
def medication_details():
    if request.method == 'POST':
        
        appointment_id = request.form['appointment_id']
        
        medication_id = request.form['medication_id']
        
        medicine_dose = request.form['medicine_dose']
        symptoms=request.form['symptoms']
        if  appointment_id == '' or medicine_dose == ''  or symptoms=='':
            return render_template('medication_details.html', error='Please fill all the fields.')
        cursor = conn.cursor()
       
       # cursor.execute("SELECT id FROM medication WHERE name=%s",(medication_name,))
       # medication_data=cursor.fetchall()
       # medication_id=medication_data[0][0]
       
        cursor.execute("SELECT * FROM appointment WHERE id=%s",(appointment_id,) )
        appointment=cursor.fetchall()
        if not appointment:
            return render_template("medication_details.html", error="Invalid Appointment ID,Enter correct ID")
        
        cursor.execute("SELECT patient_id,doctor_id FROM appointment WHERE id=%s",(appointment_id,))
        prescribes_data=cursor.fetchall()
        patient_id=prescribes_data[0][0]
        doctor_id=prescribes_data[0][1]
        
        cursor.execute("SELECT id,name FROM medication")
        medications=cursor.fetchall()
        print("medications",medications)
        
        cursor.execute("INSERT INTO prescribes (patient_id,doctor_id,appointment_id,medication_id,date_prescribed,dose) VALUES (%s,%s, %s,%s, NOW(),%s)",
                       (patient_id,doctor_id,appointment_id,medication_id,medicine_dose))
        
        cursor.execute("UPDATE appointment SET symptoms=%s WHERE patient_id=%s AND id=%s",
                   (symptoms, patient_id, appointment_id))
        conn.commit()
        return render_template("medication_details.html", medications=medications,success="Medication details added successfully!")
    else:
      
        cursor = conn.cursor()
        cursor.execute("SELECT id,name FROM medication")
        medications=cursor.fetchall()
        return render_template ('medication_details.html', medications=medications)


@app.route("/doctor")
def doctor():
    return render_template('doctor_login.html',title='Doctor | Login')
    
@app.route('/auth_doctor', methods=['POST'])
def doctor_authenticate():
    id = request.form['id']
    password = request.form['password']
    query = "SELECT * FROM doctor WHERE id = %s AND password = %s"
    params = (id, password)
    result = execute_query(conn, query, params)
    if result:
        doctor_id = result[0][0] 
        return redirect(url_for('doctor_dashboard', doctor_id=doctor_id))
    else:
        error = "Invalid username or password. Please try again."
        return render_template('doctor_login.html', error=error)

 
#needed   
@app.route('/doctor/<string:doctor_id>/dashboard',methods=['GET', 'POST'])
def doctor_dashboard(doctor_id):
    # connect to database and execute query
    query = "SELECT p.id, p.name, p.age, p.gender,ta.name, t.date FROM ((patient p JOIN treatment t ON p.id = t.patient_id) JOIN treatments_available ta ON t.treatment_id=ta.id) WHERE t.doctor_id = %s AND t.date >= NOW() ORDER BY t.date DESC;"
    params = (doctor_id,)
    result = execute_query(conn, query, params)
    
    query = "SELECT p.id, p.name, p.age, p.gender, t.date FROM patient p JOIN treatment t ON p.id = t.patient_id WHERE t.doctor_id = %s AND t.date < NOW() ORDER BY t.date DESC;"
    params = (doctor_id,)
    result1 = execute_query(conn, query, params)
    
    # pass query result to template for display
    return render_template('doctor-dashboard.html', doctor_id=doctor_id,patients=result,patients_past=result1)

# search route---needed
@app.route('/search/<string:doctor_id>', methods=['POST'])
def search(doctor_id):
    search_term = request.form['search']
    query = "SELECT id,name,age,gender FROM patient WHERE name LIKE %s OR id LIKE %s OR gender LIKE %s"
    params=(search_term,search_term,search_term)
    result = execute_query(conn, query, params)
    if(len(result)==0):
        return render_template('view_patient.html',  doctor_id=doctor_id, error="User not found")
    #print(result)
    
    query = "SELECT t.id,ta.name,t.date, t.description, t.doctor_id FROM ((patient p JOIN treatment t on p.id = t.patient_id) JOIN treatments_available ta ON t.treatment_id = ta.id) WHERE p.id = %s  ORDER BY t.date DESC"
    params = (result[0][0],)
    result1 = execute_query(conn, query, params)
    #print(result1)
    
    query = "SELECT a.id AS appointment_id, pr.date_prescribed, a.symptoms, m.name  FROM (((prescribes pr JOIN  patient p ON pr.patient_id = p.id AND pr.doctor_id = %s AND p.id=%s) LEFT JOIN appointment a  ON a.id = pr.appointment_id) JOIN medication m ON pr.medication_id=m.id)  ORDER BY a.date DESC"
    params = (doctor_id,result[0][0])

    result2 = execute_query(conn, query, params)
    #print(result2)
    
    query = "SELECT test.id,ta.name,date,result,test_report  FROM (test JOIN tests_available ta ON test.test_id= ta.id) WHERE patient_id=%s  ORDER BY date DESC"
    params = (result[0][0],)

    result3 = execute_query(conn, query, params)

    return render_template('view_patient.html', patient=result, doctor_id=doctor_id,treatment_details=result1, appointment_details=result2,test_details=result3)

#needed
@app.route('/prescribe_medication/<string:doctor_id>', methods=['GET','POST'])
def prescribe_medication(doctor_id):
    return render_template('prescribe_medication.html',  doctor_id=doctor_id)

@app.route('/prescribe_medication_patient/<string:doctor_id>/patient', methods=['GET','POST'])
def prescribe_medication_patient(doctor_id):
    search_term = request.form['search']
    query = "SELECT id FROM patient WHERE name LIKE %s OR id LIKE %s OR gender LIKE %s"
    params=(search_term,search_term,search_term)
    result = execute_query(conn, query, params)
    #print("len of result=")
    #print(len(result))
    if(len(result)==0):
        #print("len of result=")
        #print(len(result))
        return render_template('prescribe_medication_patient.html',  doctor_id=doctor_id,patient_id=0,search_term=search_term,error="User not found")
    
    query = "SELECT id , name FROM medication "
    result1 = execute_query(conn, query)
    #print("result1=",result1)
    return render_template('prescribe_medication_patient.html',  doctor_id=doctor_id,patient_id=result[0][0],search_term=search_term,medications=result1)

@app.route('/prescribe_medication_update/<string:doctor_id>/<string:patient_id>', methods=['GET','POST'])
def prescribe_medication_patient_update(doctor_id,patient_id):
    appointment_id=request.form['appointment_id']
    med_id=request.form['medication_id']
    #print(med_id)
    med_dosage=request.form['med_dosage']
    #print(med_dosage)
    
    
    if appointment_id=='':
        #print(patient_id,doctor_id,med_id,med_dosage)

        query=" INSERT INTO prescribes (patient_id, doctor_id, medication_id, date_prescribed, dose) VALUES (%s, %s,  %s , NOW(), %s);"
        params=(patient_id,doctor_id,med_id,med_dosage)

    else:
        query="SELECT id FROM appointment WHERE id=%s AND appointment.patient_id=%s "
        params=(appointment_id,patient_id)
        result=execute_query(conn, query, params)
        #print(result)
        #print(len(result))
        if(len(result)==0):
            #print("inside if clause")
            return render_template('prescribe_medication.html',  doctor_id=doctor_id, error="Invalid Appointment ID.Try Again")
        query=" INSERT INTO prescribes (patient_id, doctor_id, medication_id,date_prescribed, dose,appointment_id) VALUES (%s, %s,  %s , NOW(), %s,%s);"
        params=(patient_id,doctor_id,med_id,med_dosage,appointment_id)
    
    execute_query(conn, query, params)
   
    return render_template('prescribe_medication.html',  doctor_id=doctor_id,success="Added Successfully!")

@app.route('/doctor/<string:doctor_id>/appointments', methods=['GET','POST'])
def appointment(doctor_id):
    query = "SELECT p.id,p.name,p.age,p.gender,a.date FROM (patient p JOIN  appointment a on p.id = a.patient_id AND a.doctor_id = %s AND a.id IN (SELECT id FROM unread_notification))  ORDER BY a.date DESC"
    params = (doctor_id,)
    #print("doctor_id="+doctor_id)
    result = execute_query(conn, query, params)
    
    query = "SELECT p.id,p.name,p.age,p.gender,a.date FROM ( patient p JOIN  appointment a on p.id = a.patient_id AND a.doctor_id = %s AND a.id NOT IN (SELECT id FROM unread_notification))  ORDER BY a.date DESC"
    params = (doctor_id,)
    #print("doctor_id="+doctor_id)
    result1 = execute_query(conn, query, params)
    
    query="DELETE FROM unread_notification"
    execute_query(conn, query)
    
    #print("result-")
    #print(result)
    return render_template('doctor-appointment.html',doctor_id=doctor_id, patients=result,patients_past=result1)

@app.route('/view/<string:doctor_id>/<string:patient_id>')
def view_patient(doctor_id,patient_id):
    # get the patient data from the database or any other data source

    query = "SELECT p.id,p.name,p.age,p.gender,a.date FROM patient p JOIN appointment a on p.id = a.patient_id WHERE p.id = %s AND a.doctor_id = %s ORDER BY a.date DESC"
    params = (patient_id,doctor_id)
    #print("doctor_id="+doctor_id)
    result = execute_query(conn, query, params)
    #print(result)
    return render_template('view_patient.html',doctor_id=doctor_id, patient=result)

@app.route('/viewTreatment/<string:doctor_id>/<string:patient_id>')
def viewTreatment_patient(doctor_id,patient_id):
    # get the patient data from the database or any other data source

    query = "SELECT p.id,p.name,p.age,p.gender FROM patient p  WHERE p.id = %s  "
    params = (patient_id,)
    #print("doctor_id="+doctor_id)
    result = execute_query(conn, query, params)
    #print(result)
    
    query = "SELECT t.id,ta.name,t.date, t.description, t.doctor_id FROM (patient p JOIN treatment t on p.id = t.patient_id) JOIN treatments_available ta ON t.treatment_id=ta.id WHERE p.id = %s  ORDER BY t.date DESC"
    params = (patient_id,)
    #print("doctor_id="+doctor_id+" patient_id="+patient_id)
    result1 = execute_query(conn, query, params)
    #print(result1)
    
    query = "SELECT a.id AS appointment_id, pr.date_prescribed, a.symptoms, m.name  FROM ((prescribes pr JOIN  patient p ON pr.patient_id = p.id AND pr.doctor_id = %s AND p.id=%s) LEFT JOIN appointment a  ON a.id = pr.appointment_id ) JOIN medication m ON pr.medication_id = m.id  ORDER BY a.date DESC"
    params = (doctor_id,patient_id)
    #print("doctor_id="+doctor_id+" patient_id="+patient_id)
    result2 = execute_query(conn, query, params)
    #print(result2)
    
    query = "SELECT test.id,ta.name,date,result,test_report  FROM (test JOIN tests_available ta on test.test_id = ta.id) WHERE patient_id=%s  ORDER BY date DESC"
    params = (patient_id,)
    
    
    result3 = execute_query(conn, query, params)
    
    return render_template('view_patient.html',doctor_id=doctor_id, patient=result, treatment_details=result1, appointment_details=result2,test_details=result3)

@app.route('/update/<string:doctor_id>/<string:patient_id>')
def update_patient(doctor_id,patient_id):
    # get the patient data from the database or any other data source
    query = "SELECT p.id,p.name,p.age,p.gender,a.date FROM patient p JOIN treatment a on p.id = a.patient_id AND p.patient_id = %s AND a.doctor_id = %s ORDER BY a.date DESC"
    params = (patient_id,doctor_id)
    #print("doctor_id="+doctor_id)
    result = execute_query(conn, query, params)
    
    query = "SELECT t.id,ta.name,t.date, t.description, t.doctor_id FROM (patient p JOIN treatment t on p.id = t.patient_id AND p.patient_id = %s) JOIN treatments_available ta ON t.treatment_id=ta.id  ORDER BY t.date DESC"
    params = (patient_id)
    #print("doctor_id="+doctor_id)
    result1 = execute_query(conn, query, params)
    
    return render_template('view_patient.html',doctor_id=doctor_id, patient=result,treatment_details=result1)
 
 
@app.route('/prescribe_treatment/<string:doctor_id>', methods=['GET','POST'])
def prescribe_treatment(doctor_id):
    return render_template('prescribe_treatment.html',  doctor_id=doctor_id)

@app.route('/prescribe_treatment_patient/<string:doctor_id>/patient', methods=['GET','POST'])
def prescribe_treatment_patient(doctor_id):
    search_term = request.form['search']
    
    query = "SELECT id FROM patient WHERE name LIKE %s OR age LIKE %s OR gender LIKE %s"
    params=(search_term,search_term,search_term)
    result = execute_query(conn, query, params)
    
    query = "SELECT id , name FROM treatments_available "
    result1 = execute_query(conn, query)
    #print("result1=",result1)
    if(len(result)==0):
        return render_template('prescribe_treatment_patient.html',  doctor_id=doctor_id,patient_id=0,search_term=search_term, error="User not found")
    return render_template('prescribe_treatment_patient.html',  doctor_id=doctor_id,patient_id=result[0][0],search_term=search_term,treatments=result1)

@app.route('/prescribe_treatment_update/<string:doctor_id>/<string:patient_id>', methods=['GET','POST'])
def prescribe_treatment_patient_update(doctor_id,patient_id):
    treatment_id=request.form['treatment_id']
    treatment_description=request.form['treatment_description']
    #print(treatment_description)

    
    query=" INSERT INTO treatment (patient_id, doctor_id, treatment_id,  description) VALUES (%s, %s,  %s , %s);"
    params=(patient_id,doctor_id,treatment_id,treatment_description)
    
    execute_query(conn, query, params)
    return render_template('prescribe_treatment.html',  doctor_id=doctor_id,success="Added Successfully!")

#test
@app.route('/prescribe_test/<string:doctor_id>', methods=['GET','POST'])
def prescribe_test(doctor_id):
    return render_template('prescribe_test.html',  doctor_id=doctor_id)

@app.route('/prescribe_test_patient/<string:doctor_id>/patient', methods=['GET','POST'])
def prescribe_test_patient(doctor_id):
    search_term = request.form['search']
    
    query = "SELECT id FROM patient WHERE name LIKE %s OR age LIKE %s OR gender LIKE %s"
    params=(search_term,search_term,search_term)
    result = execute_query(conn, query, params)
    
    query = "SELECT id, name FROM tests_available "
    result1 = execute_query(conn, query)
    #print("result1 in test=",result1)
    if(len(result)==0):
        return render_template('prescribe_test_patient.html',  doctor_id=doctor_id,patient_id=0,search_term=search_term, error="User not found")
    return render_template('prescribe_test_patient.html',  doctor_id=doctor_id,patient_id=result[0][0],search_term=search_term,tests=result1)

@app.route('/prescribe_test_update/<string:doctor_id>/<string:patient_id>', methods=['GET','POST'])
def prescribe_test_patient_update(doctor_id,patient_id):
    test_id=request.form['test_id']



    
    query=" INSERT INTO test ( patient_id, test_id ) VALUES (%s, %s);"
    params=(patient_id,test_id)
    
    execute_query(conn, query, params)
    return render_template('prescribe_test.html',  doctor_id=doctor_id,success="Added Successfully!")


@app.route('/api/unread_appointments/<string:doctor_id>')
def get_unread_appointments(doctor_id):
    query="SELECT * from unread_notification JOIN appointment ON unread_notification.id=appointment.id WHERE doctor_id = %s"
    params=(doctor_id,)
    unread_appointments=execute_query(conn,query,params)
    #unread_appointments = Appointment.query.filter_by(doctor_id=doctor_id, read=False).count()
    return jsonify({'unread_appointments': len(unread_appointments)})


# Define send-email route
#@app.route('/send-email')
def send_email():
    print("sending mail")

    query="SELECT id, name, department, password, phone_number, email_id FROM doctor"
    doctors = execute_query(conn,query)
    for doctor in doctors:
        query="SELECT patient.id, patient.name, age, address, gender, patient.phone_number, description FROM ( patient JOIN treatment ON treatment.patient_id = patient.id AND treatment.doctor_id=%s) JOIN doctor ON treatment.doctor_id = doctor.id  AND doctor.email_id IS NOT NULL "
        params=(doctor[0],)
        patients = execute_query(conn,query,params)
        if patients:
            df = pd.DataFrame(patients, columns=['ID', 'Name', 'Age', 'Gender', 'Address', 'Phone Number', 'description'])
            html_table = df.to_html()
            msg = Message('Weekly Health Report', sender='dbmsassignment19@gmail.com', recipients=[doctor[5]])
            msg.html = html_table
            with app.app_context():
                mail.send(msg)
    return "Emails sent successfully!"
    """cur.execute("SELECT p.id, p.name, p.age, p.gender,p.address,p.phone_number,p.insurance_id, a.date, a.symptoms, pr.medication_name AS medication_name FROM appointment a JOIN prescribes pr ON a.id = pr.appointment_id  JOIN patient p ON a.patient_id = p.id WHERE a.date >= NOW() - INTERVAL 1 WEEK")
    emergency_cases = cur.fetchall()
    cur.close()
    if emergency_cases:
        df = pd.DataFrame(emergency_cases, columns=['ID', 'Name', 'Age', 'Gender', 'Address', 'Phone Number', 'Insurance ID',  'Date', 'Symptoms', 'Medication Name'])
        html_table = df.to_html()
        msg = Message('Emergency Health Report', sender='your-email@gmail.com', recipients=[doctor[5]])
        msg.html = html_table
        mail.send(msg)
        return "Emergency Email Sent!"
    else:
        return "No Emergency Cases Found!" """

# Schedule email to be sent once a week

def schedule_emails():
    #schedule.every().monday.at("15:46").do(send_email)
    while True:
        #print("in while loop")
        jobs = schedule.jobs
        if(len(jobs)!=0):
            #print("len=",len(jobs))
            for j in jobs:
                print(f"Next run time for job {j}: {j.next_run}")
        schedule.run_pending()
        time.sleep(60)
    

# Start the scheduler thread

"""@app.route('/file/<string:patient_id>/<string:treatment_id')
def get_file(patient_id,treatment_id):
    # Connect to the database
    
    # Retrieve the blob data for the specified file ID
    query = "SELECT data, mime_type FROM files WHERE id = %s"
    cursor.execute(query, (file_id,))
    data, mime_type = cursor.fetchone()
    # Close the database connection
    cursor.close()
    cnx.close()
    # Send the blob data as a response with the appropriate content type
    return Response(data, mimetype=mime_type)"""

@app.route('/viewimage/<int:test_id>')
def show_image(test_id):
    # Retrieve blob data from the database

    query = "SELECT test_report FROM test WHERE id=%s"
    params=(test_id,)
    result=execute_query(conn,query,params)
    if not result[0][0]:
        # print("here in if clause show_image")
        response = {'message': 'Image not found'}
        return json.dumps(response), 404
    # print("here outside if clause show_image: result=")
    # print(result)
    # print("len(result)")
    # print(len(result))
    # Return the blob data as a response
    return send_file(io.BytesIO(result[0][0]),mimetype=imghdr.what(io.BytesIO(result[0][0])))

if __name__ == '__main__':
    schedule.every().tuesday.at("00:35").do(send_email)
    scheduler_thread = threading.Thread(target=schedule_emails)
    scheduler_thread.start()
    app.run(debug=True)
from flask import Flask,render_template,request,redirect, flash
from flask import current_app as app
from .models import *

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('pwd')

        #for admin
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.password==password:
            return render_template('admin_dash.html')
        elif admin:
            return render_template('invalid_pwd.html')
        
        #for Doctor
        doctor = Doctor.query.filter_by(username=username).first()
        if doctor and doctor.password == password:
            return render_template('dr_dash.html')
        elif doctor:
            return render_template('invalid_pwd.html')
        
         #for Patient    
        patient = Patient.query.filter_by(username=username).first()
        if patient and patient.password == password:
            return render_template('patient_dash.html')
        elif patient:
            return render_template('invalid_pwd.html')

        return render_template('invalid_user.html')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name= request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('pwd')
        this_username = Patient.query.filter_by(username=username).first()
        this_email = Patient.query.filter_by(email=email).first()

        if this_username or this_email :
            return render_template('already_user_exist.html')
        else:
            patient = Patient(name=name, username=username, email=email, password=password)
            db.session.add(patient)
            db.session.commit()
            return redirect('/login')
        
    return render_template('register.html')
    
@app.route('/admin', methods=['GET'])
def admin():

    return render_template('admin_dash.html')

@app.route('/doctor', methods=['GET'])
def doctor():

    return render_template('dr_dash.html')

@app.route('/patient', methods=['GET'])
def patient():

    return render_template('patient_dash.html')
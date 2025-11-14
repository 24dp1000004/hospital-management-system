from flask import Flask,render_template,request,redirect, flash, url_for
from datetime import date, timedelta
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
            return redirect('/admin')
        elif admin:
            return render_template('invalid_pwd.html')
        
        #for Doctor
        doc = Doctor.query.filter_by(username=username).first()
        if doc and doc.password == password:
            return redirect(f'/doctor/{doc.doctor_id}')
        elif doc:
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
    this_user = Admin.query.filter_by(username='admin1').first()
    all_doctors = Doctor.query.all()
    all_patients = Patient.query.all()
    all_appoint = Appointment.query.all()
    return render_template('admin_dash.html', this_user=this_user, all_doctors=all_doctors, all_patients=all_patients, all_appoint=all_appoint)

@app.route('/doctor/<int:dr_id>' , methods=['GET'])
def doctor(dr_id):
    this_doctor =Doctor.query.filter_by(doctor_id=dr_id).first()
    appoint = Appointment.query.filter_by(doctor_id=dr_id, status="Upcoming").all()
    assigned_patients = Patient.query.filter_by(consultant=dr_id).all()
    return render_template('dr_dash.html', this_doctor=this_doctor, appoint=appoint, assigned_patients=assigned_patients)

@app.route('/patient/<int:pat_id>')
def patient(pat_id):
    this_patient = Patient.query.filter_by(patient_id=pat_id).first()

    return render_template('patient_dash.html')

@app.route("/update_patient_history/<int:appoint_id>", methods=['GET', 'POST'])
def update_patient_history(appoint_id):
    appoint = Appointment.query.filter_by(appointment_id=appoint_id).first()
    if request.method == 'POST':
        diag = request.form.get('diag')
        test = request.form.get('test')
        pres = request.form.get('pres')
        new_treatment = Treatment(appointment_id=appoint_id, diagnosis=diag, test_reports=test, prescription=pres)
        db.session.add(new_treatment)
        db.session.commit()
        return redirect(url_for('view_patient_history',appoint_id=appoint_id))
    return render_template('update_ph.html', appoint=appoint)

@app.route("/view_patient_history/<int:appoint_id>")
def view_patient_history(appoint_id):
    appoint = Appointment.query.filter_by(appointment_id=appoint_id).first()
    treatment = Treatment.query.filter_by(appointment_id=appoint_id).first()
    return render_template('view_ph.html', appoint=appoint, treatment=treatment)


@app.route('/doctor/<int:doctor_id>/availability', methods=['GET', 'POST'])
def doctor_availability(doctor_id):
    doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()
    #different slots dictionary
    doctor_time_options = {
    1: ["12:00 pm - 2:00 pm", "5:30 pm - 7:30 pm", "Not available"],
    2: ["10:00 am - 12:00 pm", "4:00 pm - 6:00 pm", "Not available"],
    3: ["9:00 am - 11:00 am", "3:00 pm - 5:00 pm", "Not available"],
    4: ["8:00 am - 10:00 am", "2:00 pm - 4:00 pm", "Not available"],
    5: ["10:00 am - 12:00 pm", "4:00 pm - 6:00 pm", "Not available"]
    }
    time_options = doctor_time_options.get(doctor_id)
    today = date.today()
    next_seven_days = [today + timedelta(days=i) for i in range(7)]
    
    if request.method == 'POST':
        Availability.query.filter_by(doctor_id=doctor_id).delete()   # Clear previous availability

        for d in next_seven_days:
            selected_slot = request.form.get(str(d))
            if selected_slot:
                new_avail = Availability(doctor_id=doctor_id, date=d, slot=selected_slot)
                db.session.add(new_avail)
        db.session.commit()
        flash("Availability saved successfully!", "success")
        return redirect(f'/doctor/{doctor.doctor_id}/availability')

    # Load saved availability
    existing = {a.date: a.slot for a in Availability.query.filter_by(doctor_id=doctor_id).all()}
    
    return render_template('update_availability.html', doctor=doctor, next_seven_days=next_seven_days, time_options=time_options, existing=existing)

@app.route('/complete_appoint/<int:appoint_id>')
def complete_appoint(appoint_id):
    appoint = Appointment.query.filter_by(appointment_id=appoint_id).first()
    appoint.status = "Completed"
    db.session.commit()
    return redirect(url_for('doctor', dr_id=appoint.doctor_id))

@app.route('/cancel_appoint/<int:appoint_id>')
def cancel_appoint(appoint_id):
    appoint = Appointment.query.filter_by(appointment_id=appoint_id).first()
    appoint.status = "Cancelled"
    db.session.commit()

    return redirect(url_for('doctor', dr_id=appoint.doctor_id))

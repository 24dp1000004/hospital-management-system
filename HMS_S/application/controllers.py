from flask import Flask,render_template,request,redirect, flash, url_for , session
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
            return redirect(f'/patient/{patient.patient_id}')
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
    appoint = Appointment.query.filter_by(doctor_id=dr_id).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    assigned_patients = Patient.query.filter_by(consultant=dr_id).all()
    return render_template('dr_dash.html', this_doctor=this_doctor, appoint=appoint, assigned_patients=assigned_patients)

@app.route('/patient/<int:pat_id>', methods=['GET']) 
def patient(pat_id):
    this_patient = Patient.query.filter_by(patient_id=pat_id).first()
    departments = Department.query.all()
    appoint = Appointment.query.filter_by(patient_id=pat_id).all()

    return render_template('patient_dash.html', this_patient=this_patient, departments=departments, appoint=appoint)

@app.route("/update_patient_history/<int:appoint_id>", methods=['GET', 'POST'])
def update_patient_history(appoint_id):
    appoint = Appointment.query.filter_by(appointment_id=appoint_id).first()
    if request.method == 'POST':
        diag = request.form.get('diag')
        test = request.form.get('test')
        pres = request.form.get('pres')
        new_treatment = Treatment(appointment_id=appoint_id, diagnosis=diag, test_reports=test, prescription=pres, patient_id=appoint.patient_id, doctor_id=appoint.doctor_id)
        db.session.add(new_treatment)
        appoint.status = "Updated"
        db.session.commit()
        return redirect(url_for('view_patient_history',appoint_id=appoint_id))
    return render_template('update_ph.html', appoint=appoint)

@app.route("/view_patient_history/<int:appoint_id>")
def view_patient_history(appoint_id):
    appoint = Appointment.query.filter_by(appointment_id=appoint_id).first()
    treatment = Treatment.query.filter_by(appointment_id=appoint_id).first()
    viewer = None
    if 'doctor_id' in session:
        viewer = "doctor"
    elif 'patient_id' in session:
        viewer = "patient"    
    return render_template('view_ph.html', appoint=appoint, treatment=treatment, viewer=viewer)


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
    appoint.patient.status = "Active" 
    appoint.patient.consultant = appoint.doctor_id
    db.session.commit()
    return redirect(url_for('doctor', dr_id=appoint.doctor_id))

@app.route('/cancel_appoint/<int:appoint_id>') 
def cancel_appoint(appoint_id):
    role = request.args.get('role')  #can be a doctor or patient to cance the appoint
    appoint = Appointment.query.filter_by(appointment_id=appoint_id).first()
    appoint.status = "Cancelled"
    db.session.commit()

    if role == 'patient':
        return redirect(url_for('patient', pat_id=appoint.patient_id))
    elif role == 'doctor':
        return redirect(url_for('doctor', dr_id=appoint.doctor_id))

@app.route('/patient/<int:pat_id>/department/<int:department_id>')     # department dash for PATIENT 
def department(pat_id, department_id):
    dept = Department.query.filter_by(department_id=department_id).first()
    doctors = Doctor.query.filter_by(dept_id=department_id).all()
    patient = Patient.query.filter_by(patient_id=pat_id).first()
    return render_template('department_dash.html', dept=dept, doctors=doctors, department_id=department_id, patient=patient)

@app.route('/patient/<int:pat_id>/department/<int:department_id>/<int:doctor_id>') 
def view_dr_details(department_id,doctor_id, pat_id):
    doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()
    patient = Patient.query.filter_by(patient_id=pat_id).first()
    department = Department.query.filter_by(department_id=department_id).first()
    return render_template('view_dr_details.html', doctor=doctor, department=department, patient=patient)

@app.route('/patient/<int:pat_id>/view_availability/<int:doctor_id>',  methods=['GET', 'POST'])
def view_doctor_availability( pat_id, doctor_id):
    patient = Patient.query.filter_by(patient_id=pat_id).first()
    doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()
    availability = Availability.query.filter_by(doctor_id=doctor_id).all()
    doctor_time_options = {
        1: ["12:00 pm - 2:00 pm", "5:30 pm - 7:30 pm"],
        2: ["10:00 am - 12:00 pm", "4:00 pm - 6:00 pm"],
        3: ["9:00 am - 11:00 am", "3:00 pm - 5:00 pm"],
        4: ["8:00 am - 10:00 am", "2:00 pm - 4:00 pm"],
        5: ["10:00 am - 12:00 pm", "4:00 pm - 6:00 pm"]
    }

    time_options = doctor_time_options.get(doctor_id)
    # Next 7 days
    today = date.today()
    next_seven_days = [today + timedelta(days=i) for i in range(7)]
    # Load saved availability of doctor
    existing = {a.date: a.slot for a in Availability.query.filter_by(doctor_id=doctor_id).all()}
    booked_slots = [(a.date, a.time) for a in Appointment.query.filter(Appointment.doctor_id == doctor_id, Appointment.status.in_(["Upcoming", "Completed"])).all()]


    if request.method == 'POST':

        selected_date = request.form.get("selected_date")
        selected_slot = request.form.get("selected_slot")

        if not selected_date or not selected_slot:
            flash("Please select a slot before booking!", "danger")
            return redirect(request.url)
        
        already_booked = Appointment.query.filter(Appointment.doctor_id == doctor.doctor_id, Appointment.date == selected_date, Appointment.time == selected_slot, Appointment.status == "Upcoming").first()

        if already_booked:
            flash("This slot is already booked by another patient.", "danger")
            return redirect(request.url)

        ap_existing = Appointment.query.filter_by(doctor_id=doctor.doctor_id, patient_id=patient.patient_id, date=selected_date, time=selected_slot).first()

        if ap_existing:
            if ap_existing.status == "Completed" or ap_existing.status == "Upcoming":
                flash("You already booked this slot with this doctor.", "warning")
                return redirect(f"/patient/{patient.patient_id}/view_availability/{doctor.doctor_id}")

        new_appt = Appointment(doctor_id=doctor.doctor_id, patient_id=patient.patient_id, date=selected_date, time=selected_slot)
        db.session.add(new_appt)
        db.session.commit()

        flash("Appointment booked successfully!", "success")
        return redirect(f"/patient/{patient.patient_id}")
        
    return render_template('view_availability.html', doctor=doctor, availability=availability, time_options=time_options, next_seven_days=next_seven_days, existing=existing, patient=patient, booked_slots=booked_slots)
  
@app.route("/patient/<int:pat_id>/past_appointments", methods=['GET'])
def past_appointments(pat_id):
    patient = Patient.query.filter_by(patient_id=pat_id).first()
    appoint = Appointment.query.filter(Appointment.patient_id==patient.patient_id, Appointment.status.in_(["Completed", "Cancelled"])).all()
    return render_template('p_past_appoint.html', patient=patient, appoint=appoint)

@app.route('/edit_patient/<int:pat_id>', methods=['GET','POST'])
def edit_patient(pat_id):
    patient = Patient.query.filter_by(patient_id=pat_id).first()
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('pwd')
        confirm_pwd = request.form.get('confirm_pwd')
        age = request.form.get('age')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        address = request.form.get('address')

        if password != confirm_pwd:
            flash("Passwords do not match", "danger")
            return redirect(request.url)

        if not phone or not phone.isdigit() or len(phone) != 10:
            flash("Invalid contact number — must be exactly 10 digits", "danger")
            return redirect(request.url)

        patient.name = name
        patient.age = age
        patient.gender = gender
        patient.phone = phone
        patient.address = address

        if password:
            patient.password = password

        db.session.commit()
        flash("Patient updated successfully!", "success")
        return redirect(url_for('patient', pat_id=patient.patient_id))

    return render_template('edit_patient.html', patient=patient)
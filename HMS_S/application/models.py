from .database import db

class Admin(db.Model):
    __tablename__ = "Admin"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

class Patient(db.Model):
    __tablename__ = "Patient"
    patient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    phone = db.Column(db.String())
    age = db.Column(db.Integer)
    gender = db.Column(db.String())
    email = db.Column(db.String(), unique=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    address = db.Column(db.String())
    patient_type = db.Column(db.String(), default='OPD')  # OPD/IPD
    status = db.Column(db.String(), default='Active')
    consultant = db.Column(db.Integer, db.ForeignKey('Doctor.doctor_id'))  #foreignkey
    appointments = db.relationship('Appointment', backref='patient', lazy=True)  # relationship
    treatment = db.relationship('Treatment', backref='patient', lazy=True) #realtionship

class Doctor(db.Model):
    __tablename__ = "Doctor"
    doctor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable = False)
    phone = db.Column(db.String(), nullable = False)
    age = db.Column(db.Integer, nullable = False)
    gender = db.Column(db.String(), nullable = False)
    email = db.Column(db.String(), unique=True, nullable = False)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    department = db.Column(db.String(), nullable = False)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)  # relationship
    dept_id= db.Column(db.Integer, db.ForeignKey('Department.department_id'))    #foreignkey

class Department(db.Model):
    __tablename__ = "Department"
    department_id = db.Column(db.Integer, primary_key = True)
    department_name = db.Column(db.String(), nullable=False)
    info = db.Column(db.String(), nullable=False)
    doctors = db.relationship('Doctor', backref='dept', lazy=True) #relationship

class Appointment(db.Model):
    __tablename__ = "Appointment"
    appointment_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String() , nullable=False)
    time = db.Column(db.String(), nullable=False)
    status = db.Column(db.String(), default='Upcoming', nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('Doctor.doctor_id'))   #foreignkey
    patent_id = db.Column(db.Integer, db.ForeignKey('Patient.patient_id'))  #foreignkey
    # treatment = db.Column(db.Integer, db.ForeignKey('Treatment.treatment_id'))  #foreignkey

class Treatment(db.Model):
    __tablename__ = "Treatment"
    treatment_id = db.Column(db.Integer, primary_key=True)
    diagnosis = db.Column(db.String(), nullable=False)
    prescription = db.Column(db.String(), nullable=False)
    status = db.Column(db.String(), nullable=False, default='Active')  #Active/Discharged
    test_reports = db.Column(db.String(), nullable=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('Doctor.doctor_id'))  #foerignkey
    patient_id = db.Column(db.Integer, db.ForeignKey('Patient.patient_id')) #foreignkey
    appointment_id = db.Column(db.Integer, db.ForeignKey('Appointment.appointment_id'))   #Foreign key
    appointment = db.relationship('Appointment', backref='treatments', lazy=True)  #relationship

class Availability(db.Model):
    __tablename__ = "Availability"
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('Doctor.doctor_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    slot = db.Column(db.String(), nullable=False)  # 'Morning' or 'Evening'
    doctor = db.relationship('Doctor', backref='availabilities')   #relationship




import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Admin(db.Model):
    __tablename__ = "admin"
    id  = db.Column(db.Integer , primary_key = True , autoincrement = True)
    name = db.Column(db.String , nullable = False)
    email = db.Column(db.String, unique = True , nullable = False)
    password = db.Column(db.String, nullable = False)


class Department(db.Model):
    __tablename__ = "department"
    id  = db.Column(db.Integer , primary_key = True , autoincrement = True)
    name = db.Column(db.String , nullable = False, unique = True)
    description = db.Column(db.String , nullable = False)
    doc_registered = db.Column(db.String , nullable = False)
    doctors = db.relationship("Doctor", backref = "department")


class Patient(db.Model):
    __tablename__ = "patient"
    id  = db.Column(db.Integer , primary_key = True , autoincrement = True)
    name = db.Column(db.String , nullable = False)
    email = db.Column(db.String, unique = True , nullable = False)
    password = db.Column(db.String, nullable = False)
    phone = db.Column(db.String, nullable =False)
    created_appointments = db.relationship("Appointment", backref = "patient")


class Doctor(db.Model):
    __tablename__ = "doctor"
    id  = db.Column(db.Integer , primary_key = True , autoincrement = True)
    name = db.Column(db.String , nullable = False)
    email = db.Column(db.String, unique = True , nullable = False)
    password = db.Column(db.String, nullable = False)
    phone = db.Column(db.String, nullable = False)
    dept_id = db.Column(db.Integer, db.ForeignKey ("department.id"), nullable = False)
    appointments = db.relationship("Appointment", backref = "doctor")


class Appointment(db.Model):
    __tablename__ = "appointment"
    id  = db.Column(db.Integer , primary_key = True , autoincrement = True)
    pat_id = db.Column(db.Integer, db.ForeignKey ("patient.id"), nullable = False)
    doc_id = db.Column(db.Integer, db.ForeignKey ("doctor.id"), nullable = False)
    date = db.Column(db.Date, default=datetime.date.today, nullable = False)
    time = db.Column(db.Time, default=datetime.datetime.now().time, nullable = False)
    status = db.Column(db.String, nullable = False)
    treatments = db.relationship("Treatment", backref = "appointment")


class Treatment(db.Model):
    __tablename__ = "treatment"
    id  = db.Column(db.Integer , primary_key = True , autoincrement = True)
    appoint_id = db.Column(db.Integer, db.ForeignKey ("appointment.id"), nullable = False)
    diagnosis = db.Column(db.String, nullable = False)
    prescription = db.Column(db.String, nullable = False)
    notes = db.Column(db.String, nullable = False)
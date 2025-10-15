from app import app
from flask import render_template,request,redirect,url_for
from .models import db,Patient,Admin,Doctor
from flask_login import login_user,login_required,current_user

@app.route("/")
def index():
    return render_template("home.html")


@app.route("/admin/login" ,  methods=["GET","POST"])
def admin_login():
    if request.method=="GET":
        return render_template("/admin/login.html")
    elif request.method=="POST":
        email = request.form.get("email")
        password = request.form.get("password")

        ad = db.session.query(Admin).filter_by(email=email).first()
        
        if ad:
            if ad.password == password:
                login_user(ad)
                return redirect(f"/admin/dashboard")
            else:
                return "Incorrect Password"

        else:
            return "Email Doesn't Exist"


@app.route("/doctor/login" ,  methods=["GET","POST"])
def doctor_login():
    if request.method=="GET":
        return render_template("/doctor/login.html")
    elif request.method=="POST":
        email = request.form.get("email")
        password = request.form.get("password")

        do = db.session.query(Doctor).filter_by(email=email).first()
        
        if do:
            if do.password == password:
                login_user(do)
                return redirect(f"/doctor/dashboard")
            else:
                return "Incorrect Password"

        else:
            return "Email Doesn't Exist"


@app.route("/patient/login" ,  methods=["GET","POST"])
def patient_login():
    if request.method=="GET":
        return render_template("/patient/login.html")
    elif request.method=="POST":
        email = request.form.get("email")
        password = request.form.get("password")

        pa = db.session.query(Patient).filter_by(email=email).first()
        
        if pa:
            if pa.password == password:
                login_user(pa)
                return redirect(f"/patient/dashboard")
            else:
                return "Incorrect Password"

        else:
            return "Email Doesn't Exist"


@app.route("/patient/register", methods=["GET" , "POST"])
def register():
    if request.method=="GET":
        return render_template("/patient/register.html")
    elif request.method=="POST":
        p_name = request.form.get("pat_name")
        p_email = request.form.get("pat_email")
        p_password = request.form.get("pat_password")
        p_phone = request.form.get("pat_phone")
        pat = db.session.query(Patient).filter_by(email = p_email).first()
        if not pat:
            pat = Patient(name=p_name, email=p_email, password=p_password, phone=p_phone)
            db.session.add(pat)
            db.session.commit()
            return redirect(url_for('patient_login'))
        else:
            return "email already exist for patient"




@app.route("/patient/dashboard" , methods=["GET" , "POST"])
@login_required
def pat_dashboard():

    return render_template("/patient/dashboard.html" , current_patient = current_user)


@app.route("/doctor/dashboard" , methods=["GET" , "POST"])
@login_required
def doc_dashboard():

    return render_template("/doctor/dashboard.html" , current_doctor = current_user)

@app.route("/admin/dashboard" , methods=["GET" , "POST"])
@login_required
def admin_dashboard():
    
    return render_template("/admin/dashboard.html" , current_admin = current_user)

    

@app.route("/doctor/stats")
def doc_stats():
    if request.args.get("do_id"):
        doc = db.session.query(Doctor).filter_by(id = request.args.get("do_id")).first()
        return f"Welcome To {doc.name} Stats Page"
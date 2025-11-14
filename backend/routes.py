from app import app
from flask import render_template,request,redirect,url_for,flash
from .models import db,Patient,Admin,Doctor,Department,Appointment
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
                flash("Incorrect Password")
                return redirect("/admin/login")

        else:
            flash("Email Doesn't Exist")
            return redirect("/admin/login")


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
                flash("Incorrect Password")
                return redirect("/doctor/login")

        else:
            flash("Email Doesn't Exist")
            return redirect("/doctor/login")


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
                flash("Incorrect Password")
                return redirect("/patient/login")

        else:
            flash ("Email Doesn't Exist")
            return redirect("/patient/login")


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
            pat = Patient(name=p_name, email=p_email, password=p_password, status = "Active", phone=p_phone)
            db.session.add(pat)
            db.session.commit()
            return redirect("/patient/login")
        else:
            flash("email already exist for patient")
            return redirect("/patient/register")




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
    docs = db.session.query(Doctor).all()
    depts = db.session.query(Department).all()
    booked_appoint = db.session.query(Appointment).filter_by(status="Booked").all()
    completed_appoint = db.session.query(Appointment).filter_by(status="Completed").all()
    canceled_appoint = db.session.query(Appointment).filter_by(status="Canceled").all()
    resheduled_appoint = db.session.query(Appointment).filter_by(status="Resheduled").all()
    active_pat = db.session.query(Patient).filter_by(status="Active").all()
    blacklist_pat = db.session.query(Patient).filter_by(status="Blacklist").all()
    active_doc = db.session.query(Doctor).filter_by(status="Active").all()
    blacklist_doc = db.session.query(Doctor).filter_by(status="Blacklist").all()
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    return render_template("/admin/dashboard.html" , current_admin = current_user, all_docs = docs, all_depts = depts,
                            booked_appoint = booked_appoint, completed_appoint = completed_appoint, canceled_appoint = canceled_appoint,
                            resheduled_appoint = resheduled_appoint, active_pat = active_pat, blacklist_pat = blacklist_pat,
                            active_doc = active_doc, blacklist_doc = blacklist_doc, total_doctors=total_doctors, total_patients=total_patients,
                            total_appointments=total_appointments)

@app.route("/doctor/stats")
def doc_stats():
    if request.args.get("do_id"):
        doc = db.session.query(Doctor).filter_by(id = request.args.get("do_id")).first()
        return f"Welcome To {doc.name} Stats Page"

@app.route("/department" , methods=["POST"])
def department():
    if request.args.get("task") == "create":
        name = request.form.get("dept_name")
        description = request.form.get("dept_description")
        dept = db.session.query(Department).filter_by(name=name, description=description).first()
        if dept:
            flash("Department Already Exist")
            return redirect("/admin/dashboard")
        else:
            new_dept = Department(name=name, description=description)
            db.session.add(new_dept)
            db.session.commit()
            flash("Department Is Created")
            return redirect("/admin/dashboard")
    elif request.args.get("task") == "edit":
        name = request.form.get("dept_name")
        description = request.form.get("dept_description")
        dept_id =request.args.get("dept_id")
        dept = db.session.query(Department).filter_by(id = dept_id).first()
        if dept:
            if name:
                dept.name = name
            if description:
                dept.description = description
            db.session.commit()
            flash(f"{dept.name} Is Updated")
            return redirect("/admin/dashboard")

        else:
            flash("Department doesn't exist.")
            return redirect("/admin/dashboard")

@app.route("/doctor" , methods=["POST"])
def doctor():
    if request.args.get("task") == "create":
        name = request.form.get("doc_name")
        email = request.form.get("doc_email")
        password = request.form.get("doc_password")
        phone = request.form.get("doc_phone")
        
        dept_id = request.form.get("doc_dept_id")
        doc = db.session.query(Doctor).filter_by(name=name, email=email, phone=phone).first()
        if doc:
            return "Doctor Already Exist"
        else:
            new_doc = Doctor(name=name, email=email, password=password, phone=phone, dept_id=dept_id)
            db.session.add(new_doc)
            db.session.commit()
            flash("Doctor Is Created")
            return redirect("/admin/dashboard")
    elif request.args.get("task") == "edit":
        name = request.form.get("doc_name")
        email = request.form.get("doc_email")
        password = request.form.get("doc_password")
        phone = request.form.get("doc_phone")
        dept_id = request.form.get("doc_dept_id")
        doc_id =request.args.get("doc_id")
        doc = db.session.query(Doctor).filter_by(id = doc_id).first()
       
        if doc:
            doc.name = name
            doc.email = email
            doc.password = password
            doc.phone = phone
            doc.dept_id = dept_id
            db.session.commit()
            flash(f"{doc.name} Is Updated")
            return redirect("/admin/dashboard")

        else:
            return "Doctor doesn't exist."
    elif request.args.get("task") == "blacklist":
        doc_id = request.args.get("doc_id")
        doc = db.session.query(Doctor).filter_by(id = doc_id).first()
        if doc:
            doc.status = "Blacklist"
            db.session.commit()
            flash(f"{doc.name} Is Blacklisted")
            return redirect("/admin/dashboard")
    elif request.args.get("task") == "whitelist":
        doc_id = request.args.get("doc_id")
        doc = db.session.query(Doctor).filter_by(id = doc_id).first()
        if doc:
            doc.status = "Active"
            db.session.commit()
            flash(f"{doc.name} Is Whitelisted")
            return redirect("/admin/dashboard")

@app.route("/patient", methods=["POST"])
def patient():
    if request.args.get("task") == "blacklist":
        pat_id = request.args.get("pat_id")
        pat = db.session.query(Patient).filter_by(id = pat_id).first()
        if pat:
            pat.status = "Blacklist"
            db.session.commit()
            flash(f"{pat.name} Is Blacklisted")
            return redirect("/admin/dashboard")
    elif request.args.get("task") == "whitelist":
        pat_id = request.args.get("pat_id")
        pat = db.session.query(Patient).filter_by(id = pat_id).first()
        if pat:
            pat.status = "Active"
            db.session.commit()
            flash(f"{pat.name} Is Whitelisted")
            return redirect("/admin/dashboard")
    elif request.args.get("task") == "edit":
        name = request.form.get("pat_name")
        email = request.form.get("pat_email")
        password = request.form.get("pat_password")
        phone = request.form.get("pat_phone")
        pat_id = request.args.get("pat_id")
        pat = db.session.query(Patient).filter_by(id = pat_id).first()
        if pat:
            pat.name = name
            pat.email = email
            pat.password = password
            pat.phone = phone
            db.session.commit()
            flash(f"{pat.name} Is Updated")
            return redirect("/admin/dashboard")

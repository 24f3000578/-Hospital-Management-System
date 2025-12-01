from app import app
from flask import render_template,request,redirect,url_for,flash
from .models import db,Patient,Admin,Doctor,Department,Appointment,Treatment,DoctorAvailability
from flask_login import login_user,login_required,current_user
from datetime import date, datetime, timedelta,time
from flask_login import current_user, logout_user
from sqlalchemy import or_, cast, String

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/logout")
@login_required
def logout():
    if isinstance(current_user, Admin):
        next_endpoint = "admin_login"
    elif isinstance(current_user, Doctor):
        next_endpoint = "doctor_login"
    elif isinstance(current_user, Patient):
        next_endpoint = "patient_login"
    else:
        next_endpoint = "patient_login"

    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for(next_endpoint))

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
    current_patient = current_user
    today = date.today()

    # Search Term
    search_term = request.args.get("search", "").strip()

    # Base Query For Departments
    dept_query = Department.query

    if search_term:
        like = f"%{search_term}%"
        dept_query = (
            dept_query
            .outerjoin(Doctor, Doctor.dept_id == Department.id)
            .filter(
                or_(
                    Department.name.ilike(like),
                    Doctor.name.ilike(like),
                )
            )
            .distinct()
        )

    all_depts = dept_query.all()
    upcoming_appointments = (
        Appointment.query
        .filter(
            Appointment.pat_id == current_patient.id,
            Appointment.date >= today,
            Appointment.status != "Canceled",
            Appointment.status != "Completed"
        )
        .order_by(Appointment.date, Appointment.time)
        .all()  
    )
    return render_template("/patient/dashboard.html" , current_patient = current_user, all_depts = all_depts,
                            upcoming_appointments=upcoming_appointments, search_term=search_term)

@app.route("/patient/profile/edit", methods=["GET", "POST"])
@login_required
def edit_patient_profile():
    patient = current_user

    if request.method == "POST":
        # Read Form Values
        name = request.form.get("name")
        phone = request.form.get("phone")
        password= request.form.get("password")

        # Update Fields
        patient.name = name
        patient.phone = phone
        patient.password = password
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("pat_dashboard"))

    # Show Form With Existing Details
    return render_template("patient/edit_profile.html", patient=patient)

@app.route("/patient/history")
@login_required
def patient_self_history():
    current_patient = current_user

    # Past Completed Appointments For The Patient
    past_appointments = (
        Appointment.query
        .filter(
            Appointment.pat_id == current_patient.id,
            Appointment.date <= date.today(),
            Appointment.status == "Completed"
        )
        .order_by(Appointment.date.desc(), Appointment.time.desc())
        .all()
    )

    return render_template(
        "doctor/patient_history.html",
        patient=current_patient,
        appointments=past_appointments,
        back_url=url_for("pat_dashboard")
    )

@app.route("/patient/doctor/<int:doctor_id>/availability")
@login_required
def patient_check_availability(doctor_id):
    # Get Doctor or 404
    doctor = Doctor.query.get_or_404(doctor_id)

    # Upcoming Availability
    today = date.today()
    slots = (
        DoctorAvailability.query
        .filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.date >= today,
            DoctorAvailability.is_available == True
        )
        .order_by(DoctorAvailability.date, DoctorAvailability.start_time)
        .all()
    )

    return render_template(
        "patient/doctor_availability.html",
        doctor=doctor,
        slots=slots,
    )

@app.route("/patient/doctor/<int:doctor_id>/details")
@login_required
def patient_doctor_details(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    return render_template(
        "patient/doctor_details.html",
        doctor=doctor,
    )

@app.route("/patient/book/<int:availability_id>", methods=["POST"])
@login_required
def book_appointment(availability_id):
    current_patient = current_user

    slot = DoctorAvailability.query.get_or_404(availability_id)

   # Prevent Past Slot Bookings
    if slot.date < date.today():
        flash("Cannot book a past slot.", "danger")
        return redirect(url_for("patient_check_availability", doctor_id=slot.doctor_id))

    # Prevent Double Bookings
    existing_appointment = Appointment.query.filter_by(
        doc_id=slot.doctor_id,
        date=slot.date,
        time=slot.start_time,
        status="Booked"
    ).first()

    if existing_appointment:
        flash("This slot has already been booked!", "danger")
        return redirect(url_for("patient_check_availability", doctor_id=slot.doctor_id))

    # Create Appointment
    new_appt = Appointment(
        doc_id=slot.doctor_id,
        pat_id=current_patient.id,
        dept_id=slot.doctor.dept_id,
        date=slot.date,
        time=slot.start_time,
        status="Booked"
    )

    db.session.add(new_appt)
    db.session.commit()

    flash("Your appointment has been booked successfully.", "success")
    return redirect(url_for("pat_dashboard"))

@app.route("/patient/appointment/<int:appt_id>/cancel", methods=["POST"])
@login_required
def cancel_patient_appointment(appt_id):
    current_patient = current_user

    appt = Appointment.query.get_or_404(appt_id)

    if appt.patient.id != current_patient.id:
        flash("You are not allowed to cancel this appointment.", "danger")
        return redirect(url_for("pat_dashboard"))

    # Update Status
    appt.status = "Canceled"
    db.session.commit()
    flash("Your appointment has been canceled.", "success")
    return redirect(url_for("pat_dashboard"))

@app.route("/doctor/dashboard", methods=["GET", "POST"])
@login_required
def doc_dashboard():
    if not isinstance(current_user._get_current_object(), Doctor):
        return redirect(url_for("admin_dashboard"))
    doctor_id = current_user.id

    if not doctor_id:
        return redirect(url_for("doctor_login"))

    # Base Date
    base_date_str = request.args.get("date")
    if base_date_str:
        base_date = date.fromisoformat(base_date_str)  # In "YYYY-MM-DD"
    else:
        base_date = date.today()

    # Base Query For This Doctor
    base_query = Appointment.query.filter_by(doc_id=doctor_id)

    # Active Appointments
    active_query = base_query.filter(
        Appointment.status != "Completed",
        Appointment.status != "Canceled"
    )

   

    # Week Appointments
    start = base_date
    end = base_date + timedelta(days=7)
    week_appointments = (
        active_query.filter(
            Appointment.date >= start,
            Appointment.date < end
        )
        .order_by(Appointment.date, Appointment.time)
        .all()
    )

     # Day Appointments
    day_appointments = (
        active_query.filter_by(date=base_date)
        .order_by(Appointment.time)
        .all()
    )

    # Completed / Canceled 
    completed_appoint = (
        base_query.filter_by(status="Completed")
        .order_by(Appointment.date, Appointment.time)
        .all()
    )

    canceled_appoint = (
        base_query.filter_by(status="Canceled")
        .order_by(Appointment.date, Appointment.time)
        .all()
    )

    # Assigned Patients

    assigned_patients = (
        db.session.query(Patient)
        .join(Appointment)
        .filter(Appointment.doc_id == doctor_id)
        .distinct()
        .all()
    )
    today = date.today()
    next_seven_days = [today + timedelta(days=i) for i in range(7)]

    # Fetch Existing Availability For 7 Days
    existing_avails = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.date >= today,
        DoctorAvailability.date < today + timedelta(days=7)
    ).all()

    # Build A Map
    avail_map = {}
    for a in existing_avails:
        key = f"{a.date.isoformat()}|{a.start_time.strftime('%H:%M')}|{a.end_time.strftime('%H:%M')}"
        avail_map[key] = a.is_available
    
    last_treatments = {}
    for appt in completed_appoint:
        last = (
            Treatment.query
            .filter_by(appoint_id=appt.id)
            .order_by(Treatment.id.desc())   # or Treatment.date.desc()
            .first()
        )
        last_treatments[appt.id] = last

    return render_template(
        "doctor/dashboard.html",
        current_doctor=current_user,
        base_date=base_date,
        timedelta=timedelta,
        day_appointments=day_appointments,
        week_appointments=week_appointments,
        completed_appoint=completed_appoint,
        canceled_appoint=canceled_appoint,
        assigned_patients=assigned_patients,
        next_seven_days=next_seven_days,
        avail_map=avail_map, last_treatments=last_treatments
    )

@app.route("/doctor/patient/<int:patient_id>/history")
@login_required
def patient_history(patient_id):
    doctor_id = current_user.id

    # Get Patient or 404
    patient = Patient.query.get_or_404(patient_id)

    # All Appointments Of Respective Patient With Respective Doctor
    appointments = (
        Appointment.query
        .filter_by(doc_id=doctor_id)
        .order_by(Appointment.date.desc(), Appointment.time.desc())
        .all()
    )

    # All Treatments For Those Appointments
    from sqlalchemy.orm import joinedload
    appointments = (
        Appointment.query
        .options(joinedload(Appointment.treatments))
        .filter(
            Appointment.doc_id == doctor_id,
            Patient.id == patient_id
        )
        .order_by(Appointment.date.desc(), Appointment.time.desc())
        .all()
    )

    return render_template(
        "doctor/patient_history.html",
        patient=patient,
        appointments=appointments,
    )

@app.route("/doctor/availability", methods=["POST"])
@login_required
def provide_availability():
    doctor_id = current_user.id

    # List Of Strings
    selected_slots = set(request.form.getlist("slots"))

    today = date.today()
    days = [today + timedelta(days=i) for i in range(7)]

    # Build The Full Grid Of Slots
    all_slot_strs = []
    for d in days:
        day_str = d.isoformat()
        all_slot_strs.append(f"{day_str}|08:00|12:00")
        all_slot_strs.append(f"{day_str}|16:00|20:00")

    # For Each Possible Slot For The Next 7 Days:
    for slot_str in all_slot_strs:
        date_str, start_str, end_str = slot_str.split("|")
        day = date.fromisoformat(date_str)
        start_t = time.fromisoformat(start_str)
        end_t = time.fromisoformat(end_str)

        availability = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            date=day,
            start_time=start_t,
            end_time=end_t
        ).first()

        if slot_str in selected_slots:
            if availability:
                availability.is_available = True
            else:
                availability = DoctorAvailability(
                    doctor_id=doctor_id,
                    date=day,
                    start_time=start_t,
                    end_time=end_t,
                    is_available=True
                )
                db.session.add(availability)
        else:
            if availability:
                availability.is_available = False

    db.session.commit()
    flash("Availability updated for the next 7 days.", "success")
    return redirect(url_for("doc_dashboard"))

@app.route("/admin/dashboard" , methods=["GET" , "POST"])
@login_required
def admin_dashboard():
    docs = db.session.query(Doctor).all()
    doctor_search = request.args.get("doctor_search", "").strip()
    patient_search = request.args.get("patient_search", "").strip()
    depts = db.session.query(Department).all()
    # Doctor Search
    if doctor_search:
        like = f"%{doctor_search}%"

        active_doc = (
            Doctor.query
            .join(Department, Doctor.dept_id == Department.id)
            .filter(
                Doctor.status == "Active",
                or_(
                    Doctor.name.ilike(like),
                    Department.name.ilike(like),
                )
            )
            .all()
        )

        blacklist_doc = (
            Doctor.query
            .join(Department, Doctor.dept_id == Department.id)
            .filter(
                Doctor.status == "Blacklist",
                or_(
                    Doctor.name.ilike(like),
                    Department.name.ilike(like),
                )
            )
            .all()
        )
    else:
        active_doc = Doctor.query.filter_by(status="Active").all()
        blacklist_doc = Doctor.query.filter_by(status="Blacklist").all()

    # Patient Search
    if patient_search:
        like = f"%{patient_search}%"

        active_pat = (
            Patient.query
            .filter(
                Patient.status == "Active",
                or_(
                    Patient.name.ilike(like),
                    cast(Patient.id, String).ilike(like),
                    Patient.email.ilike(like),
                    Patient.phone.ilike(like),
                )
            )
            .all()
        )

        blacklist_pat = (
            Patient.query
            .filter(
                Patient.status == "Blacklist",
                or_(
                    Patient.name.ilike(like),
                    cast(Patient.id, String).ilike(like),
                    Patient.email.ilike(like),
                    Patient.phone.ilike(like),
                )
            )
            .all()
        )
    else:
        active_pat = Patient.query.filter_by(status="Active").all()
        blacklist_pat = Patient.query.filter_by(status="Blacklist").all()
    booked_appoint = db.session.query(Appointment).filter_by(status="Booked").all()
    completed_appoint = db.session.query(Appointment).filter_by(status="Completed").all()
    canceled_appoint = db.session.query(Appointment).filter_by(status="Canceled").all()
    resheduled_appoint = db.session.query(Appointment).filter_by(status="Resheduled").all()
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    return render_template("/admin/dashboard.html" , current_admin = current_user, all_docs = docs, all_depts = depts,
                            booked_appoint = booked_appoint, completed_appoint = completed_appoint, canceled_appoint = canceled_appoint,
                            resheduled_appoint = resheduled_appoint, active_pat = active_pat, blacklist_pat = blacklist_pat,
                            active_doc = active_doc, blacklist_doc = blacklist_doc, total_doctors=total_doctors, total_patients=total_patients,
                            total_appointments=total_appointments, doctor_search=doctor_search, patient_search=patient_search)

@app.route("/admin/patient/<int:patient_id>/history")
@login_required
def admin_patient_history(patient_id):

    patient = Patient.query.get_or_404(patient_id)

    # All Appointments For The Patient
    appointments = (
        Appointment.query
        .filter(Appointment.pat_id == patient.id)
        .order_by(Appointment.date.desc(), Appointment.time.desc())
        .all()
    )

    return render_template(
        "doctor/patient_history.html",
        patient=patient,
        appointments=appointments,
        back_url=url_for("admin_dashboard")
    )

@app.route("/admin/department/create", methods=["POST"])
@login_required
def create_department():
    name = request.form.get("dept_name")
    description = request.form.get("dept_description")

    if not name or not description:
        flash("Name and description are required", "danger")
        return redirect(url_for("admin_dashboard"))

    dept = Department(
        name=name,
        description=description,
        doc_registered=0,
    )
    db.session.add(dept)
    db.session.commit()

    flash("Department created successfully", "success")
    return redirect(url_for("admin_dashboard"))


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



@app.route("/treatment", methods=["POST"])
def treatment():
    task = request.args.get("task")
    if task not in ("completed", "update", "canceled"):
        flash("Unknown or missing treatment action", "danger")
        return redirect(url_for("doc_dashboard"))

    appoint_id = request.args.get("appoint_id", type=int)

    if not appoint_id:
        flash("Appointment id is missing", "danger")
        return redirect("/doctor/dashboard")

    # For The Appointment
    appointment = Appointment.query.get(appoint_id)
    if not appointment:
        flash("Appointment not found", "danger")
        return redirect("/doctor/dashboard")

    # Common Form Fields
    visit_type = request.form.get("t_visit_type")
    test = request.form.get("treat_test")
    diagnosis = request.form.get("treat_diagnosis")
    prescription = request.form.get("treat_prescription")
    notes = request.form.get("treat_notes")
    if task == "completed":
        new_treat = Treatment(
            appoint_id=appointment.id,
            visit_type=visit_type,
            test=test,
            diagnosis=diagnosis,
            prescription=prescription,
            notes=notes
        )
        db.session.add(new_treat)

        appointment.status = "Completed"
        db.session.commit()

        flash(f"Appointment {appointment.id} is marked as Completed", "success")
        return redirect("/doctor/dashboard")
    elif task == "update":
        if appointment.status != "Completed":
            flash("You can only update treatments for Completed appointments.", "danger")
            return redirect("/doctor/dashboard")

        # Latest Treatment
        latest_treat = (
            Treatment.query
            .filter_by(appoint_id=appointment.id)
            .order_by(Treatment.visit_dt.desc())
            .first()
        )

        if not latest_treat:
            flash("No existing treatment found to update", "danger")
            return redirect("/doctor/dashboard")

        latest_treat.visit_type = visit_type
        latest_treat.test = test
        latest_treat.diagnosis = diagnosis
        latest_treat.prescription = prescription
        latest_treat.notes = notes

        db.session.commit()
        flash(f"Treatment for Appointment {appointment.id} updated", "success")
        return redirect("/doctor/dashboard")

    elif request.args.get("task") == "canceled":
            appointment.status = "Canceled"
            db.session.commit()
            flash(f"{appointment.patient.name} Is Canceled")
            return redirect("/doctor/dashboard")
        
    # Fallback If Task Is Unknown
    else:
        flash("Unknown treatment action", "danger")
        return redirect("/doctor/dashboard")
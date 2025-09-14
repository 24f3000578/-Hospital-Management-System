from . models import db, Admin, Department, Doctor

if db.session.query(Admin).count()==0:
    admin = Admin(name = "admin", email = "admin@myapp.com", password = "pass")
    db.session.add(admin)
    db.session.commit()

if db.session.query(Department).count()==0:
    general_medicine = Department(name = "General Medicine",
    description="Department dealing with common illnesses and general health issues.",
    doc_registered=0)
    db.session.add(general_medicine)
    db.session.commit()

    general_surgery = Department(name = "General Surgery",
    description="Performs surgeries for various medical conditions and injuries.",
    doc_registered=0)
    db.session.add(general_surgery)
    db.session.commit()

    pediatrics = Department(name = "Pediatrics",
    description="Focuses on medical care of infants, children, and adolescents.",
    doc_registered=0)
    db.session.add(pediatrics)
    db.session.commit()


if db.session.query(Doctor).count()==0:

    R = Doctor(name = "Dr. Ram", email = "ram@myapp.com", password = "pass", phone = "9999999999", dept_id = general_surgery.id)
    db.session.add(R)


    S = Doctor(name = "Dr. Shyam", email = "shyam@myapp.com", password = "pass", phone = "9999999989", dept_id = general_medicine.id)
    db.session.add(S)

    P = Doctor(name = "Dr. Prakash", email = "prakash@myapp.com", password = "pass", phone = "9999999990", dept_id = general_surgery.id)
    db.session.add(P)
    db.session.commit()

    general_medicine.doc_registered = db.session.query(Doctor).filter(Doctor.dept_id == general_medicine.id).count()
    general_surgery.doc_registered = db.session.query(Doctor).filter(Doctor.dept_id == general_surgery.id).count()
    db.session.commit()
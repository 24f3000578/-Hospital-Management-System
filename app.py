from flask import Flask
from backend.models import db,Admin,Doctor,Patient,Department
from flask_login import LoginManager
def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Hospital_db.sqlite3"
    db.init_app(app)
    app.config["SECRET_KEY"] = "Thisismysecret"
    login_manager = LoginManager(app)
    @login_manager.user_loader
    def load_user(email):
        return db.session.query(Patient).filter_by(email = email).first() or \
        db.session.query(Admin).filter_by(email = email).first() or \
        db.session.query(Doctor).filter_by(email = email).first()
    app.app_context().push()
    db.create_all()
    return app

app = create_app()

from backend.routes import *
from backend.create_initial_data import *



if __name__=="__main__":
    app.run(debug=True)
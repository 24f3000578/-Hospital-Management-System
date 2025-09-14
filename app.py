from flask import Flask
from backend.models import db
def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Hospital_db.sqlite3"
    db.init_app(app)
    app.app_context().push()
    db.create_all()
    return app

app = create_app()

from backend.routes import *
from backend.create_initial_data import *



if __name__=="__main__":
    app.run(debug=True)
from flask import Flask
from application.database import db     #database
app = None

def create_app():
    app = Flask(__name__)
    app.secret_key = "mysecret123"
    app.debug=True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.sqlite3' #database
    db.init_app(app)         #database
    app.app_context().push()
    return app

app = create_app()
from application.controllers import *       #controllers and models

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        admin = Admin.query.filter_by(username='admin1').first()
        if admin is None:
            admin = Admin(username='admin1', email='admin1@hms.com', password='6789')
            db.session.add(admin)
            db.session.commit()
    app.run()

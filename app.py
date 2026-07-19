from flask import Flask
from flask_login import LoginManager

from models import db, User

app = Flask(__name__)

app.config["SECRET_KEY"] = "cricket_ticket_booking_secret"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cricket_booking.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # return User.query.get(int(user_id))
    return db.session.get(User, int(user_id))


from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.user import user_bp
from routes.verify import verify_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)
app.register_blueprint(verify_bp)


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
"""
Run ONCE to create the admin user and a sample verify-staff user.

    python init_db.py

Edit ADMIN and STAFF dicts below before running.
"""
import hashlib
from app import create_app
from models import db, UserType, UserAuthentication, CustomerReg

ADMIN = dict(name="Admin User",  email="admin@ctbs.com",  password="Admin@123")
STAFF = dict(name="Verify Staff",email="staff@ctbs.com",  password="Staff@123")

def sha(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def make_user(name, email, password, role):
    if UserAuthentication.query.filter_by(email=email).first():
        print(f"  [skip] {email} already exists.")
        return
    utype = UserType.query.filter_by(user_type=role).first()
    u = UserAuthentication(user_type_id=utype.id, user_name=name,
                           email=email, password_sha=sha(password))
    db.session.add(u)
    db.session.flush()
    print(f"  [ok]   {role} created → {email}")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        make_user(**ADMIN, role='admin')
        make_user(**STAFF, role='verifystaff')
        db.session.commit()
    print("Done.")
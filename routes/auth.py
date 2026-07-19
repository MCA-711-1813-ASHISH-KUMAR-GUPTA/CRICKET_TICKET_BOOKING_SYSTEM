import re
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from models import db, User

auth_bp = Blueprint("auth", __name__)


# ── Validation helpers ────────────────────────────────────────────────────────
EMAIL_RE  = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
MOBILE_RE = re.compile(r'^[6-9]\d{9}$')


def _validate_registration(form):
    """Return list of error messages; empty list means valid."""
    errors = []

    name     = form.get("name",     "").strip()
    email    = form.get("email",    "").strip()
    mobile   = form.get("mobile",   "").strip()
    password = form.get("password", "")
    confirm  = form.get("confirm_password", "")
    u_type   = form.get("user_type", "").strip()

    if len(name) < 3 or len(name) > 100:
        errors.append("Name must be between 3 and 100 characters.")
    if not re.match(r'^[A-Za-z\s\'.]+$', name):
        errors.append("Name may only contain letters, spaces, and apostrophes.")

    if not EMAIL_RE.match(email):
        errors.append("Please enter a valid email address.")

    if not MOBILE_RE.match(mobile):
        errors.append("Mobile must be a 10-digit Indian number starting with 6-9.")

    if len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    if password != confirm:
        errors.append("Passwords do not match.")

    if u_type not in ("audience", "verifystaff", "admin"):
        errors.append("Please select a valid account type.")

    return errors


# ── Routes ────────────────────────────────────────────────────────────────────
@auth_bp.route("/")
def home():
    return render_template("index.html")


@auth_bp.route("/makeUser", methods=["GET", "POST"])
def make_user():
    if request.method == "POST":
        errors = _validate_registration(request.form)

        if errors:
            for err in errors:
                flash(err)
            return redirect(url_for("auth.make_user"))

        email = request.form["email"].strip()
        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.")
            return redirect(url_for("auth.make_user"))

        password_sha = hashlib.sha256(
            request.form["password"].encode()
        ).hexdigest()

        user = User(
            name=request.form["name"].strip(),
            email=email,
            mobile=request.form["mobile"].strip(),
            password_sha=password_sha,
            user_type=request.form["user_type"].strip(),
        )
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.")
        return redirect(url_for("auth.login"))

    return render_template("makeUser.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email",    "").strip()
        password = request.form.get("password", "")

        if not EMAIL_RE.match(email):
            flash("Please enter a valid email address.")
            return redirect(url_for("auth.login"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.")
            return redirect(url_for("auth.login"))

        password_sha = hashlib.sha256(password.encode()).hexdigest()
        user = User.query.filter_by(
            email=email, password_sha=password_sha
        ).first()

        if not user:
            flash("Invalid email or password. Please try again.")
            return redirect(url_for("auth.login"))

        login_user(user)

        if user.user_type == "admin":
            return redirect(url_for("admin.dash_admin"))
        if user.user_type == "verifystaff":
            return redirect(url_for("verify.dash_verify"))
        return redirect(url_for("user.dash_user"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

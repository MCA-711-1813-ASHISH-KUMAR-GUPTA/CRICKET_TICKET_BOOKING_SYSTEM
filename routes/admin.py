import re
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Venue, Team, Match, SeatPlan, Ticket

admin_bp = Blueprint("admin", __name__)

COLUMN_RE = re.compile(r'^[A-Za-z]{1,5}$')


# ── Validation helpers ────────────────────────────────────────────────────────
def _validate_match_form(form):
    errors = []
    venue_name = form.get("venue_name", "").strip()
    location   = form.get("location",   "").strip()
    team1      = form.get("team1",      "").strip()
    team2      = form.get("team2",      "").strip()
    start_raw  = form.get("start_time", "").strip()
    end_raw    = form.get("end_time",   "").strip()

    if len(venue_name) < 3:
        errors.append("Venue name must be at least 3 characters.")
    if len(location) < 3:
        errors.append("Location must be at least 3 characters.")
    if len(team1) < 2:
        errors.append("Team 1 name must be at least 2 characters.")
    if len(team2) < 2:
        errors.append("Team 2 name must be at least 2 characters.")
    if team1.lower() == team2.lower():
        errors.append("Team 1 and Team 2 must be different teams.")

    start_dt = end_dt = None
    try:
        start_dt = datetime.fromisoformat(start_raw)
    except (ValueError, TypeError):
        errors.append("Start time is invalid. Use the date-time picker.")
    try:
        end_dt = datetime.fromisoformat(end_raw)
    except (ValueError, TypeError):
        errors.append("End time is invalid. Use the date-time picker.")

    if start_dt and end_dt and end_dt <= start_dt:
        errors.append("End time must be after start time.")

    return errors


def _validate_seat_form(form):
    errors = []
    col   = form.get("column_name", "").strip().upper()
    row   = form.get("row_name",    "").strip()
    price_raw = form.get("seat_price", "").strip()
    start_raw = form.get("start_seat", "").strip()
    end_raw   = form.get("end_seat",   "").strip()

    if not COLUMN_RE.match(col):
        errors.append("Column name must be 1–5 letters (e.g. A, GA, VIP).")
    if not row:
        errors.append("Row name is required.")

    start_seat = end_seat = None
    try:
        start_seat = int(start_raw)
        if start_seat < 1:
            errors.append("Start seat number must be ≥ 1.")
    except (ValueError, TypeError):
        errors.append("Start seat number must be a valid integer.")

    try:
        end_seat = int(end_raw)
        if end_seat < 1:
            errors.append("End seat number must be ≥ 1.")
    except (ValueError, TypeError):
        errors.append("End seat number must be a valid integer.")

    if start_seat and end_seat:
        if end_seat < start_seat:
            errors.append("End seat number must be ≥ Start seat number.")
        elif (end_seat - start_seat + 1) > 500:
            errors.append("Cannot add more than 500 seats in a single block.")

    try:
        price = float(price_raw)
        if price <= 0:
            errors.append("Seat price must be a positive number.")
    except (ValueError, TypeError):
        errors.append("Seat price must be a valid number.")

    return errors


# ── Routes ────────────────────────────────────────────────────────────────────
@admin_bp.route("/dash_admin")
@login_required
def dash_admin():
    if current_user.user_type != "admin":
        flash("Admin access required.")
        return redirect(url_for("auth.login"))
    matches = Match.query.order_by(Match.id.desc()).all()
    return render_template("dash_admin.html", matches=matches)


@admin_bp.route("/matches", methods=["GET", "POST"])
@login_required
def matches():
    if current_user.user_type != "admin":
        flash("Admin access required.")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        errors = _validate_match_form(request.form)
        if errors:
            for err in errors:
                flash(err)
            return redirect(url_for("admin.matches"))

        venue_name = request.form["venue_name"].strip()
        location   = request.form["location"].strip()
        team1_name = request.form["team1"].strip()
        team2_name = request.form["team2"].strip()
        start_time = datetime.fromisoformat(request.form["start_time"])
        end_time   = datetime.fromisoformat(request.form["end_time"])

        venue = Venue.query.filter_by(venue_name=venue_name, location=location).first()
        if not venue:
            venue = Venue(venue_name=venue_name, location=location)
        db.session.add(venue)
        db.session.flush()

        team1 = Team.query.filter_by(team_name=team1_name).first() or Team(team_name=team1_name)
        team2 = Team.query.filter_by(team_name=team2_name).first() or Team(team_name=team2_name)
        db.session.add(team1)
        db.session.add(team2)
        db.session.flush()

        match = Match(
            venue_id=venue.id,
            team1_id=team1.id,
            team2_id=team2.id,
            start_time=start_time,
            end_time=end_time,
        )
        db.session.add(match)
        db.session.commit()

        flash("Match scheduled successfully!")
        return redirect(url_for("admin.matches"))

    matches = Match.query.order_by(Match.id.desc()).all()
    return render_template("matches.html", matches=matches)


@admin_bp.route("/toggle_booking/<int:match_id>")
@login_required
def toggle_booking(match_id):
    if current_user.user_type != "admin":
        flash("Admin access required.")
        return redirect(url_for("auth.login"))
    match = Match.query.get_or_404(match_id)
    match.booking_enabled = not match.booking_enabled
    db.session.commit()
    state = "opened" if match.booking_enabled else "closed"
    flash(f"Booking {state} for match #{match_id}.")
    return redirect(url_for("admin.dash_admin"))


@admin_bp.route("/toggle_verification/<int:match_id>")
@login_required
def toggle_verification(match_id):
    if current_user.user_type != "admin":
        flash("Admin access required.")
        return redirect(url_for("auth.login"))
    match = Match.query.get_or_404(match_id)
    match.verification_enabled = not match.verification_enabled
    db.session.commit()
    state = "enabled" if match.verification_enabled else "disabled"
    flash(f"Verification {state} for match #{match_id}.")
    return redirect(url_for("admin.dash_admin"))


@admin_bp.route("/seat_plan/<int:match_id>", methods=["GET", "POST"])
@login_required
def seat_plan(match_id):
    if current_user.user_type != "admin":
        flash("Admin access required.")
        return redirect(url_for("auth.login"))

    match = Match.query.get_or_404(match_id)

    if request.method == "POST":
        errors = _validate_seat_form(request.form)
        if errors:
            for err in errors:
                flash(err)
            return redirect(url_for("admin.seat_plan", match_id=match_id))

        column_name = request.form["column_name"].strip().upper()
        row_name    = request.form["row_name"].strip()
        start_seat  = int(request.form["start_seat"])
        end_seat    = int(request.form["end_seat"])
        seat_price  = float(request.form["seat_price"])

        added = 0
        skipped = 0
        for seat_no in range(start_seat, end_seat + 1):
            existing = SeatPlan.query.filter_by(
                match_id=match_id,
                column_name=column_name,
                row_name=row_name,
                seat_number=seat_no,
            ).first()
            if existing:
                skipped += 1
                continue
            db.session.add(SeatPlan(
                match_id=match_id,
                column_name=column_name,
                row_name=row_name,
                seat_number=seat_no,
                seat_price=seat_price,
            ))
            added += 1

        db.session.commit()

        msg = f"Added {added} seat(s) to {column_name}-{row_name}."
        if skipped:
            msg += f" ({skipped} duplicate(s) skipped.)"
        flash(msg)
        return redirect(url_for("admin.seat_plan", match_id=match_id))

    seats = SeatPlan.query.filter_by(match_id=match_id).order_by(
        SeatPlan.column_name, SeatPlan.row_name, SeatPlan.seat_number
    ).all()
    return render_template("seat_plan.html", seats=seats, match_id=match_id, match=match)

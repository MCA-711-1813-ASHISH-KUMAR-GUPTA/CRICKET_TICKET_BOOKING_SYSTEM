from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(20), nullable=False)  # audience/admin/verifystaff

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(15), nullable=False)

    password_sha = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Venue(db.Model):
    __tablename__ = "venues"

    id = db.Column(db.Integer, primary_key=True)

    venue_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255), nullable=False)


class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)

    team_name = db.Column(db.String(100), nullable=False)


class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)

    venue_id = db.Column(
        db.Integer,
        db.ForeignKey("venues.id"),
        nullable=False
    )

    team1_id = db.Column(
        db.Integer,
        db.ForeignKey("teams.id"),
        nullable=False
    )

    team2_id = db.Column(
        db.Integer,
        db.ForeignKey("teams.id"),
        nullable=False
    )

    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    booking_enabled = db.Column(db.Boolean, default=True)
    verification_enabled = db.Column(db.Boolean, default=True)

    venue = db.relationship("Venue")
    team1 = db.relationship("Team", foreign_keys=[team1_id])
    team2 = db.relationship("Team", foreign_keys=[team2_id])

    match_status = db.Column(
    db.String(20),
    default="UPCOMING"
    )


class SeatPlan(db.Model):
    __tablename__ = "seat_plans"

    id = db.Column(db.Integer, primary_key=True)

    match_id = db.Column(
        db.Integer,
        db.ForeignKey("matches.id"),
        nullable=False
    )

    column_name = db.Column(db.String(20), nullable=False)
    row_name = db.Column(db.String(20), nullable=False)

    seat_number = db.Column(db.Integer, nullable=False)

    seat_price = db.Column(db.Float, nullable=False)

    match = db.relationship("Match")

    __table_args__ = (
    db.UniqueConstraint(
        'match_id',
        'column_name',
        'row_name',
        'seat_number',
        name='unique_match_seat'
    ),
    )

    


class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    match_id = db.Column(
        db.Integer,
        db.ForeignKey("matches.id"),
        nullable=False
    )

    seat_plan_id = db.Column(
        db.Integer,
        db.ForeignKey("seat_plans.id"),
        nullable=False
    )

    # qr_string = db.Column(db.String(500))
    qr_string = db.Column(
    db.String(500),
    unique=True
    )
    amount = db.Column(db.Float, nullable=False)

    booked_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    is_cancelled = db.Column(
        db.Boolean,
        default=False
    )

    is_verified = db.Column(
        db.Boolean,
        default=False
    )

    customer = db.relationship("User")
    match = db.relationship("Match")
    seat_plan = db.relationship("SeatPlan")
    qr_image_path = db.Column(
                    db.String(300))
    pdf_path = db.Column(
                    db.String(300)
                )

class PaymentTransaction(db.Model):
    __tablename__ = "payment_transactions"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    match_id = db.Column(
        db.Integer,
        db.ForeignKey("matches.id"),
        nullable=False
    )

    transaction_ref = db.Column(
        db.String(200),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    customer = db.relationship("User")
    match = db.relationship("Match")

class TicketVerification(db.Model):
    __tablename__ = "ticket_verifications"

    id = db.Column(db.Integer, primary_key=True)

    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("tickets.id"),
        nullable=False
    )

    verified_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    verified_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    ticket = db.relationship("Ticket")
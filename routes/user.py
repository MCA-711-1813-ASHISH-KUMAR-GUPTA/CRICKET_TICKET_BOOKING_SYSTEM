import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from models import db, Match, SeatPlan, Ticket, PaymentTransaction
from utils.qr_gen import generate_qr
from utils.pdf_gen import generate_ticket_pdf

user_bp = Blueprint("user", __name__)


@user_bp.route("/dash_user")
@login_required
def dash_user():
    matches = Match.query.order_by(Match.id.desc()).all()
    return render_template("dash_user.html", matches=matches)


@user_bp.route("/book_tickets/<int:match_id>")
@login_required
def book_tickets(match_id):
    match = Match.query.get_or_404(match_id)
    if not match.booking_enabled:
        flash("Booking is currently closed for this match.")
        return redirect(url_for("user.dash_user"))

    seats = SeatPlan.query.filter_by(match_id=match_id).order_by(
        SeatPlan.column_name, SeatPlan.row_name, SeatPlan.seat_number
    ).all()

    booked_ids = [
        t.seat_plan_id
        for t in Ticket.query.filter_by(match_id=match_id, is_cancelled=False).all()
    ]
    return render_template(
        "book_tickets.html",
        seats=seats,
        booked_ids=booked_ids,
        match_id=match_id,
        match=match,
    )


@user_bp.route("/confirm_booking", methods=["POST"])
@login_required
def confirm_booking():
    seat_ids = request.form.getlist("seat_ids")
    payment_text = request.form.get("payment_text", "").strip()

    # ── Server-side validation ────────────────────────────────────────────────
    if not seat_ids:
        flash("Please select at least one seat before confirming.")
        return redirect(request.referrer or url_for("user.dash_user"))

    if not payment_text or len(payment_text) < 5:
        flash("A valid payment reference (minimum 5 characters) is required.")
        return redirect(request.referrer or url_for("user.dash_user"))

    # Check that all selected seat IDs are valid integers
    try:
        seat_ids = [int(sid) for sid in seat_ids]
    except ValueError:
        flash("Invalid seat selection. Please try again.")
        return redirect(url_for("user.dash_user"))

    # ── Compute totals ────────────────────────────────────────────────────────
    total_amount = 0.0
    seats_objs = []
    for sid in seat_ids:
        seat = db.session.get(SeatPlan, sid)
        if not seat:
            flash(f"Seat ID {sid} does not exist.")
            return redirect(url_for("user.dash_user"))
        seats_objs.append(seat)
        total_amount += seat.seat_price

    # ── Record payment transaction ────────────────────────────────────────────
    first_match_id = seats_objs[0].match_id
    transaction = PaymentTransaction(
        customer_id=current_user.id,
        match_id=first_match_id,
        transaction_ref=payment_text,
        amount=total_amount,
    )
    db.session.add(transaction)

    # ── Create tickets ────────────────────────────────────────────────────────
    for seat in seats_objs:
        # Double-check seat is still available (race condition guard)
        existing = Ticket.query.filter_by(
            seat_plan_id=seat.id, is_cancelled=False
        ).first()
        if existing:
            db.session.rollback()
            flash(f"Seat {seat.column_name}-{seat.row_name}-{seat.seat_number} "
                  f"was just taken. Please re-select your seats.")
            return redirect(url_for("user.book_tickets", match_id=seat.match_id))

        qr_token = str(uuid.uuid4())
        ticket = Ticket(
            customer_id=current_user.id,
            match_id=seat.match_id,
            seat_plan_id=seat.id,
            amount=seat.seat_price,
            qr_string=qr_token,
        )
        db.session.add(ticket)
        db.session.flush()

        qr_path = generate_qr(ticket.id, ticket.qr_string)
        # Save QR path before generating PDF
        ticket.qr_image_path = qr_path
        pdf_path = generate_ticket_pdf(ticket)
        ticket.pdf_path = pdf_path

        # qr_path  = generate_qr(ticket.id, ticket.qr_string)
        # pdf_path = generate_ticket_pdf(ticket)
        # ticket.qr_image_path = qr_path
        # ticket.pdf_path      = pdf_path

    db.session.commit()
    flash(f"Booking confirmed! {len(seat_ids)} ticket(s) booked for ₹{total_amount:.2f}. "
          f"Download your e-tickets from 'My Tickets'.")
    return redirect(url_for("user.my_tickets"))


@user_bp.route("/my_tickets")
@login_required
def my_tickets():
    tickets = Ticket.query.filter_by(customer_id=current_user.id).order_by(
        Ticket.booked_at.desc()
    ).all()
    return render_template("my_tickets.html", tickets=tickets)


@user_bp.route("/cancel_ticket/<int:ticket_id>")
@login_required
def cancel_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if ticket.customer_id != current_user.id:
        flash("You are not authorised to cancel this ticket.")
        return redirect(url_for("user.my_tickets"))

    if ticket.is_cancelled:
        flash("This ticket has already been cancelled.")
        return redirect(url_for("user.my_tickets"))

    if ticket.is_verified:
        flash("Verified tickets cannot be cancelled.")
        return redirect(url_for("user.my_tickets"))

    ticket.is_cancelled = True
    db.session.commit()
    flash(f"Ticket #{ticket_id} has been cancelled successfully.")
    return redirect(url_for("user.my_tickets"))


@user_bp.route("/download_ticket/<int:ticket_id>")
@login_required
def download_ticket(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)

    if not ticket:
        flash("Ticket not found.")
        return redirect(url_for("user.my_tickets"))

    if ticket.customer_id != current_user.id:
        flash("Access denied.")
        return redirect(url_for("user.my_tickets"))

    if ticket.is_cancelled:
        flash("Cannot download a cancelled ticket.")
        return redirect(url_for("user.my_tickets"))

    return send_file(f"static/{ticket.pdf_path}", as_attachment=True)

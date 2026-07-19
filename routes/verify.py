from flask import Blueprint
from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask import url_for

from flask_login import login_required
from flask_login import current_user

from models import db
from models import Match
from models import Ticket
from models import TicketVerification

import re

verify_bp = Blueprint("verify", __name__)


@verify_bp.route("/dash_verify")
@login_required
def dash_verify():
    if current_user.user_type != "verifystaff":
        return redirect(url_for("auth.login"))

    matches = Match.query.order_by(
        Match.id.desc()
    ).all()

    return render_template(
        "dash_verify.html",
        matches=matches
    )


@verify_bp.route(
    "/verify_ticket",
    methods=["GET", "POST"]
)
@login_required
def verify_ticket():
    if current_user.user_type != "verifystaff":
        return redirect(url_for("auth.login"))
    if request.method == "POST":

        qr_data = request.form["qr_data"]

        token_match = re.search(
            r"TOKEN:(.+)",
            qr_data
        )

        if not token_match:
            flash("Invalid QR")
            return redirect(
                url_for("verify.verify_ticket")
            )

        token = token_match.group(1).strip()

        ticket = Ticket.query.filter_by(
            qr_string=token
        ).first()

        if not ticket:
            
            flash("Ticket Not Found")
            return redirect(
                url_for("verify.verify_ticket")
            )
        
        match = ticket.match

        if not match.verification_enabled:
            flash(
                "Verification Disabled By Admin"
            )
            return redirect(
                url_for("verify.verify_ticket")
            )

        if ticket.is_cancelled:
            flash("Cancelled Ticket")
            return redirect(
                url_for("verify.verify_ticket")
            )

        if ticket.is_verified:
            flash("Already Verified")
            return redirect(
                url_for("verify.verify_ticket")
            )

        ticket.is_verified = True

        verify_log = TicketVerification(
            ticket_id=ticket.id,
            verified_by=current_user.id
        )

        db.session.add(verify_log)

        db.session.commit()

        flash("Ticket Verified")
        return redirect(
    url_for("verify.verify_ticket")
)

    return render_template(
        "verify_ticket.html"
    )
import os

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image
)

from reportlab.lib.styles import getSampleStyleSheet


def generate_ticket_pdf(ticket):

    folder = os.path.join(
        "static",
        "pdfs"
    )

    os.makedirs(folder, exist_ok=True)

    filename = f"ticket_{ticket.id}.pdf"

    filepath = os.path.join(
        folder,
        filename
    )

    doc = SimpleDocTemplate(filepath)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            "Cricket Ticket Booking System",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 10))

    content.append(
        Paragraph(
            f"Ticket ID : {ticket.id}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Customer : {ticket.customer.name}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Venue : {ticket.match.venue.venue_name}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Match : "
            f"{ticket.match.team1.team_name}"
            f" vs "
            f"{ticket.match.team2.team_name}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Seat : "
            f"{ticket.seat_plan.column_name}-"
            f"{ticket.seat_plan.row_name}-"
            f"{ticket.seat_plan.seat_number}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Amount : ₹{ticket.amount}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Booked At : {ticket.booked_at}",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 20))

    qr_file = os.path.join(
        "static",
        ticket.qr_image_path
    )

    if os.path.exists(qr_file):

        content.append(
            Image(
                qr_file,
                width=150,
                height=150
            )
        )

    doc.build(content)

    return f"pdfs/{filename}"
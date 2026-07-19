import os
import qrcode


def generate_qr(ticket_id, qr_token):

    qr_data = (
        f"TICKET:{ticket_id}\n"
        f"TOKEN:{qr_token}"
    )

    qr = qrcode.make(qr_data)

    folder = os.path.join(
        "static",
        "qrcodes"
    )

    os.makedirs(folder, exist_ok=True)

    filename = f"ticket_{ticket_id}.png"

    filepath = os.path.join(
        folder,
        filename
    )

    qr.save(filepath)

    return f"qrcodes/{filename}"
from io import BytesIO

import qrcode


def generate_device_qr_png(device_id: str) -> bytes:
    """
    Generate a PNG QR code containing the device_id.
    """
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
    )

    qr.add_data(device_id)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white",
    )

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    return buffer.getvalue()
import base64
from urllib.parse import urlparse, parse_qs

import pyotp
import qrcode
from PIL import Image
from numpy import asarray
from qreader import QReader
from qrcode.constants import ERROR_CORRECT_L


def generate_totp_qrcode(
    secret_key: str, output: str = "qrcode.png", encode: bool = True
):
    if encode:
        secret_key = base64.b32encode(secret_key.encode()).decode()

    totp = pyotp.TOTP(secret_key)

    otpauth_url = totp.provisioning_uri(
        name="FusionSid", issuer_name="FusionSid"
    ).replace("%3D", "")

    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(otpauth_url)

    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr.print_ascii()
    qr_img.save(output)


def get_current_totp(secret_key: str, encode: bool = True):
    if encode:
        secret_key = base64.b32encode(secret_key.encode()).decode()

    totp = pyotp.TOTP(secret_key)
    return totp.now()


def secret_from_qrcode(filename: str):
    qreader = QReader()
    image = asarray(Image.open(filename).convert("RGB"))

    otpauth_url = qreader.decode(image=image)
    if otpauth_url is None:
        raise ValueError("Invalid QR Code")

    parsed_url = urlparse(otpauth_url)
    query_params = parse_qs(parsed_url.query)

    if (secret := query_params["secret"]) is None:
        raise ValueError("Invalid QR Code")

    return secret[0]

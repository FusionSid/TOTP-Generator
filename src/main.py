import time
import datetime
import base64

import pyotp
from rich import print
from typer import Typer
from rich.progress import track

from utils import generate_totp_qrcode, get_current_totp, secret_from_qrcode

app = Typer()


@app.command()
def otpfs(secret: str, encode: bool = True):
    otp = get_current_totp(secret, encode=encode)
    print(f"[b blue]Current OTP: {otp}")


@app.command()
def otpfsl(secret: str, encode: bool = True):
    if encode:
        secret = base64.b32encode(secret.encode()).decode()

    totp = pyotp.TOTP(secret)
    while True:
        time_remaining = (
            totp.interval - datetime.datetime.now().timestamp() % totp.interval
        )
        floored = int(time_remaining)

        otp = get_current_totp(secret, encode=encode)
        print(f"[b blue]Current OTP: {otp}")
        for _ in track(range(floored), description="[red]Invalid In..."):
            time.sleep(1)

        # try and correct for the error caused by flooring it
        time.sleep(time_remaining - floored)


@app.command()
def otpff(filename: str):
    secret = secret_from_qrcode(filename)
    otp = get_current_totp(secret, encode=False)

    print(f"[b blue]Secret: {secret}")
    print(f"[b blue]Current OTP: {otp}")


@app.command()
def genqr(secret: str, output: str = "qrcode.png", encode: bool = True):
    print("[b blue] QR Code:")

    generate_totp_qrcode(secret, output, encode)
    print(f"[b green] QR Code Saved To: {output}")


if __name__ == "__main__":
    app()

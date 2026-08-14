import base64
import json


def b64_with_padding(b64: str) -> str:
    missing_padding = len(b64) % 4
    if missing_padding:
        b64 += "=" * (4 - missing_padding)
    return b64


def parse_jwt(token: str) -> None:
    # split the jwt into its 3 components
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except Exception:
        raise ValueError("Invalid JWT format: Must contain exactly 2 dots")

    # parse the header
    try:
        header_bytes = base64.urlsafe_b64decode(b64_with_padding(header_b64))
        header = json.loads(header_bytes.decode("utf-8"))
        print(f"header: {header}")
    except Exception:
        raise ValueError("invalid header")

    # parse the payload
    try:
        payload_bytes = base64.urlsafe_b64decode(b64_with_padding(payload_b64))
        payload = json.loads(payload_bytes.decode("utf-8"))
        print(f"payload: {payload}")
    except Exception:
        raise ValueError("invalid payload")

    # parse the signature
    try:
        signature_bytes = base64.urlsafe_b64decode(b64_with_padding(signature_b64))
        print(f"signature: {signature_bytes}")
    except Exception:
        raise ValueError("invalid signature")


def main():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZW1haWwiOiJnZXRtZUBjaWxsaWFubXlsZXMuY29tIiwiaWF0IjoxNzg2NzQyOTAwLCJleHAiOjE3ODY3NDY1MDB9.02uiRGXcjxSlJyQeTiswLRgplkP28Q_BL3MbPHfQw3g"
    parse_jwt(token)


if __name__ == "__main__":
    main()

import base64
import binascii
import json


TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZW1haWwiOiJnZXRtZUBjaWxsaWFubXlsZXMuY29tIiwiaWF0IjoxNzg2NzQyOTAwLCJleHAiOjE3ODY3NDY1MDB9.02uiRGXcjxSlJyQeTiswLRgplkP28Q_BL3MbPHfQw3g"


def with_base64_padding(value: str) -> str:
    return value + "=" * (-len(value) % 4)


def decode_segment_bytes(segment: str) -> bytes:
    padded = with_base64_padding(segment)
    return base64.urlsafe_b64decode(padded)


def decode_json_segment(segment: str) -> dict:
    bytes = decode_segment_bytes(segment)
    return json.loads(bytes.decode("utf-8"))


def parse_jwt(token: str) -> tuple[dict, dict, bytes]:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError as e:
        raise ValueError("Invalid JWT format: must contain exactly 2 dots") from e

    try:
        header = decode_json_segment(header_b64)
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError("Invalid header") from e

    try:
        payload = decode_json_segment(payload_b64)
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError("Invalid payload") from e

    try:
        signature = decode_segment_bytes(signature_b64)
    except binascii.Error as e:
        raise ValueError("Invalid signature") from e

    return header, payload, signature


def main():
    hedaer, payload, signature = parse_jwt(TOKEN)

    print(f"header: {hedaer}")
    print(f"payload: {payload}")
    print(f"signature: {signature}")


if __name__ == "__main__":
    main()

import base64
import binascii
import json


def with_base64_padding(value: str) -> str:
    return value + "=" * (-len(value) % 4)


def decode_segment(segment: str) -> bytes:
    return base64.urlsafe_b64decode(with_base64_padding(segment))


def decode_json_segment(segment: str) -> dict:
    segment_bytes = decode_segment(segment)
    return json.loads(segment_bytes.decode("utf-8"))


def parse_jwt(token: str) -> dict:
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
        signature = decode_segment(signature_b64)
    except binascii.Error as e:
        raise ValueError("Invalid signature") from e

    return {
        "header": header,
        "payload": payload,
        "signature": signature,
    }


def main():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZW1haWwiOiJnZXRtZUBjaWxsaWFubXlsZXMuY29tIiwiaWF0IjoxNzg2NzQyOTAwLCJleHAiOjE3ODY3NDY1MDB9.02uiRGXcjxSlJyQeTiswLRgplkP28Q_BL3MbPHfQw3g"
    parsed_token = parse_jwt(token)

    print(f"header: {parsed_token['header']}")
    print(f"payload: {parsed_token['payload']}")
    print(f"signature: {parsed_token['signature']}")


if __name__ == "__main__":
    main()

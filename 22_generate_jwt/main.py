from datetime import datetime, timedelta, timezone

import json
import jwt
import time


SECRET = "extra-super-special-secret-sauce"
ALGORITHM = "HS256"


def create_jwt(payload: dict, secret: str, algorithm: str) -> str:
    print("")
    print("Generating JWT...")
    print("")
    print(f"payload: {json.dumps(payload, indent=2)}")
    print(f'secret: "{secret}"')
    print("")
    print("")
    token = jwt.encode(payload, secret, algorithm=algorithm)
    print(token)
    print("")
    return token


def main():
    created_at = int(time.time())
    expires_at = created_at + 3600
    payload = {
        "sub": "user123",
        "email": "getme@cillianmyles.com",
        "iat": created_at,
        "exp": expires_at,
    }
    create_jwt(payload, SECRET, ALGORITHM)


if __name__ == "__main__":
    main()

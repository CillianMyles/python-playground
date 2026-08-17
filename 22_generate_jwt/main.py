from datetime import datetime, timedelta, timezone

import json
import jwt
import time


SECRET = "extra-super-special-secret-sauce"
ALGORITHM = "HS256"


def main():
    created_at = int(time.time())
    expires_at = created_at + 3600
    payload = {
        "sub": "user123",
        "email": "getme@cillianmyles.com",
        "iat": created_at,
        "exp": expires_at,
    }
    token = jwt.encode(
        payload,
        SECRET,
        algorithm=ALGORITHM,
    )

    print("")
    print("Generating JWT...")
    print("")
    print(f"payload: {json.dumps(payload, indent=2)}")
    print(f'secret: "{SECRET}"')
    print("")
    print("")
    print(token)
    print("")


if __name__ == "__main__":
    main()

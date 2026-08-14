from datetime import datetime, timedelta, timezone

import jwt


SECRET = "extra-super-special-secret-sauce"
ALGORITHM = "HS256"


def main():
    created_at = datetime.now(timezone.utc)
    expires_at = created_at + timedelta(hours=1)
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
    print(f"\nGenerating JWT...\n\n{token}\n")


if __name__ == "__main__":
    main()

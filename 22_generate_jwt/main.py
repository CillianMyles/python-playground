import jwt
import time


def main():
    secret = "extra-super-special-secret-sauce"
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
        secret,
        algorithm="HS256",
    )
    print(f"\nGenerating JWT...\n\n{token}\n")


if __name__ == "__main__":
    main()

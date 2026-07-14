---
title: "Security — JWT"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - security
  - jwt
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/"
    title: "FastAPI Docs — OAuth2 with JWT"
last_audit_date: 2026-06-10
---

# Security — JWT

Create and verify JSON Web Tokens with secure password hashing.

## Install `PyJWT`

```bash
uv add pyjwt
```

For digital signature algorithms (RSA, ECDSA), install with the `crypto` extra:

```bash
uv add "pyjwt[crypto]"
```

## Password hashing

Install `pwdlib` with Argon2 support:

```bash
uv add "pwdlib[argon2]"
```

```python
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)
```

## Token creation

```python
from datetime import datetime, timedelta, timezone
import jwt

SECRET_KEY = "your-secret-key-keep-it-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

## Token verification

```python
from jwt.exceptions import InvalidTokenError


def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError:
        return None
```

## Full auth dependency

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    username = payload.get("sub")
    if username is None:
        raise credentials_exception
    return username
```

See [security-oauth2-password.md](./security-oauth2-password.md) for the login endpoint and [security-scopes.md](./security-scopes.md) for scoped permissions.

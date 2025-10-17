from typing import Iterator
from sqlalchemy.orm import Session
from models import SessionLocal


def get_db() -> Iterator[Session]:
    """
    Dependency that provides a database session.
    Automatically closes the session when the request is complete.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

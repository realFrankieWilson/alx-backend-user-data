#!/usr/bin/env python3
"""
`auth module`
"""

from db import DB
from user import User
import bcrypt
from sqlalchemy.orm.exc import NoResultFound


def _hash_password(password: str) -> bytes:
    """A hash_password method
    Args:
        password (str): password
    Returns:
        bytes
    """
    password_in_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt()

    hashed_pass = bcrypt.hashpw(password_in_bytes, salt)
    return hashed_pass


class Auth:
    """Auth class to interact with the atuthentication database"""

    def __init__(self):
        self._db = DB()

    def register_user(
        self,
        email: str,
        password: str,
    ) -> User:
        """Registers a new user with the provided email and password
        Args:
            email (str): The user's email.
            password (str): The user's password.
        Returns:
            User: The newly created User object.
        Raises:
            ValueError: If a user with the provided email already exists.
        """
        try:
            self._db.find_user_by(email=email)
            raise ValueError(f"User {email} already exists.")
        except NoResultFound:
            return self._db.add_user(email, _hash_password(password))

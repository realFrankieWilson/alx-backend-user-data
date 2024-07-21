#!/usr/bin/env python3
"""
`auth module`, provides method for user authentication
"""

from db import DB
from user import User
import bcrypt
from sqlalchemy.orm.exc import NoResultFound
import uuid


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


def _generate_uuid() -> str:
    """A function that generates and return a new UUID
    Returns:
        str: String representation of a new UUID.
    """
    return str(uuid.uuid4())


class Auth:
    """implements the data authentication functions"""

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

    def valid_login(self, email: str, password: str) -> bool:
        """Validates user credentials
        Args:
            email (str): User email to be validated.
            password (str): User password to be validated.
        Returns:
            True: if credentials are valid, False otherwise.
        """
        try:
            user = self._db.find_user_by(email=email)
            return bcrypt.checkpw(password.encode("utf-8"), user.hashed_password)
        except NoResultFound:
            return False

    def create_session(self, email: str) -> str:
        """Creates a new session for the user and returns the session ID
        Args:
            email (str): The user's email.
        Returns:
            str: The session ID fo the user.
        """
        # try:
        #     user = self._db.find_user_by(email=email)
        # except NoResultFound:
        #     raise ValueError(f"No user found with the email {email}")
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return None
        s_id = _generate_uuid()
        self._db.update_user(user.id, session_id=s_id)

        return s_id

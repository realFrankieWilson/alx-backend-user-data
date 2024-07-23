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
            return bcrypt.checkpw(password.encode("utf-8"),
                                  user.hashed_password)
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

    def get_user_from_session_id(self, session_id: str):
        """Fetches the user associated with a given session ID.
        Args:
            session_id (str): The session ID to look up.
        Returns:
            User or None: The corresponding user if found, Otherwise None
        """
        if session_id is None:
            return None  # Return None if session id is not found

        try:
            user = self._db.find_user_by(session_id=session_id)
            return user
        except NoResultFound:
            return None

    def destroy_session(self, user_id: int) -> None:
        """Destroys the session for the specified user by setting their
        session ID to None
        Args
            user_id (int): The ID of the user whose session is to be destroyed
        Returns:
            None
        """
        if user_id is None:
            return None
        try:
            user = self._db.find_user_by(id=user_id)
            self._db.update_user(user.id, session_id=None)
        except NoResultFound:
            return None

    def get_reset_password_token(self, email: str) -> str:
        """Generates a reset password token for the user the given email

        Args:
            email (str): The email of the user requesting a password
            reset.
        Returns:
            str: The generated reset token.
        Raises:
            ValueError: If the user does not exist.
        """
        # Attempt to find the user email.
        try:
            user_email = self._db.find_user_by(email=email)
        except NoResultFound:
            raise ValueError("User not found with the provided email.")

        # Generate token.
        reset_token = str(uuid.uuid4)

        # Update the user's reset_token field in the database.
        user_email.reset_token = reset_token
        self._db._session.commit()

        return reset_token

    def update_password(self, reset_token: str, password: str) -> None:
        """Updates the user's password using the reset token.
        Args:
            reset_token (str): The reset token for the user.
            password (str): The new password to set for the user.

        Raises:
            ValueError: If the user does not exist or invalid reset token
        """
        # Attempt to find user by reset token.
        try:
            user = self._db.find_user_by(reset_token=reset_token)
        except NoResultFound:
            raise ValueError("Invalid reset token.")

        # Hash the newly created password
        hashed_password = bcrypt.hashpw(password.encode("utf-8"),
                                        bcrypt.gensalt())

        # Update the user's hashed_password and reset_token
        user.hashed_password = hashed_password
        user.reset_token = None  # Clear the reset token.
        self._db._session.commit()  # save changes

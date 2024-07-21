#!/usr/bin/env python3
"""DB module
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError

from user import Base, User


class DB:
    """DB class"""

    def __init__(self) -> None:
        """Initialize a new DB instance"""
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object"""
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Add a new use to the database

        Args:
            email (str): The email of the user.
            hashed_password (str): The hashed password of the user.
        Returns:
            User: The created User object.
        """
        new_user = User(email=email, hashed_password=hashed_password)
        self._session.add(new_user)
        self._session.commit()
        return new_user

    def find_user_by(self, **kwargs) -> User:
        """Find a user by arbitrary keywords arguments
        Args:
            **kwargs: The filtering criteria for the query.
        Returns:
            User: The first User object found.
        Raises:
            NoResultFound: If no User object found.
            InvalidRequestError: If invalid query argument are provided.
        """
        try:
            user = self._session.query(User).filter_by(**kwargs).one()
            return user
        except NoResultFound:
            raise NoResultFound("No user found matching the critieria.")
        except Exception as e:
            raise InvalidRequestError(f"Invalid query arguments: {e}")

    def update_user(self, user_id: int, **kwargs) -> None:
        """Update a user's attributes
        Args:
            user_id (int): The ID of the user to update.
            **kwargs: The attributes to update.
        Raises:
            ValueError: If an invalid attribute is passed.
        """
        valid_data = {"email", "hashed_password", "session_id", "reset_token"}
        user = self.find_user_by(id=user_id)
        for key, value in kwargs.items():
            if key not in valid_data:
                raise ValueError(f"Invalid attribute: {key}")
            setattr(user, key, value)
        self._session.commit()

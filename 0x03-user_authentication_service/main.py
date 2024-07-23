#!/usr/bin/env python3
"""
Main file
"""
import requests

BASE_URL = "localhost:5000"


def register_user(email: str, password: str) -> None:
    """Rgisters a new user"""
    url = "{}/users".format(BASE_URL)
    body = {"email": email, "password": password}

    res = requests.post(url, data=body)
    assert res.status_code == 200
    assert res.json() == {"email": email, "message": "user created"}
    res = requests.post(url, data=body)
    assert res.status_code == 400
    assert res.json() == {"message": "email already registered"}


def log_in_wrong_password(email: str, password: str) -> None:
    """Tests for wrong password"""
    url = "{}/sessions".format(BASE_URL)
    context = {"email": email, "password": password}
    res = requests.post(url, data=context)
    assert res.status_code == 401


def log_in(email: str, password: str) -> str:
    url = "{}/sessions".format(BASE_URL)
    context = {"email": email, "password": password}
    res = requests.post(url, data=context)
    assert res.status_code == 200
    assert res.json() == {"email": email, "message": "logged in"}
    return res.cookies.get("session_id")


def profile_unlogged() -> None:
    """Tests for unlogged user activity"""
    url = "{}/profile".format(BASE_URL)
    res = requests.get(url)
    assert res.status_code == 403


def profile_logged(session_id: str) -> None:
    """Tests for Successfully logging in a user"""
    url = "{}/profile".format(BASE_URL)
    cookie_ses = {"session": session_id}
    res = requests.get(url, cookies=cookie_ses)
    assert res.status_code == 200
    assert "email" in res.json()


def log_out(session_id: str) -> None:
    """Logs a user out"""
    url = "{}/sessions".format(BASE_URL)
    cookie_ses = {"session_id": session_id}
    res = requests.delete(url, )


def reset_password_token(email: str) -> str:
    """Resets password token"""
    res = requests.post(f"{BASE_URL}/reset_password_token",
                        data={"email": email})
    assert res.status_code == 200
    return res.json.get("reset_token")


def update_password(email: str, reset_token: str, new_password: str) -> None:
    res = requests.put(
        f"{BASE_URL}/reset_password",
        data={"email": email, "reset_token": reset_token,
              "new_password": new_password},
    )
    assert res.status_code == 200


EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"


if __name__ == "__main__":

    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    profile_logged(session_id)
    log_out(session_id)
    reset_token = reset_password_token(EMAIL)
    update_password(EMAIL, reset_token, NEW_PASSWD)
    log_in(EMAIL, NEW_PASSWD)

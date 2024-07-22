#!/usr/bin/env python3
"""Module `app`, a basic flask app"""
from flask import Flask, jsonify, request, abort
from auth import Auth

app = Flask(__name__)

AUTH = Auth()


@app.route("/", methods=["GET"])
def message():
    """A flask method that returns a simple dictionary"""
    return jsonify({"message": "Bienvenue"})


@app.route("/users", methods=["POST"])
def user():
    """A user function that implements the POST /users route"""
    email = request.form.get("email")
    password = request.form.get("password")

    # Imput validations
    if not email or not password:
        return jsonify({"message": "email and password are required"}), 400

    try:
        # Attempt to register the user
        user = AUTH.register_user(email=email, password=password)
        return jsonify({"email": user.email, "message": "user created"}), 200
    except Exception as e:
        # Handle the case where user is not created successfully
        return jsonify({"message": "email already registered"}), 400


@app.route("/sessions", methods=["POST"])
def login():
    """Handles user login"""
    email = request.form.get("email")
    password = request.form.get("password")
    authenticated_user = AUTH.valid_login(email, password)

    if not authenticated_user:
        abort(401)
    # Create a session for the user.
    session_id = AUTH.create_session(email)
    status = {"email": email, "message": "logged in"}
    res = jsonify(status)
    res.set_cookie("session_id", session_id)
    return res


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")

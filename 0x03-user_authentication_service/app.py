#!/usr/bin/env python3
"""Module `app`, a basic flask app"""
from flask import Flask, jsonify, request, abort, redirect
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


@app.route("/sessions", methods=["DELETE"])
def logout():
    """Logout a user by destroying their session."""
    session_id = request.cookies.get("session_id")

    if not session_id:
        return jsonify({"message": "session_id not provided"}), 400

    user = None
    try:
        user = request._db.find_user_by(session_id=session_id)
    except Exception:
        return jsonify({"message": "user not found"}), 403

    if user:
        AUTH.destroy_session(user.id)
        return redirect("/")
    else:
        return jsonify({"message": "user not found"}), 403


@app.route("/profile", methods=["GET"])
def profile():
    """Get the user's profile based on the session ID"""
    session_id = request.cookies.get("session_id")

    if session_id is None:
        abort(403)
    user = AUTH.get_user_from_session_id(session_id)

    if user is None:
        abort(403)
    return jsonify({"email": user.email}), 200


@app.route("/reset_password", methods=["POST"])
def reset_password():
    """Handles password reset requests."""
    email = request.form.get("email")

    if not email:
        abort(400, "Email field is required")
    try:
        # Attempt to generate a reset token.
        reset_token = AUTH.get_reset_password_token(email)
    except ValueError:
        abort(403, "Email not registered.")

    return jsonify({"email": email, "reset_token": reset_token}), 200


@app.route("/reset_password", methods=["PUT"])
def update_password():
    """Responds to the put /reset_password route."""
    email = request.form.get("email")
    reset_token = request.form.get("reset_token")
    new_password = request.form.get("new_password")

    try:
        Auth.update_password(reset_token, new_password)
    except Exception:
        abort(403)
    context = {"email": email, "message": "Password updated"}
    return jsonify(context), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")

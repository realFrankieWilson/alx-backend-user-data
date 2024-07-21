#!/usr/bin/env python3
"""Module `app`, a basic flask app"""
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET"])
def message():
    """A flask method that returns a simple dictionary"""
    return jsonify({"message": "Bienvenue"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")

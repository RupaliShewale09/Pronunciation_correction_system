from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, verify_jwt_in_request
from backend.database.db import db
from backend.database.user import User
from backend.utils.security import hash_password, verify_password

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "User already exists"}), 400

    new_user = User(
        username=data["username"],
        password=hash_password(data["password"])
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Signup successful"})


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(username=data["username"]).first()

    if not user or not verify_password(data["password"], user.password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token
    })

@auth_bp.route("/verify-token", methods=["POST"])
def verify_token():
    try:
        verify_jwt_in_request()  # Will raise an error if token invalid/expired
        return jsonify({"valid": True}), 200
    except:
        return jsonify({"valid": False}), 401

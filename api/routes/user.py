from flask import Blueprint, jsonify, request, session

from services.user_service import user_service


user_routes = Blueprint("user_routes", __name__)


@user_routes.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    try:
        user = user_service.register(
            username=data.get("username"),
            password=data.get("password"),
            display_name=data.get("displayName"),
        )
        session["username"] = user["username"]
        return jsonify({"user": user}), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@user_routes.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    try:
        user = user_service.authenticate(data.get("username"), data.get("password"))
        session["username"] = user["username"]
        return jsonify({"user": user})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 401


@user_routes.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


@user_routes.route("/account", methods=["DELETE"])
def delete_account():
    username = session.get("username")
    if not username:
        return jsonify({"error": "Login required"}), 401
    try:
        result = user_service.delete_user(username)
        session.clear()
        return jsonify(result)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404


@user_routes.route("/me", methods=["GET"])
def me():
    username = session.get("username")
    if not username:
        return jsonify({"authenticated": False, "user": None})
    user = user_service.get_user(username)
    if not user:
        session.pop("username", None)
        return jsonify({"authenticated": False, "user": None})
    return jsonify({"authenticated": True, "user": user})


@user_routes.route("/preferences", methods=["GET"])
def get_preferences():
    return jsonify(user_service.get_preferences(username=session.get("username")))


@user_routes.route("/preferences", methods=["PUT"])
def update_preferences():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(user_service.update_preferences(data, username=session.get("username")))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404


@user_routes.route("/api-keys/status")
def api_key_status():
    return jsonify(user_service.api_key_status())

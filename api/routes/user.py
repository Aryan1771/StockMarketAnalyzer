from flask import Blueprint, jsonify, redirect, request, session

from services.oauth_service import oauth_service
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
    return jsonify({**user_service.api_key_status(), "oauth": oauth_service.provider_status()})


@user_routes.route("/oauth/providers", methods=["GET"])
def oauth_providers():
    return jsonify(oauth_service.provider_status())


@user_routes.route("/oauth/<provider>/start", methods=["GET"])
def oauth_start(provider):
    if provider not in {"google", "microsoft"}:
        return jsonify({"error": "Unsupported OAuth provider"}), 404
    if not oauth_service.provider_status().get(provider):
        return jsonify({"error": f"{provider.title()} sign-in is not configured"}), 400

    next_path = request.args.get("next", "/watchlist")
    payload = oauth_service.begin(provider, request.url_root.rstrip("/"), next_path=next_path)
    session[f"oauth_state_{provider}"] = payload["state"]
    session[f"oauth_next_{provider}"] = payload["nextPath"]
    session[f"oauth_redirect_{provider}"] = payload["redirectUri"]
    return redirect(payload["url"])


@user_routes.route("/oauth/<provider>/callback", methods=["GET"])
def oauth_callback(provider):
    if provider not in {"google", "microsoft"}:
        return jsonify({"error": "Unsupported OAuth provider"}), 404

    error = request.args.get("error")
    if error:
        return redirect(oauth_service.frontend_redirect(
            session.pop(f"oauth_next_{provider}", "/watchlist"),
            status="error",
        ))

    code = request.args.get("code")
    state = request.args.get("state")
    if not code:
        return redirect(oauth_service.frontend_redirect(
            session.pop(f"oauth_next_{provider}", "/watchlist"),
            status="error",
        ))

    try:
        user = oauth_service.complete(
            provider=provider,
            code=code,
            state=state,
            saved_state=session.pop(f"oauth_state_{provider}", None),
            redirect_uri=session.pop(f"oauth_redirect_{provider}", ""),
        )
        session["username"] = user["username"]
        next_path = session.pop(f"oauth_next_{provider}", "/watchlist")
        return redirect(oauth_service.frontend_redirect(next_path, status="success"))
    except Exception:
        next_path = session.pop(f"oauth_next_{provider}", "/watchlist")
        return redirect(oauth_service.frontend_redirect(next_path, status="error"))

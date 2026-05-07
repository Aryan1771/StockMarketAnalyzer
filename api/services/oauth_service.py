import secrets
from urllib.parse import urlencode

import requests

from config import (
    FRONTEND_APP_URL,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    MICROSOFT_CLIENT_ID,
    MICROSOFT_CLIENT_SECRET,
    MICROSOFT_TENANT_ID,
)
from services.user_service import user_service


class OauthService:
    def provider_status(self):
        return {
            "google": bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET),
            "microsoft": bool(MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET),
        }

    def begin(self, provider, base_url, next_path="/watchlist"):
        next_path = next_path if next_path.startswith("/") else "/watchlist"
        state = secrets.token_urlsafe(24)
        redirect_uri = self._redirect_uri(base_url, provider)
        return {
            "provider": provider,
            "state": state,
            "nextPath": next_path,
            "redirectUri": redirect_uri,
            "url": self._authorize_url(provider, redirect_uri, state),
        }

    def complete(self, provider, code, state, saved_state, redirect_uri):
        if not saved_state or state != saved_state:
            raise ValueError("OAuth state validation failed")

        if provider == "google":
            userinfo = self._google_userinfo(code, redirect_uri)
        elif provider == "microsoft":
            userinfo = self._microsoft_userinfo(code, redirect_uri)
        else:
            raise ValueError("Unsupported OAuth provider")

        provider_user_id = userinfo.get("sub") or userinfo.get("id")
        email = userinfo.get("email") or userinfo.get("preferred_username")
        display_name = userinfo.get("name") or email or provider_user_id
        if not provider_user_id:
            raise ValueError("OAuth provider did not return a user id")

        return user_service.get_or_create_oauth_user(
            provider=provider,
            provider_user_id=provider_user_id,
            email=email,
            display_name=display_name,
        )

    def frontend_redirect(self, next_path="/watchlist", status="success"):
        base = FRONTEND_APP_URL.rstrip("/")
        target = next_path if next_path.startswith("/") else "/watchlist"
        separator = "&" if "?" in target else "?"
        return f"{base}{target}{separator}oauth={status}"

    def _authorize_url(self, provider, redirect_uri, state):
        if provider == "google":
            params = {
                "client_id": GOOGLE_CLIENT_ID,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": "openid email profile",
                "state": state,
                "prompt": "select_account",
            }
            return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

        if provider == "microsoft":
            params = {
                "client_id": MICROSOFT_CLIENT_ID,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "response_mode": "query",
                "scope": "openid profile email User.Read",
                "state": state,
                "prompt": "select_account",
            }
            return f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}/oauth2/v2.0/authorize?{urlencode(params)}"

        raise ValueError("Unsupported OAuth provider")

    def _google_userinfo(self, code, redirect_uri):
        token_response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=12,
        )
        token_response.raise_for_status()
        access_token = token_response.json().get("access_token")
        if not access_token:
            raise ValueError("Google did not return an access token")

        userinfo_response = requests.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=12,
        )
        userinfo_response.raise_for_status()
        return userinfo_response.json()

    def _microsoft_userinfo(self, code, redirect_uri):
        token_response = requests.post(
            f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}/oauth2/v2.0/token",
            data={
                "client_id": MICROSOFT_CLIENT_ID,
                "client_secret": MICROSOFT_CLIENT_SECRET,
                "code": code,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=12,
        )
        token_response.raise_for_status()
        access_token = token_response.json().get("access_token")
        if not access_token:
            raise ValueError("Microsoft did not return an access token")

        userinfo_response = requests.get(
            "https://graph.microsoft.com/oidc/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=12,
        )
        userinfo_response.raise_for_status()
        return userinfo_response.json()

    def _redirect_uri(self, base_url, provider):
        return f"{base_url.rstrip('/')}/api/user/oauth/{provider}/callback"


oauth_service = OauthService()

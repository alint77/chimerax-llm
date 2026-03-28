# vim: set expandtab shiftwidth=4 softtabstop=4:

"""GitHub Copilot OAuth authentication (device flow).

Reads existing tokens from opencode's auth store or the VS Code Copilot
extension.  Can also run the full device-flow login to obtain a fresh token.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Optional
import urllib.request
import urllib.error

# Same client ID used by opencode – registered GitHub OAuth app for Copilot.
_CLIENT_ID = "Ov23li8tweQw6odWQebz"
_DEVICE_CODE_URL = "https://github.com/login/device/code"
_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
_USER_AGENT = "ChimeraLLM/0.1"
_POLL_SAFETY_MARGIN = 3  # seconds


def _opencode_auth_path() -> Path:
    """Path to opencode's auth.json."""
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "opencode" / "auth.json"
    xdg = os.environ.get("XDG_DATA_HOME", "")
    if xdg:
        return Path(xdg) / "opencode" / "auth.json"
    if os.uname().sysname == "Darwin":
        return Path.home() / ".local" / "share" / "opencode" / "auth.json"
    return Path.home() / ".local" / "share" / "opencode" / "auth.json"


def get_token() -> Optional[str]:
    """Return a cached Copilot OAuth token, or *None* if none found.

    Searches (in order):
    1. opencode auth store  (~/.local/share/opencode/auth.json)
    """
    # 1. opencode auth store
    p = _opencode_auth_path()
    if p.is_file():
        try:
            data = json.loads(p.read_text())
            entry = data.get("github-copilot", {})
            tok = entry.get("refresh") or entry.get("access")
            if tok:
                return tok
        except (json.JSONDecodeError, OSError):
            pass

    return None


# ---------------------------------------------------------------------------
# Device-flow login (interactive)
# ---------------------------------------------------------------------------

class DeviceFlowError(RuntimeError):
    pass


def _post_json(url: str, body: dict) -> dict:
    """POST JSON and return parsed response."""
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": _USER_AGENT,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def start_device_flow() -> dict:
    """Initiate a device-flow login.  Returns a dict with keys:

    - ``verification_uri``  – URL the user should open
    - ``user_code``         – code to enter on that page
    - ``device_code``       – opaque code for polling  (internal)
    - ``interval``          – poll interval in seconds  (internal)
    """
    return _post_json(_DEVICE_CODE_URL, {
        "client_id": _CLIENT_ID,
        "scope": "read:user",
    })


def poll_for_token(device_code: str, interval: int = 5, timeout: int = 300) -> str:
    """Poll GitHub until the user completes the device-flow authorization.

    Returns the OAuth access token on success.
    Raises ``DeviceFlowError`` on failure or timeout.
    """
    deadline = time.monotonic() + timeout
    poll_interval = interval

    while time.monotonic() < deadline:
        time.sleep(poll_interval + _POLL_SAFETY_MARGIN)

        try:
            data = _post_json(_ACCESS_TOKEN_URL, {
                "client_id": _CLIENT_ID,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            })
        except urllib.error.HTTPError:
            raise DeviceFlowError("HTTP error while polling for token")

        if data.get("access_token"):
            token = data["access_token"]
            _save_token(token)
            return token

        error = data.get("error", "")
        if error == "authorization_pending":
            continue
        if error == "slow_down":
            poll_interval = data.get("interval", poll_interval + 5)
            continue
        if error:
            raise DeviceFlowError(f"Device flow error: {error}")

    raise DeviceFlowError("Timed out waiting for authorization")


def _save_token(token: str) -> None:
    """Persist the token to opencode's auth store so both tools share it."""
    p = _opencode_auth_path()
    p.parent.mkdir(parents=True, exist_ok=True)

    # Merge with existing data if present
    existing: dict = {}
    if p.is_file():
        try:
            existing = json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    existing["github-copilot"] = {
        "type": "oauth",
        "refresh": token,
        "access": token,
        "expires": 0,
    }

    p.write_text(json.dumps(existing, indent=2))
    os.chmod(p, 0o600)

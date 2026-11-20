from __future__ import annotations

import requests
from requests import Response


class BettingApi:
    """Thin wrapper that adds the user header and the base URL."""

    def __init__(self, base_url: str, user_id: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"x-user-id": user_id})

    def matches(self) -> list[dict]:
        """Return the match catalogue as decoded JSON."""
        return self._get("/api/matches").json()

    def balance(self) -> float:
        """Return the current balance."""
        return float(self._get("/api/balance").json()["balance"])

    def reset_balance(self) -> Response:
        """Reset the balance and return the raw response."""
        response = self.session.post(f"{self.base_url}/api/reset-balance", timeout=self.timeout)
        response.raise_for_status()
        return response

    def place_bet(self, match_id: str, selection: str, stake: float | str) -> Response:
        """Post a bet and return the raw response for assertions."""
        return self.session.post(
            f"{self.base_url}/api/place-bet",
            json={"matchId": match_id, "selection": selection, "stake": stake},
            timeout=self.timeout,
        )

    def _get(self, path: str) -> Response:
        response = self.session.get(f"{self.base_url}{path}", timeout=self.timeout)
        response.raise_for_status()
        return response

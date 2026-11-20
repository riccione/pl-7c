from __future__ import annotations

import pytest

from framework.api.client import BettingApi

MAX_STAKE = 100.00


@pytest.mark.api
def test_stake_above_balance_is_rejected(
    api: BettingApi,
    upcoming_match: dict,
) -> None:
    """Reject a stake larger than the balance and never go negative.

    The starting balance is above the stake ceiling, so a legal stake cannot
    exceed it. The test spends the balance down first, then submits one euro
    more than what is left. An accepted bet is BUG-02, so it is marked with
    an imperative xfail that records the amounts. A setup error or a server
    error still fails normally instead of hiding behind the marker.
    """
    api.reset_balance()
    try:
        starting = api.balance()
        assert starting > 0

        if starting >= MAX_STAKE:
            spend = api.place_bet(upcoming_match["id"], "HOME", MAX_STAKE)
            assert spend.status_code == 200

        remaining = api.balance()
        stake = round(min(remaining + 1.00, MAX_STAKE), 2)
        assert stake > remaining

        response = api.place_bet(upcoming_match["id"], "DRAW", stake)

        if response.status_code == 200:
            actual_balance = api.balance()
            pytest.xfail(
                f"BUG-02: accepted {stake:.2f} with {remaining:.2f} available, "
                f"balance now {actual_balance:.2f}"
            )

        assert response.status_code == 422
        assert api.balance() == pytest.approx(remaining, abs=0.001)
    finally:
        api.reset_balance()

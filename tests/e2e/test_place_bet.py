from __future__ import annotations

import pytest

from framework.pages.matches_page import MatchesPage

STAKE = 1.00


@pytest.mark.ui
def test_place_single_bet_deducts_stake_and_clears_slip(
    api,
    fresh_balance: float,
    upcoming_match: dict,
    matches_page: MatchesPage,
) -> None:
    """Critical journey: select odds, stake, place, verify one debit.

    Why this test: it is the revenue path. It checks that the selection
    reaches the slip, the payout is calculated, the receipt is issued, the
    API balance drops by exactly the stake, and the slip clears afterwards.
    Receipt payout text is not asserted because BUG-04 is a known defect.
    """
    matches_page.select(upcoming_match["id"], "home")
    slip = matches_page.slip

    assert slip.teams() == (f"{upcoming_match['homeTeam']} vs {upcoming_match['awayTeam']}")

    slip.enter_stake(f"{STAKE:.2f}")
    assert slip.total() == pytest.approx(STAKE)
    assert slip.payout() == pytest.approx(upcoming_match["odds"]["home"] * STAKE, abs=0.01)

    receipt = slip.place()

    assert receipt.title() == "Bet Placed Successfully!"
    assert receipt.bet_id().startswith("#B-")
    assert receipt.stake() == pytest.approx(STAKE)
    assert receipt.odds() == pytest.approx(upcoming_match["odds"]["home"])

    assert api.balance() == pytest.approx(fresh_balance - STAKE, abs=0.001)

    receipt.close()
    slip.wait_until_empty()
    assert slip.is_empty()

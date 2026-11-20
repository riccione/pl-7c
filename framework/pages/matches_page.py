from __future__ import annotations

from typing import ClassVar

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from framework.pages.base_page import BasePage
from framework.pages.bet_slip_page import BetSlipPage


class MatchesPage(BasePage):
    """The home page: a list of matches with 1, X, 2 buttons."""

    ODDS = (By.CSS_SELECTOR, "#match-list .oddsButton")
    VALID_SIDES: ClassVar[frozenset[str]] = frozenset({"home", "draw", "away"})

    def __init__(self, driver: WebDriver, url: str, timeout: float = 10) -> None:
        super().__init__(driver, timeout)
        self.url = url
        self.slip = BetSlipPage(driver, timeout)

    def open(self) -> None:
        self.driver.get(self.url)
        self.visible(self.ODDS)

    def select(self, match_id: str, side: str) -> None:
        """Select home, draw, or away odds for a specific match."""
        if side not in self.VALID_SIDES:
            raise ValueError(
                f"Invalid selection side: {side!r}. Expected one of {sorted(self.VALID_SIDES)}."
            )

        locator = (By.ID, f"odds-{match_id}-{side}")
        self.click(locator)
        self.slip.wait_for_selection()

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from framework.pages.base_page import BasePage, money
from framework.pages.receipt_modal import ReceiptModal


class BetSlipPage(BasePage):
    """Stake, payout, and the Place Bet action."""

    COUNT = (By.ID, "bet-slip-count")
    TEAMS = (By.CSS_SELECTOR, "#bet-slip .betSelectionTeams")
    STAKE = (By.ID, "bet-slip-stake-input")
    TOTAL = (By.ID, "bet-slip-total-stake")
    PAYOUT = (By.ID, "bet-slip-potential-payout")
    PLACE = (By.ID, "bet-slip-place-bet")

    def wait_for_selection(self) -> None:
        self.wait.until(lambda d: d.find_element(*self.COUNT).text.strip() == "1")
        self.visible(self.STAKE)

    def teams(self) -> str:
        return self.text(self.TEAMS)

    def enter_stake(self, stake: str) -> None:
        field = self.visible(self.STAKE)
        field.clear()
        field.send_keys(stake)
        field.send_keys(Keys.TAB)
        expected = float(stake)
        self.wait.until(lambda d: money(d.find_element(*self.TOTAL).text) == expected)

    def total(self) -> float:
        return money(self.text(self.TOTAL))

    def payout(self) -> float:
        return money(self.text(self.PAYOUT))

    def place(self) -> ReceiptModal:
        self.click(self.PLACE)
        receipt = ReceiptModal(self.driver, self.timeout)
        receipt.wait_open()
        return receipt

    def wait_until_empty(self) -> None:
        self.wait.until(lambda d: d.find_element(*self.COUNT).text.strip() == "0")

    def is_empty(self) -> bool:
        return self.driver.find_element(
            *self.COUNT
        ).text.strip() == "0" and not self.driver.find_elements(*self.STAKE)

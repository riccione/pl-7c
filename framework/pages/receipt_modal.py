from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from framework.pages.base_page import BasePage, money


class ReceiptModal(BasePage):
    """Fields and actions on the receipt shown after a successful bet."""

    ROOT = (By.ID, "modal-success")
    TITLE = (By.CSS_SELECTOR, "#modal-success .modalTitle")
    BET_ID = (By.ID, "modal-success-bet-id")
    STAKE = (By.ID, "modal-success-stake")
    ODDS = (By.ID, "modal-success-odds")
    CLOSE = (By.ID, "modal-success-close")

    def wait_open(self) -> None:
        self.wait.until(EC.visibility_of_element_located(self.ROOT))
        self.wait.until(EC.text_to_be_present_in_element(self.TITLE, "Bet Placed Successfully!"))

    def title(self) -> str:
        return self.text(self.TITLE)

    def bet_id(self) -> str:
        return self.text(self.BET_ID)

    def stake(self) -> float:
        return money(self.text(self.STAKE))

    def odds(self) -> float:
        return money(self.text(self.ODDS))

    def close(self) -> None:
        self.click(self.CLOSE)
        self.wait.until(EC.invisibility_of_element_located(self.ROOT))

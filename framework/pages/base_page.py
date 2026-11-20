from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

Locator = tuple[str, str]


def money(text: str) -> float:
    """Convert text such as ``€18.50`` to a float."""
    return float(text.replace("€", "").replace(",", "").strip())


class BasePage:
    def __init__(self, driver: WebDriver, timeout: float = 10) -> None:
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def visible(self, locator: Locator) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator: Locator) -> None:
        self.visible(locator).click()

    def text(self, locator: Locator) -> str:
        return self.visible(locator).text.strip()

from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from datetime import date
from urllib.parse import quote, urlsplit, urlunsplit

import allure
import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

from framework.api.client import BettingApi
from framework.pages.matches_page import MatchesPage

BASE_URL = os.getenv("BETTING_BASE_URL", "https://qae-assignment-tau.vercel.app").rstrip("/")
_user_id = os.getenv("BETTING_USER_ID")
if not _user_id:
    raise RuntimeError("BETTING_USER_ID environment variable is required")
USER_ID = _user_id
HEADLESS = os.getenv("HEADLESS", "true").lower() != "false"
TIMEOUT = float(os.getenv("SELENIUM_TIMEOUT", "10"))

logger = logging.getLogger(__name__)


@pytest.fixture
def api() -> BettingApi:
    return BettingApi(BASE_URL, USER_ID)


@pytest.fixture
def driver(request: pytest.FixtureRequest) -> Iterator[WebDriver]:
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,900")

    browser = webdriver.Chrome(options=options)
    browser.set_page_load_timeout(TIMEOUT * 2)
    setattr(request.node, "_driver", browser)  # noqa: B010
    try:
        yield browser
    finally:
        browser.quit()


@pytest.fixture
def matches_page(driver: WebDriver) -> MatchesPage:
    url = f"{BASE_URL}/?user-id={quote(USER_ID)}"
    page = MatchesPage(driver, url, TIMEOUT)
    page.open()
    return page


@pytest.fixture
def upcoming_match(api: BettingApi) -> dict:
    """Return the earliest match scheduled for today or later."""
    matches = api.matches()
    if not matches:
        pytest.skip("The match catalogue is empty")

    today = date.today().isoformat()
    future = [match for match in matches if match["kickoffDate"] >= today]
    if not future:
        pytest.skip("No upcoming matches are available")
    return min(future, key=lambda match: match["kickoffDate"])


@pytest.fixture
def fresh_balance(api: BettingApi) -> Iterator[float]:
    """Reset the balance, expose the stored value, and restore it after.

    The reset response and the stored balance currently disagree, so this
    reads the balance back instead of trusting the response.
    """
    api.reset_balance()
    balance = api.balance()
    try:
        yield balance
    finally:
        api.reset_balance()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach a screenshot to failed UI tests before the browser quits."""
    outcome = yield
    report = outcome.get_result()
    if report.when not in ("setup", "call") or not report.failed:
        return

    driver = getattr(item, "_driver", None)
    if driver is None:
        return

    try:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="failure-screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
        parts = urlsplit(driver.current_url)
        safe_url = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
        allure.attach(
            safe_url,
            name="failure-url",
            attachment_type=allure.attachment_type.TEXT,
        )
    except (WebDriverException, OSError):
        # Never mask the original test failure with an attachment error.
        logger.warning("Could not attach failure screenshot", exc_info=True)

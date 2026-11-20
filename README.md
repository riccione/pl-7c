# Betting QA automation

A small Python test suite for the single bet placement flow. It includes one UI
end-to-end test and one API business-rule test.

Tech stack: Python, pytest, Selenium, requests, mypy, Allure, uv.

## Requirements

- Python 3.11+
- uv
- Chrome or Chromium

Selenium Manager handles browser driver installation automatically.

## Setup

1. Clone the repo and install dependencies:

```bash
uv sync
```

2. Set the required environment variable:

```bash
export BETTING_USER_ID="<your-user-id>"
```

Optionally, configure the application URL:

```
export BETTING_BASE_URL="https://qae-assignment-tau.vercel.app"
```

The user ID is a credential. Do not commit it. In CI, set it as a secret.

If you prefer a local file:

```bash
cp .env.example .env
# edit .env, then load it into the shell
set -a; source .env; set +a
```

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `BETTING_BASE_URL` | `https://qae-assignment-tau.vercel.app` | App under test (optional) |
| `BETTING_USER_ID` | required | Sent as `x-user-id` and in the page URL |
| `HEADLESS` | `true` | Set to `false` to watch the browser |
| `SELENIUM_TIMEOUT` | `10` | Explicit wait timeout in seconds |

## Running tests

```bash
uv run pytest                 # full suite
uv run pytest -m ui           # UI journeys only
uv run pytest -m api          # API checks only
HEADLESS=false uv run pytest -m ui
```

Run linting:
```bash
uv run ruff check .
```

## Tests

`tests/e2e/test_place_bet.py` - Verifies the successful betting journey,
receipt, balance deduction, and cleared bet slip (UI).

`tests/api/test_insufficient_balance.py` - Verifies that the backend rejects a
stake exceeding the available balance (API).

The API test currently reports XFAIL because the application accepts bets that
exceed the available balance (BUG-02). It will become a normal passing test once
the defect is fixed.

## Test Reports

Pytest saves Allure results to `allure-results/`.

Generate an HTML report:

```bash
npx --yes allure-commandline@2.46.1 generate allure-results \
  --clean --single-file -o allure-report
```

Open `allure-report/index.html` in a browser.

The Allure CLI requires Java 8 or newer. Generating the report with npx also requires Node.js.

Failed UI tests automatically attach a screenshot and the current page URL. Xfailed tests do not.

## Structure

```
framework/
  api/
    client.py            BettingApi: matches, balance, reset, place-bet
  pages/
    base_page.py         explicit waits, click, text
    matches_page.py      open the app, select an outcome
    bet_slip_page.py     stake, payout, place, empty check
    receipt_modal.py     receipt fields and close
tests/
  conftest.py            env constants and five fixtures
  api/
    test_insufficient_balance.py
  e2e/
    test_place_bet.py
```

## Notes

- Page objects encapsulate browser interactions, selectors, and explicit waits.
- Tests use a shared test account. Avoid running them in parallel.
- The UI test places a €1.00 bet and resets the account balance before execution.
- Known defects and manual testing results are documented in `docs/defect-report.md`.

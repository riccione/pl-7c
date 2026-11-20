# Defect report: single bet placement

| Application | Sports Betting QA, https://qae-assignment-tau.vercel.app |
| Environment | Desktop Chrome, build 1.0.0 |
| Test user | configured via BETTING_USER_ID (not committed) |
| Scope | TC-01, TC-02, TC-04, plus exploratory checks on filters, selection handling, error modal, reset, and API |
| Result | 7 defects: 3 Critical, 3 High, 1 Medium |

---

## 1. Summary

| ID | Title | Severity | Area |
| --- | --- | --- | --- |
| BUG-01 | Double-click places two bets and debits the stake twice | Critical | Place bet |
| BUG-02 | API accepts stakes above the balance and produces a negative balance | Critical | Balance |
| BUG-03 | Past matches are listed and can be bet on | Critical | Match list |
| BUG-04 | Receipt payout ignores the odds and always shows 2x the stake | High | Receipt |
| BUG-05 | Success receipt swaps home and away teams | High | Receipt |
| BUG-07 | Reset-balance response disagrees with the stored balance | High | Reset |
| BUG-06 | Balance is not refreshed after a successful bet | Medium | Balance |

---

## 2. Defects

### BUG-01: Double-click places two bets and debits the stake twice

Severity: Critical

Reproduction steps:

1. Open the app with the configured user, for example `?user-id=$BETTING_USER_ID`.
2. Select Ajax vs AZ Alkmaar, HOME, odds 1.85.
3. Enter stake `1.01`.
4. Open DevTools -> Network tab.
5. Double-click Place Bet.
6. Inspect the network requests and account balance.

Expected Result:

Expected one bet request and one debit. A second submission while the first is
in progress should be ignored or rejected with 409, as specified.

Actual: two POST /api/place-bet requests were sent, both returned 200, and the
balance was debited twice. The UI displayed only one receipt (#B-22465).

A separate concurrent API test also returned two successful responses instead of
rejecting the second in-progress request with 409.

Business impact: A user can be charged twice for one intended bet, resulting in
financial discrepancies, refund requests, and loss of trust.

Evidence: Two successful network requests (200), corresponding balance deductions, and one receipt displayed in the UI.
See screenshot [evidence/bug-01-duplicate-bet-receipt.png](evidence/bug-01-duplicate-bet-receipt.png)

---

### BUG-02: API accepts stakes above the balance and produces a negative balance

Severity: Critical

Reproduction steps:

1. Ensure the account balance is €120.00.
2. Send POST /api/place-bet with:
  - stake: 100
  - selection: "AWAY"
  - matchId: "eredivisie-ajax-az-2026-11-21"
3. Send the same request again.
4. Inspect both responses and the final account balance.

Expected Result:

Expected the first request to succeed, leaving €4.95, and the second request to
be rejected with 422 because the remaining balance is insufficient.

Actual: both requests returned 200, and the account balance became -95.05.

The same balance-control issue was also observed through the UI when the
displayed balance became stale. A subsequent bet was accepted even though the
server-side balance was insufficient.

Business impact:

The application allows users to place bets without sufficient funds, creating
negative balances and direct financial risk for the operator.

Evidence:

API responses showed successful placement of both bets and a final balance of
negative balance. Additional UI testing also produced a negative server-side balance.

See screenshot: [evidence/bug-02-negative-balance.png](evidence/bug-02-negative-balance.png)

---

### BUG-03: Past matches are listed and can be bet on

Severity: Critical

Reproduction steps:

1. Find Manchester Utd vs Chelsea, labelled PAST, dated 27 February 2026.
2. Select HOME odds 2.45.
3. Enter stake 1.00.
4. Place the bet.

Expected Result: Expected past events to be hidden or unavailable for selection,
with bet placement rejected if attempted.

Actual: the selection was accepted, and the bet was successfully placed
(#B-79787). The account balance decreased from €115.50 to €114.50.

Business impact:

Users can place bets on events whose results may already be known, creating a
serious betting-integrity and potential fraud risk.

Evidence:

The receipt was displayed for a match labelled PAST. The API returned 200 for
matchId: "premier-league-manutd-chelsea".

See screenshot: [evidence/bug-03-past-match-receipt.png](evidence/bug-03-past-match-receipt.png)

---

### BUG-04: Receipt payout ignores the odds and always shows 2x the stake

Severity: High

Reproduction steps:

1. Place a €1.00 bet at odds 3.70 on Ajax vs AZ Alkmaar, DRAW.
2. Compare the potential payout in the bet slip, API response, and receipt.
3. Repeat with a €10.00 stake at odds 1.85.

Expected Result: 

Expected the receipt to display the same potential payout as the bet slip and
API, calculated using the selected odds.

Actual:

- €1.00 at odds 3.70: slip €3.70, API €3.70, receipt €2.00.
- €10.00 at odds 1.85: slip €18.50, API €18.50, receipt €20.00.

The receipt consistently calculates the payout as stake × 2.00, regardless of the selected odds.

Business impact:

The receipt is the customer's record of the bet. Incorrect payout information
can cause disputes, undermine trust, and create problems during settlement.

Evidence: Receipt #B-94629 displayed Potential Payout €2.00 for a €1.00 stake at odds 3.70.

See screenshot: [evidence/bug-04-receipt-draw-3.70-payout-2.00.png](evidence/bug-04-receipt-draw-3.70-payout-2.00.png)

---

### BUG-05: Success receipt swaps home and away teams

Severity: High

Reproduction steps:

1. Bet on Ajax vs AZ Alkmaar, HOME.
2. Read the match line on the receipt.
3. Repeat with Manchester Utd vs Chelsea.

Expected Result: the receipt to display the same home and away team order as the
match list and bet slip:

- Ajax vs AZ Alkmaar
- Manchester Utd vs Chelsea

Actual: the receipt reverses the teams:

- AZ Alkmaar vs Ajax
- Chelsea vs Manchester Utd

The match list and bet slip display the correct order.

Business impact:

The receipt identifies the fixture incorrectly, potentially confusing customers
and weakening the reliability of bet records during disputes or settlement.

Evidence:

See screenshot: [evidence/bug-05-receipt-swap-01.png](evidence/bug-05-receipt-swap-01.png)
See screenshot: [evidence/bug-05-receipt-swap-02.png](evidence/bug-05-receipt-swap-02.png)

---

### BUG-06: Balance is not refreshed after a successful bet

Severity: High

Reproduction steps:

1. Start with €120 in the UI and on the server.
2. Place a €100 bet.
3. Read the header and the bet slip without reloading.
4. Query `GET /api/balance`.

Expected Result: the UI to show the updated balance of €20.00 after the successful bet.

Actual: the UI continued to display €120.00, while the API returned a balance of
€20.00. The stale value remained after closing the receipt and was corrected
only after reloading the page.

Business impact:

Users see an incorrect available balance and may make further betting decisions
based on funds they no longer have.

Evidence:
The UI displayed €120.00 after the bet, while GET /api/balance returned 20.

---

### BUG-07: reset-balance response disagrees with the stored balance

Severity: High

Reproduction steps:

1. Call `POST /api/reset-balance`.
2. Immediately call `GET /api/balance` with a cache-busting query and `cache: "no-store"`.
3. Repeat twice.

Expected Result: the reset endpoint to return the same balance that is stored
and returned by the balance endpoint.

Actual: POST /api/reset-balance consistently returned 125.50, while the
subsequent GET /api/balance returned 120.00.

The inconsistency was reproduced across three consecutive attempts.

Business impact:

Clients relying on the reset response may display or use an incorrect account
balance. This also makes test setup unreliable and can lead to inconsistent
results across test runs.

Evidence:

Three consecutive request pairs:

- POST /api/reset-balance: 125.50
- GET /api/balance: 120.00

---

## 3. Execution summary

| Scenario | Result | Notes |
| --- | --- | --- |
| TC-01 happy path | Fail | Bet places, but receipt payout and team order are wrong, and the balance stays stale |
| TC-02 stake validation | Fail | UI min and max work; API allows overdraft; currency is wrong |
| TC-04 double submit | Fail | Double click creates two bets; no 409 |
| Exploratory past matches | Fail | Past events are selectable and bettable |
| Exploratory filters | Fail | Boundary exclusion, static count, no empty state, invalid range accepted, cap at 10 |
| Exploratory reset | Fail | Response and stored value differ |

## 4. Checks that passed

- Error modal title, body, Rebet, Close, and top-right X matched the specification.
- Rebet retries once per click, does not debit on failure, and succeeds after the simulated failure is removed.
- Close and X both clear the selection and stake without changing the balance.
- Selecting another outcome replaces the previous selection and updates the odds.
- Remove All and the per-selection remove control both clear the bet slip.
- Date filtering works for a single day and for an inclusive date range.
- The API returns 422 for stake 0.99, 1.001, 100.01, a string stake, lowercase selection, blank match ID, and unknown match.
- The API returns 401 when the user header is missing.

## 5. Notes and limitations

- Testing involved bet placement and modified the test account balance. The
  account ended with a negative balance due to the balance-validation defect
  (BUG-02)
- Failure states were simulated by overriding window.fetch in the browser to
  return HTTP 500. The backend was not modified for these checks.
- Screenshots are stored in docs/evidence/ and referenced in the relevant defect
  reports.

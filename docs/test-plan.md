# Test plan: single bet placement

- Manual QA test plan, part A
- Application: Sports Betting QA
- Environment: Desktop Chrome / Edge
- Testing type: Manual black-box testing (UI and API)

---

## 1. Objective

Verify that users can place a single bet, that stake and payout calculations are
correct, and that the account balance is updated only when a bet is successfully
placed.

Testing focuses on financial correctness, input validation, selection handling,
and error scenarios.

---

## 2. Test data and environment

| Ref | Value |
| --- | --- |
| Test User | qa-single-bet-01 |
| Starting balance | €120.00, reset before each scenario that moves money |
| Stake, happy path | €10.00 |
| Minimum stake | €1.00* |
| Typical odds | HOME 2.50 / DRAW 3.40 / AWAY 4.20 |
| Expected payout | 10.00 × 2.50 = €25.00 |
| Balance after success | €110.00 |

*The specification contains conflicting minimum stake values (€1.00 and €1.01).
This plan uses €1.00 as a provisional assumption.

Reset the account balance before scenarios that involve placing bets.

---

## 3. Test scenarios

### TC-01: Successful single bet placement

Priority: Critical

Risk rationale: Bet placement is the main functionality of the application.
Incorrect stake deductions, payout calculations, or confirmation details can
directly affect users financially.

Preconditions: balance reset to €120.00. An upcoming match with known odds is
available.

Steps

1: Open the web url. Select upcoming football match.
2: Select HOME with odds of 2.50.
3: Enter a stake of `10.00` into the stake field.
4: Check the displayed potential payout.
5: Click Place Bet button once.
6: Check the confimation receipt.
7: Close the receipt and check the account balance.

Expected result

- The bet is placed successfully.
- The receipt displays the correct match, selection, odds, stake, payout, Bet ID, and timestamp.
- Potential payout is €25.00, assuming the agreed rounding rule.
- The stake is deducted exactly once.
- The balance changes from €120.00 to €110.00.
- The bet slip is cleared after successful placement.

---

### TC-02: Stake validation and boundary matrix

Priority: Critical

Risk rationale: Incorrect validation can allow invalid bets, unexpected
deductions, or negative account balances. Validation must work in both the UI
and API.

Preconditions: balance €120.00 and a valid selection.

Steps

1. Try entering an empty stake and non-numeric values (abc, 1e2).
2. Try values below the minimum: €0.99 and €0.
3. Try the minimum stake: €1.00 and €1.01.
4. Try values around the maximum: €120.00 and €120.01.
5. Try values with more than two decimal places: €1.005 and €10.999.
6. Set the account balance to €5.00 and try stakes of €5.00 and €5.01.
7. Repeat relevant invalid-value checks directly through the API.

Expected result

- Invalid stakes are rejected with clear validation messages.
- The min and max values are handled correctly, including their boundaries.
- Values with unsupported precision are rejected rather than silently modified.
- A bet exceeding the available balance is rejected.
- A stake equal to the available balance is accepted, leaving a zero balance.
- UI and API enforce the same validation rules.
- Rejected bets do not change the balance or create a receipt.

---

### TC-03: Selection replacement and bet slip handling

Priority: High

Risk rationale: The app supports only one active selection. Incorrect selection
handling could result in users placing bets on an unintended outcome or with
outdated odds.

Preconditions: Match list is loaded and at least one match has all three outcomes available.

Steps

1. Select HOME, then DRAW, then AWAY for the same match.
2. Check the bet slip after each selection.
3. Enter a €10.00 stake and switch to another outcome.
4. Remove the selection using the individual remove button.
5. Select another outcome and click Remove All.
6. Try to place a bet with an empty slip.

Expected result
- Only one selection is present at any time.
- Selecting another outcome replaces the previous selection.
- Odds and potential payout update correctly.
- Removing a selection clears the relevant slip data.
- Remove All clears the entire slip.
- Placing a bet without a selection is not possible.

---

### TC-04: Prevent duplicate bet submissions

Priority: Critical

Risk rationale: Multiple submissions can create duplicate bets and deduct money
more than once. This is particularly important when users click repeatedly or
experience network delays.

Preconditions: User has €120.00 balance, a valid selection, and a €10.00 stake.

Steps

1. Enable network throttling in browser DevTools (optional).
2. Click Place Bet twice quickly.
3. Check the button state and outgoing API requests.
4. Wait for the request to finish.
5. Check the receipt and account balance.
6. Repeat by sending two placement requests simultaneously through the API.

Expected result

- The Place Bet button is disabled while the request is processing.
- Only one bet is successfully created.
- A concurrent duplicate request is rejected with HTTP 409.
- Only one receipt is displayed.
- The account balance is reduced by €10.00, not €20.00.
- The UI and server show consistent bet information.

---

### TC-05: Bet placement failure and recovery 

Priority: High

Risk rationale: Failed transactions must not result in unexpected deductions or
leave the user unable to continue. Retry functionality must also avoid duplicate
transactions. 

Preconditions: User has €120.00 balance, a valid selection, and a €10.00 stake.
Browser DevTools is available to simulate a server error. 

Steps

1. Simulate a failed API response (HTTP 500).
2. Click Place Bet.
3. Check the error modal and available actions.
4. Check the account balance.
5. Click Rebet while the error is still active.
6. Remove the error override and retry.
7. Repeat the failure scenario using Close and the top-right X.

Expected result

- An appropriate error message is displayed.
- The loading state ends after the failed request.
- The error modal provides Rebet and Close actions.
- A failed request does not create a bet or deduct money.
- Rebet retries the same selection and stake.
- A successful retry creates exactly one bet and deducts the stake once.
- Close and X dismiss the modal and clear the selection and stake.
- The balance remains unchanged after unsuccessful attempts.

---

### TC-06: Date and odds filters validation

Priority: Medium

Risk rationale: Incorrect filters can hide available matches or display
misleading results. Boundary values and invalid ranges should be handled
correctly. 

Preconditions: Match data includes different dates and odds values, including
boundary values where available. 

Steps

1. Apply a date filter for a single day.
2. Apply a date range with the same start and end date.
3. Apply a range covering multiple days.
4. Set the minimum and maximum odds to the same value (e.g. 2.50).
5. Set odds to the supported minimum and maximum (1.01 and 1000.00).
6. Enter an invalid range where the minimum is greater than the maximum.
7. Clear all filters.

Expected result

- Date filters include matches on both boundary dates.
- Odds filters include values equal to the selected minimum and maximum.
- Invalid ranges are rejected with clear feedback.
- Clearing filters restores the original match list.
- The displayed match count reflects the filtered results.
- An empty result displays an appropriate message instead of a blank list.

---

## 5. Additional API checks 

The following checks complement the main scenarios and cover cases that cannot be tested through the normal UI:

- Requests without valid authentication return HTTP 401.
- Unsupported HTTP methods return HTTP 405.
- Malformed JSON returns HTTP 400.
- Invalid match IDs and selections return HTTP 422.
- API validation cannot be bypassed by sending requests directly.
- A successful bet response contains the correct stake, odds, payout, balance, and currency.
- Resetting the balance updates the stored balance correctly.
- Concurrent requests do not create duplicate bets.

---

## 8. Open questions and assumptions

During test design, I identified a few areas that need clarification:

| # | Question |
| --- | --- |
| Min stake | Is the minimum €1.00 or €1.01? The specification mentions both. |
| Payout rounding | Should payouts be rounded or truncated to two decimal places? |
| Decimal format | Should the application accept both 10.00 and 10,00? |
| HTTP 409 | What should the user see when another bet request is already in progress? |
| Selection handling | Should the entered stake remain when the user changes the selected outcome? |
| Timestamp | Should the receipt display local time or UTC? |

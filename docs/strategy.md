# Strategy and recommendations

## Why these two tests

I chose these tests because they cover the two most important parts of the
betting flow: placing a valid bet and preventing an invalid one.

UI E2E test: Covers the main user journey, from selecting an outcome and
entering a stake to placing the bet. It verifies the receipt, balance deduction,
and that the bet slip is cleared.

API test: Checks that the backend rejects a bet when the stake exceeds the
available balance and that a rejected bet does not change the balance. This rule
must be enforced by the backend, even if someone bypasses the UI.

Together, these tests cover the main betting flow and an important financial
business rule without making the test suite unnecessarily large.

## What I left for manual testing 

- Duplicate submissions and concurrency: These need reliable control over
  request timing. I would automate them once the backend supports idempotency
  and predictable test conditions.
- Receipt content: The incorrect payout and team order are already documented
  defects. I'll add automated assertions after they are fixed.
- Filters: There are many possible combinations, but they have less impact than
  the core betting flow.
- Error handling and recovery: These are better tested at the component or API
  integration level using controlled error responses.
- Exploratory, visual, and accessibility testing: These still benefit from human
  review, especially when checking layout, usability, and unexpected behaviour.
- Cross-browser testing: Not included because the assignment is limited to the
  main flow in Chrome.

## Recommendations if the project scales

1. Add automated checks to CI/CD. Run linting and API tests on every pull
   request. Run the UI smoke test on merges and on a schedule. Publish test
   results and Allure reports so failures are easy to investigate.

2. Improve test data management. Provide a reliable way to reset balances and
   prepare predictable match data. Use separate test users for parallel runs to
   prevent tests from affecting each other. Add idempotency support to make
   duplicate-submission behaviour easier to test.

3. Expand API and component coverage. Add tests for stake limits, input
   validation, past matches, reset-balance consistency, and API error responses.
   Use component tests with mocked API responses for error modals and recovery
   flows. This provides broader coverage without relying on slow, fragile UI
   tests.

4. Before expanding the suite, I would clarify the minimum stake, payout
   rounding rules, expected behaviour when odds change, the receipt timezone,
   and the expected HTTP status codes for invalid requests and unsupported
   methods. Clear rules make tests more reliable and reduce disagreements about
   whether something is a defect.

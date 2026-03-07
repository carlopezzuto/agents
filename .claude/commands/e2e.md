---
description: Generate and run end-to-end tests with Playwright. Creates test journeys, runs tests, captures screenshots/videos/traces, and uploads artifacts.
---

# E2E Command

This command invokes the **e2e-runner** agent to generate, maintain, and execute end-to-end tests using Playwright for Python.

## What This Command Does

1. **Generate Test Journeys** - Create Playwright tests for user flows
2. **Run E2E Tests** - Execute tests across browsers
3. **Capture Artifacts** - Screenshots, videos, traces on failures
4. **Upload Results** - HTML reports and JUnit XML
5. **Identify Flaky Tests** - Quarantine unstable tests

## When to Use

Use `/e2e` when:

- Testing critical user journeys (login, trading, payments)
- Verifying multi-step flows work end-to-end
- Testing UI interactions and navigation
- Validating integration between frontend and backend
- Preparing for production deployment

## How It Works

The e2e-runner agent will:

1. **Analyze user flow** and identify test scenarios
2. **Generate Playwright test** using Page Object Model pattern
3. **Run tests** across multiple browsers (Chrome, Firefox, Safari)
4. **Capture failures** with screenshots, videos, and traces
5. **Generate report** with results and artifacts
6. **Identify flaky tests** and recommend fixes

## Example Usage

````
User: /e2e Test the market search and view flow

Agent (e2e-runner):
# E2E Test Generation: Market Search and View Flow

## Test Scenario Identified

**User Journey:** Market Search → View Results → Click Market → View Details

**Test Coverage:**
1. Navigate to markets page
2. Perform semantic search
3. Verify search results
4. Click on first result
5. Verify market details page loads
6. Verify chart renders

## Generated Test Code

```python
# tests/e2e/markets/test_search_and_view.py
import pytest
from playwright.sync_api import Page, expect


class MarketsPage:
    """Page Object for Markets page."""

    def __init__(self, page: Page):
        self.page = page
        self.search_input = page.locator('input[placeholder="Search markets"]')
        self.market_cards = page.locator('[data-testid="market-card"]')

    def goto(self):
        self.page.goto("/markets")

    def search_markets(self, query: str):
        self.search_input.fill(query)
        self.page.wait_for_timeout(600)  # Debounce


class MarketDetailsPage:
    """Page Object for Market Details page."""

    def __init__(self, page: Page):
        self.page = page
        self.market_name = page.locator("h1")
        self.market_description = page.locator('[data-testid="market-description"]')
        self.price_chart = page.locator('[data-testid="price-chart"]')


class TestMarketSearchAndViewFlow:
    """E2E tests for market search and view flow."""

    def test_user_can_search_markets_and_view_details(self, page: Page):
        """Complete user journey: search -> view market."""
        # 1. Navigate to markets page
        markets_page = MarketsPage(page)
        markets_page.goto()

        # Verify page loaded
        expect(page).to_have_title(r"Markets")
        expect(page.locator("h1")).to_contain_text("Markets")

        # 2. Perform semantic search
        markets_page.search_markets("election")

        # Wait for API response
        page.wait_for_response(
            lambda resp: "/api/markets/search" in resp.url and resp.status == 200
        )

        # 3. Verify search results
        expect(markets_page.market_cards.first).to_be_visible()
        result_count = markets_page.market_cards.count()
        assert result_count > 0

        # Take screenshot of search results
        page.screenshot(path="artifacts/search-results.png")

        # 4. Click on first result
        first_market_title = markets_page.market_cards.first.text_content()
        markets_page.market_cards.first.click()

        # 5. Verify market details page loads
        expect(page).to_have_url(r"/markets/[a-z0-9-]+")

        details_page = MarketDetailsPage(page)
        expect(details_page.market_name).to_be_visible()
        expect(details_page.market_description).to_be_visible()

        # 6. Verify chart renders
        expect(details_page.price_chart).to_be_visible()

        # Verify market name matches
        details_title = details_page.market_name.text_content()
        assert first_market_title[:20].lower() in details_title.lower()

        # Take screenshot of market details
        page.screenshot(path="artifacts/market-details.png")

    def test_search_with_no_results_shows_empty_state(self, page: Page):
        """Empty search results should show appropriate message."""
        markets_page = MarketsPage(page)
        markets_page.goto()

        # Search for non-existent market
        markets_page.search_markets("xyznonexistentmarket123456")

        # Verify empty state
        no_results = page.locator('[data-testid="no-results"]')
        expect(no_results).to_be_visible()
        expect(no_results).to_contain_text("No markets found")

        market_count = markets_page.market_cards.count()
        assert market_count == 0

    def test_can_clear_search_and_see_all_markets(self, page: Page):
        """Clearing search should show all markets again."""
        markets_page = MarketsPage(page)
        markets_page.goto()

        # Initial market count
        initial_count = markets_page.market_cards.count()

        # Perform search
        markets_page.search_markets("trump")
        page.wait_for_load_state("networkidle")

        # Verify filtered results
        filtered_count = markets_page.market_cards.count()
        assert filtered_count < initial_count

        # Clear search
        markets_page.search_input.clear()
        page.wait_for_load_state("networkidle")

        # Verify all markets shown again
        final_count = markets_page.market_cards.count()
        assert final_count == initial_count
```
````

## Running Tests

```bash
# Run the generated test
pytest tests/e2e/markets/test_search_and_view.py -v

============================= test session starts ==============================
collected 3 items

tests/e2e/markets/test_search_and_view.py::TestMarketSearchAndViewFlow::test_user_can_search_markets_and_view_details PASSED  [ 33%]
tests/e2e/markets/test_search_and_view.py::TestMarketSearchAndViewFlow::test_search_with_no_results_shows_empty_state PASSED  [ 66%]
tests/e2e/markets/test_search_and_view.py::TestMarketSearchAndViewFlow::test_can_clear_search_and_see_all_markets PASSED  [100%]

============================== 3 passed in 9.14s ===============================

Artifacts generated:
- artifacts/search-results.png
- artifacts/market-details.png
- playwright-report/index.html
```

## Test Report

```
╔══════════════════════════════════════════════════════════════╗
║                    E2E Test Results                          ║
╠══════════════════════════════════════════════════════════════╣
║ Status:     ✅ ALL TESTS PASSED                              ║
║ Total:      3 tests                                          ║
║ Passed:     3 (100%)                                         ║
║ Failed:     0                                                ║
║ Flaky:      0                                                ║
║ Duration:   9.1s                                             ║
╚══════════════════════════════════════════════════════════════╝

Artifacts:
📸 Screenshots: 2 files
📹 Videos: 0 files (only on failure)
🔍 Traces: 0 files (only on failure)
📊 HTML Report: playwright-report/index.html

View report: pytest --html=report.html
```

✅ E2E test suite ready for CI/CD integration!

````

## Test Artifacts

When tests run, the following artifacts are captured:

**On All Tests:**
- HTML Report with timeline and results
- JUnit XML for CI integration

**On Failure Only:**
- Screenshot of the failing state
- Video recording of the test
- Trace file for debugging (step-by-step replay)
- Network logs
- Console logs

## Viewing Artifacts

```bash
# View HTML report in browser
playwright show-report

# View specific trace file
playwright show-trace artifacts/trace-abc123.zip

# Screenshots are saved in artifacts/ directory
xdg-open artifacts/search-results.png  # Linux
open artifacts/search-results.png       # macOS
````

## Flaky Test Detection

If a test fails intermittently:

```
⚠️  FLAKY TEST DETECTED: tests/e2e/markets/test_trade.py

Test passed 7/10 runs (70% pass rate)

Common failure:
"Timeout waiting for element '[data-testid="confirm-btn"]'"

Recommended fixes:
1. Add explicit wait: page.wait_for_selector('[data-testid="confirm-btn"]')
2. Increase timeout: expect(locator).to_be_visible(timeout=10000)
3. Check for race conditions in component
4. Verify element is not hidden by animation

Quarantine recommendation: Mark as pytest.mark.skip(reason="flaky") until fixed
```

## Browser Configuration

Tests run on multiple browsers by default:

- ✅ Chromium (Desktop Chrome)
- ✅ Firefox (Desktop)
- ✅ WebKit (Desktop Safari)
- ✅ Mobile Chrome (optional)

Configure in `conftest.py` or `pytest.ini` to adjust browsers.

## CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/e2e.yml
- name: Install Playwright
  run: playwright install --with-deps

- name: Run E2E tests
  run: pytest tests/e2e/ --html=report.html --self-contained-html

- name: Upload artifacts
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: |
      report.html
      artifacts/
```

## Rankle-Specific Critical Flows

For Rankle, prioritize these E2E tests:

**🔴 CRITICAL (Must Always Pass):**

1. User can upload candidate CSV
2. User can upload job description
3. Candidate-job matching executes
4. Rankings display correctly
5. Explainability panel shows reasoning
6. Bias detection alerts display
7. Export results works

**🟡 IMPORTANT:**

1. Skill taxonomy browsing
2. Configuration settings persist
3. Filter and sort candidates
4. Batch processing completes
5. Progress indicators update
6. Error states display correctly

## Best Practices

**DO:**

- ✅ Use Page Object Model for maintainability
- ✅ Use data-testid attributes for selectors
- ✅ Wait for API responses, not arbitrary timeouts
- ✅ Test critical user journeys end-to-end
- ✅ Run tests before merging to main
- ✅ Review artifacts when tests fail

**DON'T:**

- ❌ Use brittle selectors (CSS classes can change)
- ❌ Test implementation details
- ❌ Run tests against production
- ❌ Ignore flaky tests
- ❌ Skip artifact review on failures
- ❌ Test every edge case with E2E (use unit tests)

## Important Notes

**CRITICAL for Rankle:**

- E2E tests involving real data MUST use anonymized test data
- Never run tests with real PII
- Set `pytest.mark.skip` for tests requiring external APIs in CI
- Use fixtures with synthetic candidate/job data only

## Integration with Other Commands

- Use `/plan` to identify critical journeys to test
- Use `/tdd` for unit tests (faster, more granular)
- Use `/e2e` for integration and user journey tests
- Use `/code-review` to verify test quality

## Related Agents

This command invokes the `e2e-runner` agent located at:
`~/.claude/agents/e2e-runner.md`

## Quick Commands

```bash
# Run all E2E tests
pytest tests/e2e/ -v

# Run specific test file
pytest tests/e2e/markets/test_search.py -v

# Run in headed mode (see browser)
pytest tests/e2e/ --headed

# Debug test with Playwright inspector
PWDEBUG=1 pytest tests/e2e/test_example.py -v

# Generate test code interactively
playwright codegen http://localhost:8000

# View HTML report
pytest tests/e2e/ --html=report.html && xdg-open report.html

# Run with trace on failure
pytest tests/e2e/ --tracing=retain-on-failure

# Run specific browser only
pytest tests/e2e/ --browser chromium
pytest tests/e2e/ --browser firefox
pytest tests/e2e/ --browser webkit
```

## Pytest Configuration

```python
# conftest.py for Playwright fixtures
import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for all tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture
def page(context):
    """Create a new page for each test."""
    page = context.new_page()
    yield page
    page.close()
```

## Async Alternative

```python
# tests/e2e/test_async_example.py
import pytest
from playwright.async_api import Page, expect, async_playwright


class TestMarketSearchE2EAsync:
    """Async end-to-end tests using Playwright."""

    @pytest.mark.asyncio
    async def test_user_can_search_and_view_market(self):
        """Complete user journey with async Playwright."""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            await page.goto("http://localhost:8000/")

            # Search for market
            await page.fill('input[placeholder="Search markets"]', "election")
            await page.wait_for_timeout(600)

            # Verify results
            results = page.locator('[data-testid="market-card"]')
            await expect(results).to_have_count(5, timeout=5000)

            # Click first result
            await results.first.click()

            # Verify market page loaded
            await expect(page).to_have_url(r"/markets/")
            await expect(page.locator("h1")).to_be_visible()

            await browser.close()
```

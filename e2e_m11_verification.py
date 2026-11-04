import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("Navigating to MADI TERMINAL...")
        await page.goto("http://localhost:3000")
        await page.wait_for_timeout(3000)

        # 1. Capture Active Chart with Indicator & Timeframe selection
        print("Capturing 1. madi_terminal_chart_active.png...")
        await page.screenshot(path="madi_terminal_chart_active.png")

        # 2. Execute Paper Order (BUY 1.0) and inspect paper positions
        print("Clicking BUY 1.0 and capturing 2. madi_terminal_paper_order.png...")
        await page.click("#btn-buy")
        await page.wait_for_timeout(1000)
        await page.click("#tab-positions")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="madi_terminal_paper_order.png")

        # 3. Strategy Tester Simulation
        print("Running Backtest and capturing 3. madi_terminal_strategy_tester.png...")
        await page.click("#tab-strategy")
        await page.wait_for_timeout(500)
        await page.click("#btn-run-strategy")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="madi_terminal_strategy_tester.png")

        # 4. Strategy Tester List of Trades & History
        print("Opening List of Trades tab and capturing 4. madi_terminal_trades_history.png...")
        await page.click("#tab-trades")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="madi_terminal_trades_history.png")

        await browser.close()
        print("Playwright E2E verification journeys completed successfully!")

if __name__ == "__main__":
    asyncio.run(run())

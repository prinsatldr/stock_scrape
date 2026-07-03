import mysql.connector
from datetime import datetime

from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    page.set_default_timeout(60000)

    page.goto("https://nepalstock.com/today-price")
    page.wait_for_load_state("networkidle")

    # Search company
    textbox = page.get_by_role(
        "textbox",
        name="Stock Symbol or Company Name"
    )

    textbox.wait_for()
    textbox.click()
    textbox.fill("LBBL")

    # Select autocomplete suggestion
    company = page.get_by_role(
        "button",
        name="(LBBL) Lumbini Bikas Bank Ltd."
    )

    company.wait_for()
    company.click()

    # Filter
    filter_btn = page.get_by_role("button", name="Filter")
    filter_btn.wait_for()
    filter_btn.click()

    # Wait until filtered table appears
    rows = page.locator("table tbody tr")
    rows.first.wait_for()

    # First row
    row = rows.first
    cols = row.locator("td")

    trade_date = datetime.now()

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="stock",
        port=3307
    )

    cursor = conn.cursor()

    close_price = float(cols.nth(2).inner_text().replace(",", ""))
    open_price = float(cols.nth(3).inner_text().replace(",", ""))
    high_price = float(cols.nth(4).inner_text().replace(",", ""))
    low_price = float(cols.nth(5).inner_text().replace(",", ""))

    traded_quantity = int(cols.nth(6).inner_text().replace(",", ""))

    traded_value = float(cols.nth(7).inner_text().replace(",", ""))

    total_trades = int(cols.nth(8).inner_text().replace(",", ""))

    ltp = float(cols.nth(9).inner_text().split("(")[0].replace(",", ""))

    previous_close = float(cols.nth(10).inner_text().replace(",", ""))

    # Print scraped data
    for i in range(cols.count()):
        print(i, cols.nth(i).inner_text())

    sql = """
    INSERT INTO stock_history
    (
        trade_date,
        close_price,
        open_price,
        high_price,
        low_price,
        traded_quantity,
        traded_value,
        total_trades,
        ltp,
        previous_close
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    values = (
        trade_date,
        close_price,
        open_price,
        high_price,
        low_price,
        traded_quantity,
        traded_value,
        total_trades,
        ltp,
        previous_close
    )

    cursor.execute(sql, values)
    conn.commit()

    print("Data inserted successfully!")

    cursor.close()
    conn.close()

    browser.close()
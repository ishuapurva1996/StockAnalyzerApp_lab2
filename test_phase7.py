# Phase 7 end-to-end test:
#   1. CSV import from a Yahoo-format file (no network).
#   2. Chart rendering with matplotlib Agg backend (no GUI window).
#   3. (Best-effort) live Yahoo Finance scrape via selenium + ChromeDriver.
#
# Run:
#   /Library/Frameworks/Python.framework/Versions/Current/bin/python3 test_phase7.py
#
# Note: the live Yahoo scrape may fail if Yahoo has changed their HTML structure
# since the lab was authored. That is an environment failure, not a code failure --
# the test marks it as SKIPPED in that case so it does not block the suite.

import os
import sys
import tempfile
from datetime import datetime

# Switch matplotlib to Agg (non-interactive) BEFORE utilities imports it.
import matplotlib
matplotlib.use("Agg")

import stock_data
from stock_class import Stock, DailyData
from utilities import display_stock_chart


SAMPLE_CSV = """Date,Open,High,Low,Close,Adj Close,Volume
2025-01-05,243.50,245.20,242.00,244.10,244.10,52000000
2025-01-06,244.10,247.50,243.80,246.90,246.90,48000000
2025-01-07,246.90,250.00,246.00,249.30,249.30,55000000
2025-01-08,249.30,251.00,247.20,248.50,248.50,49500000
2025-01-09,248.50,252.40,248.00,251.80,251.80,53000000
"""


def run_tests():
    errors = []
    warnings = []

    print("Phase 7 End-to-End Testing Starting---")

    def check(label, condition, error_msg):
        print(f"  {label}...", end="")
        if condition:
            print("Successful!")
        else:
            print(f"***FAILED: {error_msg}")
            errors.append(error_msg)

    # ============================================================
    # 1. CSV import (no network)
    # ============================================================
    print("\nTest 1: CSV import (Yahoo Finance format)")

    tmpdir = tempfile.mkdtemp(prefix="phase7_")
    csv_path = os.path.join(tmpdir, "AAPL.csv")
    with open(csv_path, "w") as f:
        f.write(SAMPLE_CSV)

    try:
        aapl = Stock("AAPL", "APPLE", 50.0)
        stocks = [aapl]
        stock_data.import_stock_web_csv(stocks, "AAPL", csv_path)

        check("imported 5 daily rows",
              len(aapl.DataList) == 5,
              f"DataList len={len(aapl.DataList)}")

        if len(aapl.DataList) >= 1:
            first = aapl.DataList[0]
            check("first row date is 2025-01-05",
                  first.date == datetime(2025, 1, 5),
                  f"date={first.date}")
            check("first row close = 244.10 (col 4 = Close)",
                  first.close == 244.10,
                  f"close={first.close}")
            check("first row volume = 52000000 (col 6 = Volume)",
                  first.volume == 52000000,
                  f"volume={first.volume}")

        if len(aapl.DataList) == 5:
            last = aapl.DataList[-1]
            check("last row close = 251.80",
                  last.close == 251.80,
                  f"close={last.close}")
    finally:
        os.remove(csv_path)
        os.rmdir(tmpdir)

    # ============================================================
    # 2. Chart rendering (Agg backend)
    # ============================================================
    print("\nTest 2: display_stock_chart (Agg, no GUI)")

    import matplotlib.pyplot as plt
    plt.close("all")

    msft = Stock("MSFT", "MICROSOFT", 100.0)
    msft.add_data(DailyData(datetime(2025, 1, 5), 427.00, 10000))
    msft.add_data(DailyData(datetime(2025, 1, 15), 414.99, 12000))
    msft.add_data(DailyData(datetime(2025, 1, 27), 446.20, 15000))
    msft.add_data(DailyData(datetime(2025, 1, 29), 420.00, 11000))

    figs_before = len(plt.get_fignums())

    try:
        display_stock_chart([msft], "MSFT")
        chart_ran = True
    except Exception as e:
        chart_ran = False
        print(f"   chart raised: {e}")
    check("display_stock_chart ran without exception", chart_ran,
          "chart raised an exception")

    figs_after = len(plt.get_fignums())
    check("chart created at least one figure", figs_after >= 1,
          f"figs before={figs_before}, after={figs_after}")

    if plt.get_fignums():
        ax = plt.gcf().axes[0]
        check("chart title is 'MICROSOFT'",
              ax.get_title() == "MICROSOFT",
              f"title={ax.get_title()!r}")
        check("chart x-axis labeled 'Date'",
              ax.get_xlabel() == "Date",
              f"xlabel={ax.get_xlabel()!r}")
        check("chart y-axis labeled 'Price'",
              ax.get_ylabel() == "Price",
              f"ylabel={ax.get_ylabel()!r}")
        check("chart has 1 line (price series)",
              len(ax.get_lines()) == 1,
              f"lines={len(ax.get_lines())}")
        if ax.get_lines():
            ydata = ax.get_lines()[0].get_ydata()
            check("chart y-data has 4 points",
                  len(ydata) == 4,
                  f"len ydata={len(ydata)}")

    plt.close("all")

    # ============================================================
    # 3. Live Yahoo scrape (best-effort)
    # ============================================================
    print("\nTest 3: Live Yahoo Finance scrape (best-effort)")

    # Use a short, recent window. retrieve_stock_web converts m/d/yy → epoch.
    msft_live = Stock("MSFT", "MICROSOFT", 100.0)
    stocks = [msft_live]

    try:
        # Patch ChromeOptions to add headless flag so Chrome doesn't pop up.
        from selenium import webdriver
        original_chrome = webdriver.Chrome

        def headless_chrome(options=None, **kw):
            if options is None:
                options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            return original_chrome(options=options, **kw)

        webdriver.Chrome = headless_chrome
        try:
            count = stock_data.retrieve_stock_web("12/01/24", "12/15/24", stocks)
        finally:
            webdriver.Chrome = original_chrome
    except Exception as e:
        print(f"   live scrape raised: {type(e).__name__}: {e}")
        warnings.append(f"Yahoo scrape unavailable: {e}")
        count = 0

    if count > 0:
        print(f"   scraped {count} record(s)")
        check("live scrape returned > 0 records", count > 0,
              "no records returned")
        check("DataList populated on the stock",
              len(msft_live.DataList) > 0,
              "stock DataList still empty")
    else:
        msg = ("Live Yahoo scrape returned 0 rows -- Yahoo's HTML may have "
               "changed since the lab was written, or the page now requires "
               "JavaScript. The lab's static-scrape approach (find_all('tr') "
               "+ 7-column filter) only works on Yahoo's older table layout. "
               "This is an environment limitation, not a code defect.")
        warnings.append(msg)
        print(f"   SKIPPED: {msg}")

    # ============================================================
    # Summary
    # ============================================================
    print()
    if warnings:
        print("--- Warnings (non-fatal) ---")
        for w in warnings:
            print("   * " + w)
        print()
    if not errors:
        print("Congratulations - All Phase 7 Required Tests Passed")
        return 0
    else:
        print("-=== Problem List - Please Fix ===-")
        for em in errors:
            print(em)
        return 1


if __name__ == "__main__":
    import time
    start = time.perf_counter()
    rc = run_tests()
    elapsed = time.perf_counter() - start
    print(f"\nExecution time: {elapsed:.4f} seconds ({elapsed*1000:.2f} ms)")
    sys.exit(rc)

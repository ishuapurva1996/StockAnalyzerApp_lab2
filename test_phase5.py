# Phase 5 unit test: console add_stock_data, display_report, display_chart.
#
# Run:
#   /Library/Frameworks/Python.framework/Versions/Current/bin/python3 test_phase5.py

import builtins
import io
import sys
import types
from contextlib import redirect_stdout
from datetime import datetime


def _stub_modules():
    for name in [
        "selenium",
        "selenium.webdriver",
        "selenium.webdriver.common",
        "selenium.webdriver.common.keys",
        "bs4",
        "pandas",
        "matplotlib",
        "matplotlib.pyplot",
    ]:
        if name not in sys.modules:
            sys.modules[name] = types.ModuleType(name)
    sys.modules["selenium.webdriver"].ChromeOptions = lambda: types.SimpleNamespace(
        add_experimental_option=lambda *a, **kw: None
    )
    sys.modules["selenium.webdriver"].Chrome = lambda **kw: None
    sys.modules["selenium.webdriver.common.keys"].Keys = type("Keys", (), {})
    sys.modules["bs4"].BeautifulSoup = lambda *a, **kw: None


_stub_modules()

import stock_console
from stock_class import Stock, DailyData


# Silence clear_screen during tests.
stock_console.clear_screen = lambda: None


def call(fn, inputs, *args):
    """Run fn(*args) feeding `inputs` to input(); return captured stdout."""
    real_input = builtins.input
    feed = iter(inputs)
    builtins.input = lambda prompt="": next(feed)
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            fn(*args)
    finally:
        builtins.input = real_input
    return buf.getvalue()


def run_tests():
    errors = []
    print("Phase 5 Unit Testing Starting---")

    def check(label, condition, error_msg):
        print(f"  {label}...", end="")
        if condition:
            print("Successful!")
        else:
            print(f"***FAILED: {error_msg}")
            errors.append(error_msg)

    # ---------------- add_stock_data ----------------
    print("Testing add_stock_data (happy path, 2 entries)...")
    stocks = [Stock("MSFT", "MICROSOFT", 100.0)]
    out = call(
        stock_console.add_stock_data,
        ["MSFT",
         "1/5/25,427.00,10000",
         "1/15/25,414.99,12000",
         ""],  # blank to quit
        stocks,
    )
    check("2 daily records added", len(stocks[0].DataList) == 2,
          f"DataList len={len(stocks[0].DataList)}")
    check("first entry has correct close",
          stocks[0].DataList[0].close == 427.00,
          f"close={stocks[0].DataList[0].close}")
    check("first entry has correct date",
          stocks[0].DataList[0].date == datetime.strptime("1/5/25", "%m/%d/%y"),
          f"date={stocks[0].DataList[0].date}")
    check("first entry has correct volume",
          stocks[0].DataList[0].volume == 10000,
          f"volume={stocks[0].DataList[0].volume}")
    check("second entry has correct close",
          stocks[0].DataList[1].close == 414.99,
          f"close={stocks[0].DataList[1].close}")
    check("output contains 'Ready to add data for'",
          "Ready to add data for" in out,
          "missing prompt header")

    print("Testing add_stock_data (unknown symbol)...")
    stocks = [Stock("MSFT", "MICROSOFT", 100.0)]
    out = call(stock_console.add_stock_data, ["XYZ", ""], stocks)
    check("no data added when symbol unknown",
          len(stocks[0].DataList) == 0,
          "data added despite unknown symbol")
    check("output shows 'not found'", "not found" in out.lower(),
          "missing not-found message")

    print("Testing add_stock_data (invalid line then valid)...")
    stocks = [Stock("MSFT", "MICROSOFT", 100.0)]
    out = call(
        stock_console.add_stock_data,
        ["MSFT",
         "garbage",                    # too few fields
         "1/5/25,abc,10000",           # invalid price
         "1/5/25,427.00,10000",        # valid
         ""],
        stocks,
    )
    check("only valid record added after errors",
          len(stocks[0].DataList) == 1 and stocks[0].DataList[0].close == 427.00,
          f"DataList={[(d.close,) for d in stocks[0].DataList]}")
    check("output flagged invalid data", "Invalid" in out,
          "missing 'Invalid' diagnostic")

    # ---------------- display_report ----------------
    print("Testing display_report (stock with data)...")
    msft = Stock("MSFT", "MICROSOFT", 100.0)
    msft.add_data(DailyData(datetime.strptime("1/5/25", "%m/%d/%y"), 427.00, 10000))
    msft.add_data(DailyData(datetime.strptime("1/15/25", "%m/%d/%y"), 414.99, 12000))
    msft.add_data(DailyData(datetime.strptime("1/27/25", "%m/%d/%y"), 446.20, 15000))
    msft.add_data(DailyData(datetime.strptime("1/29/25", "%m/%d/%y"), 420.00, 11000))
    aapl = Stock("AAPL", "APPLE", 50.0)  # no data
    out = call(stock_console.display_report, [""], [msft, aapl])
    check("report header present", "Stock Report ---" in out, "missing header")
    check("MSFT report line", "MSFT MICROSOFT" in out, f"missing MSFT line: {out!r}")
    check("AAPL report line", "AAPL APPLE" in out, f"missing AAPL line: {out!r}")
    check("AAPL shows '*** No daily history.'",
          "*** No daily history." in out,
          "missing no-history marker for AAPL")
    check("MSFT start price $427.00", "$427.00" in out, "missing start price")
    check("MSFT end price $420.00", "$420.00" in out, "missing end price")
    check("MSFT high $446.20", "$446.20" in out, "missing high price")
    check("MSFT low $414.99", "$414.99" in out, "missing low price")
    # profit = (420.00 - 427.00) * 100 = -700
    check("MSFT profit/loss -$700.00", "-$700.00" in out, "missing profit/loss")
    check("report footer", "--- Report Complete ---" in out, "missing footer")

    # ---------------- display_chart ----------------
    print("Testing display_chart...")
    captured = {}

    def fake_chart(stock_list, symbol):
        captured["stock_list"] = stock_list
        captured["symbol"] = symbol

    real_chart = stock_console.display_stock_chart
    stock_console.display_stock_chart = fake_chart
    try:
        stocks = [Stock("MSFT", "MICROSOFT", 100.0), Stock("AAPL", "APPLE", 50.0)]
        out = call(stock_console.display_chart, ["MSFT"], stocks)
    finally:
        stock_console.display_stock_chart = real_chart

    check("display_chart printed stock list bracket",
          "[MSFT" in out and "AAPL" in out,
          f"output: {out!r}")
    check("display_chart called display_stock_chart with 'MSFT'",
          captured.get("symbol") == "MSFT",
          f"got symbol={captured.get('symbol')!r}")
    check("display_chart passed full stock_list",
          captured.get("stock_list") is stocks,
          "stock_list not forwarded")

    # display_chart with lowercase symbol
    print("Testing display_chart (lowercase input)...")
    captured.clear()
    stock_console.display_stock_chart = fake_chart
    try:
        out = call(stock_console.display_chart, ["msft"], [Stock("MSFT", "MICROSOFT", 100.0)])
    finally:
        stock_console.display_stock_chart = real_chart
    check("symbol uppercased before chart call",
          captured.get("symbol") == "MSFT",
          f"got symbol={captured.get('symbol')!r}")

    print()
    if not errors:
        print("Congratulations - All Phase 5 Tests Passed")
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

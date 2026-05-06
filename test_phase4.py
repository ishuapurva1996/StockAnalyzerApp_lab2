# Phase 4 unit test: console stock management functions.
# Patches input() to feed scripted answers and clear_screen() to a no-op,
# then asserts side effects on stock_list and substrings in captured output.
#
# Run:
#   python3 test_phase4.py

import builtins
import io
import sys
import types
from contextlib import redirect_stdout


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
from stock_class import Stock


# Silence clear_screen during tests.
stock_console.clear_screen = lambda: None


def call(fn, inputs, *args):
    """Run fn(*args) with input() feeding from inputs list. Return captured stdout."""
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
    print("Phase 4 Unit Testing Starting---")

    def check(label, condition, error_msg):
        print(f"  {label}...", end="")
        if condition:
            print("Successful!")
        else:
            print(f"***FAILED: {error_msg}")
            errors.append(error_msg)

    # --- add_stock: add MSFT then stop ---
    print("Testing add_stock...")
    stocks = []
    out = call(
        stock_console.add_stock,
        ["MSFT", "MICROSOFT", "60", "0"],
        stocks,
    )
    check("one stock added", len(stocks) == 1, f"len={len(stocks)}")
    check("symbol is MSFT", stocks[0].symbol == "MSFT", f"symbol={stocks[0].symbol!r}")
    check("name is MICROSOFT", stocks[0].name == "MICROSOFT", f"name={stocks[0].name!r}")
    check("shares is 60.0", stocks[0].shares == 60.0, f"shares={stocks[0].shares}")
    check("output shows 'Add Stock ---'", "Add Stock ---" in out, "missing header")

    # --- add_stock: lower-case input gets uppercased ---
    print("Testing add_stock symbol casing...")
    stocks = []
    call(stock_console.add_stock, ["aapl", "Apple", "10", "0"], stocks)
    check("symbol uppercased", stocks[0].symbol == "AAPL", f"symbol={stocks[0].symbol!r}")

    # --- add_stock: invalid shares are rejected, then valid retry ---
    print("Testing add_stock invalid shares...")
    stocks = []
    call(stock_console.add_stock,
         ["MSFT", "MICROSOFT", "abc", "",  # invalid first attempt + Press Enter
          "MSFT", "MICROSOFT", "60", "0"], # valid second attempt then exit
         stocks)
    check("only valid stock added after retry", len(stocks) == 1 and stocks[0].shares == 60.0,
          f"stocks={[(s.symbol, s.shares) for s in stocks]}")

    # --- buy_stock: increases shares ---
    print("Testing buy_stock...")
    stocks = [Stock("MSFT", "MICROSOFT", 100.0)]
    out = call(stock_console.buy_stock, ["MSFT", "40", ""], stocks)
    check("MSFT shares now 140", stocks[0].shares == 140.0, f"shares={stocks[0].shares}")
    check("output shows 'Buy Shares ---'", "Buy Shares ---" in out, "missing header")
    check("output shows stock list bracket", "[MSFT" in out, "missing list bracket")

    # --- buy_stock: unknown symbol ---
    print("Testing buy_stock unknown symbol...")
    stocks = [Stock("MSFT", "MICROSOFT", 100.0)]
    out = call(stock_console.buy_stock, ["XYZ", ""], stocks)
    check("MSFT shares unchanged", stocks[0].shares == 100.0, f"shares={stocks[0].shares}")
    check("output shows 'not found'", "not found" in out.lower(), "missing not-found message")

    # --- sell_stock: decreases shares ---
    print("Testing sell_stock...")
    stocks = [Stock("MSFT", "MICROSOFT", 100.0)]
    out = call(stock_console.sell_stock, ["MSFT", "25", ""], stocks)
    check("MSFT shares now 75", stocks[0].shares == 75.0, f"shares={stocks[0].shares}")
    check("output shows 'Sell Shares ---'", "Sell Shares ---" in out, "missing header")

    # --- delete_stock: removes target ---
    print("Testing delete_stock...")
    stocks = [Stock("MSFT", "MICROSOFT", 100.0), Stock("AAPL", "APPLE", 50.0)]
    out = call(stock_console.delete_stock, ["MSFT", ""], stocks)
    check("list shrank to 1", len(stocks) == 1, f"len={len(stocks)}")
    check("MSFT gone", all(s.symbol != "MSFT" for s in stocks), "MSFT still present")
    check("AAPL kept", any(s.symbol == "AAPL" for s in stocks), "AAPL missing")
    check("output shows 'Delete Stock ---'", "Delete Stock ---" in out, "missing header")

    # --- delete_stock: unknown symbol ---
    print("Testing delete_stock unknown symbol...")
    stocks = [Stock("MSFT", "MICROSOFT", 100.0)]
    out = call(stock_console.delete_stock, ["XYZ", ""], stocks)
    check("list unchanged", len(stocks) == 1, f"len={len(stocks)}")

    # --- list_stocks: empty ---
    print("Testing list_stocks (empty)...")
    out = call(stock_console.list_stocks, [""], [])
    check("header present", "Stock List" in out and "SYMBOL" in out and "NAME" in out and "SHARES" in out,
          f"missing header columns: {out!r}")

    # --- list_stocks: with stocks ---
    print("Testing list_stocks (with stocks)...")
    stocks = [Stock("MSFT", "MICROSOFT", 100.0), Stock("AAPL", "APPLE", 50.0)]
    out = call(stock_console.list_stocks, [""], stocks)
    check("MSFT row present", "MSFT" in out and "MICROSOFT" in out, f"missing MSFT row: {out!r}")
    check("AAPL row present", "AAPL" in out and "APPLE" in out, f"missing AAPL row: {out!r}")
    check("shares 100.0 shown", "100.0" in out, "missing shares 100.0")

    # --- update_shares menu: Buy then Exit ---
    print("Testing update_shares menu (buy)...")
    stocks = [Stock("MSFT", "MICROSOFT", 100.0)]
    call(stock_console.update_shares,
         ["1", "MSFT", "10", "", "0"],  # 1=Buy, MSFT, 10 shares, press enter, 0=Exit
         stocks)
    check("buy via update_shares menu", stocks[0].shares == 110.0, f"shares={stocks[0].shares}")

    # --- update_shares menu: Sell then Exit ---
    print("Testing update_shares menu (sell)...")
    stocks = [Stock("MSFT", "MICROSOFT", 100.0)]
    call(stock_console.update_shares,
         ["2", "MSFT", "25", "", "0"],  # 2=Sell, MSFT, 25 shares, press enter, 0=Exit
         stocks)
    check("sell via update_shares menu", stocks[0].shares == 75.0, f"shares={stocks[0].shares}")

    # --- update_shares menu: invalid option then exit ---
    print("Testing update_shares menu (invalid then exit)...")
    stocks = [Stock("MSFT", "MICROSOFT", 100.0)]
    call(stock_console.update_shares, ["9", "0"], stocks)  # invalid then exit
    check("invalid option leaves shares alone", stocks[0].shares == 100.0,
          f"shares={stocks[0].shares}")

    print()
    if not errors:
        print("Congratulations - All Phase 4 Tests Passed")
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

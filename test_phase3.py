# Phase 3 smoke test: verifies delete_stock() and report rendering in display_stock_data().
# Run with a Python that has tkinter:
#   /Library/Frameworks/Python.framework/Versions/Current/bin/python3 test_phase3.py

import sys
import types
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

import tkinter

tkinter.Tk.mainloop = lambda self: None

import stock_GUI
from stock_class import Stock, DailyData


def run_tests():
    errors = []
    print("Phase 3 Unit Testing Starting---")

    print("Constructing StockApp...", end="")
    try:
        app = stock_GUI.StockApp()
        print("Successful!")
    except Exception as e:
        print(f"***FAILED: {e}")
        return 1
    app.root.withdraw()

    def check(label, condition, error_msg):
        print(f"  {label}...", end="")
        if condition:
            print("Successful!")
        else:
            print(f"***FAILED: {error_msg}")
            errors.append(error_msg)

    # --- Seed two stocks: MSFT (with data) and AAPL (no data) ---
    msft = Stock("MSFT", "MICROSOFT", 100.0)
    msft.add_data(DailyData(datetime.strptime("01/05/25", "%m/%d/%y"), 427.00, 10000))  # start
    msft.add_data(DailyData(datetime.strptime("01/15/25", "%m/%d/%y"), 414.99, 12000))  # low
    msft.add_data(DailyData(datetime.strptime("01/27/25", "%m/%d/%y"), 446.20, 15000))  # high
    msft.add_data(DailyData(datetime.strptime("01/29/25", "%m/%d/%y"), 420.00, 11000))  # end (loss)
    aapl = Stock("AAPL", "APPLE", 50.0)
    app.stock_list.extend([msft, aapl])
    app.stockList.insert("end", "MSFT")
    app.stockList.insert("end", "AAPL")

    # --- Test report rendering for stock WITH data ---
    print("Testing report rendering (stock with data)...")
    app.stockList.selection_clear(0, "end")
    app.stockList.selection_set(0)  # MSFT
    app.display_stock_data()
    report = app.stockReport.get("1.0", "end")
    check("report contains symbol+name", "MSFT MICROSOFT" in report,
          f"missing 'MSFT MICROSOFT' in: {report!r}")
    check("report contains shares", "100.0" in report, f"missing shares in: {report!r}")
    check("report shows start price $427.00", "$427.00" in report,
          f"missing start price in: {report!r}")
    check("report shows end price $420.00", "$420.00" in report,
          f"missing end price in: {report!r}")
    check("report shows high $446.20", "$446.20" in report,
          f"missing high price in: {report!r}")
    check("report shows low $414.99", "$414.99" in report,
          f"missing low price in: {report!r}")
    # profit/loss = (420.00 - 427.00) * 100 = -700.00
    check("report shows profit/loss -$700.00", "-$700.00" in report,
          f"missing profit/loss in: {report!r}")
    check("report ends with 'Report Complete'", "Report Complete" in report,
          f"missing footer in: {report!r}")

    history = app.dailyDataList.get("1.0", "end")
    check("history shows all 4 daily rows",
          history.count("\n") >= 6,  # 2 header lines + 4 data lines
          f"history line count too low: {history!r}")

    # --- Test report rendering for stock WITHOUT data ---
    print("Testing report rendering (stock with no data)...")
    app.stockList.selection_clear(0, "end")
    app.stockList.selection_set(1)  # AAPL
    app.display_stock_data()
    report = app.stockReport.get("1.0", "end")
    check("empty-data report contains symbol", "AAPL APPLE" in report,
          f"missing AAPL APPLE in: {report!r}")
    check("empty-data report shows '*** No daily history.'",
          "*** No daily history." in report,
          f"missing no-history marker in: {report!r}")

    # --- Test delete_stock with confirm=YES ---
    print("Testing delete_stock (confirm yes)...")
    # Patch askyesno to auto-confirm
    stock_GUI.messagebox.askyesno = lambda *a, **kw: True
    app.stockList.selection_clear(0, "end")
    app.stockList.selection_set(1)  # AAPL
    before_len = len(app.stock_list)
    before_listbox = app.stockList.size()
    app.delete_stock()
    check("stock_list shrank by 1",
          len(app.stock_list) == before_len - 1,
          f"stock_list len {len(app.stock_list)} (expected {before_len - 1})")
    check("listbox shrank by 1",
          app.stockList.size() == before_listbox - 1,
          f"listbox size {app.stockList.size()} (expected {before_listbox - 1})")
    check("AAPL removed from stock_list",
          all(s.symbol != "AAPL" for s in app.stock_list),
          "AAPL still in stock_list")

    # --- Test delete_stock with confirm=NO ---
    print("Testing delete_stock (confirm no)...")
    stock_GUI.messagebox.askyesno = lambda *a, **kw: False
    app.stockList.selection_clear(0, "end")
    app.stockList.selection_set(0)  # MSFT
    before_len = len(app.stock_list)
    app.delete_stock()
    check("stock_list unchanged when user cancels",
          len(app.stock_list) == before_len,
          f"stock_list shrank despite cancel ({len(app.stock_list)} vs {before_len})")

    # --- Test delete_stock with no selection ---
    print("Testing delete_stock (no selection)...")
    stock_GUI.messagebox.showwarning = lambda *a, **kw: None
    app.stockList.selection_clear(0, "end")
    before_len = len(app.stock_list)
    app.delete_stock()
    check("no-selection delete is a no-op",
          len(app.stock_list) == before_len,
          f"stock_list shrank without selection ({len(app.stock_list)} vs {before_len})")

    app.root.destroy()

    print()
    if not errors:
        print("Congratulations - All Phase 3 Tests Passed")
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

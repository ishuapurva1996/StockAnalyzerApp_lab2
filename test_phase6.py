# Phase 6 unit test: console manage_data, retrieve_from_web, import_csv.
#
# Run:
#   /Library/Frameworks/Python.framework/Versions/Current/bin/python3 test_phase6.py

import builtins
import io
import os
import sys
import tempfile
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
import stock_data
from stock_class import Stock, DailyData


stock_console.clear_screen = lambda: None


def call(fn, inputs, *args):
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
    print("Phase 6 Unit Testing Starting---")

    def check(label, condition, error_msg):
        print(f"  {label}...", end="")
        if condition:
            print("Successful!")
        else:
            print(f"***FAILED: {error_msg}")
            errors.append(error_msg)

    # ---------------- manage_data menu dispatch ----------------
    print("Testing manage_data menu (Save dispatch)...")
    saved_with = []
    loaded_with = []
    real_save = stock_data.save_stock_data
    real_load = stock_data.load_stock_data
    stock_data.save_stock_data = lambda lst: saved_with.append(lst)
    stock_data.load_stock_data = lambda lst: loaded_with.append(lst)
    try:
        stocks = [Stock("MSFT", "MICROSOFT", 100.0)]
        out = call(stock_console.manage_data, ["1", "", "0"], stocks)
        check("save_stock_data invoked once",
              len(saved_with) == 1 and saved_with[0] is stocks,
              f"saved_with={saved_with}")
        check("output shows 'Data Saved'",
              "Data Saved to Database" in out, "missing save confirmation")

        print("Testing manage_data menu (Load dispatch)...")
        out = call(stock_console.manage_data, ["2", "", "0"], stocks)
        check("load_stock_data invoked",
              len(loaded_with) == 1 and loaded_with[0] is stocks,
              f"loaded_with={loaded_with}")
        check("output shows 'Data Loaded'",
              "Data Loaded from Database" in out, "missing load confirmation")
    finally:
        stock_data.save_stock_data = real_save
        stock_data.load_stock_data = real_load

    print("Testing manage_data menu (invalid then exit)...")
    saved_with = []
    stock_data.save_stock_data = lambda lst: saved_with.append(lst)
    try:
        out = call(stock_console.manage_data, ["9", "0"], [Stock("MSFT", "MICROSOFT", 100.0)])
        check("invalid option does not save",
              len(saved_with) == 0, f"saved_with={saved_with}")
    finally:
        stock_data.save_stock_data = real_save

    # ---------------- retrieve_from_web ----------------
    print("Testing retrieve_from_web (success)...")
    seen_args = {}
    real_retrieve = stock_data.retrieve_stock_web
    def fake_retrieve(start, end, lst):
        seen_args["start"] = start
        seen_args["end"] = end
        seen_args["list"] = lst
        return 17
    stock_data.retrieve_stock_web = fake_retrieve
    try:
        stocks = [Stock("MSFT", "MICROSOFT", 100.0)]
        out = call(stock_console.retrieve_from_web,
                   ["01/05/25", "01/31/25", ""], stocks)
        check("retrieve_stock_web called with start date",
              seen_args.get("start") == "01/05/25",
              f"start={seen_args.get('start')!r}")
        check("retrieve_stock_web called with end date",
              seen_args.get("end") == "01/31/25",
              f"end={seen_args.get('end')!r}")
        check("retrieve_stock_web received stock_list",
              seen_args.get("list") is stocks,
              "stock_list not forwarded")
        check("output shows 'Records Retrieved:  17'",
              "Records Retrieved" in out and "17" in out,
              f"output: {out!r}")
    finally:
        stock_data.retrieve_stock_web = real_retrieve

    print("Testing retrieve_from_web (driver missing)...")
    def raise_warning(*a, **kw):
        raise RuntimeWarning("Chrome Driver Not Found")
    stock_data.retrieve_stock_web = raise_warning
    try:
        stocks = [Stock("MSFT", "MICROSOFT", 100.0)]
        out = call(stock_console.retrieve_from_web,
                   ["01/05/25", "01/31/25", ""], stocks)
        check("driver missing produces error message",
              "Cannot Get Data from Web" in out or "Chrome Driver" in out,
              f"output: {out!r}")
    finally:
        stock_data.retrieve_stock_web = real_retrieve

    # ---------------- import_csv ----------------
    print("Testing import_csv...")
    seen = {}
    real_import = stock_data.import_stock_web_csv
    def fake_import(lst, symbol, filename):
        seen["list"] = lst
        seen["symbol"] = symbol
        seen["filename"] = filename
    stock_data.import_stock_web_csv = fake_import
    try:
        stocks = [Stock("AAPL", "APPLE", 50.0)]
        out = call(stock_console.import_csv,
                   ["AAPL", "/tmp/AAPL.csv", ""], stocks)
        check("import_stock_web_csv called with symbol",
              seen.get("symbol") == "AAPL", f"symbol={seen.get('symbol')!r}")
        check("import_stock_web_csv called with filename",
              seen.get("filename") == "/tmp/AAPL.csv",
              f"filename={seen.get('filename')!r}")
        check("import_stock_web_csv received stock_list",
              seen.get("list") is stocks, "stock_list not forwarded")
        check("output shows 'CSV File Imported'",
              "CSV File Imported" in out, f"output: {out!r}")
    finally:
        stock_data.import_stock_web_csv = real_import

    # ---------------- Save / Load round-trip (real sqlite) ----------------
    print("Testing save -> load round-trip in temp directory...")
    cwd_before = os.getcwd()
    tmpdir = tempfile.mkdtemp(prefix="phase6_")
    try:
        os.chdir(tmpdir)
        stock_data.create_database()

        # build a stock with some daily data and persist
        msft = Stock("MSFT", "MICROSOFT", 100.0)
        msft.add_data(DailyData(datetime.strptime("01/05/25", "%m/%d/%y"), 427.00, 10000))
        msft.add_data(DailyData(datetime.strptime("01/15/25", "%m/%d/%y"), 414.99, 12000))
        original = [msft]
        stock_data.save_stock_data(original)

        # load into a fresh list via manage_data option 2
        loaded = []
        out = call(stock_console.manage_data, ["2", "", "0"], loaded)

        check("loaded list contains 1 stock", len(loaded) == 1,
              f"len={len(loaded)}")
        if loaded:
            check("loaded symbol is MSFT", loaded[0].symbol == "MSFT",
                  f"symbol={loaded[0].symbol!r}")
            check("loaded shares preserved", loaded[0].shares == 100.0,
                  f"shares={loaded[0].shares}")
            check("loaded daily data has 2 rows",
                  len(loaded[0].DataList) == 2,
                  f"DataList len={len(loaded[0].DataList)}")
            if len(loaded[0].DataList) == 2:
                # data should be sorted by date after load_stock_data
                sorted_loaded = sorted(loaded[0].DataList, key=lambda d: d.date)
                check("first loaded close = 427.00",
                      sorted_loaded[0].close == 427.00,
                      f"close={sorted_loaded[0].close}")
                check("second loaded close = 414.99",
                      sorted_loaded[1].close == 414.99,
                      f"close={sorted_loaded[1].close}")
        check("manage_data load printed confirmation",
              "Data Loaded from Database" in out,
              "missing load confirmation")
    finally:
        os.chdir(cwd_before)
        # cleanup
        for f in os.listdir(tmpdir):
            os.remove(os.path.join(tmpdir, f))
        os.rmdir(tmpdir)

    print()
    if not errors:
        print("Congratulations - All Phase 6 Tests Passed")
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

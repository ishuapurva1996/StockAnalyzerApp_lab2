# Phase 2 smoke test: verifies stock_GUI.StockApp builds the expected widget tree.
# Run with a Python that has tkinter:  /usr/bin/python3 test_phase2.py

import sys
import types


# Stub third-party imports so the test runs without selenium / bs4 / pandas / matplotlib installed.
# (Phase 2 only tests the GUI scaffolding, not web scraping or charting.)
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

# Disable the blocking mainloop so __init__ returns control to us.
tkinter.Tk.mainloop = lambda self: None

import stock_GUI


def run_tests():
    errors = []

    print("Phase 2 Unit Testing Starting---")

    # Build the app
    print("Constructing StockApp...", end="")
    try:
        app = stock_GUI.StockApp()
        print("Successful!")
    except Exception as e:
        print(f"***FAILED: {e}")
        return 1

    # Hide the window so it doesn't flash on screen
    app.root.withdraw()

    def check(label, condition, error_msg):
        print(f"  {label}...", end="")
        if condition:
            print("Successful!")
        else:
            print(f"***FAILED: {error_msg}")
            errors.append(error_msg)

    # --- Required widget attributes ---
    print("Checking widget attributes...")
    required_widgets = [
        ("headingLabel", tkinter.Label),
        ("stockList", tkinter.Listbox),
        ("addSymbolEntry", tkinter.Entry),
        ("addNameEntry", tkinter.Entry),
        ("addSharesEntry", tkinter.Entry),
        ("updateSharesEntry", tkinter.Entry),
        ("dailyDataList", tkinter.Text),
        ("stockReport", tkinter.Text),
    ]
    for name, expected_type in required_widgets:
        widget = getattr(app, name, None)
        check(
            f"self.{name} is {expected_type.__name__}",
            isinstance(widget, expected_type),
            f"self.{name} missing or wrong type (got {type(widget).__name__})",
        )

    # --- Menubar with File / Web / Chart cascades ---
    print("Checking menubar...")
    menubar = app.root.cget("menu")
    check("root has menubar attached", menubar != "", "root.config(menu=...) was not called")

    expected_menus = ["File", "Web", "Chart"]
    actual_menus = []
    for i in range(app.menubar.index("end") + 1 if app.menubar.index("end") is not None else 0):
        try:
            actual_menus.append(app.menubar.entrycget(i, "label"))
        except tkinter.TclError:
            pass
    for menu_label in expected_menus:
        check(
            f"menubar has '{menu_label}' cascade",
            menu_label in actual_menus,
            f"menubar missing '{menu_label}' (found {actual_menus})",
        )

    # --- File menu items ---
    file_items = []
    end = app.filemenu.index("end")
    if end is not None:
        for i in range(end + 1):
            try:
                file_items.append(app.filemenu.entrycget(i, "label"))
            except tkinter.TclError:
                file_items.append("<separator>")
    check(
        "File menu has Load, Save, Exit",
        any("Load" in s for s in file_items)
        and any("Save" in s for s in file_items)
        and any("Exit" in s for s in file_items),
        f"File menu items unexpected: {file_items}",
    )

    # --- Web menu items ---
    web_items = []
    end = app.webmenu.index("end")
    if end is not None:
        for i in range(end + 1):
            try:
                web_items.append(app.webmenu.entrycget(i, "label"))
            except tkinter.TclError:
                web_items.append("<separator>")
    check(
        "Web menu has Scrape and Import CSV",
        any("Scrape" in s for s in web_items) and any("Import" in s and "CSV" in s for s in web_items),
        f"Web menu items unexpected: {web_items}",
    )

    # --- Chart menu items ---
    chart_items = []
    end = app.chartmenu.index("end")
    if end is not None:
        for i in range(end + 1):
            try:
                chart_items.append(app.chartmenu.entrycget(i, "label"))
            except tkinter.TclError:
                chart_items.append("<separator>")
    check(
        "Chart menu has at least one item",
        len(chart_items) >= 1,
        f"Chart menu items unexpected: {chart_items}",
    )

    # --- ttk.Notebook with Main / History / Report tabs ---
    print("Checking notebook tabs...")
    tab_labels = [app.tabs.tab(i, option="text") for i in range(len(app.tabs.tabs()))]
    for expected in ["Main", "History", "Report"]:
        check(
            f"notebook has '{expected}' tab",
            expected in tab_labels,
            f"notebook missing '{expected}' (found {tab_labels})",
        )

    # --- ListboxSelect binding ---
    print("Checking event bindings...")
    binding = app.stockList.bind("<<ListboxSelect>>")
    check(
        "stockList is bound to <<ListboxSelect>>",
        binding != "",
        "stockList missing <<ListboxSelect>> binding",
    )

    # Clean up
    app.root.destroy()

    print()
    if not errors:
        print("Congratulations - All Phase 2 Tests Passed")
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

# DATA-200 Lab 2 — Stock Analysis

**Status: ✅ Complete — all 7 phases implemented, 125/125 tests passing, report and class diagram generated.**

This document is the canonical project tracker. It records the skills demonstrated, the phased build plan with checkpoints, the Lab-2 deliverables table, the per-phase test summary, every artifact in the project folder, and the environment used.

---

## Skills Demonstrated

### Python language & OOP
- [x] Class design with `@property` getters/setters (`Stock`, `DailyData`)
- [x] Encapsulation: blocking direct mutation of `symbol` and `shares`
- [x] Module organization across `stock_class.py`, `stock_data.py`, `stock_GUI.py`, `stock_console.py`, `utilities.py`
- [x] List sorting with `key=lambda` (alphabetical stocks, chronological data)
- [x] Date handling with `datetime.strptime` / `strftime` and `time.mktime`
- [x] IS-A / HAS-A modelling — diagrammed in `class_diagram.png` / `class_diagram.drawio`

### Data persistence
- [x] SQLite via `sqlite3` — schema creation, INSERT, SELECT, composite primary key
- [x] CSV import via the `csv` module (`csv.reader`, `next()` to skip header)

### Web scraping (Lab 2 focus)
- [x] Browser automation with `selenium` + ChromeDriver (auto-managed by Selenium Manager — selenium 4.43)
- [x] Setting Chrome options (`excludeSwitches`, disabling JavaScript prefs, `--headless=new` for tests)
- [x] HTML parsing with `BeautifulSoup` — `find('table')`, `find_all('tr')`, `find_all('td')`
- [x] Building Yahoo! Finance history URLs from epoch-second date ranges
- [x] Filtering rows by column count to ignore dividends / splits
- [x] Live verified: pulled 10 MSFT records 12/01/24 – 12/15/24 in Phase 7

### GUI (tkinter)
- [x] Menubar with cascading menus (File / Web / Chart)
- [x] `Listbox` with `<<ListboxSelect>>` event binding
- [x] `ttk.Notebook` tabs (Main / History / Report)
- [x] Dialog boxes: `messagebox`, `simpledialog.askstring`, `filedialog.askopenfilename`

### Console UI
- [x] Menu-driven loops with input validation (Manage Stocks, Update Shares, Manage Data)
- [x] Formatted output with `str.format` / f-strings (table headers, signed `-$X,XXX.XX` profit/loss)

### Visualization
- [x] Line charts with `matplotlib.pyplot` (interactive default backend + Agg in tests)

### Testing
- [x] Per-phase test files (`test_phase1.py` … `test_phase7.py`) — 125 assertions total
- [x] Execution-time reporting on every test run (`Execution time: X.XXXX seconds`)
- [x] tkinter mainloop patching for headless GUI tests
- [x] Real SQLite save→load round-trip (Phase 6)
- [x] matplotlib Agg backend for headless chart verification (Phase 7)

---

## Build Plan (Phased)

### Phase 1 — Core helpers ✅
- [x] `utilities.py`: `sortStocks`, `sortDailyData`, `display_stock_chart`
- [x] **Checkpoint:** `test_phase1.py` (wraps `stock_class.main()` with timing) — 7 assertions pass

### Phase 2 — GUI scaffolding
- [x] `stock_GUI.py` `__init__`: menubar, File / Web / Chart menus
- [x] Heading label, stock `Listbox` (`self.stockList`)
- [x] `ttk.Notebook` with Main / History / Report tabs
- [x] Main tab: Add Stock (`addSymbolEntry`, `addNameEntry`, `addSharesEntry` + Add button)
- [x] Main tab: Update Shares (`updateSharesEntry` + Buy / Sell buttons)
- [x] Main tab: Delete Stock button
- [x] History tab: `dailyDataList` Text widget
- [x] Report tab: `stockReport` Text widget
- [x] **Checkpoint:** `test_phase2.py` smoke test passes (all 19 widget/menu/tab/binding checks)

### Phase 3 — GUI completion
- [x] `delete_stock(self)` — confirm dialog, remove from list + listbox
- [x] Report rendering inside `display_stock_data()` (start/end/high/low/profit-loss)
- [x] **Checkpoint:** `test_phase3.py` smoke test passes (17 report/delete_stock assertions)

### Phase 4 — Console stock management
- [x] `add_stock`, `update_shares`, `buy_stock`, `sell_stock`, `delete_stock`, `list_stocks`
- [x] **Checkpoint:** `test_phase4.py` smoke test passes (25 console-flow assertions)

### Phase 5 — Console data entry, report, chart
- [x] `add_stock_data` — comma-separated daily entry loop
- [x] `display_report` — per-stock summary
- [x] `display_chart` — picks symbol then calls `display_stock_chart`
- [x] **Checkpoint:** `test_phase5.py` smoke test passes (23 data-entry/report/chart assertions)

### Phase 6 — Console Lab 2 hooks
- [x] `manage_data` menu (Save / Load / Retrieve from Web / Import CSV)
- [x] `retrieve_from_web` — date prompts → `stock_data.retrieve_stock_web`
- [x] `import_csv` — symbol + filename prompts → `stock_data.import_stock_web_csv`
- [x] **Checkpoint:** `test_phase6.py` smoke test passes (20 menu/dispatch/round-trip assertions, including real SQLite save→load)

### Phase 7 — ChromeDriver setup & end-to-end
- [x] ~~Install matching ChromeDriver into `lab2/`~~ — superseded by Selenium Manager (selenium 4.10+ auto-downloads matching driver)
- [x] ~~Add lab2 folder to `PATH`~~ — not needed with Selenium Manager
- [x] `pip install selenium beautifulsoup4 pandas matplotlib` — installed selenium 4.43, bs4 4.14, matplotlib 3.10 (pandas 3.0 already present)
- [x] **Live web test:** `retrieve_stock_web("12/01/24", "12/15/24", [MSFT])` returned 10 records from Yahoo Finance (headless Chrome 147)
- [x] **CSV test:** `import_stock_web_csv` parses Yahoo-format CSV → 5 DailyData rows with correct date/close/volume columns
- [x] **Chart test:** `display_stock_chart` (Agg backend) renders MSFT line with title, axis labels, and 4 data points
- [x] **Checkpoint:** `test_phase7.py` smoke test passes (14 end-to-end assertions)

---

## Lab 2 Deliverables (from PDF §1–2)

| Function | File | Status |
|---|---|---|
| `retrieve_stock_web(dateStart, dateEnd, stock_list)` | `stock_data.py` | ✅ implemented & live-tested (10 MSFT rows scraped) |
| `import_stock_web_csv(stock_list, symbol, filename)` | `stock_data.py` | ✅ implemented & tested (5/21 row sample CSV) |
| `scrape_web_data(self)` | `stock_GUI.py` | ✅ implemented (smoke-tested via test_phase2) |
| `importCSV_web_data(self)` | `stock_GUI.py` | ✅ implemented (smoke-tested via test_phase2) |
| `retrieve_from_web(stock_list)` | `stock_console.py` | ✅ implemented & tested (Phase 6) |
| `import_csv(stock_list)` | `stock_console.py` | ✅ implemented & tested (Phase 6) |

---

## Test Suite Summary

| Phase | File | Assertions | What it covers |
|---|---|---:|---|
| 1 | `test_phase1.py` | 7 | `Stock` / `DailyData` class behaviour (immutability, buy/sell, daily data) |
| 2 | `test_phase2.py` | 19 | GUI scaffolding — widgets, menus, notebook tabs, listbox binding |
| 3 | `test_phase3.py` | 17 | Report rendering (start/end/high/low/profit-loss); `delete_stock` confirm flow |
| 4 | `test_phase4.py` | 25 | Console add/buy/sell/delete/list flows + `update_shares` submenu |
| 5 | `test_phase5.py` | 23 | `add_stock_data` parser; `display_report`; `display_chart` symbol forwarding |
| 6 | `test_phase6.py` | 20 | `manage_data` dispatch; `retrieve_from_web`; `import_csv`; **real SQLite round-trip** |
| 7 | `test_phase7.py` | 14 | CSV parse + chart figure + **live Yahoo scrape** end-to-end |
| **Total** |  | **125** | All passing |

Run any single phase:
```bash
/Library/Frameworks/Python.framework/Versions/Current/bin/python3 test_phase<N>.py
```
Run all seven in sequence:
```bash
PY=/Library/Frameworks/Python.framework/Versions/Current/bin/python3
for n in 1 2 3 4 5 6 7; do "$PY" test_phase$n.py | tail -2; done
```

Every test prints `Execution time: X.XXXX seconds (X.XX ms)` on the last line.

---

## Artifacts & Files

### Lab source files (deliverables)
- `stock_class.py` — `Stock`, `DailyData` (with built-in unit tests in `main()`)
- `utilities.py` — `clear_screen`, `sortStocks`, `sortDailyData`, `display_stock_chart`
- `stock_data.py` — SQLite save/load, `retrieve_stock_web`, `import_stock_web_csv`
- `stock_GUI.py` — `StockApp` tkinter controller (menubar, listbox, notebook, all handlers)
- `stock_console.py` — Console menus and Lab-2 hooks
- `stocks.py` — Single entry point that launches GUI or console

### Test files
- `test_phase1.py` … `test_phase7.py` — see Test Suite Summary above

### Sample data
- `AAPL.csv` — 21-row Yahoo-format CSV (Jan 2025) for the Import-CSV demos

### Documentation
- `SKILLS.md` — this file
- `Lab2_Report.docx` — submission-ready report (cover + class diagram + 23 screenshot placeholders + per-phase test sections)
- `class_diagram.png` — UML class diagram embedded in the report
- `class_diagram.drawio` — editable diagram for [app.diagrams.net](https://app.diagrams.net)
- `SJSU_Lab2_Stock_Analysis.pdf` — the original lab handout (reference)

### Generators (re-runnable)
- `build_diagram.py` — regenerates `class_diagram.png` and `class_diagram.drawio`
- `build_report.py` — regenerates `Lab2_Report.docx` (auto-embeds the PNG)

---

## Environment

| Component | Version | Notes |
|---|---|---|
| Python | 3.13.5 | Use `/Library/Frameworks/Python.framework/Versions/Current/bin/python3` (Homebrew Python lacks tkinter) |
| Chrome | 147.0.7727.138 | |
| selenium | 4.43.0 | Selenium Manager auto-downloads matching ChromeDriver — no manual install or PATH edit needed |
| beautifulsoup4 | 4.14.3 | |
| matplotlib | 3.10.9 | Agg backend used in tests; default backend for live charts |
| pandas | 3.0.2 | |
| python-docx | latest | Used only by `build_report.py` |

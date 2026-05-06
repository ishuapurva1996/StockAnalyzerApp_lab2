# Stock Analyzer (DATA 200 Lab 2)

Python stock portfolio manager with **tkinter GUI** and **console** interfaces, **SQLite** persistence, **Yahoo! Finance** scraping (Selenium + BeautifulSoup) and CSV import, and **matplotlib** price charts.

Submitted for SJSU DATA 200 — Lab 2.

## Features

- Track multiple stocks (symbol, company name, share count) with buy / sell operations
- Two ways to load price history:
  - Web scraping from `finance.yahoo.com/quote/<SYM>/history` via Selenium + BeautifulSoup
  - CSV import in Yahoo! Finance format
- SQLite save/load (`stocks.db`) with composite primary key on `(symbol, date)` so re-imports are idempotent
- Per-stock report: start / end / high / low and signed profit-loss
- Line chart of close price vs. date (matplotlib)
- 125 unit-test assertions across 7 phases — all passing

## Project Structure

```
stocks.py              # Entry point — launches GUI (or console)
stock_class.py         # Stock and DailyData classes
stock_data.py          # SQLite save/load, web scrape, CSV import
stock_console.py       # Console UI
stock_GUI.py           # Tkinter GUI
utilities.py           # sortStocks, sortDailyData, display_stock_chart, clear_screen

test_phase1.py ... test_phase7.py   # Unit tests (run individually or all)

AAPL.csv               # Sample Yahoo! Finance CSV for CSV-import demo
class_diagram.png      # UML class diagram (IS-A and HAS-A relationships)
class_diagram.drawio   # Editable diagram source
Lab2_Report.docx       # Full lab report with screenshots and unit-test results
```

## Requirements

- Python 3.10+ with `tkinter` and `matplotlib` (the macOS framework Python at
  `/Library/Frameworks/Python.framework/Versions/Current/bin/python3` ships with both)
- Selenium 4+ (with Chrome installed) — required only for web scraping
- BeautifulSoup 4

```bash
pip install selenium beautifulsoup4 pandas matplotlib
```

## Usage

```bash
python3 stocks.py
```

By default this launches the **GUI** version. To use the console version, edit `stocks.py` and switch which line is commented:

```python
# stock_console.py    # console version
stock_GUI.main()      # GUI version (default)
```

### GUI workflow

1. **Add Stock** — enter a symbol, company name, and share count.
2. Select the stock in the listbox.
3. **Web → Scrape Data from Yahoo! Finance…** — enter date range (`m/d/yy`) to pull daily history.
   *Or* **Web → Import CSV From Yahoo! Finance…** — pick a Yahoo CSV file.
4. **History** and **Report** tabs render the daily data and summary.
5. **Chart → Display Stock Chart…** — opens a matplotlib line chart.
6. **File → Save Data…** / **Load Data…** — persists to / restores from `stocks.db`.

### Console workflow

The console version exposes the same operations through numbered menus (`Manage Stocks`, `Add Daily Stock Data`, `Show Report`, `Show Chart`, `Manage Data`).

## Running Tests

Each phase covers a discrete part of the implementation:

| Phase | What is tested | Assertions |
|---|---|---|
| 1 | `Stock` and `DailyData` classes | 7 |
| 2 | GUI scaffolding (widgets, menus, tabs) | 19 |
| 3 | GUI completion — delete, report rendering | 17 |
| 4 | Console stock management (add/buy/sell/delete/list) | 25 |
| 5 | Console data entry, report, chart | 23 |
| 6 | Console Lab-2 hooks (manage_data, scrape, CSV) | 20 |
| 7 | End-to-end (CSV parse, chart render, live Yahoo scrape) | 14 |

Run a single phase:

```bash
python3 test_phase1.py
```

Run all phases:

```bash
for n in 1 2 3 4 5 6 7; do python3 test_phase$n.py; done
```

Phases 2, 3, and 7 require `tkinter` / `matplotlib`, so use the macOS framework Python:

```bash
/Library/Frameworks/Python.framework/Versions/Current/bin/python3 test_phase2.py
```

## Class Diagram

`class_diagram.png` shows the three classes (`Stock`, `DailyData`, `StockApp`) with their IS-A (inheritance from `object`) and HAS-A (composition) relationships. `Stock` HAS-A list of `DailyData`; `StockApp` HAS-A list of `Stock` plus several tkinter widgets.

## Report

The full lab report — narrative for each section, sample output screenshots for every console and GUI workflow, and per-phase unit-test results — is in `Lab2_Report.docx`.

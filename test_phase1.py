# Phase 1 wrapper: runs the unit tests defined in stock_class.main()
# and reports the total execution time.
#
# Run:
#   /Library/Frameworks/Python.framework/Versions/Current/bin/python3 test_phase1.py

import sys
import time

import stock_class


if __name__ == "__main__":
    start = time.perf_counter()
    stock_class.main()
    elapsed = time.perf_counter() - start
    print(f"\nExecution time: {elapsed:.4f} seconds ({elapsed*1000:.2f} ms)")

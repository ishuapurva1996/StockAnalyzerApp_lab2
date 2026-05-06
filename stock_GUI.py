# Summary: This module contains the user interface and logic for a graphical user interface version of the stock manager program.

from datetime import datetime
from os import path
from tkinter import *
from tkinter import ttk
from tkinter import messagebox, simpledialog, filedialog
import csv
import stock_data
from stock_class import Stock, DailyData
from utilities import clear_screen, display_stock_chart, sortStocks, sortDailyData

class StockApp:
    def __init__(self):
        self.stock_list = []
        #check for database, create if not exists
        if path.exists("stocks.db") == False:
            stock_data.create_database()

 # This section creates the user interface

        # Create Window
        self.root = Tk()
        self.root.title("Pragya's Stock Manager")


        # Add Menubar
        self.menubar = Menu(self.root)

        # Add File Menu
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Load Data...", command=self.load)
        self.filemenu.add_command(label="Save Data...", command=self.save)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.root.quit)

        # Add Web Menu
        self.webmenu = Menu(self.menubar, tearoff=0)
        self.webmenu.add_command(label="Scrape Data from Yahoo! Finance...", command=self.scrape_web_data)
        self.webmenu.add_command(label="Import CSV From Yahoo! Finance...", command=self.importCSV_web_data)

        # Add Chart Menu
        self.chartmenu = Menu(self.menubar, tearoff=0)
        self.chartmenu.add_command(label="Display Stock Chart...", command=self.display_chart)

        # Add menus to window
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.menubar.add_cascade(label="Web", menu=self.webmenu)
        self.menubar.add_cascade(label="Chart", menu=self.chartmenu)
        self.root.config(menu=self.menubar)

        # Add heading information
        self.headingLabel = Label(self.root, text="Stock Manager", font=("Helvetica", 16))
        self.headingLabel.pack(pady=5)

        # Add stock list
        self.stockList = Listbox(self.root, height=5)
        self.stockList.pack(fill=X, padx=10)
        self.stockList.bind("<<ListboxSelect>>", self.update_data)

        # Add Tabs
        self.tabs = ttk.Notebook(self.root)
        self.mainTab = Frame(self.tabs)
        self.historyTab = Frame(self.tabs)
        self.reportTab = Frame(self.tabs)
        self.tabs.add(self.mainTab, text="Main")
        self.tabs.add(self.historyTab, text="History")
        self.tabs.add(self.reportTab, text="Report")
        self.tabs.pack(fill=BOTH, expand=1, padx=10, pady=5)

        # Set Up Main Tab
        # -- Add Stock section
        Label(self.mainTab, text="Add Stock", font=("Helvetica", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky=W, pady=(5, 0))
        Label(self.mainTab, text="Symbol:").grid(row=1, column=0, sticky=E)
        self.addSymbolEntry = Entry(self.mainTab)
        self.addSymbolEntry.grid(row=1, column=1, sticky=W)
        Label(self.mainTab, text="Name:").grid(row=2, column=0, sticky=E)
        self.addNameEntry = Entry(self.mainTab)
        self.addNameEntry.grid(row=2, column=1, sticky=W)
        Label(self.mainTab, text="Shares:").grid(row=3, column=0, sticky=E)
        self.addSharesEntry = Entry(self.mainTab)
        self.addSharesEntry.grid(row=3, column=1, sticky=W)
        Button(self.mainTab, text="Add Stock", command=self.add_stock).grid(row=4, column=0, columnspan=2, pady=5)

        # -- Update Shares section
        Label(self.mainTab, text="Update Shares", font=("Helvetica", 12, "bold")).grid(row=5, column=0, columnspan=2, sticky=W, pady=(10, 0))
        Label(self.mainTab, text="Shares:").grid(row=6, column=0, sticky=E)
        self.updateSharesEntry = Entry(self.mainTab)
        self.updateSharesEntry.grid(row=6, column=1, sticky=W)
        Button(self.mainTab, text="Buy", command=self.buy_shares).grid(row=7, column=0, pady=5)
        Button(self.mainTab, text="Sell", command=self.sell_shares).grid(row=7, column=1, pady=5)

        # -- Delete Stock section
        Label(self.mainTab, text="Delete Stock", font=("Helvetica", 12, "bold")).grid(row=8, column=0, columnspan=2, sticky=W, pady=(10, 0))
        Button(self.mainTab, text="Delete Selected Stock", command=self.delete_stock).grid(row=9, column=0, columnspan=2, pady=5)

        # Setup History Tab
        self.dailyDataList = Text(self.historyTab, width=60, height=20)
        self.dailyDataList.pack(fill=BOTH, expand=1, padx=5, pady=5)

        # Setup Report Tab
        self.stockReport = Text(self.reportTab, width=60, height=20)
        self.stockReport.pack(fill=BOTH, expand=1, padx=5, pady=5)

        ## Call MainLoop
        self.root.mainloop()

# This section provides the functionality
       
    # Load stocks and history from database.
    def load(self):
        self.stockList.delete(0,END)
        stock_data.load_stock_data(self.stock_list)
        sortStocks(self.stock_list)
        for stock in self.stock_list:
            self.stockList.insert(END,stock.symbol)
        messagebox.showinfo("Load Data","Data Loaded")

    # Save stocks and history to database.
    def save(self):
        stock_data.save_stock_data(self.stock_list)
        messagebox.showinfo("Save Data","Data Saved")

    # Refresh history and report tabs
    def update_data(self, evt):
        self.display_stock_data()

    # Display stock price and volume history.
    def display_stock_data(self):
        symbol = self.stockList.get(self.stockList.curselection())
        for stock in self.stock_list:
            if stock.symbol == symbol:
                self.headingLabel['text'] = stock.name + " - " + str(stock.shares) + " Shares"
                self.dailyDataList.delete("1.0",END)
                self.stockReport.delete("1.0",END)
                self.dailyDataList.insert(END,"- Date -   - Price -   - Volume -\n")
                self.dailyDataList.insert(END,"=================================\n")
                for daily_data in stock.DataList:
                    row = daily_data.date.strftime("%m/%d/%y") + "   " +  '${:0,.2f}'.format(daily_data.close) + "   " + str(daily_data.volume) + "\n"
                    self.dailyDataList.insert(END,row)

                #display report
                self.stockReport.insert(END, "Stock Report ---\n")
                self.stockReport.insert(END, "Report for: " + stock.symbol + " " + stock.name + "\n")
                self.stockReport.insert(END, "Shares: " + str(stock.shares) + "\n\n")
                if len(stock.DataList) == 0:
                    self.stockReport.insert(END, "*** No daily history.\n")
                else:
                    sorted_data = sorted(stock.DataList, key=lambda d: d.date)
                    start = sorted_data[0]
                    end = sorted_data[-1]
                    high = max(sorted_data, key=lambda d: d.close)
                    low = min(sorted_data, key=lambda d: d.close)
                    profit = (end.close - start.close) * stock.shares
                    profit_str = ("-${:0,.2f}".format(abs(profit)) if profit < 0 else "${:0,.2f}".format(profit))
                    self.stockReport.insert(END, "Start Date: " + start.date.strftime("%m/%d/%y") + "   Price: " + '${:0,.2f}'.format(start.close) + "\n")
                    self.stockReport.insert(END, "End Date:   " + end.date.strftime("%m/%d/%y") + "   Price: " + '${:0,.2f}'.format(end.close) + "\n")
                    self.stockReport.insert(END, "High:       " + high.date.strftime("%m/%d/%y") + "   Price: " + '${:0,.2f}'.format(high.close) + "\n")
                    self.stockReport.insert(END, "Low:        " + low.date.strftime("%m/%d/%y") + "   Price: " + '${:0,.2f}'.format(low.close) + "\n")
                    self.stockReport.insert(END, "\nProfit/Loss: " + profit_str + "\n")
                self.stockReport.insert(END, "\n--- Report Complete ---\n")


    
    # Add new stock to track.
    def add_stock(self):
        new_stock = Stock(self.addSymbolEntry.get(),self.addNameEntry.get(),float(str(self.addSharesEntry.get())))
        self.stock_list.append(new_stock)
        self.stockList.insert(END,self.addSymbolEntry.get())
        self.addSymbolEntry.delete(0,END)
        self.addNameEntry.delete(0,END)
        self.addSharesEntry.delete(0,END)

    # Buy shares of stock.
    def buy_shares(self):
        symbol = self.stockList.get(self.stockList.curselection())
        for stock in self.stock_list:
            if stock.symbol == symbol:
                stock.buy(float(self.updateSharesEntry.get()))
                self.headingLabel['text'] = stock.name + " - " + str(stock.shares) + " Shares"
        messagebox.showinfo("Buy Shares","Shares Purchased")
        self.updateSharesEntry.delete(0,END)

    # Sell shares of stock.
    def sell_shares(self):
        symbol = self.stockList.get(self.stockList.curselection())
        for stock in self.stock_list:
            if stock.symbol == symbol:
                stock.sell(float(self.updateSharesEntry.get()))
                self.headingLabel['text'] = stock.name + " - " + str(stock.shares) + " Shares"
        messagebox.showinfo("Sell Shares","Shares Sold")
        self.updateSharesEntry.delete(0,END)

    # Remove stock and all history from being tracked.
    def delete_stock(self):
        selection = self.stockList.curselection()
        if not selection:
            messagebox.showwarning("Delete Stock", "No stock selected.")
            return
        symbol = self.stockList.get(selection)
        if not messagebox.askyesno("Delete Stock", "Are you sure you want to delete " + symbol + "?"):
            return
        self.stock_list[:] = [s for s in self.stock_list if s.symbol != symbol]
        self.stockList.delete(selection)
        self.headingLabel['text'] = "Stock Manager"
        self.dailyDataList.delete("1.0", END)
        self.stockReport.delete("1.0", END)

    # Get data from web scraping.
    def scrape_web_data(self):
        dateFrom = simpledialog.askstring("Starting Date","Enter Starting Date (m/d/yy)")
        dateTo = simpledialog.askstring("Ending Date","Enter Ending Date (m/d/yy")
        try:
            stock_data.retrieve_stock_web(dateFrom,dateTo,self.stock_list)
        except:
            messagebox.showerror("Cannot Get Data from Web","Check Path for Chrome Driver")
            return
        self.display_stock_data()
        messagebox.showinfo("Get Data From Web","Data Retrieved")

    # Import CSV stock history file.
    def importCSV_web_data(self):
        symbol = self.stockList.get(self.stockList.curselection())
        filename = filedialog.askopenfilename(title="Select " + symbol + " File to Import",filetypes=[('Yahoo Finance! CSV','*.csv')])
        if filename != "":
            stock_data.import_stock_web_csv(self.stock_list,symbol,filename)
            self.display_stock_data()
            messagebox.showinfo("Import Complete",symbol + "Import Complete")   
    
    # Display stock price chart.
    def display_chart(self):
        symbol = self.stockList.get(self.stockList.curselection())
        display_stock_chart(self.stock_list,symbol)


def main():
        app = StockApp()
        

if __name__ == "__main__":
    # execute only if run as a script
    main()
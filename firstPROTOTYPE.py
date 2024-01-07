import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from math import isnan
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Transaction:
    def __init__(self, amount, timestamp, category):
        self.amount = amount
        self.timestamp = timestamp
        self.category = category

    def __str__(self):
        return f"{self.category}: {self.format_currency(self.amount)} IDR at {self.timestamp}"

    @staticmethod
    def format_currency(amount):
        return "{:,.2f}".format(amount)

class Account:
    def __init__(self, account_number, account_holder, balance):
        self.account_number = account_number
        self.account_holder = account_holder
        self.balance = balance
        self.transactions = []

    def deposit(self, amount, category):
        self.balance += amount
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        transaction = Transaction(amount, timestamp, category)
        self.transactions.append(transaction)

    def withdraw(self, amount, category):
        if amount <= self.balance:
            self.balance -= amount
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            transaction = Transaction(-amount, timestamp, category)
            self.transactions.append(transaction)
        else:
            messagebox.showinfo("Insufficient Funds", "Insufficient funds.")

    def get_balance(self):
        return self.balance

    def get_transaction_history(self):
        return self.transactions

class Bank:
    def __init__(self, bank_name):
        self.bank_name = bank_name
        self.accounts = {}

    def create_account(self, account_number, account_holder, initial_balance):
        if account_number not in self.accounts:
            account = Account(account_number, account_holder, initial_balance)
            self.accounts[account_number] = account
            return account
        return None

    def get_account(self, account_number):
        return self.accounts.get(account_number)

    def transfer_funds(self, from_account, to_account, amount):
        if from_account in self.accounts and to_account in self.accounts:
            if self.accounts[from_account].balance >= amount:
                self.accounts[from_account].withdraw(amount, "Transfer")
                self.accounts[to_account].deposit(amount, "Transfer")
                return True
        return False

class FlazzCardApp:
    def __init__(self, root, bank, account):
        self.root = root
        self.root.title("Flazz Card Usage History")
        self.bank = bank
        self.account = account
        self.selected_category = tk.StringVar()

        self.add_money_label = tk.Label(root, text="Enter the amount to add (in IDR):")
        self.entry_add_money = tk.Entry(root)
        self.add_money_button = tk.Button(root, text="Add Money", command=self.add_money)

        self.use_money_label = tk.Label(root, text="Select Category:")
        self.category_menu = ttk.Combobox(root, textvariable=self.selected_category,
            values=["Toll Road", "Public Transportation", "Supermarket", "Gas Station","Recreational", "Other"])
        self.category_menu.bind("<<ComboboxSelected>>", self.select_category)
        self.use_money_button = tk.Button(root, text="Use Money", command=self.use_money, state="disabled")

        self.history_label = tk.Label(root, text="Transaction History")
        self.history_text = tk.Text(root, height=10, width=40)
        self.history_text.config(state="disabled")

        self.balance_label = tk.Label(root, text=f"Remaining Balance: {self.format_currency(self.account.get_balance())} IDR")

        self.figure, self.ax = plt.subplots(nrows=2, ncols=2, figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)  
        self.canvas_widget = self.canvas.get_tk_widget()

        self.export_button = tk.Button(root, text="Export to Excel", command=self.export_to_excel, height=2, width=20)

        self.add_money_label.grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.entry_add_money.grid(row=0, column=1, pady=10, padx=10)
        self.add_money_button.grid(row=0, column=2, pady=10, padx=10)

        self.use_money_label.grid(row=1, column=0, pady=10, padx=10, sticky="w")
        self.category_menu.grid(row=1, column=1, pady=10, padx=10)
        self.use_money_button.grid(row=1, column=2, pady=10, padx=10)

        self.history_label.grid(row=2, column=0, columnspan=3, pady=20)
        self.history_text.grid(row=3, column=0, columnspan=3, pady=10, padx=10, sticky="w")

        self.balance_label.grid(row=4, column=0, columnspan=3, pady=10, padx=10)

        self.canvas_widget.grid(row=0, column=3, rowspan=5, pady=10, padx=20, sticky="nsew") 

        self.export_button.grid(row=5, column=0, columnspan=4, pady=20)

        self.figure.subplots_adjust(wspace=0.5, hspace=0.5)

        for ax_row in self.ax:
            for ax in ax_row:
                ax.title.set_bbox(dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="w"))

        for ax_row in self.ax:
            for ax in ax_row:
                ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=True)
                ax.set_xticks(ax.get_xticks())
                ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

        self.update_charts()

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(3, weight=1)

    def add_money(self):
        amount = float(self.entry_add_money.get())
        category = "Deposit"
        if not isnan(amount):
            self.account.deposit(amount, category)
            self.update_history()
            self.update_balance()
            self.update_charts()

    def use_money(self):
        amount = float(self.entry_add_money.get())  
        category = self.selected_category.get()
        if not isnan(amount) and category:
            if self.account.get_balance() >= amount:
                self.account.withdraw(amount, category)
                self.update_history()
                self.update_balance()
                self.update_charts()
            else:
                messagebox.showinfo("Insufficient Balance", f"Not enough balance. Current balance: {self.format_currency(self.account.get_balance())} IDR")

    def update_history(self):
        self.display_transactions(self.account.get_transaction_history())

    def update_balance(self):
        self.balance_label.config(text=f"Remaining Balance: {self.format_currency(self.account.get_balance())} IDR")

    def select_category(self, event):
        selected_category = self.selected_category.get()
        if selected_category != "Select Category":
            self.use_money_button.config(state="normal")
        else:
            self.use_money_button.config(state="disabled")

    def display_transactions(self, transactions):
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, tk.END)
        for transaction in transactions:
            self.history_text.insert(tk.END, str(transaction) + "\n")
        self.history_text.config(state="disabled")

    def update_charts(self):
        self.update_spending_pattern_chart()
        self.update_deposit_chart()
        self.update_spending_chart()
        self.update_stats_chart()

    def update_spending_pattern_chart(self):
        categories = []
        spending = []

        for transaction in self.account.get_transaction_history():
            if transaction.category not in categories:
                categories.append(transaction.category)
                spending.append(0)

            category_index = categories.index(transaction.category)
            spending[category_index] += transaction.amount

        self.ax[0, 0].clear()
        self.ax[0, 0].plot(categories, spending, marker='o', color='blue', linestyle='-', linewidth=2)
        self.ax[0, 0].set_title('Spending Pattern')
        self.ax[0, 0].set_xlabel('Categories')
        self.ax[0, 0].set_ylabel('Total Spending (IDR)')

    def update_deposit_chart(self):
        deposit_dates = [transaction.timestamp for transaction in self.account.get_transaction_history() if transaction.amount > 0]
        deposit_amounts = [transaction.amount for transaction in self.account.get_transaction_history() if transaction.amount > 0]

        self.ax[0, 1].clear()
        self.ax[0, 1].plot(deposit_dates, deposit_amounts, marker='o', color='green', linestyle='-', linewidth=2)
        self.ax[0, 1].set_title('Deposit History')
        self.ax[0, 1].set_xlabel('Timestamp')
        self.ax[0, 1].set_ylabel('Deposit Amount (IDR)')

    def update_spending_chart(self):
        spending_dates = [transaction.timestamp for transaction in self.account.get_transaction_history() if transaction.amount < 0]
        spending_amounts = [abs(transaction.amount) for transaction in self.account.get_transaction_history() if transaction.amount < 0]

        self.ax[1, 0].clear()
        self.ax[1, 0].plot(spending_dates, spending_amounts, marker='o', color='red', linestyle='-', linewidth=2)
        self.ax[1, 0].set_title('Spending History')
        self.ax[1, 0].set_xlabel('Timestamp')
        self.ax[1, 0].set_ylabel('Spending Amount (IDR)')

    def update_stats_chart(self):
        stats_dates = [transaction.timestamp for transaction in self.account.get_transaction_history()]
        stats_balance = [transaction.amount for transaction in self.account.get_transaction_history()]

        self.ax[1, 1].clear()
        self.ax[1, 1].plot(stats_dates, stats_balance, marker='o', color='purple', linestyle='-', linewidth=2)
        self.ax[1, 1].set_title('Transaction Statistics')
        self.ax[1, 1].set_xlabel('Timestamp')
        self.ax[1, 1].set_ylabel('Transaction Amount (IDR)')

        self.canvas.draw()

    def export_to_excel(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

        if file_path:
            transactions = self.account.get_transaction_history()
            data = {"Category": [], "Amount": [], "Timestamp": []}

            for transaction in transactions:
                data["Category"].append(transaction.category)
                data["Amount"].append(transaction.amount)
                data["Timestamp"].append(transaction.timestamp)

            df = pd.DataFrame(data)
            df["Remaining Balance"] = [self.account.get_balance()] * len(df)
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Export Successful", f"Transaction history exported to {file_path}")

    @staticmethod
    def format_currency(amount):
        return "{:,.2f}".format(amount)

if __name__ == "__main__":
    root = tk.Tk()
    bank = Bank("MyFlazzID")
    account_number = "2702414841"
    account_holder = "Alrismany Abigail"
    initial_balance = 0
    account = bank.create_account(account_number, account_holder, initial_balance)

    if account:
        app = FlazzCardApp(root, bank, account)
        root.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import pandas as pd
from math import isnan
from datetime import datetime

class SetupWindow:
    def __init__(self, root, bank):
        # Initialize the setup window
        self.root = root
        self.root.title("Register / Login")
        self.bank = bank

        # Create a custom style for the labels, entry widgets, and button
        custom_style = ttk.Style()
        custom_style.configure("CustomLabel.TLabel", font=("Arial", 14), foreground="#2E86C1")  # Change the font and text color for labels
        custom_style.configure("CustomEntry.TEntry", font=("Arial", 14), foreground="#2E86C1")  # Change the font and text color for entry widgets
        custom_style.configure("Custom.TButton", font=("Arial", 14), foreground="green", background="#3498DB")  # Change font, text color, and button color

        # Create GUI elements for entering account information using custom style
        self.account_number_label = ttk.Label(root, text="Enter your Binusian ID Flazz number:", style="CustomLabel.TLabel")
        self.entry_account_number = ttk.Entry(root, validate="key", validatecommand=(root.register(self.validate_account_number), "%P"), style="CustomEntry.TEntry")

        self.account_holder_label = ttk.Label(root, text="Enter your account Full name:", style="CustomLabel.TLabel")
        self.entry_account_holder = ttk.Entry(root, validate="key", validatecommand=(root.register(self.validate_full_name), "%P"), style="CustomEntry.TEntry")

        # Button to create an account
        self.setup_button = ttk.Button(root, text="Create Account", command=self.setup_account, style="Custom.TButton")

        # Grid layout for the GUI elements
        self.account_number_label.grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.entry_account_number.grid(row=0, column=1, pady=10, padx=10)

        self.account_holder_label.grid(row=1, column=0, pady=10, padx=10, sticky="w")
        self.entry_account_holder.grid(row=1, column=1, pady=10, padx=10)

        self.setup_button.grid(row=2, column=0, columnspan=2, pady=20)

    # Validate Binusian ID Flazz number
    def validate_account_number(self, value):
        return value.isdigit() and len(value) <= 10

    # Validate full name
    def validate_full_name(self, value):
        return all(c.isalpha() or c.isspace() or c == '-' for c in value)

    # Create a new account
    def setup_account(self):
        account_number = self.entry_account_number.get()
        account_holder = self.entry_account_holder.get()

        # Check if provided information is valid
        if len(account_number) == 10 and account_holder:
            initial_balance = 0
            account = self.bank.create_account(account_number, account_holder, initial_balance)

            # If account creation is successful, launch the main application
            if account:
                self.root.destroy()
                app = FlazzCardApp(tk.Tk(), self.bank, account)
            else:
                # Show an error message if account with the same number already exists
                messagebox.showinfo("Account Creation Failed", "Account with this number already exists.")
        else:
            # Show an error message for invalid information
            messagebox.showinfo("Invalid Information", "Please provide a valid 10-digit Binusian ID number and account Full name.")


# Define a class to represent individual transactions
class Transaction:
    def __init__(self, amount, timestamp, category):
        # Initialize transaction attributes
        self.amount = amount  # Transaction amount (positive for deposits, negative for withdrawals)
        self.timestamp = timestamp  # Timestamp when the transaction occurred
        self.category = category  # Category of the transaction (e.g., "Toll Road", "Supermarket")

    def __str__(self):
        # String representation of the transaction for display purposes
        return f"{self.category}: {self.format_currency(self.amount)} IDR at {self.timestamp}"

    @staticmethod
    def format_currency(amount):
        # Helper method to format currency with commas and two decimal places
        return "{:,.2f}".format(amount)

# Define a class to represent a bank account
class Account:
    def __init__(self, account_number, account_holder, balance):
        # Initialize account attributes
        self.account_number = account_number  # Unique identifier for the account
        self.account_holder = account_holder  # Full name of the account holder
        self.balance = balance  # Current balance in the account
        self.transactions = []  # List to store transaction history

    def deposit(self, amount, category):
        # Deposit funds into the account
        self.balance += amount
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        transaction = Transaction(amount, timestamp, category)
        self.transactions.append(transaction)

    def withdraw(self, amount, category):
        # Withdraw funds from the account if there are sufficient funds
        if amount <= self.balance:
            self.balance -= amount
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            transaction = Transaction(-amount, timestamp, category)
            self.transactions.append(transaction)
        else:
            # Display a message for insufficient funds
            messagebox.showinfo("Insufficient Funds", "Insufficient funds.")

    def get_balance(self):
        # Get the current balance of the account
        return self.balance

    def get_transaction_history(self):
        # Get the transaction history of the account
        return self.transactions

# Define a class to represent a bank
class Bank:
    def __init__(self, bank_name):
        # Initialize bank attributes
        self.bank_name = bank_name  # Name of the bank
        self.accounts = {}  # Dictionary to store accounts (account_number: Account)

    def create_account(self, account_number, account_holder, initial_balance):
        # Create a new account if the account number is unique
        if account_number not in self.accounts:
            account = Account(account_number, account_holder, initial_balance)
            self.accounts[account_number] = account
            return account
        return None

    def get_account(self, account_number):
        # Get the account associated with a given account number
        return self.accounts.get(account_number)

    def transfer_funds(self, from_account, to_account, amount):
        # Transfer funds from one account to another if there are sufficient funds
        if from_account in self.accounts and to_account in self.accounts:
            if self.accounts[from_account].balance >= amount:
                self.accounts[from_account].withdraw(amount, "Transfer")
                self.accounts[to_account].deposit(amount, "Transfer")
                return True
        return False

#define a class to represent the main application for flazz card usage
class FlazzCardApp:
    def __init__(self, root, bank, account):
        #initialize the mian application window
        self.root = root
        self.root.title("Flazz Card Usage History")
        self.bank = bank
        self.account = account
        self.selected_category = tk.StringVar()

        #GUI elements for adding and using money
        self.add_money_label = tk.Label(root, text="Enter the amount to add (in IDR):")
        self.entry_add_money = tk.Entry(root)
        self.add_money_button = tk.Button(root, text="Add Money", command=self.add_money, bg="green", fg="white")

        self.use_money_label = tk.Label(root, text="Select Category:")
        self.category_menu = ttk.Combobox(root, textvariable=self.selected_category,
            values=["Toll Road", "Public Transportation", "Supermarket", "Gas Station","Recreational", "Other"])
        self.category_menu.bind("<<ComboboxSelected>>", self.select_category)
        self.use_money_button = tk.Button(root, text="Use Money", command=self.use_money, bg="red", fg="white")

        #GUI elements for displaying the transaction history
        self.history_label = tk.Label(root, text="Transaction History")
        self.history_text = tk.Text(root, height=10, width=50)
        self.history_text.config(state="disabled")

        #GUI elements for displaying the remaining transactions balance information
        self.balance_label = tk.Label(root, text=f"Remaining Balance: {self.format_currency(self.account.get_balance())} IDR", font=("Helvetica", 16, "bold"))

        #matplotlib charts and canvas
        self.figure, self.ax = plt.subplots(nrows=2, ncols=2, figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()

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

        # Additional GUI elements for ecporting and saving history and charts
        self.export_button = tk.Button(root, text="Export to Excel", command=self.export_to_excel, height=2, width=20)
        self.export_button.grid(row=5, column=0, pady=20, padx=5)

        self.export_pdf_button = tk.Button(root, text="Export to PDF", command=self.export_to_pdf, height=2, width=20)
        self.export_pdf_button.grid(row=5, column=1, pady=20, padx=5)

        self.save_chart_button = tk.Button(root, text="Save Chart as JPEG", command=self.save_chart_as_jpeg, height=2, width=20)
        self.save_chart_button.grid(row=5, column=2, pady=20, padx=5)

        #dark mode button and log out button
        self.dark_mode_button = tk.Button(root, text="Toggle Dark Mode", command=self.toggle_dark_mode)
        self.dark_mode_button.grid(row=6, column=3, pady=10, padx=5)

        self.logout_button = tk.Button(root, text="Logout", command=self.logout, height=2, width=18, font=("Arial", 18), fg="white", bg="dark gray")
        self.logout_button.grid(row=5, column=3, pady=20, padx=5)
        
        # Full chart button
        self.full_chart_button = tk.Button(root, text="Full Transaction History Chart", command=self.show_full_chart)
        self.full_chart_button.grid(row=6, column=0, pady=10, padx=5)

        # adjusting layout and applying initial themes
        self.figure.subplots_adjust(wspace=0.5, hspace=0.5)
        self.dark_mode = False
        self.apply_theme()

    # method to toggle between dark and light mode   
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    # Method to apply the selected theme (dark or light)
    def apply_theme(self):
        # Theme settings for various GUI elements and charts
        if self.dark_mode:
            self.root.configure(bg="#121212")  
            self.history_text.config(bg="#1E1E1E", fg="white")  
            self.balance_label.config(bg="#121212", fg="white") 

            for ax_row in self.ax:
                for ax in ax_row:
                    ax.set_facecolor("#121212")
                    ax.tick_params(axis='x', colors='white')
                    ax.tick_params(axis='y', colors='white')
                    ax.title.set_color('white')
                    ax.xaxis.label.set_color('white')
                    ax.yaxis.label.set_color('white')

            self.canvas_widget.config(bg="#121212") 

        else:
            self.root.configure(bg="white")
            self.history_text.config(bg="white", fg="black")
            self.balance_label.config(bg="white", fg="black")

            for ax_row in self.ax:
                for ax in ax_row:
                    ax.set_facecolor("white")
                    ax.tick_params(axis='x', colors='black')
                    ax.tick_params(axis='y', colors='black')
                    ax.title.set_color('black')
                    ax.xaxis.label.set_color('black')
                    ax.yaxis.label.set_color('black')

            self.canvas_widget.config(bg="white")

        self.update_charts()
        
        for ax_row in self.ax:
            for ax in ax_row:
                ax.title.set_bbox(dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="w"))

        for ax_row in self.ax:
            for ax in ax_row:
                ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=True)
                ax.set_xticks(ax.get_xticks())
                ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

        self.update_charts()
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(3, weight=1)
        
    # Method to show the full transaction history chart    
    def show_full_chart(self):
        full_chart_root = tk.Tk()
        full_chart_page = FullChartPage(full_chart_root, self.bank, self.account)
        full_chart_root.mainloop()

    # Method to add money to the account
    def add_money(self):
        amount_str = self.entry_add_money.get()

        try:
            amount = float(amount_str)

            if amount >= 0:
                category = "Deposit"
                self.account.deposit(amount, category)
                self.update_history()
                self.update_balance()
                self.update_charts()
            else:
                messagebox.showinfo("Invalid Amount", "Please enter a non-negative amount.")
        except ValueError:
            messagebox.showinfo("Invalid Amount", "Please enter a valid numeric amount.")

    # Method to use money from the account
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

    # Method to update the transaction history display
    def update_history(self):
        self.display_transactions(self.account.get_transaction_history())

    # Method to update the displayed balance
    def update_balance(self):
        self.balance_label.config(text=f"Remaining Balance: {self.format_currency(self.account.get_balance())} IDR")

    # Method to handle category selection
    def select_category(self, event):
        selected_category = self.selected_category.get()
        if selected_category != "Select Category":
            self.use_money_button.config(state="normal")
        else:
            self.use_money_button.config(state="disabled")

    # Method to display transactions in the history text box
    def display_transactions(self, transactions):
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, tk.END)
        for transaction in transactions:
            self.history_text.insert(tk.END, str(transaction) + "\n")
        self.history_text.config(state="disabled")

    # Method to update the charts based on transaction history
    def update_charts(self):
        self.update_spending_pattern_chart()
        self.update_deposit_chart()
        self.update_spending_chart()
        self.update_stats_chart()

    # Methods to "update" each specific charts
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

    # Method to export transaction history to Excel
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

    # Method to export transaction history to PDF
    def export_to_pdf(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])

        if file_path:
            transactions = self.account.get_transaction_history()

            pdf = canvas.Canvas(file_path, pagesize=letter)
            pdf.setFont("Helvetica", 12)

            pdf.drawString(100, 750, "Transaction History")
            pdf.drawString(100, 730, "-------------------") # As a seperator

            y_position = 710
            for transaction in transactions:
                pdf.drawString(100, y_position, str(transaction))
                y_position -= 20

            pdf.save()

            messagebox.showinfo("Export Successful", f"Transaction history exported to {file_path}")

    # Method to save the chart as a JPEG file
    def save_chart_as_jpeg(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])

        if file_path:
            self.figure.savefig(file_path, format="jpeg")
            messagebox.showinfo("Save Successful", f"Chart saved as {file_path}")

    # Method to handle logout
    def logout(self):
        answer = simpledialog.askstring("Warning", "Are you sure you want to log out?\nAll transaction history will be deleted.\nType 'yes' to confirm:", parent=self.root)
        if answer == 'yes':
            self.root.destroy()
            root_setup = tk.Tk()
            bank_setup = Bank("MyFlazzID")
            setup_window = SetupWindow(root_setup, bank_setup)
            root_setup.mainloop()

    # Static method to format currency
    @staticmethod
    def format_currency(amount):
        return "{:,.2f}".format(amount)

# Define a class for displaying the full transaction history chart page
class FullChartPage:
    # Initialize the full chart page with inputs for safe and danger zones
    def __init__(self, root, bank, account):
        self.root = root
        self.root.title("Full Transaction History Chart")
        self.bank = bank
        self.account = account

        # GUI elements for entering safe and danger zones
        self.safe_zone_label = tk.Label(root, text="Enter Safe Zone (IDR):")
        self.entry_safe_zone = tk.Entry(root)

        self.danger_zone_label = tk.Label(root, text="Enter Danger Zone (IDR):")
        self.entry_danger_zone = tk.Entry(root)

        self.check_zone_button = tk.Button(root, text="Check Zone", command=self.check_zone)

        # Matplotlib chart and canvas for displaying the full transaction history
        self.full_chart_figure, self.full_chart_ax = plt.subplots(figsize=(10, 6))
        self.full_chart_canvas = FigureCanvasTkAgg(self.full_chart_figure, master=root)
        self.full_chart_canvas_widget = self.full_chart_canvas.get_tk_widget()

        # Variables to store safe and danger zones
        self.safe_zone = None
        self.danger_zone = None

        # Label to display safe and danger zones
        self.safe_danger_label = tk.Label(root, text="")

        # Layout configuration
        self.safe_zone_label.grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.entry_safe_zone.grid(row=0, column=1, pady=10, padx=10)

        self.danger_zone_label.grid(row=1, column=0, pady=10, padx=10, sticky="w")
        self.entry_danger_zone.grid(row=1, column=1, pady=10, padx=10)

        self.check_zone_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.full_chart_canvas_widget.grid(row=3, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")

        self.full_chart_figure.subplots_adjust(wspace=0.5, hspace=0.5)

    # Method to check and display safe and danger zones on the full chart
    def check_zone(self):
        safe_zone_str = self.entry_safe_zone.get()
        danger_zone_str = self.entry_danger_zone.get()

        try:
            self.safe_zone = float(safe_zone_str)
            self.danger_zone = float(danger_zone_str)

            if self.safe_zone < 0 or self.danger_zone < 0:
                messagebox.showinfo("Invalid Zone", "Please enter non-negative values.")
            else:
                self.plot_full_chart()  # Call the plot_full_chart method
        except ValueError:
            messagebox.showinfo("Invalid Zone", "Please enter valid numeric values.")

    # Method to plot the full chart
    def plot_full_chart(self):
        # Get the transaction history from the account
        transactions = self.account.get_transaction_history()

        # Extract dates and amounts from transactions
        dates = [transaction.timestamp for transaction in transactions]
        amounts = [transaction.amount for transaction in transactions]

        # Clear the existing content of the chart
        self.full_chart_ax.clear()

        # Plot the transaction amounts over time
        self.full_chart_ax.plot(dates, amounts, marker='o', color='black', linestyle='-', linewidth=2)

        # Add horizontal lines for the safe and danger zones
        self.full_chart_ax.axhline(self.safe_zone, color='green', linestyle='--', label='Safe Zone')
        self.full_chart_ax.axhline(self.danger_zone, color='red', linestyle='--', label='Danger Zone')

        # Add legend to the chart
        self.full_chart_ax.legend()

        # Set title and labels for the axes
        self.full_chart_ax.set_title('Full Transaction History')
        self.full_chart_ax.set_xlabel('Timestamp')
        self.full_chart_ax.set_ylabel('Transaction Amount (IDR)')

        # Draw the updated chart on the canvas
        self.full_chart_canvas.draw()

if __name__ == "__main__":
    root_setup = tk.Tk()
    bank_setup = Bank("MyFlazzID")
    setup_window = SetupWindow(root_setup, bank_setup)
    root_setup.mainloop()
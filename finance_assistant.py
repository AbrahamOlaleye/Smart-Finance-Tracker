import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re

class FinancialRecord:
    """
    Base class for managing financial records.
    """
    def __init__(self):
        """Initialize with default financial data."""
        self.income = 0
        self.savings = 0
        self.savings_goal = 0

    def add_income(self, amount):
        """
        Add income to the total.
        :param amount: Amount to be added to the income.
        """
        if amount > 0:
            self.income += amount
            self.save_data()

    def set_savings_goal(self, goal):
        """
        Set a savings goal.
        :param goal: Target savings amount.
        """
        if goal >= 0:
            self.savings_goal = goal
            self.save_data()

    def save_data(self):
        """Method to save data. To be overridden in derived classes."""
        pass

class FinanceData(FinancialRecord):
    """
    Derived class for managing personal finance data, including expenses.
    Inherits from FinancialRecord.
    """
    def __init__(self):
        """Initialize with an empty expenses dictionary and database details."""
        super().__init__()
        self.expenses = {}
        self.database = "finance_data.db"
        self.text_file = "finance_data.txt"
        self.original_savings = 0
        self.deficit = 0
        self.conn = sqlite3.connect(self.database)  # Database connection
        self.create_database()
        self.read_data_from_file()

    def create_database(self):
        """
        Create a SQLite database to store expenses.
        """
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS expenses
                              (id INTEGER PRIMARY KEY, category TEXT, description TEXT, amount REAL)''')

    def read_data_from_file(self):
        """
        Read financial data from a text file and load it into the database and the class attributes.
        """
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses")  # Clear existing database records
            try:
                with open(self.text_file, 'r') as file:
                    content = file.readlines()
                    in_expenses_section = False
                    for line in content:
                        # Parse and set income, savings, and savings goal
                        if line.startswith("Income:"):
                            self.income = float(line.split(":")[1].strip())
                        elif line.startswith("Savings:"):
                            self.savings = float(line.split(":")[1].strip())
                        elif line.startswith("SavingsGoal:"):
                            self.savings_goal = float(line.split(":")[1].strip())
                        elif line.startswith("Expenses:"):
                            in_expenses_section = True
                        elif in_expenses_section and line.strip():
                            # Parse and add expenses
                            category, description, amount = line.strip().split(", ")
                            cursor.execute("INSERT INTO expenses (category, description, amount) VALUES (?, ?, ?)",
                                           (category, description, float(amount)))
                            if category not in self.expenses:
                                self.expenses[category] = []
                            self.expenses[category].append((description, float(amount)))
                conn.commit()
                self.original_savings = self.savings
            except FileNotFoundError:
                print("No previous data found. Starting fresh.")

    def add_expense(self, category, description, amount, save_to_db=True):
        """
        Add an expense to the records.
        :param category: Category of the expense.
        :param description: Description of the expense.
        :param amount: Amount of the expense.
        :param save_to_db: Flag to indicate if the expense should be saved to the database.
        """
        if amount > 0:
            if category not in self.expenses:
                self.expenses[category] = []
            self.expenses[category].append((description, amount))
            if save_to_db:
                self.save_expense_to_db(category, description, amount)
            self.adjust_savings_if_needed()
            self.save_data_to_file()

    def save_expense_to_db(self, category, description, amount):
        """
        Save an expense to the SQLite database.
        :param category: Category of the expense.
        :param description: Description of the expense.
        :param amount: Amount of the expense.
        """
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO expenses (category, description, amount) VALUES (?, ?, ?)",
                           (category, description, amount))
            conn.commit()

    def save_data_to_file(self):
        """
        Save financial data to a text file.
        """
        with open(self.text_file, 'w') as file:
            file.write(f"Income: {self.income}\n")
            file.write(f"Savings: {self.savings}\n")
            file.write(f"SavingsGoal: {self.savings_goal}\n")
            file.write("Expenses:\n")
            for category, items in self.expenses.items():
                for desc, amount in items:
                    file.write(f"{category}, {desc}, {amount}\n")

    def adjust_savings_if_needed(self):
        """
        Adjust savings if expenses exceed income.
        """
        total_expenses = sum(amount for items in self.expenses.values() for _, amount in items)
        budget = self.income - total_expenses
        if budget < 0:
            self.deficit = -budget
            self.savings -= self.deficit
            if self.savings < 0:
                self.savings = 0
            self.save_data()

    def display_financial_summary(self):
        """
        Display a summary of the financial data.
        """
        print("\nFinancial Summary:")
        print(f"Total Income: ${self.income:.2f}")
        print(f"Original Savings: ${self.original_savings:.2f}")
        print(f"Current Savings: ${self.savings:.2f}")
        print("Expenses:")
        for category, items in self.expenses.items():
            for desc, amount in items:
                print(f"{category}: {desc} - ${amount:.2f}")
        total_expenses = sum(amount for items in self.expenses.values() for _, amount in items)
        print(f"Total Expenses: ${total_expenses:.2f}")
        print(f"Deficit: ${self.deficit:.2f}")
        remaining_budget = max(self.income - total_expenses, 0)
        print(f"Remaining Budget: ${remaining_budget:.2f}")
        print(f"Savings Goal: ${self.savings_goal:.2f}\n")

    def visualize_expenses(self):
        """
        Visualize expenses in a bar plot and a pie chart.
        """
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(10, 6))
        for category, items in self.expenses.items():
            sns.barplot(x=[amount for _, amount in items], y=[f"{category}: {desc}" for desc, _ in items])
        plt.title('Expense Breakdown')
        plt.xlabel('Amount ($)')
        plt.ylabel('Description')
        plt.show()

        remaining_budget = max(self.income - sum(amount for items in self.expenses.values() for _, amount in items), 0)
        data = {
            'Remaining Income': remaining_budget,
            'Savings': self.savings,
            'Deficit': self.deficit
        }
        labels, sizes = zip(*[(k, v) for k, v in data.items() if v > 0])
        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, autopct=lambda pct: f'{pct:.1f}% (${pct/100*sum(sizes):.2f})', startangle=140)
        plt.axis('equal')
        plt.title('Financial Overview')
        plt.show()

    def print_database_contents(self):
        """
        Print the contents of the expenses table from the SQLite database.
        """
        print("\nDatabase Contents:")
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses")
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    print(f"ID: {row[0]}, Category: {row[1]}, Description: {row[2]}, Amount: ${row[3]}")
            else:
                print("No expenses recorded in the database.")

def main():
    """
    Main function to run the Personal Finance Assistant application.
    """
    finance_data = FinanceData()

    while True:
        print("\nPersonal Finance Assistant")
        print("1. Add Income")
        print("2. Add Expense")
        print("3. Set Savings Goal")
        print("4. Display Financial Summary")
        print("5. Visualize Expenses")
        print("6. Print Database Contents")
        print("7. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            try:
                amount = float(input("Enter the income amount: "))
                finance_data.add_income(amount)
                print("Income added successfully.")
            except ValueError:
                print("Invalid input. Please enter a numeric value.")

        elif choice == '2':
            category = input("Enter expense category: ")
            description = input("Enter expense description: ")
            try:
                amount = float(input("Enter the expense amount: "))
                finance_data.add_expense(category, description, amount)
                print("Expense added successfully.")
            except ValueError:
                print("Invalid input. Please enter a numeric value.")

        elif choice == '3':
            try:
                goal = float(input("Enter your savings goal: "))
                finance_data.set_savings_goal(goal)
                print("Savings goal set successfully.")
            except ValueError:
                print("Invalid input. Please enter a numeric value.")

        elif choice == '4':
            finance_data.display_financial_summary()

        elif choice == '5':
            finance_data.visualize_expenses()

        elif choice == '6':
            finance_data.print_database_contents()

        elif choice == '7':
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please choose a valid option.")

if __name__ == "__main__":
    main()

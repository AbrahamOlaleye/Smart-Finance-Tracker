import os
from finance_assistant import FinanceData

def test_add_income():
    finance_data = FinanceData()
    finance_data.add_income(4500)
    assert finance_data.income == 9000

def test_set_savings_goal():
    finance_data = FinanceData()
    finance_data.set_savings_goal(6000)
    assert finance_data.savings_goal == 6000

def test_adjust_savings():
    finance_data = FinanceData()
    finance_data.add_income(500)
    finance_data.add_expense("Rent", "Monthly Rent", 1000)
    finance_data.adjust_savings_if_needed()
    assert finance_data.savings == 1500

def test_add_expense():
    finance_data = FinanceData()
    finance_data.add_expense("Groceries", "Bread", 2.25)
    assert finance_data.expenses["Groceries"][1] == ("Bread", 2.25)

def test_expenses_from_file():
    finance_data = FinanceData()
    # Check if expenses from the file match the expected values
    expected_expenses = {
        "Groceries": [("Milk", 3.50), ("Bread", 2.25), ("Eggs", 4.00)],
        "Utilities": [("Electricity", 50.00), ("Water", 30.00), ("Internet", 45.00)],
        "Transport": [("Gas", 60.00), ("Bus Pass", 20.00)],
        "Entertainment": [("Movie Tickets", 15.00), ("Streaming Service", 12.99)],
        "Health": [("Gym Membership", 35.00), ("Vitamins", 20.50)],
        "Personal": [("Clothing", 100.00), ("Haircut", 25.00)],
        "Education": [("Books", 80.00), ("Online Course", 50.00)],
        "Miscellaneous": [("Donation", 10.00), ("Gifts", 40.00)],
    }
    for category, items in expected_expenses.items():
        for desc, amount in items:
            assert (desc, amount) in finance_data.expenses[category]

def test_database_contents():
    finance_data = FinanceData()
    # Check if the database contains the expected expenses
    expected_expenses = {
        "Groceries": [("Milk", 3.50), ("Bread", 2.25), ("Eggs", 4.00)],
        "Utilities": [("Electricity", 50.00), ("Water", 30.00), ("Internet", 45.00)],
        "Transport": [("Gas", 60.00), ("Bus Pass", 20.00)],
        "Entertainment": [("Movie Tickets", 15.00), ("Streaming Service", 12.99)],
        "Health": [("Gym Membership", 35.00), ("Vitamins", 20.50)],
        "Personal": [("Clothing", 100.00), ("Haircut", 25.00)],
        "Education": [("Books", 80.00), ("Online Course", 50.00)],
        "Miscellaneous": [("Donation", 10.00), ("Gifts", 40.00)],
    }
    for category, items in expected_expenses.items():
        for desc, amount in items:
            # Check if the expense is in the database
            with finance_data.conn as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM expenses WHERE category=? AND description=? AND amount=?",
                               (category, desc, amount))
                result = cursor.fetchone()
                assert result is not None

if __name__ == '__main__':
    # Remove the existing database file if it exists
    if os.path.exists("finance_data.db"):
        os.remove("finance_data.db")

    # Run the test functions
    test_add_income()
    test_set_savings_goal()
    test_expenses_from_file()

    print("All tests passed.")

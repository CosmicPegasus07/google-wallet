import sqlite3
import datetime
import json
import os

def populate_mock_data(db_name='mock_finance.db'):
    """Populate database with mock data for testing"""
    db_path = os.path.join(os.path.dirname(__file__), db_name)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Mock users
    users = [
        ("Alice Johnson", "alice_wallet_123", "alice@example.com", "hash123"),
        ("Bob Smith", "bob_wallet_456", "bob@example.com", "hash456"),
        ("Charlie Brown", "charlie_wallet_789", "charlie@example.com", "hash789"),
        ("Diana Prince", "diana_wallet_101", "diana@example.com", "hash101"),
        ("Eve Wilson", "eve_wallet_202", "eve@example.com", "hash202")
    ]

    cursor.executemany("""
        INSERT INTO users (name, google_wallet_cred, email, password_hash) 
        VALUES (?, ?, ?, ?)
    """, users)

    # Mock groups
    groups = [
        ("Family Trip", "Summer vacation expenses", 1),
        ("Office Lunch", "Team lunch expenses", 2),
        ("Roommates", "Shared apartment expenses", 3),
        ("Friends Dinner", "Weekend dinner group", 1)
    ]

    cursor.executemany("""
        INSERT INTO groups (name, description, created_by)
        VALUES (?, ?, ?)
    """, groups)

    # Mock user-group relationships
    user_groups = [
        # Family Trip (group_id=1): Alice, Bob, Charlie
        (1, 1), (2, 1), (3, 1),
        # Office Lunch (group_id=2): Bob, Diana, Eve
        (2, 2), (4, 2), (5, 2),
        # Roommates (group_id=3): Charlie, Diana, Eve
        (3, 3), (4, 3), (5, 3),
        # Friends Dinner (group_id=4): Alice, Bob, Diana
        (1, 4), (2, 4), (4, 4)
    ]

    cursor.executemany("""
        INSERT INTO user_groups (user_id, group_id) VALUES (?, ?)
    """, user_groups)

    # Mock expenses
    expenses = [
        # Family Trip expenses
        (1, 1, 150.00, 'USD', 'Hotel booking', '2024-01-15', 'Grand Hotel', 'accommodation'),
        (1, 2, 85.50, 'USD', 'Dinner at restaurant', '2024-01-16', 'Italian Bistro', 'food'),
        (1, 3, 45.00, 'USD', 'Gas for road trip', '2024-01-17', 'Shell Station', 'transport'),

        # Office Lunch expenses
        (2, 2, 120.00, 'USD', 'Team lunch', '2024-01-20', 'Corporate Cafe', 'food'),
        (2, 4, 75.25, 'USD', 'Coffee and snacks', '2024-01-21', 'Starbucks', 'food'),

        # Roommates expenses
        (3, 3, 200.00, 'USD', 'Monthly utilities', '2024-01-01', 'Home', 'utilities'),
        (3, 4, 180.00, 'USD', 'Groceries', '2024-01-10', 'Supermarket', 'food'),

        # Friends Dinner expenses
        (4, 1, 95.75, 'USD', 'Weekend dinner', '2024-01-25', 'Fancy Restaurant', 'food'),
    ]

    cursor.executemany("""
        INSERT INTO expenses (group_id, payer_id, amount, currency, description, expense_date, location, type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, expenses)

    # Mock expense shares (equal splits for all expenses)
    expense_shares = []

    # Family Trip - Hotel (expense_id=1): Alice, Bob, Charlie
    expense_shares.extend([
        (1, 1, 50.00),  # Alice
        (1, 2, 50.00),  # Bob
        (1, 3, 50.00),  # Charlie
    ])

    # Family Trip - Dinner (expense_id=2): Alice, Bob, Charlie
    expense_shares.extend([
        (2, 1, 28.50),  # Alice
        (2, 2, 28.50),  # Bob
        (2, 3, 28.50),  # Charlie
    ])

    # Family Trip - Gas (expense_id=3): Alice, Bob, Charlie
    expense_shares.extend([
        (3, 1, 15.00),  # Alice
        (3, 2, 15.00),  # Bob
        (3, 3, 15.00),  # Charlie
    ])

    # Office Lunch - Team lunch (expense_id=4): Bob, Diana, Eve
    expense_shares.extend([
        (4, 2, 40.00),  # Bob
        (4, 4, 40.00),  # Diana
        (4, 5, 40.00),  # Eve
    ])

    # Office Lunch - Coffee (expense_id=5): Bob, Diana, Eve
    expense_shares.extend([
        (5, 2, 25.08),  # Bob
        (5, 4, 25.08),  # Diana
        (5, 5, 25.09),  # Eve
    ])

    # Roommates - Utilities (expense_id=6): Charlie, Diana, Eve
    expense_shares.extend([
        (6, 3, 66.67),  # Charlie
        (6, 4, 66.67),  # Diana
        (6, 5, 66.66),  # Eve
    ])

    # Roommates - Groceries (expense_id=7): Charlie, Diana, Eve
    expense_shares.extend([
        (7, 3, 60.00),  # Charlie
        (7, 4, 60.00),  # Diana
        (7, 5, 60.00),  # Eve
    ])

    # Friends Dinner (expense_id=8): Alice, Bob, Diana
    expense_shares.extend([
        (8, 1, 31.92),  # Alice
        (8, 2, 31.92),  # Bob
        (8, 4, 31.91),  # Diana
    ])

    cursor.executemany("""
        INSERT INTO expense_shares (expense_id, user_id, share_amount)
        VALUES (?, ?, ?)
    """, expense_shares)

    conn.commit()
    conn.close()
    print("Mock data populated successfully!")

if __name__ == "__main__":
    populate_mock_data()
import sqlite3
import datetime
import json

def populate_mock_data(db_name='mock_finance.db'):
    """Populate database with mock data for testing"""
    conn = sqlite3.connect(f'database/{db_name}')
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
        ("Family Trip", "Summer vacation expenses", 1, "family"),
        ("Office Lunch", "Team lunch expenses", 2, "work"),
        ("Roommates", "Shared apartment expenses", 3, "home"),
        ("Friends Dinner", "Weekend dinner group", 1, "friends")
    ]

    cursor.executemany("""
        INSERT INTO groups (name, description, created_by, group_type) 
        VALUES (?, ?, ?, ?)
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

    conn.commit()
    conn.close()
    print("Mock data populated successfully!")

if __name__ == "__main__":
    populate_mock_data()
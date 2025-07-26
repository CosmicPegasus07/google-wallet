import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bill_splitter import BillSplitter
from src.groups_manager import GroupsManager
from tabulate import tabulate
import json

def test_bill_splitting():
    """Test all bill splitting scenarios"""
    print("🧪 Testing Bill Splitting Functionality\n")
    
    bs = BillSplitter()
    gm = GroupsManager()
    
    # Use existing Family Trip group (ID: 1) with Alice, Bob, Charlie
    group_id = 1
    
    print("👥 Group members for testing:")
    members = gm.get_group_members(group_id)
    print(tabulate(members, headers="keys", tablefmt="grid"))
    
    # Test 1: Equal Split
    print("\n+1️⃣ Testing Equal Split - $150 dinner bill")
    expense_id_1 = bs.create_expense(group_id, 1, 150.0, "Team Dinner", split_type="equal")
    equal_splits = bs.split_equal(expense_id_1, group_id, 150.0)
    
    split_table = []
    for user_id, split_info in equal_splits.items():
        split_table.append([
            split_info['user_name'],
            f"${split_info['share_amount']:.2f}",
            f"{split_info['percentage']:.1f}%"
        ])
    print(tabulate(split_table, headers=["Name", "Amount", "Percentage"], tablefmt="grid"))
    
    # Test 2: Percentage Split
    print("\n2️⃣ Testing Percentage Split - $200 grocery bill")
    expense_id_2 = bs.create_expense(group_id, 2, 200.0, "Groceries", split_type="percentage")
    percentage_map = {1: 40.0, 2: 35.0, 3: 25.0}  # Alice 40%, Bob 35%, Charlie 25%
    percentage_splits = bs.split_percentage(expense_id_2, group_id, 200.0, percentage_map)
    
    split_table = []
    for user_id, split_info in percentage_splits.items():
        split_table.append([
            split_info['user_name'],
            f"${split_info['share_amount']:.2f}",
            f"{split_info['percentage']:.1f}%"
        ])
    print(tabulate(split_table, headers=["Name", "Amount", "Percentage"], tablefmt="grid"))
    
    # Test 3: Custom Amount Split
    print("\n3️⃣ Testing Custom Amount Split - $85.50 lunch bill")
    expense_id_3 = bs.create_expense(group_id, 3, 85.50, "Lunch", split_type="custom")
    amount_map = {1: 35.50, 2: 25.00, 3: 25.00}  # Custom amounts
    custom_splits = bs.split_custom_amounts(expense_id_3, group_id, 85.50, amount_map)
    
    split_table = []
    for user_id, split_info in custom_splits.items():
        split_table.append([
            split_info['user_name'],
            f"${split_info['share_amount']:.2f}",
            f"{split_info['percentage']:.1f}%"
        ])
    print(tabulate(split_table, headers=["Name", "Amount", "Percentage"], tablefmt="grid"))
    
    # Test 4: Itemized Split
    print("\n4️⃣ Testing Itemized Split - Shopping receipt")
    expense_id_4 = bs.create_expense(group_id, 1, 75.00, "Shopping", split_type="itemized")
    items = [
        {'name': 'Milk', 'price': 15.00, 'assigned_users': [1, 2]},  # Alice & Bob
        {'name': 'Bread', 'price': 10.00, 'assigned_users': [2, 3]},  # Bob & Charlie
        {'name': 'Shared Snacks', 'price': 50.00, 'assigned_users': []}  # Everyone (equal split)
    ]
    itemized_splits = bs.split_itemized(expense_id_4, group_id, items)
    
    split_table = []
    for user_id, split_info in itemized_splits.items():
        split_table.append([
            split_info['user_name'],
            f"${split_info['share_amount']:.2f}",
            f"{split_info['percentage']:.1f}%"
        ])
    print(tabulate(split_table, headers=["Name", "Amount", "Percentage"], tablefmt="grid"))
    
    # Test 5: Receipt Processing
    print("\n5️⃣ Testing Complete Receipt Processing")
    receipt_data = {
        'total_amount': 125.75,
        'description': 'Restaurant Bill',
        'location': 'Pizza Palace',
        'receipt_text': 'Pizza Palace\n2x Pizza $25.00\n3x Drinks $15.75\nTax $10.00\nTotal: $125.75',
        'items': [
            {'name': 'Pizza', 'price': 50.00},
            {'name': 'Drinks', 'price': 15.75},
            {'name': 'Tax & Service', 'price': 60.00}
        ]
    }
    
    result = bs.process_receipt_and_split(
        group_id, 2, receipt_data, 
        split_type="equal"
    )
    
    print(f"Receipt processed - Expense ID: {result['expense_id']}")
    print(f"Total Amount: ${result['total_amount']:.2f}")
    
    split_table = []
    for user_id, split_info in result['splits'].items():
        split_table.append([
            split_info['user_name'],
            f"${split_info['share_amount']:.2f}",
            f"{split_info['percentage']:.1f}%"
        ])
    print(tabulate(split_table, headers=["Name", "Amount", "Percentage"], tablefmt="grid"))
    
    # Test 6: Group Balances
    print("\n6️⃣ Current Group Balances:")
    balances = bs.get_group_balances(group_id)
    
    balance_table = []
    for user_id, balance_info in balances.items():
        status_emoji = "💰" if balance_info['status'] == 'owed_money' else "💸" if balance_info['status'] == 'owes_money' else "✅"
        balance_table.append([
            balance_info['name'],
            f"${balance_info['paid']:.2f}",
            f"${balance_info['owes']:.2f}",
            f"${balance_info['balance']:.2f}",
            f"{balance_info['status']} {status_emoji}"
        ])
    
    print(tabulate(balance_table, headers=["Name", "Paid", "Owes", "Balance", "Status"], tablefmt="grid"))
    
    print("\n✅ Bill splitting functionality test completed!")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n🧪 Testing Edge Cases\n")
    
    bs = BillSplitter()
    
    # Test rounding with odd amounts
    print("7️⃣ Testing Rounding - $10.01 split 3 ways")
    expense_id = bs.create_expense(1, 1, 10.01, "Rounding Test")
    splits = bs.split_equal(expense_id, 1, 10.01)
    
    total_check = sum(split['share_amount'] for split in splits.values())
    print(f"Original: $10.01, Total after split: ${total_check:.2f}")
    
    # Test percentage validation
    print("\n8️⃣ Testing Percentage Validation")
    try:
        expense_id = bs.create_expense(1, 1, 100.0, "Bad Percentage Test")
        bs.split_percentage(expense_id, 1, 100.0, {1: 50.0, 2: 30.0})  # Only 80%
    except ValueError as e:
        print(f"✅ Caught expected error: {e}")
    
    print("\n✅ Edge cases test completed!")

if __name__ == "__main__":
    test_bill_splitting()
    test_edge_cases()
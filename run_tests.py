#!/usr/bin/env python3
"""
Main test runner script
Run this to set up database and test all functionality
"""

import os
import sys
import subprocess

def setup_environment():
    """Set up the testing environment"""
    print("🚀 Setting up Google Wallet Groups Test Environment\n")
    
    # Create database directory if it doesn't exist
    os.makedirs('database', exist_ok=True)
    
    # Set up database
    print("📊 Setting up database...")
    from database.setup_database import setup_database
    from database.mock_data import populate_mock_data
    
    setup_database()
    populate_mock_data()
    
    print("✅ Database setup completed!\n")

def run_all_tests():
    """Run all test scripts"""
    print("🧪 Running All Tests\n")
    
    # Run groups tests
    print("=" * 60)
    print("GROUPS MANAGEMENT TESTS")
    print("=" * 60)
    from tests.test_groups import test_groups_functionality
    test_groups_functionality()
    
    print("\n\n")
    
    # Run splitting tests
    print("=" * 60)
    print("BILL SPLITTING TESTS")
    print("=" * 60)
    from tests.test_splitting import test_bill_splitting, test_edge_cases
    test_bill_splitting()
    test_edge_cases()
    
    print("\n\n")
    print("🎉 All tests completed successfully!")
    print("\nYour groups management system is ready for integration!")

def demo_scenarios():
    """Run demo scenarios to show functionality"""
    print("\n🎬 Demo Scenarios\n")
    
    from src.groups_manager import GroupsManager
    from src.bill_splitter import BillSplitter
    
    gm = GroupsManager()
    bs = BillSplitter()
    
    print("Scenario 1: Family creates group and splits restaurant bill")
    print("-" * 55)
    
    # Create family group
    family_group = gm.create_group("Johnson Family", "Family expenses", 1, "family")
    gm.add_member(family_group, 2)  # Add Bob
    gm.add_member(family_group, 4)  # Add Diana
    
    # Process restaurant receipt
    receipt = {
        'total_amount': 89.50,
        'description': 'Family Dinner at Olive Garden',
        'location': 'Olive Garden',
        'receipt_text': 'Family dinner receipt...'
    }
    
    result = bs.process_receipt_and_split(family_group, 1, receipt, "equal")
    
    print(f"✅ Created family group and split ${result['total_amount']:.2f} bill")
    for user_id, split in result['splits'].items():
        print(f"   {split['user_name']}: ${split['share_amount']:.2f}")
    
    print("\nScenario 2: Roommates with different consumption patterns")
    print("-" * 58)
    
    # Use roommates group (ID: 3)
    grocery_receipt = {
        'total_amount': 156.30,
        'description': 'Weekly Groceries',
        'location': 'Supermarket'
    }
    
    # Different percentages based on consumption
    percentage_config = {'percentage_map': {3: 45.0, 4: 35.0, 5: 20.0}}
    
    result = bs.process_receipt_and_split(3, 3, grocery_receipt, "percentage", percentage_config)
    
    print(f"✅ Split ${result['total_amount']:.2f} grocery bill by consumption:")
    for user_id, split in result['splits'].items():
        print(f"   {split['user_name']}: ${split['share_amount']:.2f} ({split['percentage']:.1f}%)")

if __name__ == "__main__":
    # Check if database exists, if not set it up
    if not os.path.exists('database/mock_finance.db'):
        setup_environment()
    
    # Run tests
    run_all_tests()
    
    # Run demo scenarios
    demo_scenarios()
    
    print("\n" + "="*60)
    print("🎯 NEXT STEPS FOR YOUR HACKATHON:")
    print("="*60)
    print("1. Review the code structure and functionality")
    print("2. Integrate with Google Wallet API when you get cloud credits")
    print("3. Add receipt scanning/OCR functionality")
    print("4. Create Google ADK agents based on this foundation")
    print("5. Build frontend interface for your team")
    print("\n💡 Your groups management system is ready for integration!")
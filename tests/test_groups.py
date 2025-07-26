import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.groups_manager import GroupsManager
from tabulate import tabulate

def test_groups_functionality():
    """Test all group management functions"""
    print("🧪 Testing Groups Management Functionality\n")
    
    gm = GroupsManager()
    
    # Test 1: Create new groups
    print("1️⃣ Creating new groups...")
    new_group_id = gm.create_group("Test Group", "Test group for demonstration", 1, "test")
    
    # Test 2: Add members
    print("\n2️⃣ Adding members to groups...")
    gm.add_member(new_group_id, 2)
    gm.add_member(new_group_id, 3)
    
    # Test 3: Get group members
    print("\n3️⃣ Group members:")
    members = gm.get_group_members(new_group_id)
    print(tabulate(members, headers="keys", tablefmt="grid"))
    
    # Test 4: Get user groups
    print("\n4️⃣ Groups for User 1:")
    user_groups = gm.get_user_groups(1)
    print(tabulate(user_groups, headers="keys", tablefmt="grid"))
    
    # Test 5: Group details
    print("\n5️⃣ Detailed group information:")
    details = gm.get_group_details(1)  # Family Trip group
    print(f"Group: {details['name']}")
    print(f"Description: {details['description']}")
    print(f"Creator: {details['creator_name']}")
    print(f"Members: {len(details['members'])}")
    
    # Test 6: List all groups
    print("\n6️⃣ All groups in system:")
    all_groups = gm.list_all_groups()
    print(tabulate(all_groups, headers="keys", tablefmt="grid"))
    
    print("\n✅ Groups functionality test completed!")

if __name__ == "__main__":
    test_groups_functionality()
#!/usr/bin/env python3
"""
Interactive CLI for Google Wallet Groups Management
"""

import os
import sys
from tabulate import tabulate
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.user_manager import UserManager
from src.groups_manager import GroupsManager
from src.bill_splitter import BillSplitter

class GoogleWalletGroupsCLI:
    def __init__(self):
        # Initialize managers
        self.user_manager = UserManager()
        self.groups_manager = GroupsManager()
        self.bill_splitter = BillSplitter()
        
        # Current session user
        self.current_user = None
        
        # Initialize database if needed
        self.ensure_database()
    
    def ensure_database(self):
        """Ensure database is set up"""
        if not os.path.exists('database/mock_finance.db'):
            print("🔧 Setting up database for first time...")
            from database.setup_database import setup_database
            setup_database()
            print("✅ Database created!")
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*60)
        print(f"🏦 GOOGLE WALLET GROUPS - {title.upper()}")
        print("="*60)
    
    def print_menu(self, title, options):
        """Print formatted menu"""
        print(f"\n📋 {title}")
        print("-" * len(title))
        for key, value in options.items():
            print(f"{key}. {value}")
        print("0. Back to Main Menu")
    
    def get_input(self, prompt, input_type=str, required=True, options=None):
        """Get validated input from user"""
        while True:
            try:
                value = input(f"\n{prompt}: ").strip()
                
                if not value and required:
                    print("❌ This field is required!")
                    continue
                
                if not value and not required:
                    return None
                
                # Convert to required type
                if input_type == int:
                    value = int(value)
                elif input_type == float:
                    value = float(value)
                
                # Validate options if provided
                if options and value not in options:
                    print(f"❌ Please choose from: {options}")
                    continue
                
                return value
                
            except ValueError:
                print(f"❌ Please enter a valid {input_type.__name__}!")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                sys.exit()
    
    def select_user(self, prompt="Select user", exclude_ids=None) -> int:
        """Interactive user selection"""
        exclude_ids = exclude_ids or []
        users = self.user_manager.list_all_users()
        available_users = [u for u in users if u['user_id'] not in exclude_ids]
        
        if not available_users:
            print("❌ No users available!")
            return None
        
        print(f"\n{prompt}:")
        for i, user in enumerate(available_users, 1):
            print(f"{i}. {user['name']} ({user['email']})")
        
        choice = self.get_input("Enter choice", int)
        if 1 <= choice <= len(available_users):
            return available_users[choice-1]['user_id']
        
        print("❌ Invalid choice!")
        return None
    
    def select_group(self, user_id=None, prompt="Select group") -> int:
        """Interactive group selection"""
        if user_id:
            groups = self.groups_manager.get_user_groups(user_id)
        else:
            groups = self.groups_manager.list_all_groups()
        
        if not groups:
            print("❌ No groups available!")
            return None
        
        print(f"\n{prompt}:")
        for i, group in enumerate(groups, 1):
            if user_id:
                print(f"{i}. {group['name']} ({group['group_type']}) - Role: {group['role']}")
            else:
                print(f"{i}. {group['name']} ({group['group_type']}) - {group['member_count']} members")
        
        choice = self.get_input("Enter choice", int)
        if 1 <= choice <= len(groups):
            return groups[choice-1]['group_id']
        
        print("❌ Invalid choice!")
        return None
    
    # === MAIN MENU ===
    def main_menu(self):
        """Main application menu"""
        while True:
            self.clear_screen()
            self.print_header("MAIN MENU")
            
            if self.current_user:
                user_info = self.user_manager.get_user_by_id(self.current_user)
                print(f"👤 Logged in as: {user_info['name']} ({user_info['email']})")
            
            options = {
                "1": "👤 User Management",
                "2": "👥 Group Management", 
                "3": "💰 Bill Splitting",
                "4": "📊 View Balances & Reports",
                "5": "🔄 Switch User" if self.current_user else "🔑 Select Current User"
            }
            
            self.print_menu("Main Menu", options)
            
            choice = self.get_input("Enter your choice", int, options=list(range(6)))
            
            if choice == 1:
                self.user_management_menu()
            elif choice == 2:
                self.group_management_menu()
            elif choice == 3:
                self.bill_splitting_menu()
            elif choice == 4:
                self.reports_menu()
            elif choice == 5:
                self.select_current_user()
            elif choice == 0:
                print("\n👋 Thank you for using Google Wallet Groups!")
                break
    
    # === USER MANAGEMENT ===
    def user_management_menu(self):
        """User management submenu"""
        while True:
            self.clear_screen()
            self.print_header("USER MANAGEMENT")
            
            options = {
                "1": "➕ Create New User",
                "2": "📋 List All Users",
                "3": "🔍 Find User by Email",
                "4": "🔍 Find User by Name",
                "5": "✏️ Update User",
                "6": "🗑️ Delete User"
            }
            
            self.print_menu("User Management", options)
            
            choice = self.get_input("Enter your choice", int, options=list(range(7)))
            
            if choice == 1:
                self.create_user()
            elif choice == 2:
                self.list_users()
            elif choice == 3:
                self.find_user_by_email()
            elif choice == 4:
                self.find_user_by_name()
            elif choice == 5:
                self.update_user()
            elif choice == 6:
                self.delete_user()
            elif choice == 0:
                break
    
    def create_user(self):
        """Create a new user"""
        print("\n➕ Creating New User")
        print("-" * 20)
        
        name = self.get_input("Full Name")
        email = self.get_input("Email Address")
        password = self.get_input("Password (optional)", required=False)
        wallet_cred = self.get_input("Google Wallet Credential (optional)", required=False)
        
        user_id = self.user_manager.create_user(name, email, password, wallet_cred)
        
        if user_id:
            print(f"\n✅ User created successfully! User ID: {user_id}")
            
            if not self.current_user:
                use_as_current = self.get_input("Use this as current user? (y/n)", options=['y', 'n', 'Y', 'N'])
                if use_as_current.lower() == 'y':
                    self.current_user = user_id
        
        input("\nPress Enter to continue...")
    
    def list_users(self):
        """List all users"""
        users = self.user_manager.list_all_users()
        
        if not users:
            print("\n❌ No users found!")
        else:
            print(f"\n📋 All Users ({len(users)} total):")
            print(tabulate(users, headers="keys", tablefmt="grid"))
        
        input("\nPress Enter to continue...")
    
    def find_user_by_email(self):
        """Find user by email"""
        email = self.get_input("Enter email to search")
        user = self.user_manager.find_user_by_email(email)
        
        if user:
            print(f"\n✅ User found:")
            print(tabulate([user], headers="keys", tablefmt="grid"))
        else:
            print(f"\n❌ No user found with email: {email}")
        
        input("\nPress Enter to continue...")
    
    def find_user_by_name(self):
        """Find user by name"""
        name = self.get_input("Enter name to search (partial match allowed)")
        users = self.user_manager.find_user_by_name(name)
        
        if users:
            print(f"\n✅ Found {len(users)} user(s):")
            print(tabulate(users, headers="keys", tablefmt="grid"))
        else:
            print(f"\n❌ No users found matching: {name}")
        
        input("\nPress Enter to continue...")
    
    def update_user(self):
        """Update user information"""
        user_id = self.select_user("Select user to update")
        if not user_id:
            return
        
        user = self.user_manager.get_user_by_id(user_id)
        print(f"\nUpdating user: {user['name']} ({user['email']})")
        
        new_name = self.get_input(f"New name (current: {user['name']})", required=False)
        new_email = self.get_input(f"New email (current: {user['email']})", required=False)
        
        if new_name or new_email:
            self.user_manager.update_user(user_id, new_name, new_email)
        else:
            print("No changes made.")
        
        input("\nPress Enter to continue...")
    
    def delete_user(self):
        """Delete a user"""
        user_id = self.select_user("Select user to delete")
        if not user_id:
            return
        
        user = self.user_manager.get_user_by_id(user_id)
        confirm = self.get_input(f"Are you sure you want to delete {user['name']}? (yes/no)", options=['yes', 'no'])
        
        if confirm == 'yes':
            self.user_manager.delete_user(user_id)
            
            if self.current_user == user_id:
                self.current_user = None
                print("⚠️  Current user deleted. Please select a new current user.")
        
        input("\nPress Enter to continue...")
    
    def select_current_user(self):
        """Select current user for session"""
        user_id = self.select_user("Select current user for this session")
        if user_id:
            self.current_user = user_id
            user = self.user_manager.get_user_by_id(user_id)
            print(f"✅ Current user set to: {user['name']}")
        
        input("\nPress Enter to continue...")
    
    # === GROUP MANAGEMENT ===
    def group_management_menu(self):
        """Group management submenu"""
        while True:
            self.clear_screen()
            self.print_header("GROUP MANAGEMENT")
            
            options = {
                "1": "➕ Create New Group",
                "2": "📋 List My Groups",
                "3": "📋 List All Groups",
                "4": "👥 View Group Details",
                "5": "👤 Add Member to Group",
                "6": "🚫 Remove Member from Group",
                "7": "🗑️ Delete Group"
            }
            
            self.print_menu("Group Management", options)
            
            choice = self.get_input("Enter your choice", int, options=list(range(8)))
            
            if choice == 1:
                self.create_group()
            elif choice == 2:
                self.list_my_groups()
            elif choice == 3:
                self.list_all_groups()
            elif choice == 4:
                self.view_group_details()
            elif choice == 5:
                self.add_group_member()
            elif choice == 6:
                self.remove_group_member()
            elif choice == 7:
                self.delete_group()
            elif choice == 0:
                break
    
    def create_group(self):
        """Create a new group"""
        if not self.current_user:
            print("❌ Please select a current user first!")
            input("Press Enter to continue...")
            return
        
        print("\n➕ Creating New Group")
        print("-" * 20)
        
        name = self.get_input("Group Name")
        description = self.get_input("Description (optional)", required=False)
        
        group_types = ["family", "friends", "work", "roommates", "custom"]
        print("\nGroup Types:")
        for i, gtype in enumerate(group_types, 1):
            print(f"{i}. {gtype.title()}")
        
        type_choice = self.get_input("Select group type", int)
        if 1 <= type_choice <= len(group_types):
            group_type = group_types[type_choice-1]
        else:
            group_type = "custom"
        
        group_id = self.groups_manager.create_group(name, description or "", self.current_user, group_type)
        
        print(f"\n✅ Group created successfully! Group ID: {group_id}")
        
        # Ask to add members
        add_members = self.get_input("Add members now? (y/n)", options=['y', 'n', 'Y', 'N'])
        if add_members.lower() == 'y':
            self.add_members_to_group(group_id)
        
        input("\nPress Enter to continue...")
    
    def add_members_to_group(self, group_id):
        """Add multiple members to a group"""
        while True:
            # Get current members to exclude
            current_members = self.groups_manager.get_group_members(group_id)
            current_member_ids = [m['user_id'] for m in current_members]
            
            user_id = self.select_user("Select member to add", exclude_ids=current_member_ids)
            if not user_id:
                break
            
            self.groups_manager.add_member(group_id, user_id)
            
            more = self.get_input("Add another member? (y/n)", options=['y', 'n', 'Y', 'N'])
            if more.lower() != 'y':
                break
    
    def list_my_groups(self):
        """List groups for current user"""
        if not self.current_user:
            print("❌ Please select a current user first!")
            input("Press Enter to continue...")
            return
        
        groups = self.groups_manager.get_user_groups(self.current_user)
        
        if not groups:
            print("\n❌ You are not a member of any groups!")
        else:
            print(f"\n📋 Your Groups ({len(groups)} total):")
            print(tabulate(groups, headers="keys", tablefmt="grid"))
        
        input("\nPress Enter to continue...")
    
    def list_all_groups(self):
        """List all groups in system"""
        groups = self.groups_manager.list_all_groups()
        
        if not groups:
            print("\n❌ No groups found!")
        else:
            print(f"\n📋 All Groups ({len(groups)} total):")
            print(tabulate(groups, headers="keys", tablefmt="grid"))
        
        input("\nPress Enter to continue...")
    
    def view_group_details(self):
        """View detailed group information"""
        group_id = self.select_group(prompt="Select group to view details")
        if not group_id:
            return
        
        details = self.groups_manager.get_group_details(group_id)
        
        print(f"\n📋 Group Details: {details['name']}")
        print("-" * 40)
        print(f"Description: {details['description']}")
        print(f"Type: {details['group_type']}")
        print(f"Creator: {details['creator_name']}")
        print(f"Created: {details['created_at']}")
        
        print(f"\n👥 Members ({len(details['members'])}):")
        if details['members']:
            members_table = []
            for member in details['members']:
                members_table.append([
                    member['name'],
                    member['email'],
                    member['role'],
                    member['joined_at']
                ])
            print(tabulate(members_table, headers=["Name", "Email", "Role", "Joined"], tablefmt="grid"))
        
        input("\nPress Enter to continue...")
    
    def add_group_member(self):
        """Add member to existing group"""
        group_id = self.select_group(self.current_user if self.current_user else None)
        if not group_id:
            return
        
        # Get current members
        current_members = self.groups_manager.get_group_members(group_id)
        current_member_ids = [m['user_id'] for m in current_members]
        
        user_id = self.select_user("Select user to add", exclude_ids=current_member_ids)
        if not user_id:
            return
        
        self.groups_manager.add_member(group_id, user_id)
        input("\nPress Enter to continue...")
    
    def remove_group_member(self):
        """Remove member from group"""
        group_id = self.select_group(self.current_user if self.current_user else None)
        if not group_id:
            return
        
        members = self.groups_manager.get_group_members(group_id)
        if not members:
            print("❌ No members in this group!")
            return
        
        print("\nSelect member to remove:")
        for i, member in enumerate(members, 1):
            print(f"{i}. {member['name']} ({member['role']})")
        
        choice = self.get_input("Enter choice", int)
        if 1 <= choice <= len(members):
            user_id = members[choice-1]['user_id']
            self.groups_manager.remove_member(group_id, user_id)
        else:
            print("❌ Invalid choice!")
        
        input("\nPress Enter to continue...")
    
    # === BILL SPLITTING ===
    def bill_splitting_menu(self):
        """Bill splitting submenu"""
        while True:
            self.clear_screen()
            self.print_header("BILL SPLITTING")
            
            options = {
                "1": "🧾 Process New Receipt/Bill",
                "2": "⚖️ Equal Split",
                "3": "📊 Percentage Split", 
                "4": "💰 Custom Amount Split",
                "5": "📝 Itemized Split",
                "6": "📋 View Recent Expenses"
            }
            
            self.print_menu("Bill Splitting", options)
            
            choice = self.get_input("Enter your choice", int, options=list(range(7)))
            
            if choice == 1:
                self.process_receipt()
            elif choice == 2:
                self.equal_split()
            elif choice == 3:
                self.percentage_split()
            elif choice == 4:
                self.custom_amount_split()
            elif choice == 5:
                self.itemized_split()
            elif choice == 6:
                self.view_recent_expenses()
            elif choice == 0:
                break
    
    def process_receipt(self):
        """Process a complete receipt"""
        if not self.current_user:
            print("❌ Please select a current user first!")
            input("Press Enter to continue...")
            return
        
        group_id = self.select_group(self.current_user)
        if not group_id:
            return
        
        print("\n🧾 Processing Receipt")
        print("-" * 20)
        
        total_amount = self.get_input("Total Amount", float)
        description = self.get_input("Description")
        location = self.get_input("Location (optional)", required=False)
        receipt_text = self.get_input("Receipt Text (optional)", required=False)
        
        # Select split type
        split_types = ["equal", "percentage", "custom", "itemized"]
        print("\nSplit Types:")
        for i, stype in enumerate(split_types, 1):
            print(f"{i}. {stype.title()}")
        
        split_choice = self.get_input("Select split type", int)
        if 1 <= split_choice <= len(split_types):
            split_type = split_types[split_choice-1]
        else:
            split_type = "equal"
        
        # Prepare receipt data
        receipt_data = {
            'total_amount': total_amount,
            'description': description,
            'location': location,
            'receipt_text': receipt_text
        }
        
        # Get split configuration based on type
        split_config = None
        if split_type == "percentage":
            split_config = self.get_percentage_config(group_id)
        elif split_type == "custom":
            split_config = self.get_custom_amount_config(group_id, total_amount)
        elif split_type == "itemized":
            receipt_data['items'] = self.get_itemized_config(group_id)
        
        # Process the receipt
        try:
            result = self.bill_splitter.process_receipt_and_split(
                group_id, self.current_user, receipt_data, split_type, split_config
            )
            
            self.display_split_results(result)
            
        except Exception as e:
            print(f"❌ Error processing receipt: {e}")
        
        input("\nPress Enter to continue...")
    
    def equal_split(self):
        """Create equal split expense"""
        if not self.current_user:
            print("❌ Please select a current user first!")
            input("Press Enter to continue...")
            return
        
        group_id = self.select_group(self.current_user)
        if not group_id:
            return
        
        print("\n⚖️ Equal Split")
        print("-" * 15)
        
        amount = self.get_input("Total Amount", float)
        description = self.get_input("Description")
        
        expense_id = self.bill_splitter.create_expense(group_id, self.current_user, amount, description, split_type="equal")
        splits = self.bill_splitter.split_equal(expense_id, group_id, amount)
        
        result = {
            'expense_id': expense_id,
            'total_amount': amount,
            'split_type': 'equal',
            'splits': splits
        }
        
        self.display_split_results(result)
        input("\nPress Enter to continue...")
    
    def percentage_split(self):
        """Create percentage-based split"""
        if not self.current_user:
            print("❌ Please select a current user first!")
            input("Press Enter to continue...")
            return
        
        group_id = self.select_group(self.current_user)
        if not group_id:
            return
        
        print("\n📊 Percentage Split")
        print("-" * 18)
        
        amount = self.get_input("Total Amount", float)
        description = self.get_input("Description")
        
        percentage_map = self.get_percentage_config(group_id)['percentage_map']
        
        expense_id = self.bill_splitter.create_expense(group_id, self.current_user, amount, description, split_type="percentage")
        splits = self.bill_splitter.split_percentage(expense_id, group_id, amount, percentage_map)
        
        result = {
            'expense_id': expense_id,
            'total_amount': amount,
            'split_type': 'percentage',
            'splits': splits
        }
        
        self.display_split_results(result)
        input("\nPress Enter to continue...")
    
    def custom_amount_split(self):
        """Create custom amount split"""
        if not self.current_user:
            print("❌ Please select a current user first!")
            input("Press Enter to continue...")
            return
        
        group_id = self.select_group(self.current_user)
        if not group_id:
            return
        
        print("\n💰 Custom Amount Split")
        print("-" * 22)
        
        amount = self.get_input("Total Amount", float)
        description = self.get_input("Description")
        
        amount_map = self.get_custom_amount_config(group_id, amount)['amount_map']
        
        expense_id = self.bill_splitter.create_expense(group_id, self.current_user, amount, description, split_type="custom")
        splits = self.bill_splitter.split_custom_amounts(expense_id, group_id, amount, amount_map)
        
        result = {
            'expense_id': expense_id,
            'total_amount': amount,
            'split_type': 'custom',
            'splits': splits
        }
        
        self.display_split_results(result)
        input("\nPress Enter to continue...")
    
    def itemized_split(self):
        """Create itemized split"""
        if not self.current_user:
            print("❌ Please select a current user first!")
            input("Press Enter to continue...")
            return
        
        group_id = self.select_group(self.current_user)
        if not group_id:
            return
        
        print("\n📝 Itemized Split")
        print("-" * 17)
        
        description = self.get_input("Description")
        items = self.get_itemized_config(group_id)
        
        total_amount = sum(item['price'] for item in items)
        
        expense_id = self.bill_splitter.create_expense(group_id, self.current_user, total_amount, description, split_type="itemized")
        splits = self.bill_splitter.split_itemized(expense_id, group_id, items)
        
        result = {
            'expense_id': expense_id,
            'total_amount': total_amount,
            'split_type': 'itemized',
            'splits': splits
        }
        
        self.display_split_results(result)
        input("\nPress Enter to continue...")
    
    def get_percentage_config(self, group_id):
        """Get percentage configuration from user"""
        members = self.groups_manager.get_group_members(group_id)
        percentage_map = {}
        total_percentage = 0
        
        print("\nEnter percentage for each member:")
        for member in members:
            while True:
                try:
                    percentage = float(input(f"{member['name']}: "))
                    if 0 <= percentage <= 100:
                        percentage_map[member['user_id']] = percentage
                        total_percentage += percentage
                        break
                    else:
                        print("❌ Percentage must be between 0 and 100!")
                except ValueError:
                    print("❌ Please enter a valid number!")
        
        if abs(total_percentage - 100.0) > 0.01:
            print(f"⚠️  Warning: Total percentage is {total_percentage}%, not 100%")
            confirm = self.get_input("Continue anyway? (y/n)", options=['y', 'n', 'Y', 'N'])
            if confirm.lower() != 'y':
                return self.get_percentage_config(group_id)
        
        return {'percentage_map': percentage_map}
    
    def get_custom_amount_config(self, group_id, total_amount):
        """Get custom amount configuration from user"""
        members = self.groups_manager.get_group_members(group_id)
        amount_map = {}
        assigned_total = 0
        
        print(f"\nEnter amount for each member (Total: ${total_amount:.2f}):")
        for member in members:
            while True:
                try:
                    amount = float(input(f"{member['name']}: $"))
                    if amount >= 0:
                        amount_map[member['user_id']] = amount
                        assigned_total += amount
                        break
                    else:
                        print("❌ Amount must be positive!")
                except ValueError:
                    print("❌ Please enter a valid number!")
        
        if abs(assigned_total - total_amount) > 0.01:
            print(f"⚠️  Warning: Assigned total is ${assigned_total:.2f}, bill total is ${total_amount:.2f}")
            confirm = self.get_input("Continue anyway? (y/n)", options=['y', 'n', 'Y', 'N'])
            if confirm.lower() != 'y':
                return self.get_custom_amount_config(group_id, total_amount)
        
        return {'amount_map': amount_map}
    
    def get_itemized_config(self, group_id):
        """Get itemized configuration from user"""
        members = self.groups_manager.get_group_members(group_id)
        items = []
        
        print("\nEnter items (press Enter with empty name to finish):")
        while True:
            name = self.get_input("Item name", required=False)
            if not name:
                break
            
            price = self.get_input("Item price", float)
            
            print("Who should pay for this item?")
            print("0. Everyone (equal split)")
            for i, member in enumerate(members, 1):
                print(f"{i}. {member['name']}")
            
            assigned_users = []
            while True:
                choice = self.get_input("Enter choice (0 for everyone, or member numbers separated by commas)", str)
                
                if choice == "0":
                    assigned_users = []  # Empty means everyone
                    break
                
                try:
                    choices = [int(c.strip()) for c in choice.split(',')]
                    if all(1 <= c <= len(members) for c in choices):
                        assigned_users = [members[c-1]['user_id'] for c in choices]
                        break
                    else:
                        print("❌ Invalid member numbers!")
                except ValueError:
                    print("❌ Please enter valid numbers separated by commas!")
            
            items.append({
                'name': name,
                'price': price,
                'assigned_users': assigned_users
            })
            
            print(f"✅ Added: {name} - ${price:.2f}")
        
        return items
    
    def display_split_results(self, result):
        """Display split results in a nice format"""
        print(f"\n✅ Split Results - Expense ID: {result['expense_id']}")
        print(f"💰 Total Amount: ${result['total_amount']:.2f}")
        print(f"🔄 Split Type: {result['split_type'].title()}")
        print("-" * 40)
        
        split_table = []
        for user_id, split_info in result['splits'].items():
            split_table.append([
                split_info['user_name'],
                f"${split_info['share_amount']:.2f}",
                f"{split_info['percentage']:.1f}%"
            ])
        
        print(tabulate(split_table, headers=["Name", "Amount", "Percentage"], tablefmt="grid"))
    
    def view_recent_expenses(self):
        """View recent expenses"""
        if not self.current_user:
            print("❌ Please select a current user first!")
            input("Press Enter to continue...")
            return
        
        group_id = self.select_group(self.current_user)
        if not group_id:
            return
        
        # Get recent expenses for the group
        query = """
            SELECT e.expense_id, e.description, e.amount, e.expense_date, 
                   u.name as payer, e.split_type
            FROM expenses e
            JOIN users u ON e.payer_id = u.user_id
            WHERE e.group_id = ?
            ORDER BY e.created_at DESC
            LIMIT 10
        """
        
        results = self.bill_splitter.db.execute_query(query, (group_id,), fetch=True)
        
        if not results:
            print("\n❌ No expenses found for this group!")
        else:
            expenses = []
            for row in results:
                expenses.append({
                    'expense_id': row[0],
                    'description': row[1],
                    'amount': f"${row[2]:.2f}",
                    'date': row[3],
                    'payer': row[4],
                    'split_type': row[5]
                })
            
            print(f"\n📋 Recent Expenses:")
            print(tabulate(expenses, headers="keys", tablefmt="grid"))
        
        input("\nPress Enter to continue...")
    
    # === REPORTS ===
    def reports_menu(self):
        """Reports and balances submenu"""
        while True:
            self.clear_screen()
            self.print_header("BALANCES & REPORTS")
            
            options = {
                "1": "💰 View Group Balances",
                "2": "👤 My Balance Summary",
                "3": "📊 Group Expense Summary",
                "4": "🔍 Settlement Suggestions"
            }
            
            self.print_menu("Reports", options)
            
            choice = self.get_input("Enter your choice", int, options=list(range(5)))
            
            if choice == 1:
                self.view_group_balances()
            elif choice == 2:
                self.my_balance_summary()
            elif choice == 3:
                self.group_expense_summary()
            elif choice == 4:
                self.settlement_suggestions()
            elif choice == 0:
                break
    
    def view_group_balances(self):
        """View balances for a specific group"""
        if not self.current_user:
            print("❌ Please select a current user first!")
            input("Press Enter to continue...")
            return
        
        group_id = self.select_group(self.current_user)
        if not group_id:
            return
        
        balances = self.bill_splitter.get_group_balances(group_id)
        group_name = self.groups_manager.get_group_name(group_id)
        
        print(f"\n💰 Balances for '{group_name}'")
        print("-" * 40)
        
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
        
        print(tabulate(balance_table, headers=["Name", "Paid", "Owes", "Net Balance", "Status"], tablefmt="grid"))
        
        input("\nPress Enter to continue...")
    
    def my_balance_summary(self):
        """Show balance summary for current user across all groups"""
        if not self.current_user:
            print("❌ Please select a current user first!")
            input("Press Enter to continue...")
            return
        
        user_groups = self.groups_manager.get_user_groups(self.current_user)
        
        if not user_groups:
            print("\n❌ You are not a member of any groups!")
            input("Press Enter to continue...")
            return
        
        user_name = self.user_manager.get_user_by_id(self.current_user)['name']
        print(f"\n👤 Balance Summary for {user_name}")
        print("-" * 40)
        
        summary_table = []
        total_paid = 0
        total_owes = 0
        
        for group in user_groups:
            balances = self.bill_splitter.get_group_balances(group['group_id'])
            if self.current_user in balances:
                balance_info = balances[self.current_user]
                total_paid += balance_info['paid']
                total_owes += balance_info['owes']
                
                summary_table.append([
                    group['name'],
                    f"${balance_info['paid']:.2f}",
                    f"${balance_info['owes']:.2f}",
                    f"${balance_info['balance']:.2f}"
                ])
        
        print(tabulate(summary_table, headers=["Group", "Paid", "Owes", "Net Balance"], tablefmt="grid"))
        
        net_balance = total_paid - total_owes
        print(f"\n📊 Overall Summary:")
        print(f"Total Paid: ${total_paid:.2f}")
        print(f"Total Owes: ${total_owes:.2f}")
        print(f"Net Balance: ${net_balance:.2f}")
        
        if net_balance > 0:
            print("💰 You are owed money overall!")
        elif net_balance < 0:
            print("💸 You owe money overall!")
        else:
            print("✅ You are settled overall!")
        
        input("\nPress Enter to continue...")
    
    def group_expense_summary(self):
        """Show expense summary for a group"""
        if not self.current_user:
            print("❌ Please select a current user first!")
            input("Press Enter to continue...")
            return
        
        group_id = self.select_group(self.current_user)
        if not group_id:
            return
        
        query = """
            SELECT 
                COUNT(*) as total_expenses,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount,
                MIN(amount) as min_amount,
                MAX(amount) as max_amount,
                split_type,
                COUNT(*) as count_by_type
            FROM expenses 
            WHERE group_id = ?
            GROUP BY split_type
        """
        
        results = self.bill_splitter.db.execute_query(query, (group_id,), fetch=True)
        group_name = self.groups_manager.get_group_name(group_id)
        
        print(f"\n📊 Expense Summary for '{group_name}'")
        print("-" * 40)
        
        if not results:
            print("❌ No expenses found for this group!")
        else:
            total_expenses = 0
            total_amount = 0
            
            split_summary = []
            for row in results:
                split_summary.append([
                    row[5].title(),
                    row[6],
                    f"${sum(r[1] for r in results if r[5] == row[5]):.2f}"
                ])
                total_expenses += row[6]
                total_amount += sum(r[1] for r in results if r[5] == row[5])
            
            print(tabulate(split_summary, headers=["Split Type", "Count", "Total Amount"], tablefmt="grid"))
            
            print(f"\n📈 Overall Statistics:")
            print(f"Total Expenses: {total_expenses}")
            print(f"Total Amount: ${total_amount:.2f}")
            if total_expenses > 0:
                print(f"Average per Expense: ${total_amount/total_expenses:.2f}")
        
        input("\nPress Enter to continue...")
    
    def settlement_suggestions(self):
        """Suggest settlements to minimize transactions"""
        if not self.current_user:
            print("❌ Please select a current user first!")
            input("Press Enter to continue...")
            return
        
        group_id = self.select_group(self.current_user)
        if not group_id:
            return
        
        balances = self.bill_splitter.get_group_balances(group_id)
        group_name = self.groups_manager.get_group_name(group_id)
        
        # Separate creditors and debtors
        creditors = []  # People who are owed money
        debtors = []    # People who owe money
        
        for user_id, balance_info in balances.items():
            if balance_info['balance'] > 0.01:  # Owed money
                creditors.append((user_id, balance_info['name'], balance_info['balance']))
            elif balance_info['balance'] < -0.01:  # Owes money
                debtors.append((user_id, balance_info['name'], -balance_info['balance']))
        
        print(f"\n🔍 Settlement Suggestions for '{group_name}'")
        print("-" * 40)
        
        if not creditors and not debtors:
            print("✅ Everyone is settled! No transactions needed.")
        else:
            suggestions = []
            
            # Simple settlement algorithm
            i, j = 0, 0
            while i < len(creditors) and j < len(debtors):
                creditor_id, creditor_name, credit_amount = creditors[i]
                debtor_id, debtor_name, debt_amount = debtors[j]
                
                # Amount to settle
                settle_amount = min(credit_amount, debt_amount)
                
                suggestions.append([
                    debtor_name,
                    creditor_name,
                    f"${settle_amount:.2f}"
                ])
                
                # Update remaining amounts
                creditors[i] = (creditor_id, creditor_name, credit_amount - settle_amount)
                debtors[j] = (debtor_id, debtor_name, debt_amount - settle_amount)
                
                # Move to next if settled
                if creditors[i][2] < 0.01:
                    i += 1
                if debtors[j][2] < 0.01:
                    j += 1
            
            if suggestions:
                print("💡 Suggested Transactions:")
                print(tabulate(suggestions, headers=["From", "To", "Amount"], tablefmt="grid"))
                print(f"\nTotal transactions needed: {len(suggestions)}")
            else:
                print("✅ No settlements needed!")
        
        input("\nPress Enter to continue...")

def main():
    """Main application entry point"""
    app = GoogleWalletGroupsCLI()
    
    try:
        app.main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Thank you for using Google Wallet Groups!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please report this issue to the development team.")

if __name__ == "__main__":
    main()
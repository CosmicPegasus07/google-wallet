import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.utils import DatabaseManager, round_to_cents, calculate_percentage

class BillSplitter:
    def __init__(self, db_path='database/mock_finance.db'):
        self.db = DatabaseManager(db_path)
    
    def create_expense(self, group_id: int, payer_id: int, amount: float, 
                      description: str, expense_date: str = None, 
                      location: str = None, expense_type: str = 'general',
                      split_type: str = 'equal') -> int:
        """Create a new expense record"""
        if not expense_date:
            expense_date = datetime.now().strftime('%Y-%m-%d')
        
        query = """
            INSERT INTO expenses (group_id, payer_id, amount, currency, description, 
                                expense_date, location, type, split_type) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        expense_id = self.db.execute_query(
            query, (group_id, payer_id, amount, 'USD', description, 
                   expense_date, location, expense_type, split_type)
        )
        
        print(f"✅ Expense created with ID: {expense_id}")
        return expense_id
    
    def split_equal(self, expense_id: int, group_id: int, total_amount: float, 
                   excluded_users: List[int] = None) -> Dict:
        """Split bill equally among group members"""
        excluded_users = excluded_users or []
        
        # Get group members
        members = self.get_group_members(group_id)
        eligible_members = [m for m in members if m['user_id'] not in excluded_users]
        
        if not eligible_members:
            raise ValueError("No eligible members to split the bill")
        
        # Calculate equal share
        num_members = len(eligible_members)
        equal_share = round_to_cents(total_amount / num_members)
        
        # Handle rounding differences
        remaining_amount = total_amount - (equal_share * num_members)
        
        splits = {}
        for i, member in enumerate(eligible_members):
            share = equal_share
            # Add remaining cents to first member(s)
            if i == 0 and remaining_amount != 0:
                share += round_to_cents(remaining_amount)
            
            splits[member['user_id']] = {
                'user_name': member['name'],
                'share_amount': share,
                'percentage': round((share / total_amount) * 100, 2)
            }
            
            # Insert into database
            self.insert_expense_share(expense_id, member['user_id'], share, 
                                    splits[member['user_id']]['percentage'])
        
        print(f"✅ Equal split completed for {num_members} members")
        return splits
    
    def split_percentage(self, expense_id: int, group_id: int, total_amount: float,
                        percentage_map: Dict[int, float]) -> Dict:
        """Split bill based on custom percentages"""
        # Validate percentages sum to 100
        total_percentage = sum(percentage_map.values())
        if abs(total_percentage - 100.0) > 0.01:
            raise ValueError(f"Percentages must sum to 100%, got {total_percentage}%")
        
        splits = {}
        total_assigned = 0
        
        for user_id, percentage in percentage_map.items():
            share_amount = round_to_cents(calculate_percentage(total_amount, percentage))
            total_assigned += share_amount
            
            user_name = self.get_user_name(user_id)
            splits[user_id] = {
                'user_name': user_name,
                'share_amount': share_amount,
                'percentage': percentage
            }
            
            self.insert_expense_share(expense_id, user_id, share_amount, percentage)
        
        # Handle rounding differences
        difference = round_to_cents(total_amount - total_assigned)
        if difference != 0:
            # Add difference to the first user
            first_user = list(percentage_map.keys())[0]
            splits[first_user]['share_amount'] += difference
            
            # Update database
            self.update_expense_share(expense_id, first_user, 
                                    splits[first_user]['share_amount'])
        
        print(f"✅ Percentage split completed for {len(percentage_map)} members")
        return splits
    
    def split_custom_amounts(self, expense_id: int, group_id: int, total_amount: float,
                           amount_map: Dict[int, float]) -> Dict:
        """Split bill with custom amounts for each person"""
        total_assigned = sum(amount_map.values())
        
        if abs(total_assigned - total_amount) > 0.01:
            raise ValueError(f"Custom amounts ({total_assigned}) don't match total ({total_amount})")
        
        splits = {}
        for user_id, amount in amount_map.items():
            share_amount = round_to_cents(amount)
            percentage = round((share_amount / total_amount) * 100, 2)
            
            user_name = self.get_user_name(user_id)
            splits[user_id] = {
                'user_name': user_name,
                'share_amount': share_amount,
                'percentage': percentage
            }
            
            self.insert_expense_share(expense_id, user_id, share_amount, percentage)
        
        print(f"✅ Custom amount split completed for {len(amount_map)} members")
        return splits
    
    def split_itemized(self, expense_id: int, group_id: int, items: List[Dict],
                      default_split: str = 'equal') -> Dict:
        """Split bill based on itemized purchases"""
        # items = [{'name': 'Pizza', 'price': 25.00, 'assigned_users': [1, 2]}, ...]
        
        user_totals = {}
        total_amount = 0
        
        for item in items:
            item_price = item['price']
            assigned_users = item.get('assigned_users', [])
            
            # Insert item into database
            assigned_users_json = json.dumps(assigned_users) if assigned_users else None
            item_query = """
                INSERT INTO expense_items (expense_id, name, unit_price, total_price, assigned_users)
                VALUES (?, ?, ?, ?, ?)
            """
            self.db.execute_query(item_query, (expense_id, item['name'], item_price, 
                                             item_price, assigned_users_json))
            
            if assigned_users:
                # Split among assigned users
                per_person = round_to_cents(item_price / len(assigned_users))
                for user_id in assigned_users:
                    user_totals[user_id] = user_totals.get(user_id, 0) + per_person
            else:
                # Will be split according to default_split method
                total_amount += item_price
        
        # Handle items without specific assignment
        if total_amount > 0:
            if default_split == 'equal':
                members = self.get_group_members(group_id)
                per_person = round_to_cents(total_amount / len(members))
                for member in members:
                    user_totals[member['user_id']] = user_totals.get(member['user_id'], 0) + per_person
        
        # Convert to splits format and save to database
        splits = {}
        grand_total = sum(user_totals.values())
        
        for user_id, amount in user_totals.items():
            user_name = self.get_user_name(user_id)
            percentage = round((amount / grand_total) * 100, 2) if grand_total > 0 else 0
            
            splits[user_id] = {
                'user_name': user_name,
                'share_amount': round_to_cents(amount),
                'percentage': percentage
            }
            
            self.insert_expense_share(expense_id, user_id, splits[user_id]['share_amount'], percentage)
        
        print(f"✅ Itemized split completed for {len(items)} items")
        return splits
    
    def process_receipt_and_split(self, group_id: int, payer_id: int, receipt_data: Dict,
                                split_type: str = 'equal', split_config: Dict = None) -> Dict:
        """Process receipt and create expense with splits"""
        # Extract data from receipt
        total_amount = receipt_data.get('total_amount', 0)
        description = receipt_data.get('description', 'Receipt expense')
        location = receipt_data.get('location', '')
        items = receipt_data.get('items', [])
        
        # Create expense
        expense_id = self.create_expense(
            group_id, payer_id, total_amount, description, 
            location=location, split_type=split_type
        )
        
        # Apply splitting logic
        if split_type == 'equal':
            excluded_users = split_config.get('excluded_users', []) if split_config else []
            splits = self.split_equal(expense_id, group_id, total_amount, excluded_users)
        
        elif split_type == 'percentage':
            if not split_config or 'percentage_map' not in split_config:
                raise ValueError("Percentage map required for percentage split")
            splits = self.split_percentage(expense_id, group_id, total_amount, 
                                         split_config['percentage_map'])
        
        elif split_type == 'custom':
            if not split_config or 'amount_map' not in split_config:
                raise ValueError("Amount map required for custom split")
            splits = self.split_custom_amounts(expense_id, group_id, total_amount,
                                             split_config['amount_map'])
        
        elif split_type == 'itemized':
            if not items:
                raise ValueError("Items required for itemized split")
            splits = self.split_itemized(expense_id, group_id, items, 
                                       split_config.get('default_split', 'equal') if split_config else 'equal')
        
        else:
            raise ValueError(f"Unknown split type: {split_type}")
        
        # Store receipt data
        if receipt_data.get('receipt_text'):
            receipt_query = """
                INSERT INTO expense_receipts (expense_id, url, receipt_text)
                VALUES (?, ?, ?)
            """
            self.db.execute_query(receipt_query, (expense_id, 'local_receipt', 
                                                receipt_data['receipt_text']))
        
        return {
            'expense_id': expense_id,
            'total_amount': total_amount,
            'split_type': split_type,
            'splits': splits
        }
    
    def get_group_balances(self, group_id: int) -> Dict:
        """Calculate who owes what in a group"""
        query = """
            SELECT 
                u.user_id,
                u.name,
                COALESCE(SUM(CASE WHEN e.payer_id = u.user_id THEN e.amount ELSE 0 END), 0) as paid,
                COALESCE(SUM(es.share_amount), 0) as owes
            FROM users u
            JOIN user_groups ug ON u.user_id = ug.user_id
            LEFT JOIN expenses e ON e.group_id = ug.group_id
            LEFT JOIN expense_shares es ON es.user_id = u.user_id AND es.expense_id = e.expense_id
            WHERE ug.group_id = ?
            GROUP BY u.user_id, u.name
            ORDER BY u.name
        """
        
        results = self.db.execute_query(query, (group_id,), fetch=True)
        
        balances = {}
        for row in results:
            user_id, name, paid, owes = row
            balance = round_to_cents(paid - owes)
            
            balances[user_id] = {
                'name': name,
                'paid': round_to_cents(paid),
                'owes': round_to_cents(owes),
                'balance': balance,
                'status': 'owes_money' if balance < 0 else 'owed_money' if balance > 0 else 'settled'
            }
        
        return balances
    
    # Helper methods
    def insert_expense_share(self, expense_id: int, user_id: int, 
                           share_amount: float, percentage: float = None):
        """Insert expense share into database"""
        query = """
            INSERT INTO expense_shares (expense_id, user_id, share_amount, percentage)
            VALUES (?, ?, ?, ?)
        """
        self.db.execute_query(query, (expense_id, user_id, share_amount, percentage))
    
    def update_expense_share(self, expense_id: int, user_id: int, new_amount: float):
        """Update existing expense share"""
        query = """
            UPDATE expense_shares 
            SET share_amount = ? 
            WHERE expense_id = ? AND user_id = ?
        """
        self.db.execute_query(query, (new_amount, expense_id, user_id))
    
    def get_group_members(self, group_id: int) -> List[Dict]:
        """Get group members (reused from GroupsManager)"""
        query = """
            SELECT u.user_id, u.name, u.email
            FROM users u
            JOIN user_groups ug ON u.user_id = ug.user_id
            WHERE ug.group_id = ?
        """
        results = self.db.execute_query(query, (group_id,), fetch=True)
        
        return [{'user_id': row[0], 'name': row[1], 'email': row[2]} for row in results]
    
    def get_user_name(self, user_id: int) -> str:
        """Get user name by ID"""
        query = "SELECT name FROM users WHERE user_id = ?"
        result = self.db.execute_query(query, (user_id,), fetch=True)
        return result[0][0] if result else f"User_{user_id}"
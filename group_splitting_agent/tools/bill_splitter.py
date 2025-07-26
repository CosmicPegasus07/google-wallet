import json
from typing import List, Dict
from group_splitting_agent.tools.utils import round_to_cents, calculate_percentage
from group_splitting_agent.tools.sql_execution import execute_query


def split_equal(total_amount: float, eligible_members: List[int]) -> Dict:
    """Split bill equally among group members"""
    
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

    return splits

def split_percentage(total_amount: float,
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
        
        # Get user name from database
        user_query = f"SELECT name FROM users WHERE user_id = {user_id}"
        user_result = execute_query(user_query)
        user_name = user_result[0][0] if user_result else f"User {user_id}"
        splits[user_id] = {
            'user_name': user_name,
            'share_amount': share_amount,
            'percentage': percentage
        }
    
    
    # Handle rounding differences
    difference = round_to_cents(total_amount - total_assigned)
    if difference != 0:
        # Add difference to the first user
        first_user = list(percentage_map.keys())[0]
        splits[first_user]['share_amount'] += difference
    
    return splits

def split_custom_amounts(expense_id: int, group_id: int, total_amount: float,
                        amount_map: Dict[int, float]) -> Dict:
    """Split bill with custom amounts for each person"""
    total_assigned = sum(amount_map.values())
    
    if abs(total_assigned - total_amount) > 0.01:
        raise ValueError(f"Custom amounts ({total_assigned}) don't match total ({total_amount})")
    
    splits = {}
    for user_id, amount in amount_map.items():
        share_amount = round_to_cents(amount)
        percentage = round((share_amount / total_amount) * 100, 2)
        
        # Get user name from database
        user_query = f"SELECT name FROM users WHERE user_id = {user_id}"
        user_result = execute_query(user_query)
        user_name = user_result[0][0] if user_result else f"User {user_id}"
        splits[user_id] = {
            'user_name': user_name,
            'share_amount': share_amount,
            'percentage': percentage
        }
        
    
    return splits

def split_itemized(expense_id: int, group_id: int, items: List[Dict],
                    default_split: str = 'equal') -> Dict:
    """Split bill based on itemized purchases"""
    # items = [{'name': 'Pizza', 'price': 25.00, 'assigned_users': [1, 2]}, ...]
    
    user_totals = {}
    total_amount = 0
    
    for item in items:
        item_price = item['price']
        assigned_users = item.get('assigned_users', [])

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
            # Get group members from database
            members_query = f"""
                SELECT u.user_id, u.name
                FROM users u
                JOIN user_groups ug ON u.user_id = ug.user_id
                WHERE ug.group_id = {group_id}
            """
            members_result = execute_query(members_query)
            members = [{'user_id': row[0], 'name': row[1]} for row in members_result]
            per_person = round_to_cents(total_amount / len(members))
            for member in members:
                user_totals[member['user_id']] = user_totals.get(member['user_id'], 0) + per_person
    
    # Convert to splits format and save to database
    splits = {}
    grand_total = sum(user_totals.values())
    
    for user_id, amount in user_totals.items():
        # Get user name from database
        user_query = f"SELECT name FROM users WHERE user_id = {user_id}"
        user_result = execute_query(user_query)
        user_name = user_result[0][0] if user_result else f"User {user_id}"
        percentage = round((amount / grand_total) * 100, 2) if grand_total > 0 else 0
        
        splits[user_id] = {
            'user_name': user_name,
            'share_amount': round_to_cents(amount),
            'percentage': percentage
        }
    
    return splits



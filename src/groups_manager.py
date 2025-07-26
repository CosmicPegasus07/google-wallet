import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.utils import DatabaseManager

class GroupsManager:
    def __init__(self, db_path='database/mock_finance.db'):
        self.db = DatabaseManager(db_path)
    
    def create_group(self, name: str, description: str, created_by: int, 
                    group_type: str = 'custom') -> int:
        """Create a new group"""
        query = """
            INSERT INTO groups (name, description, created_by, group_type) 
            VALUES (?, ?, ?, ?)
        """
        group_id = self.db.execute_query(query, (name, description, created_by, group_type))
        
        # Add creator as admin
        self.add_member(group_id, created_by, role='admin')
        
        print(f"✅ Group '{name}' created with ID: {group_id}")
        return group_id
    
    def add_member(self, group_id: int, user_id: int, role: str = 'member') -> bool:
        """Add a member to a group"""
        try:
            query = """
                INSERT INTO user_groups (user_id, group_id, role) 
                VALUES (?, ?, ?)
            """
            self.db.execute_query(query, (user_id, group_id, role))
            
            # Get user and group names for confirmation
            user_name = self.get_user_name(user_id)
            group_name = self.get_group_name(group_id)
            print(f"✅ Added {user_name} to '{group_name}' as {role}")
            return True
        except sqlite3.IntegrityError:
            print(f"❌ User {user_id} is already in group {group_id}")
            return False
    
    def remove_member(self, group_id: int, user_id: int) -> bool:
        """Remove a member from a group"""
        query = "DELETE FROM user_groups WHERE user_id = ? AND group_id = ?"
        self.db.execute_query(query, (user_id, group_id))
        
        user_name = self.get_user_name(user_id)
        group_name = self.get_group_name(group_id)
        print(f"✅ Removed {user_name} from '{group_name}'")
        return True
    
    def get_group_members(self, group_id: int) -> List[Dict]:
        """Get all members of a group"""
        query = """
            SELECT u.user_id, u.name, u.email, ug.role, ug.joined_at
            FROM users u
            JOIN user_groups ug ON u.user_id = ug.user_id
            WHERE ug.group_id = ?
            ORDER BY ug.joined_at
        """
        results = self.db.execute_query(query, (group_id,), fetch=True)
        
        members = []
        for row in results:
            members.append({
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'role': row[3],
                'joined_at': row[4]
            })
        
        return members
    
    def get_user_groups(self, user_id: int) -> List[Dict]:
        """Get all groups for a user"""
        query = """
            SELECT g.group_id, g.name, g.description, g.group_type, 
                   ug.role, g.created_at
            FROM groups g
            JOIN user_groups ug ON g.group_id = ug.group_id
            WHERE ug.user_id = ?
            ORDER BY g.created_at DESC
        """
        results = self.db.execute_query(query, (user_id,), fetch=True)
        
        groups = []
        for row in results:
            groups.append({
                'group_id': row[0],
                'name': row[1],
                'description': row[2],
                'group_type': row[3],
                'role': row[4],
                'created_at': row[5]
            })
        
        return groups
    
    def get_group_details(self, group_id: int) -> Dict:
        """Get detailed information about a group"""
        query = """
            SELECT g.group_id, g.name, g.description, g.group_type, 
                   g.created_at, u.name as creator_name
            FROM groups g
            JOIN users u ON g.created_by = u.user_id
            WHERE g.group_id = ?
        """
        result = self.db.execute_query(query, (group_id,), fetch=True)
        
        if not result:
            return None
        
        row = result[0]
        group_details = {
            'group_id': row[0],
            'name': row[1],
            'description': row[2],
            'group_type': row[3],
            'created_at': row[4],
            'creator_name': row[5],
            'members': self.get_group_members(group_id)
        }
        
        return group_details
    
    def get_user_name(self, user_id: int) -> str:
        """Get user name by ID"""
        query = "SELECT name FROM users WHERE user_id = ?"
        result = self.db.execute_query(query, (user_id,), fetch=True)
        return result[0][0] if result else f"User_{user_id}"
    
    def get_group_name(self, group_id: int) -> str:
        """Get group name by ID"""
        query = "SELECT name FROM groups WHERE group_id = ?"
        result = self.db.execute_query(query, (group_id,), fetch=True)
        return result[0][0] if result else f"Group_{group_id}"
    
    def list_all_groups(self) -> List[Dict]:
        """List all groups in the system"""
        query = """
            SELECT g.group_id, g.name, g.description, g.group_type, 
                   u.name as creator, COUNT(ug.user_id) as member_count
            FROM groups g
            JOIN users u ON g.created_by = u.user_id
            LEFT JOIN user_groups ug ON g.group_id = ug.group_id
            GROUP BY g.group_id
            ORDER BY g.created_at DESC
        """
        results = self.db.execute_query(query, fetch=True)
        
        groups = []
        for row in results:
            groups.append({
                'group_id': row[0],
                'name': row[1],
                'description': row[2],
                'group_type': row[3],
                'creator': row[4],
                'member_count': row[5]
            })
        
        return groups
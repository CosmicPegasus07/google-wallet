import sqlite3
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.utils import DatabaseManager

class UserManager:
    def __init__(self, db_path='database/mock_finance.db'):
        self.db = DatabaseManager(db_path)
    
    def create_user(self, name: str, email: str, password: str = None, 
                   google_wallet_cred: str = None) -> int:
        """Create a new user"""
        # Simple password hashing (use proper hashing in production)
        password_hash = hashlib.md5(password.encode()).hexdigest() if password else "temp_hash"
        
        query = """
            INSERT INTO users (name, google_wallet_cred, email, password_hash) 
            VALUES (?, ?, ?, ?)
        """
        
        try:
            user_id = self.db.execute_query(
                query, (name, google_wallet_cred or f"wallet_{name.lower()}", email, password_hash)
            )
            print(f"✅ User '{name}' created with ID: {user_id}")
            return user_id
        except sqlite3.IntegrityError:
            print(f"❌ User with email '{email}' already exists")
            return None
    
    def list_all_users(self) -> List[Dict]:
        """List all users in the system"""
        query = """
            SELECT user_id, name, email, created_at
            FROM users
            ORDER BY name
        """
        results = self.db.execute_query(query, fetch=True)
        
        users = []
        for row in results:
            users.append({
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'created_at': row[3]
            })
        
        return users
    
    def find_user_by_email(self, email: str) -> Dict:
        """Find user by email"""
        query = "SELECT user_id, name, email FROM users WHERE email = ?"
        result = self.db.execute_query(query, (email,), fetch=True)
        
        if result:
            return {
                'user_id': result[0][0],
                'name': result[0][1],
                'email': result[0][2]
            }
        return None
    
    def find_user_by_name(self, name: str) -> List[Dict]:
        """Find users by name (partial match)"""
        query = "SELECT user_id, name, email FROM users WHERE name LIKE ?"
        results = self.db.execute_query(query, (f"%{name}%",), fetch=True)
        
        users = []
        for row in results:
            users.append({
                'user_id': row[0],
                'name': row[1],
                'email': row[2]
            })
        
        return users
    
    def get_user_by_id(self, user_id: int) -> Dict:
        """Get user by ID"""
        query = "SELECT user_id, name, email FROM users WHERE user_id = ?"
        result = self.db.execute_query(query, (user_id,), fetch=True)
        
        if result:
            return {
                'user_id': result[0][0],
                'name': result[0][1],
                'email': result[0][2]
            }
        return None
    
    def update_user(self, user_id: int, name: str = None, email: str = None) -> bool:
        """Update user information"""
        updates = []
        params = []
        
        if name:
            updates.append("name = ?")
            params.append(name)
        
        if email:
            updates.append("email = ?")
            params.append(email)
        
        if not updates:
            return False
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
        
        self.db.execute_query(query, params)
        print(f"✅ User {user_id} updated successfully")
        return True
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user (use carefully!)"""
        # Check if user has any expenses or group memberships
        check_query = """
            SELECT COUNT(*) FROM expenses WHERE payer_id = ?
            UNION ALL
            SELECT COUNT(*) FROM user_groups WHERE user_id = ?
        """
        results = self.db.execute_query(check_query, (user_id, user_id), fetch=True)
        
        total_relations = sum(row[0] for row in results)
        
        if total_relations > 0:
            print(f"❌ Cannot delete user {user_id} - has {total_relations} related records")
            return False
        
        query = "DELETE FROM users WHERE user_id = ?"
        self.db.execute_query(query, (user_id,))
        print(f"✅ User {user_id} deleted successfully")
        return True
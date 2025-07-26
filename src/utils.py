import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class DatabaseManager:
    def __init__(self, db_path='database/mock_finance.db'):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute a query and return results if needed"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.lastrowid

def format_currency(amount, currency='USD'):
    """Format amount as currency"""
    return f"{currency} {amount:.2f}"

def calculate_percentage(amount, percentage):
    """Calculate percentage of amount"""
    return (amount * percentage) / 100

def round_to_cents(amount):
    """Round amount to 2 decimal places"""
    return round(amount, 2)
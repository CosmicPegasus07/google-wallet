#!/usr/bin/env python3
"""
Quick start script for Google Wallet Groups CLI
"""

import os
import sys

def setup_first_time():
    """Set up database and create sample user"""
    print("🚀 Welcome to Google Wallet Groups!")
    print("Setting up for first time use...\n")
    
    # Create database
    from database.setup_database import setup_database
    setup_database()
    
    # Create a sample user
    sys.path.append('src')
    from src.user_manager import UserManager
    
    um = UserManager()
    
    print("Let's create your first user:")
    name = input("Your name: ")
    email = input("Your email: ")
    
    user_id = um.create_user(name, email, "password123")
    
    print(f"\n✅ Setup complete! Your user ID is: {user_id}")
    print(f"\n✅ Setup complete! Your user ID is: {user_id}")
    print("You can now run the main application with: python cli_app.py")
    
    return user_id

def main():
    """Main quick start function"""
    if not os.path.exists('database/mock_finance.db'):
        setup_first_time()
        input("\nPress Enter to start the application...")

    # Start the main CLI app
    from cli_app import main as cli_main
    cli_main()

if __name__ == "__main__":
    main()
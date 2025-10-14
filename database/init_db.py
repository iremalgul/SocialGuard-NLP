"""
Database Initialization Script
Run this script to create database tables
"""
import sys
from database.database import init_db, engine
from sqlalchemy import text

def check_database_connection():
    """Check if database connection is successful"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ Database connection successful!")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL is running")
        print("2. Database 'cyberbullying_db' exists")
        print("3. Database credentials in config/settings.py are correct")
        return False

def main():
    """Main initialization function"""
    print("=" * 60)
    print("Database Initialization Script")
    print("=" * 60)
    print()
    
    # Check connection
    print("Step 1: Checking database connection...")
    if not check_database_connection():
        sys.exit(1)
    
    print()
    print("Step 2: Creating database tables...")
    try:
        init_db()
        print("✓ All tables created successfully!")
        print()
        print("Tables created:")
        print("  - users (Kullanıcı bilgileri)")
        print("  - analyses (Sosyal medya analizleri)")
        print("  - manual_predictions (Manuel tahminler)")
        print()
        print("=" * 60)
        print("Database initialization completed successfully! 🎉")
        print("=" * 60)
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


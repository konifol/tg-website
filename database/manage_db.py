#!/usr/bin/env python3
"""
Database Management Script for Bot Creator Platform
This script provides various database management functions
"""

import os
import sys
import argparse
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import hashlib
import secrets

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'botcreator'),
            'password': os.getenv('DB_PASSWORD', 'botcreator123'),
            'database': os.getenv('DB_NAME', 'botcreator'),
            'charset': 'utf8mb4'
        }
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            print(f"✅ Connected to database: {self.config['database']}")
            return True
        except Error as e:
            print(f"❌ Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ Database connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                self.connection.commit()
                result = cursor.rowcount
            
            cursor.close()
            return result
        except Error as e:
            print(f"❌ Error executing query: {e}")
            return None
    
    def create_tables(self):
        """Create all necessary tables"""
        print("📋 Creating database tables...")
        
        # Read and execute the SQL script
        sql_file = os.path.join(os.path.dirname(__file__), 'init_database.sql')
        
        try:
            with open(sql_file, 'r') as f:
                sql_script = f.read()
            
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement and not statement.startswith('--'):
                    try:
                        self.execute_query(statement)
                        print(f"✅ Executed: {statement[:50]}...")
                    except Error as e:
                        print(f"⚠️  Warning executing statement: {e}")
                        continue
            
            print("✅ Database tables created successfully!")
            
        except FileNotFoundError:
            print(f"❌ SQL file not found: {sql_file}")
            return False
        
        return True
    
    def drop_tables(self):
        """Drop all tables (DANGEROUS!)"""
        print("⚠️  WARNING: This will delete ALL data!")
        confirm = input("Type 'YES' to confirm: ")
        
        if confirm != 'YES':
            print("❌ Operation cancelled")
            return False
        
        tables = ['bot_sessions', 'bots', 'users']
        
        for table in tables:
            try:
                self.execute_query(f"DROP TABLE IF EXISTS `{table}`")
                print(f"✅ Dropped table: {table}")
            except Error as e:
                print(f"❌ Error dropping table {table}: {e}")
        
        return True
    
    def reset_database(self):
        """Reset database to initial state"""
        print("🔄 Resetting database...")
        
        if self.drop_tables():
            if self.create_tables():
                print("✅ Database reset successfully!")
                return True
        
        return False
    
    def show_tables(self):
        """Show all tables in the database"""
        print("📊 Database tables:")
        
        result = self.execute_query("SHOW TABLES")
        if result:
            for row in result:
                table_name = list(row.values())[0]
                print(f"  - {table_name}")
                
                # Show table structure
                desc_result = self.execute_query(f"DESCRIBE `{table_name}`")
                if desc_result:
                    print("    Columns:")
                    for col in desc_result:
                        print(f"      {col['Field']} - {col['Type']} ({col['Null']})")
                print()
    
    def show_data(self, table_name):
        """Show data from a specific table"""
        print(f"📋 Data from table: {table_name}")
        
        result = self.execute_query(f"SELECT * FROM `{table_name}` LIMIT 10")
        if result:
            for row in result:
                print(f"  {row}")
        else:
            print("  No data found")
    
    def create_admin_user(self, email, name, password):
        """Create an admin user"""
        print(f"👤 Creating admin user: {email}")
        
        # Hash password
        password_hash = self._hash_password(password)
        
        # Check if user exists
        existing = self.execute_query("SELECT id FROM users WHERE email = %s", (email,))
        if existing:
            print("❌ User already exists")
            return False
        
        # Create user
        query = """
        INSERT INTO users (email, name, password_hash, created_at, updated_at, is_active)
        VALUES (%s, %s, %s, NOW(), NOW(), TRUE)
        """
        
        result = self.execute_query(query, (email, name, password_hash))
        if result:
            print("✅ Admin user created successfully!")
            return True
        
        return False
    
    def _hash_password(self, password):
        """Hash password using werkzeug-like method"""
        # This is a simplified hash - in production use proper hashing
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256()
        hash_obj.update((password + salt).encode())
        return f"$2b$12${salt}${hash_obj.hexdigest()}"
    
    def backup_database(self, backup_file):
        """Create a backup of the database"""
        print(f"💾 Creating backup: {backup_file}")
        
        try:
            # Use mysqldump for backup
            import subprocess
            
            cmd = [
                'mysqldump',
                f'--host={self.config["host"]}',
                f'--port={self.config["port"]}',
                f'--user={self.config["user"]}',
                f'--password={self.config["password"]}',
                '--single-transaction',
                '--routines',
                '--triggers',
                self.config['database']
            ]
            
            with open(backup_file, 'w') as f:
                subprocess.run(cmd, stdout=f, check=True)
            
            print("✅ Database backup created successfully!")
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"❌ Error creating backup: {e}")
            return False
    
    def restore_database(self, backup_file):
        """Restore database from backup"""
        print(f"🔄 Restoring database from: {backup_file}")
        
        if not os.path.exists(backup_file):
            print(f"❌ Backup file not found: {backup_file}")
            return False
        
        try:
            # Use mysql for restore
            import subprocess
            
            cmd = [
                'mysql',
                f'--host={self.config["host"]}',
                f'--port={self.config["port"]}',
                f'--user={self.config["user"]}',
                f'--password={self.config["password"]}',
                self.config['database']
            ]
            
            with open(backup_file, 'r') as f:
                subprocess.run(cmd, stdin=f, check=True)
            
            print("✅ Database restored successfully!")
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"❌ Error restoring database: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Database Management for Bot Creator Platform')
    parser.add_argument('action', choices=[
        'create', 'drop', 'reset', 'show', 'backup', 'restore', 'admin'
    ], help='Action to perform')
    parser.add_argument('--table', help='Table name for show action')
    parser.add_argument('--backup-file', default='backup.sql', help='Backup file name')
    parser.add_argument('--email', help='Admin email for create admin action')
    parser.add_argument('--name', help='Admin name for create admin action')
    parser.add_argument('--password', help='Admin password for create admin action')
    
    args = parser.parse_args()
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    try:
        if not db_manager.connect():
            sys.exit(1)
        
        if args.action == 'create':
            db_manager.create_tables()
        
        elif args.action == 'drop':
            db_manager.drop_tables()
        
        elif args.action == 'reset':
            db_manager.reset_database()
        
        elif args.action == 'show':
            if args.table:
                db_manager.show_data(args.table)
            else:
                db_manager.show_tables()
        
        elif args.action == 'backup':
            db_manager.backup_database(args.backup_file)
        
        elif args.action == 'restore':
            db_manager.restore_database(args.backup_file)
        
        elif args.action == 'admin':
            if not all([args.email, args.name, args.password]):
                print("❌ Please provide --email, --name, and --password for admin creation")
                sys.exit(1)
            db_manager.create_admin_user(args.email, args.name, args.password)
    
    finally:
        db_manager.disconnect()

if __name__ == '__main__':
    main()
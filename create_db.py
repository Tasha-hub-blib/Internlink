import sqlite3

def create_database():
    """
    Create SQLite database and tables for InternLink
    """
    print("\n" + "="*50)
    print("Creating InternLink Database...")
    print("="*50 + "\n")
    
    try:
        # Connect to database (creates file if it doesn't exist)
        conn = sqlite3.connect('internlink.db')
        cursor = conn.cursor()
        print("✓ Connected to database")
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                user_type TEXT NOT NULL DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ Created 'users' table")
        
        # Create profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                phone TEXT,
                university TEXT,
                course TEXT,
                year INTEGER,
                gpa REAL,
                skills TEXT,
                interests TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        print("✓ Created 'profiles' table")
        
        # Create applications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                position TEXT NOT NULL,
                company TEXT NOT NULL,
                date_applied TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Pending',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        print("✓ Created 'applications' table")
        
        conn.commit()
        conn.close()
        
        print("\n" + "="*50)
        print("✅ DATABASE SETUP COMPLETE!")
        print("="*50)
        print("\nDatabase file: internlink.db")
        print("\nNext steps:")
        print("1. Run: python app.py")
        print("2. Open your HTML file in browser")
        print("3. Create an account!")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    create_database()
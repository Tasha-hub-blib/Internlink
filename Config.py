
DB_CONFIG = {
   
    'host': 'localhost',
    
    
    'port': 3306,
    
   
    'user': 'root',
    
    
    'password': 'your_password_here',
    
    
    'database': 'internlink_db',
    
    
    'autocommit': False,
    
   
    'charset': 'utf8mb4',
    
    
    'collation': 'utf8mb4_unicode_ci',
}


SECRET_KEY = 'your-secret-key-here-change-this-in-production'

MAX_FILE_SIZE = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

SESSION_TIMEOUT = 30
"""
SETUP INSTRUCTIONS:

1. Install MySQL on your computer if not already installed

2. Create the database by running these SQL commands:
   
   CREATE DATABASE internlink_db;
   USE internlink_db;

3. Update the DB_CONFIG dictionary above with your MySQL credentials:
   - user: Your MySQL username (default is 'root')
   - password: Your MySQL password
   - host: 'localhost' for local development
   - database: 'internlink_db' (or your preferred database name)

4. Run the database_setup.sql file to create all necessary tables

5. Install required Python packages:
   pip install flask flask-cors mysql-connector-python werkzeug

6. Keep this file secure and never commit it to public repositories
   with real credentials!
"""
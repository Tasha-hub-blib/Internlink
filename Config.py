# ==================== DATABASE CONFIGURATION ====================
# This file contains all database connection settings
# IMPORTANT: Keep this file secure and never share your database credentials

# Database connection configuration dictionary
DB_CONFIG = {
    # MySQL server host (use 'localhost' for local development)
    'host': 'localhost',
    
    # MySQL server port (default is 3306)
    'port': 3306,
    
    # MySQL username
    # CHANGE THIS to your MySQL username
    'user': 'root',
    
    # MySQL password
    # CHANGE THIS to your MySQL password
    'password': 'your_password_here',
    
    # Database name
    # CHANGE THIS if you want to use a different database name
    'database': 'internlink_db',
    
    # Automatically reconnect if connection is lost
    'autocommit': False,
    
    # Use unicode for text encoding
    'charset': 'utf8mb4',
    
    # Collation for unicode support
    'collation': 'utf8mb4_unicode_ci',
}

# ==================== APPLICATION SETTINGS ====================
# These are optional settings you can use in your application

# Secret key for session management (change this to a random string)
SECRET_KEY = 'your-secret-key-here-change-this-in-production'

# Maximum upload file size (in bytes) - 16MB
MAX_FILE_SIZE = 16 * 1024 * 1024

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

# Session timeout (in minutes)
SESSION_TIMEOUT = 30

# ==================== NOTES ====================
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
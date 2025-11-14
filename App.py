# ==================== IMPORTS ====================
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

# ==================== APP INITIALIZATION ====================
app = Flask(__name__)
CORS(app)

# ==================== DATABASE CONNECTION ====================
DATABASE = 'internlink.db'

def get_db_connection():
    """
    Create and return a database connection
    """
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/api/signup', methods=['POST'])
def signup():
    """
    Handle user registration/signup
    PHASE 1: Student registration only
    Expected JSON data: first_name, last_name, email, password
    """
    try:
        data = request.get_json()
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')
        user_type = 'student'
        
        if not all([first_name, last_name, email, password]):
            return jsonify({'message': 'All fields are required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'message': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'message': 'Email already registered'}), 400
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Insert new user
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, password, user_type)
            VALUES (?, ?, ?, ?, ?)
        """, (first_name, last_name, email, hashed_password, user_type))
        
        conn.commit()
        user_id = cursor.lastrowid
        
        user_data = {
            'id': user_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'user_type': user_type
        }
        
        conn.close()
        return jsonify({'message': 'Signup successful', 'user': user_data}), 201
        
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({'message': 'An error occurred during signup'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """
    Handle user login
    PHASE 1: Student login only
    Expected JSON data: email, password
    """
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'message': 'Email and password are required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'message': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user['password'], password):
            conn.close()
            return jsonify({'message': 'Invalid email or password'}), 401
        
        if user['user_type'] != 'student':
            conn.close()
            return jsonify({'message': 'Organization portal coming soon in Phase 2!'}), 403
        
        user_data = {
            'id': user['id'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email'],
            'user_type': user['user_type']
        }
        
        conn.close()
        return jsonify({'message': 'Login successful', 'user': user_data}), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'message': 'An error occurred during login'}), 500
@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """
    Handle forgot password request
    For now, just validates email exists
    In production, you'd send an actual email with reset link
    """
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'message': 'Email is required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'message': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        # For security, always return success even if email not found
        # This prevents email enumeration attacks
        if user:
            # TODO: In production, generate reset token and send email
            # For now, just return success
            return jsonify({
                'message': 'If an account exists with this email, you will receive password reset instructions.'
            }), 200
        else:
            # Still return success for security
            return jsonify({
                'message': 'If an account exists with this email, you will receive password reset instructions.'
            }), 200
        
    except Exception as e:
        print(f"Forgot password error: {e}")
        return jsonify({'message': 'An error occurred'}), 500

# ==================== PROFILE ROUTES ====================

@app.route('/api/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    """
    Get user profile by user ID
    """
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'message': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
        profile = cursor.fetchone()
        
        conn.close()
        
        if profile:
            return jsonify(dict(profile)), 200
        else:
            return jsonify({'message': 'Profile not found'}), 404
            
    except Exception as e:
        print(f"Get profile error: {e}")
        return jsonify({'message': 'An error occurred'}), 500

@app.route('/api/profile', methods=['POST'])
def save_profile():
    """
    Create or update user profile
    Expected JSON data: user_id, phone, university, course, year, gpa, skills, interests
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'message': 'User ID is required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'message': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
        # Check if profile exists
        cursor.execute("SELECT id FROM profiles WHERE user_id = ?", (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update
            cursor.execute("""
                UPDATE profiles 
                SET phone = ?, university = ?, course = ?, year = ?, 
                    gpa = ?, skills = ?, interests = ?, updated_at = ?
                WHERE user_id = ?
            """, (
                data.get('phone'),
                data.get('university'),
                data.get('course'),
                data.get('year'),
                data.get('gpa'),
                data.get('skills'),
                data.get('interests'),
                datetime.now(),
                user_id
            ))
        else:
            # Insert
            cursor.execute("""
                INSERT INTO profiles 
                (user_id, phone, university, course, year, gpa, skills, interests)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                data.get('phone'),
                data.get('university'),
                data.get('course'),
                data.get('year'),
                data.get('gpa'),
                data.get('skills'),
                data.get('interests')
            ))
        
        conn.commit()
        
        # Get profile
        cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
        profile = cursor.fetchone()
        
        conn.close()
        return jsonify(dict(profile)), 200
        
    except Exception as e:
        print(f"Save profile error: {e}")
        return jsonify({'message': 'An error occurred while saving profile'}), 500

# ==================== APPLICATION ROUTES ====================

@app.route('/api/applications/<int:user_id>', methods=['GET'])
def get_applications(user_id):
    """
    Get all applications for a user
    """
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'message': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM applications 
            WHERE user_id = ? 
            ORDER BY date_applied DESC
        """, (user_id,))
        
        applications = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(applications), 200
        
    except Exception as e:
        print(f"Get applications error: {e}")
        return jsonify({'message': 'An error occurred'}), 500

@app.route('/api/apply', methods=['POST'])
def apply_internship():
    """
    Submit internship application
    Expected JSON data: user_id, position, company
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        position = data.get('position')
        company = data.get('company')
        
        if not all([user_id, position, company]):
            return jsonify({'message': 'All fields are required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'message': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
        # Check if already applied
        cursor.execute("""
            SELECT id FROM applications 
            WHERE user_id = ? AND position = ? AND company = ?
        """, (user_id, position, company))
        
        if cursor.fetchone():
            conn.close()
            return jsonify({'message': 'Already applied to this internship'}), 400
        
        # Insert application
        cursor.execute("""
            INSERT INTO applications (user_id, position, company, status)
            VALUES (?, ?, ?, ?)
        """, (user_id, position, company, 'Pending'))
        
        conn.commit()
        application_id = cursor.lastrowid
        
        cursor.execute("SELECT * FROM applications WHERE id = ?", (application_id,))
        application = cursor.fetchone()
        
        conn.close()
        return jsonify(dict(application)), 201
        
    except Exception as e:
        print(f"Apply error: {e}")
        return jsonify({'message': 'An error occurred while submitting application'}), 500

# ==================== RUN SERVER ====================
if __name__ == '__main__':
    import os
    
    print("\n" + "="*60)
    print("🎓 INTERNLINK STUDENT PORTAL - PHASE 1")
    print("="*60)
    print("✓ Student registration and login")
    print("✓ Profile management")
    print("✓ Internship browsing")
    print("✓ Application tracking")
    print("\n📋 Phase 2 will include:")
    print("  - Organization accounts")
    print("  - Post internships")
    print("  - Review applications")
    print("="*60)
    
    # Get port from environment variable (for deployment) or use 5000 (for local)
    port = int(os.environ.get('PORT', 5000))
    # Set debug=False for production, True for local development
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"\n🚀 Server running on port {port}")
    print("   Press CTRL+C to stop\n")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import random
import string
import os


DATABASE = 'internlink.db'

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row 
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


def init_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                user_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                phone TEXT,
                university TEXT,
                course TEXT,
                year TEXT,
                gpa TEXT,
                skills TEXT,
                interests TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
       
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                position TEXT NOT NULL,
                company TEXT NOT NULL,
                status TEXT DEFAULT 'Pending',
                date_applied TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reset_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                code TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
        print("✓ Database initialized")


init_db()


app = Flask(__name__)
CORS(app)


@app.route('/')
def serve_index():
    return render_template('index.html')


def generate_reset_code():
    return ''.join(random.choices(string.digits, k=6))



@app.route('/api/signup', methods=['POST'])
def signup():
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
        
        
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'message': 'Email already registered'}), 400
        
        
        hashed_password = generate_password_hash(password)
        
        
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
        
        if user:
            
            reset_code = generate_reset_code()
            
            
            cursor.execute("""
                INSERT INTO reset_codes (email, code)
                VALUES (?, ?)
            """, (email, reset_code))
            conn.commit()
            
           
            print(f"Reset code for {email}: {reset_code}")
            
            conn.close()
            return jsonify({
                'message': f'Reset code sent! For demo purposes, your code is: {reset_code}',
                'reset_code': reset_code  
            }), 200
        else:
            conn.close()
            
            return jsonify({
                'message': 'If an account exists with this email, you will receive a reset code.'
            }), 200
        
    except Exception as e:
        print(f"Forgot password error: {e}")
        return jsonify({'message': 'An error occurred'}), 500

@app.route('/api/verify-reset-code', methods=['POST'])
def verify_reset_code():
    try:
        data = request.get_json()
        email = data.get('email')
        code = data.get('code')
        
        if not all([email, code]):
            return jsonify({'message': 'Email and code are required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'message': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
        
        cursor.execute("""
            SELECT id FROM reset_codes 
            WHERE email = ? AND code = ? AND used = 0
            ORDER BY created_at DESC
            LIMIT 1
        """, (email, code))
        
        reset_record = cursor.fetchone()
        conn.close()
        
        if reset_record:
            return jsonify({'message': 'Code verified successfully'}), 200
        else:
            return jsonify({'message': 'Invalid or expired code'}), 400
        
    except Exception as e:
        print(f"Verify code error: {e}")
        return jsonify({'message': 'An error occurred'}), 500

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        email = data.get('email')
        code = data.get('code')
        new_password = data.get('new_password')
        
        if not all([email, code, new_password]):
            return jsonify({'message': 'All fields are required'}), 400
        
        if len(new_password) < 8:
            return jsonify({'message': 'Password must be at least 8 characters'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'message': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
       
        cursor.execute("""
            SELECT id FROM reset_codes 
            WHERE email = ? AND code = ? AND used = 0
            ORDER BY created_at DESC
            LIMIT 1
        """, (email, code))
        
        reset_record = cursor.fetchone()
        
        if not reset_record:
            conn.close()
            return jsonify({'message': 'Invalid or expired code'}), 400
        
        
        cursor.execute("""
            UPDATE reset_codes 
            SET used = 1 
            WHERE id = ?
        """, (reset_record['id'],))
        
        
        hashed_password = generate_password_hash(new_password)
        cursor.execute("""
            UPDATE users 
            SET password = ? 
            WHERE email = ?
        """, (hashed_password, email))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Password reset successful'}), 200
        
    except Exception as e:
        print(f"Reset password error: {e}")
        return jsonify({'message': 'An error occurred'}), 500



@app.route('/api/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
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
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'message': 'User ID is required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'message': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
        
        cursor.execute("SELECT id FROM profiles WHERE user_id = ?", (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            
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
        
        
        cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
        profile = cursor.fetchone()
        
        conn.close()
        return jsonify(dict(profile)), 200
        
    except Exception as e:
        print(f"Save profile error: {e}")
        return jsonify({'message': 'An error occurred while saving profile'}), 500



@app.route('/api/applications/<int:user_id>', methods=['GET'])
def get_applications(user_id):
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
        
       
        cursor.execute("""
            SELECT id FROM applications 
            WHERE user_id = ? AND position = ? AND company = ?
        """, (user_id, position, company))
        
        if cursor.fetchone():
            conn.close()
            return jsonify({'message': 'Already applied to this internship'}), 400
        
        
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


if __name__ == '__main__':
    
    print("\n" + "="*60)
    print("🎓 INTERNLINK STUDENT PORTAL - PHASE 1")
    print("="*60)
    print("✓ Student registration and login")
    print("✓ Password reset functionality")
    print("✓ Profile management")
    print("✓ Internship browsing")
    print("✓ Application tracking")
    print("\n📋 Phase 2 will include:")
    print("  - Organization accounts")
    print("  - Post internships")
    print("  - Review applications")
    print("="*60)
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"\n🚀 Server running on port {port}")
    print("   Press CTRL+C to stop\n")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
import os
import json
import sqlite3
import base64
import random
import string
import csv
from io import StringIO
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from datetime import datetime
import qrcode
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Database Setup ---
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    # Add dummy data
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                 ('student1', 'password', 'student'))
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                 ('faculty1', 'password', 'faculty'))
    conn.commit()
    conn.close()

# --- Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'student':
            return redirect(url_for('student_dashboard'))
        elif session['role'] == 'faculty':
            return redirect(url_for('faculty_dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match")
        
        conn = get_db_connection()
        # Check if username already exists
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            conn.close()
            return render_template('signup.html', error="Username already exists")
        
        # Insert new student user
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                    (username, password, 'student'))
        conn.commit()
        conn.close()
        
        return redirect(url_for('login', message="Account created successfully! Please login."))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                          (username, password)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            if user['role'] == 'faculty':
                return redirect(url_for('faculty_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            return render_template('login.html', error="Invalid username or password")
    
    message = request.args.get('message', '')
    return render_template('login.html', message=message)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    attendance_history = conn.execute(
        'SELECT * FROM attendance WHERE student_id = ? ORDER BY date DESC', 
        (session['user_id'],)
    ).fetchall()
    
    total_days = len(attendance_history)
    present_days = sum(1 for row in attendance_history if row['status'] == 'Present')
    absent_days = total_days - present_days
    attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0

    stats = {
        'total': total_days,
        'present': present_days,
        'absent': absent_days,
        'rate': round(attendance_rate, 1)
    }
    
    conn.close()
    return render_template('student_dashboard.html', history=attendance_history, stats=stats)

@app.route('/faculty/dashboard')
def faculty_dashboard():
    if 'user_id' not in session or session['role'] != 'faculty':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    attendance_report = conn.execute('''
        SELECT u.username, a.date, a.status
        FROM attendance a
        JOIN users u ON u.id = a.student_id
        ORDER BY a.date DESC, u.username
    ''').fetchall()
    conn.close()
    
    return render_template('faculty_dashboard.html', report=attendance_report)

@app.route('/faculty/add_student', methods=['GET', 'POST'])
def add_student():
    if 'user_id' not in session or session['role'] != 'faculty':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        # Check if username already exists
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            conn.close()
            return render_template('add_student.html', error="Username already exists")
        
        # Insert new student user
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                    (username, password, 'student'))
        conn.commit()
        conn.close()
        
        return render_template('add_student.html', success=f"Student '{username}' added successfully!")
    
    return render_template('add_student.html')

# --- API Endpoints for Secret Code ---
active_secret_code = {"code": None, "timestamp": None}

@app.route('/api/generate_code')
def generate_code():
    if 'user_id' not in session or session['role'] != 'faculty':
        return jsonify({"error": "Unauthorized"}), 403
        
    global active_secret_code
    timestamp = datetime.now()
    # Generate a random 6-character alphanumeric code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    active_secret_code['code'] = code
    active_secret_code['timestamp'] = timestamp
    
    return jsonify({
        "secret_code": code,
        "message": "New secret code generated."
    })

@app.route('/api/mark_attendance', methods=['POST'])
def mark_attendance():
    if 'user_id' not in session or session['role'] != 'student':
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    submitted_code = data.get('code')
    student_id = session['user_id']

    if not submitted_code or not active_secret_code['code']:
        return jsonify({"success": False, "message": "No active attendance code."})

    # Check if code is valid and not too old (e.g., within 2 minutes)
    time_difference = datetime.now() - active_secret_code['timestamp']
    if submitted_code.upper() == active_secret_code['code'] and time_difference.total_seconds() < 120:
        conn = get_db_connection()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check if already marked
        existing = conn.execute(
            'SELECT * FROM attendance WHERE student_id = ? AND date = ?',
            (student_id, today)
        ).fetchone()

        if existing:
            message = "Attendance already marked for today."
            success = False
        else:
            conn.execute(
                'INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)',
                (student_id, today, 'Present')
            )
            conn.commit()
            message = "Attendance marked successfully!"
            success = True
        
        conn.close()
        return jsonify({"success": success, "message": message})
    else:
        return jsonify({"success": False, "message": "Invalid or expired code."})

@app.route('/student/profile', methods=['GET', 'POST'])
def student_profile():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    if request.method == 'POST':
        # Update profile information
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if new_password:
            if new_password != confirm_password:
                conn.close()
                return render_template('student_profile.html', error="Passwords do not match")
            
            # Update password
            conn.execute('UPDATE users SET password = ? WHERE id = ?', 
                        (new_password, session['user_id']))
        
        # Update other profile info (you might want to add these columns to your database)
        # For now, we'll just update the password
        conn.commit()
        conn.close()
        
        return render_template('student_profile.html', success="Profile updated successfully!")
    
    # Get current user info
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    return render_template('student_profile.html', user=user)

@app.route('/faculty/export_report')
def export_report():
    if 'user_id' not in session or session['role'] != 'faculty':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    attendance_report = conn.execute('''
        SELECT u.username, a.date, a.status 
        FROM attendance a 
        JOIN users u ON a.student_id = u.id 
        ORDER BY a.date DESC, u.username
    ''').fetchall()
    conn.close()
    
    # Create CSV data
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Student', 'Date', 'Status'])
    
    for row in attendance_report:
        cw.writerow([row['username'], row['date'], row['status']])
    
    output = si.getvalue()
    si.close()
    
    # Create file-like object for download
    buffer = BytesIO()
    buffer.write(output.encode('utf-8'))
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'attendance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mimetype='text/csv'
    )

@app.route('/faculty/analytics')
def analytics():
    if 'user_id' not in session or session['role'] != 'faculty':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get overall statistics
    total_students = conn.execute('SELECT COUNT(*) as count FROM users WHERE role = "student"').fetchone()['count']
    total_attendance = conn.execute('SELECT COUNT(*) as count FROM attendance').fetchone()['count']
    present_count = conn.execute('SELECT COUNT(*) as count FROM attendance WHERE status = "Present"').fetchone()['count']
    
    # Calculate attendance rate
    attendance_rate = (present_count / total_attendance * 100) if total_attendance > 0 else 0
    
    # Get daily attendance for the last 7 days
    daily_stats = conn.execute('''
        SELECT date, COUNT(*) as total, 
               SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present
        FROM attendance 
        WHERE date >= date('now', '-7 days')
        GROUP BY date 
        ORDER BY date DESC
    ''').fetchall()
    
    # Get top students by attendance
    top_students = conn.execute('''
        SELECT u.username, 
               COALESCE(COUNT(a.id), 0) as total_days,
               COALESCE(SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END), 0) as present_days
        FROM users u
        LEFT JOIN attendance a ON u.id = a.student_id
        WHERE u.role = 'student'
        GROUP BY u.id, u.username
        ORDER BY present_days DESC
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('analytics.html', 
                         total_students=total_students,
                         total_attendance=total_attendance,
                         present_count=present_count,
                         attendance_rate=round(attendance_rate, 1),
                         daily_stats=daily_stats,
                         top_students=top_students)

if __name__ == '__main__':
    if not os.path.exists('database.db'):
        init_db()
    app.run(debug=True, port=5001) 
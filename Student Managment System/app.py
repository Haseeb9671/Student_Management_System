import os
from flask import Flask, render_template, request, redirect, jsonify, session, send_from_directory
from werkzeug.utils import secure_filename
import mysql.connector
from datetime import datetime
import csv
import io

app = Flask(__name__)
app.secret_key = 'secret_key_for_session' 

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
CSV_BACKUP_FOLDER = 'csv_backups'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CSV_BACKUP_FOLDER, exist_ok=True)

db_config = {
    'user': 'root',
    'password': '', 
    'host': 'localhost',
    'database': 'student_db'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# --- CSV Functions ---
def backup_csv(uploaded_file):
    """Save uploaded CSV with timestamp to backups folder"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_name = secure_filename(uploaded_file.filename)
        backup_name = f"{timestamp}_{original_name}"
        backup_path = os.path.join(CSV_BACKUP_FOLDER, backup_name)
        
        uploaded_file.seek(0)
        uploaded_file.save(backup_path)
        
        return backup_name
    except Exception as e:
        print(f"Backup Error: {e}")
        return None

def get_csv_backups():
    """Get list of all CSV backups with student count"""
    try:
        files = []
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for filename in os.listdir(CSV_BACKUP_FOLDER):
            if filename.endswith('.csv'):
                filepath = os.path.join(CSV_BACKUP_FOLDER, filename)
                stat = os.stat(filepath)
                
                # Count students linked to this CSV
                cursor.execute("SELECT COUNT(*) FROM students WHERE csv_source=%s", (filename,))
                student_count = cursor.fetchone()[0]
                
                files.append({
                    'name': filename,
                    'size': round(stat.st_size / 1024, 2),
                    'date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                    'students': student_count
                })
        
        conn.close()
        return sorted(files, key=lambda x: x['date'], reverse=True)
    except:
        return []

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/homepage')
def homepage():
    if 'role' not in session: 
        return redirect('/')
    return render_template('homepage.html')

# --- LOGIN ---
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password'] 

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM admins WHERE username=%s", (username,))
    admin_user = cursor.fetchone()

    if admin_user and admin_user['password'] == password:
        session['role'] = 'admin'
        session['user_id'] = admin_user['username']
        session['user_name'] = "Administrator"
        conn.close()
        return redirect('/homepage')

    cursor.execute("SELECT * FROM students WHERE reg_number=%s", (username,))
    student = cursor.fetchone()
    conn.close()

    if student and student['password'] == password:
        session['role'] = 'student'
        session['user_id'] = student['reg_number']
        session['user_name'] = student['name']
        return redirect('/homepage')
    
    return render_template('index.html')

# --- DASHBOARD ---
@app.route('/dashboard')
def dashboard():
    if session.get('role') != 'admin': 
        return redirect('/')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    now = datetime.now()
    current_month_str = now.strftime('%Y-%m') 
    month_name = now.strftime('%B') 
    today_str = now.strftime('%Y-%m-%d')
    
    query = """
    SELECT s.name, s.reg_number, s.email, s.department, s.csv_source,
           g.assignment_score, g.quiz_score, g.behavior_score, 
           g.mid_term_score, g.final_term_score, g.assignment_file
    FROM students s
    LEFT JOIN grades g ON s.reg_number = g.student_reg
    ORDER BY s.reg_number
    """
    cursor.execute(query)
    students = cursor.fetchall()
    
    for s in students:
        for key in ['assignment_score', 'quiz_score', 'behavior_score', 'mid_term_score', 'final_term_score']:
            if s[key] is None: 
                s[key] = 0

        month_filter = f"{current_month_str}%"
        cursor.execute("SELECT COUNT(*) as days_present FROM attendance WHERE student_reg=%s AND date LIKE %s AND status='Present'", 
                       (s['reg_number'], month_filter))
        attendance_data = cursor.fetchone()
        s['attendance'] = attendance_data['days_present'] if attendance_data else 0

        cursor.execute("SELECT status FROM attendance WHERE student_reg=%s AND date=%s", (s['reg_number'], today_str))
        today_status = cursor.fetchone()
        s['today_status'] = today_status['status'] if today_status else None

        total = (s['assignment_score'] + s['quiz_score'] + s['behavior_score'] + 
                 s['mid_term_score'] + s['final_term_score'])
        s['total'] = total
        s['grade'] = 'A' if total >= 85 else 'B' if total >= 70 else 'C' if total >= 50 else 'F'

    conn.close()
    
    csv_backups = get_csv_backups()
    
    return render_template('dashboard.html', students=students, current_month=month_name, csv_backups=csv_backups)

# --- MANUAL ATTENDANCE ---
@app.route('/mark_manual_attendance/<reg_num>/<status>')
def mark_manual_attendance(reg_num, status):
    if session.get('role') != 'admin': 
        return redirect('/')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute("SELECT * FROM attendance WHERE student_reg=%s AND date=%s", (reg_num, today_str))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("UPDATE attendance SET status=%s, method='Manual' WHERE student_reg=%s AND date=%s", 
                       (status, reg_num, today_str))
    else:
        cursor.execute("INSERT INTO attendance (student_reg, date, status, method) VALUES (%s, %s, %s, 'Manual')", 
                       (reg_num, today_str, status))
    
    conn.commit()
    conn.close()
    return redirect('/dashboard')

# --- STUDENT DASHBOARD ---
@app.route('/student_dashboard')
def student_dashboard():
    if session.get('role') != 'student': 
        return redirect('/')
    
    reg_num = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM grades WHERE student_reg=%s", (reg_num,))
    grades = cursor.fetchone()

    now = datetime.now()
    current_month_str = now.strftime('%Y-%m')
    month_name = now.strftime('%B')
    
    month_filter = f"{current_month_str}%"
    cursor.execute("SELECT COUNT(*) as days_present FROM attendance WHERE student_reg=%s AND date LIKE %s AND status='Present'", 
                   (reg_num, month_filter))
    attendance_data = cursor.fetchone()
    days_present = attendance_data['days_present'] if attendance_data else 0

    conn.close()
    return render_template('student_dashboard.html', 
                           student_name=session['user_name'], 
                           grades=grades, 
                           attendance=days_present,
                           current_month=month_name)

# --- API STATS ---
@app.route('/api/stats')
def stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT s.name, 
               (COALESCE(g.assignment_score, 0) + 
                COALESCE(g.quiz_score, 0) + 
                COALESCE(g.behavior_score, 0) + 
                COALESCE(g.mid_term_score, 0) + 
                COALESCE(g.final_term_score, 0)) as total 
        FROM students s 
        JOIN grades g ON s.reg_number = g.student_reg
        LIMIT 20
    """
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    if not data: 
        return jsonify({'labels': [], 'values': []})
    return jsonify({'labels': [row[0] for row in data], 'values': [row[1] for row in data]})

# --- PASSWORD MANAGEMENT ---
@app.route('/change_password')
def change_password():
    if 'role' not in session: 
        return redirect('/')
    return render_template('change_password.html')

@app.route('/perform_password_change', methods=['POST'])
def perform_password_change():
    if 'role' not in session: 
        return redirect('/')
    
    current_pass = request.form['current_password']
    new_pass = request.form['new_password']
    confirm_pass = request.form['confirm_password']
    user_id = session['user_id']
    role = session['role']

    if new_pass != confirm_pass:
        return render_template('change_password.html', msg="Passwords do not match!")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    table = "admins" if role == 'admin' else "students"
    id_col = "username" if role == 'admin' else "reg_number"
    cursor.execute(f"SELECT * FROM {table} WHERE {id_col}=%s", (user_id,))
    user = cursor.fetchone()

    if user and user['password'] == current_pass:
        cursor.execute(f"UPDATE {table} SET password=%s WHERE {id_col}=%s", (new_pass, user_id))
        conn.commit()
        conn.close()
        return render_template('change_password.html', msg="Success!")
    else:
        conn.close()
        return render_template('change_password.html', msg="Incorrect Password!")

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- CSV MANAGEMENT ---
@app.route('/download_csv/<filename>')
def download_csv_backup(filename):
    if session.get('role') != 'admin': 
        return redirect('/')
    return send_from_directory(CSV_BACKUP_FOLDER, filename, as_attachment=True)

@app.route('/delete_csv/<filename>')
def delete_csv_backup(filename):
    if session.get('role') != 'admin': 
        return redirect('/')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT reg_number FROM students WHERE csv_source=%s", (filename,))
        students_to_delete = cursor.fetchall()
        
        for (reg_num,) in students_to_delete:
            cursor.execute("DELETE FROM grades WHERE student_reg=%s", (reg_num,))
            cursor.execute("DELETE FROM attendance WHERE student_reg=%s", (reg_num,))
            cursor.execute("DELETE FROM students WHERE reg_number=%s", (reg_num,))
        
        conn.commit()
        conn.close()
            
    except Exception as e:
        print(f"Delete Error: {e}")
    
    return redirect('/dashboard')

# --- STUDENT MANAGEMENT ---
@app.route('/add_student', methods=['POST'])
def add_student():
    reg_num = request.form['reg_num']
    name = request.form['name']
    email = request.form.get('email', '')
    department = request.form.get('department', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO students (reg_number, name, email, department, password, csv_source) VALUES (%s, %s, %s, %s, %s, 'manual')", 
                       (reg_num, name, email, department, reg_num))
        cursor.execute("INSERT INTO grades (student_reg) VALUES (%s)", (reg_num,))
        conn.commit()
    except: 
        pass
    finally: 
        conn.close()
    return redirect('/dashboard')

@app.route('/update_grades', methods=['POST'])
def update_grades():
    reg_num = request.form['reg_num']
    assignment = request.form.get('assignment', 0)
    quiz = request.form.get('quiz', 0)
    behavior = request.form.get('behavior', 0)
    mids = request.form.get('Mids', 0)
    finals = request.form.get('Final', 0)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE grades 
        SET assignment_score=%s, quiz_score=%s, behavior_score=%s, mid_term_score=%s, final_term_score=%s 
        WHERE student_reg=%s
    """, (assignment, quiz, behavior, mids, finals, reg_num))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

@app.route('/remove_student/<reg_num>')
def remove_student(reg_num):
    if session.get('role') != 'admin': 
        return redirect('/')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM grades WHERE student_reg=%s", (reg_num,))
        cursor.execute("DELETE FROM attendance WHERE student_reg=%s", (reg_num,))
        cursor.execute("DELETE FROM students WHERE reg_number=%s", (reg_num,))
        conn.commit()
    except: 
        pass
    finally: 
        conn.close()
    return redirect('/dashboard')

# --- CSV UPLOAD ---
@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if session.get('role') != 'admin': 
        return redirect('/')
    if 'file' not in request.files: 
        return "No file part"
    
    file = request.files['file']
    
    if file and file.filename.endswith('.csv'):
        backup_name = backup_csv(file)
        
        file.seek(0)
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            for row in csv_input:
                reg_num = row.get('reg_number') or row.get('REG_NO')
                name = row.get('name') or row.get('FULL_NAME')
                email = row.get('email') or row.get('UNIVERSITY_EMAIL', '')
                dept = row.get('department') or row.get('DEPARTMENT', '')
                
                cursor.execute("SELECT * FROM students WHERE reg_number=%s", (reg_num,))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO students (reg_number, name, email, department, password, csv_source) VALUES (%s, %s, %s, %s, %s, %s)", 
                                   (reg_num, name, email, dept, reg_num, backup_name))
                    cursor.execute("INSERT INTO grades (student_reg) VALUES (%s)", (reg_num,))
            conn.commit()
        except Exception as e:
            print(f"Upload Error: {e}")
        finally: 
            conn.close()
    
    return redirect('/dashboard')

@app.route('/upload_assignment', methods=['POST'])
def upload_assignment():
    if 'file' not in request.files: 
        return "No file part"
    
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        conn = get_db_connection()
        cursor = conn.cursor()
        reg_num = session['user_id']
        cursor.execute("UPDATE grades SET assignment_file=%s WHERE student_reg=%s", (filename, reg_num))
        conn.commit()
        conn.close()
    return redirect('/student_dashboard')

# --- MOBILE REGISTRATION ---
@app.route('/register_mobile')
def register_mobile(): 
    return render_template('register_mobile.html')

@app.route('/submit_registration', methods=['POST'])
def submit_registration():
    name = request.form['name']
    reg_num = request.form['reg_num']
    email = request.form['email']
    department = request.form['department']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM students WHERE reg_number=%s", (reg_num,))
        if cursor.fetchone(): 
            return "Error: Student exists"
        
        cursor.execute("INSERT INTO students (reg_number, name, email, department, password, csv_source) VALUES (%s, %s, %s, %s, %s, 'mobile')", 
                       (reg_num, name, email, department, reg_num))
        cursor.execute("INSERT INTO grades (student_reg) VALUES (%s)", (reg_num,))
        conn.commit()
        
        return "Registration Submitted!"
    except: 
        return "Error"
    finally: 
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
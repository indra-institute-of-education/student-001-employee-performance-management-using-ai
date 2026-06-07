# app_final.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# MySQL Configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Change this to your MySQL password if you have one
    'database': 'employee_system'
}

# Email configuration
EMAIL_CONFIG = {
    'sender': 'divyadharshini04.hr@gmail.com',
    'password': 'fhhp tfuk jeto albi',  # App password
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587
}

# Department mapping
DEPT_MAP = {'sales': 0, 'hr': 1, 'it': 2, 'operation': 3, 'finance': 4}
DEPT_NAMES = {v: k.capitalize() for k, v in DEPT_MAP.items()}
EDU_MAP = {'diploma': 0, 'bachelors': 1, 'masters': 2, 'mba': 3}
EDU_NAMES = {v: k.capitalize() for k, v in EDU_MAP.items()}
ROLE_MAP = {'executive': 0, 'analyst': 1, 'scientist': 2, 'manager': 3}
ROLE_NAMES = {v: k.capitalize() for k, v in ROLE_MAP.items()}

# Database setup
def get_db():
    """Get MySQL database connection"""
    try:
        conn = mysql.connector.connect(
            host=MYSQL_CONFIG['host'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['database']
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    """Initialize database and create tables if they don't exist"""
    try:
        # First connect without database to create it if needed
        conn = mysql.connector.connect(
            host=MYSQL_CONFIG['host'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
        cursor.execute(f"USE {MYSQL_CONFIG['database']}")
        
        # Create employee table if not exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee (
            emp_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            age INT NOT NULL,
            department INT NOT NULL,
            education INT NOT NULL,
            jobrole INT NOT NULL,
            experience INT NOT NULL,
            income INT NOT NULL,
            trainings INT NOT NULL,
            worklife INT NOT NULL,
            satisfaction INT NOT NULL,
            overtime INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("[OK] Employee table checked/created")
        
        # Create evaluations table (team leader data)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            emp_id INT NOT NULL,
            work_quality INT NOT NULL,
            productivity INT NOT NULL,
            attendance FLOAT NOT NULL,
            teamwork INT NOT NULL,
            communication INT NOT NULL,
            task_completion INT NOT NULL,
            problem_solving INT NOT NULL,
            initiative INT NOT NULL,
            adaptability INT NOT NULL,
            deadline INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employee(emp_id) ON DELETE CASCADE
        )
        ''')
        print("[OK] Evaluations table checked/created")
        
        # Create hr_analysis table (final performance ratings)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS hr_analysis (
            hr_id INT AUTO_INCREMENT PRIMARY KEY,
            emp_id INT NOT NULL,
            performance_score FLOAT NOT NULL,
            performance_level VARCHAR(20) NOT NULL,
            ml_prediction INT,
            email_sent BOOLEAN DEFAULT FALSE,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employee(emp_id) ON DELETE CASCADE
        )
        ''')
        print("[OK] HR Analysis table checked/created")
        
        # Create email_log table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            emp_id INT NOT NULL,
            email VARCHAR(100) NOT NULL,
            subject VARCHAR(200) NOT NULL,
            status TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employee(emp_id) ON DELETE CASCADE
        )
        ''')
        print("[OK] Email_log table checked/created")
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("[OK] Users table checked/created")
        
        # Insert default admin if it doesn't exist
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            default_password = 'admin123'  # Change this to a secure password!
            hashed = generate_password_hash(default_password)
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                           ('admin', hashed))
            print("[INFO] Default admin created (username: admin, password: admin123)")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("\n[SUCCESS] MySQL database initialized successfully")
        print("   Tables: employee, evaluations, hr_analysis, email_log, users")
        
    except Error as e:
        print(f"[ERROR] Error initializing database: {e}")

# Initialize database
print("\n" + "=" * 60)
print("INITIALIZING DATABASE...")
print("=" * 60)
init_db()
print("=" * 60 + "\n")

def save_hr_analysis(emp_id, performance_score, performance_level, ml_prediction=None, email_sent=False):
    """Save HR analysis results to database"""
    try:
        conn = get_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO hr_analysis (emp_id, performance_score, performance_level, ml_prediction, email_sent)
            VALUES (%s, %s, %s, %s, %s)
            ''', (emp_id, performance_score, performance_level, ml_prediction, email_sent))
            conn.commit()
            hr_id = cursor.lastrowid
            print(f"[OK] HR analysis saved for emp_id {emp_id} with score {performance_score} ({performance_level})")
            cursor.close()
            conn.close()
            return hr_id
    except Exception as e:
        print(f"[ERROR] Error saving HR analysis: {e}")
        return None

def get_hr_analysis(emp_id):
    """Get HR analysis for an employee"""
    try:
        conn = get_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('''
            SELECT * FROM hr_analysis WHERE emp_id = %s ORDER BY analyzed_at DESC LIMIT 1
            ''', (emp_id,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result
    except Exception as e:
        print(f"[ERROR] Error getting HR analysis: {e}")
        return None

def send_email(to_email, name, level, score):
    """Send performance email with personalized content"""
    subject = "Your Performance Evaluation Result"
    
    # Create detailed feedback based on performance level
    if level == "High":
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }}
                .header {{ background: linear-gradient(135deg, #28a745, #218838); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ padding: 20px; }}
                .score-box {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center; }}
                .score {{ font-size: 48px; font-weight: bold; color: #28a745; }}
                .feedback {{ background: #e8f5e9; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0; }}
                .incentive {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
                .footer {{ margin-top: 30px; text-align: center; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Congratulations!</h1>
                </div>
                <div class="content">
                    <h2>Dear {name},</h2>
                    
                    <p>We are delighted to inform you that your recent performance evaluation has been rated as <strong style="color: #28a745;">EXCELLENT</strong>.</p>
                    
                    <div class="score-box">
                        <h3>Your Performance Score</h3>
                        <div class="score">{score}</div>
                        <p>out of 5.0</p>
                    </div>
                    
                    <div class="feedback">
                        <h3>What You Did Well:</h3>
                        <ul>
                            <li>Consistently exceeded expectations in all areas</li>
                            <li>Demonstrated exceptional leadership and initiative</li>
                            <li>Outstanding teamwork and collaboration skills</li>
                            <li>High quality work with attention to detail</li>
                            <li>Excellent problem-solving abilities</li>
                        </ul>
                    </div>
                    
                    <div class="incentive">
                        <h3>Incentive Reward</h3>
                        <p>As a recognition of your outstanding performance, you will receive:</p>
                        <ul>
                            <li><strong>15% bonus</strong> on your monthly salary</li>
                            <li>Special recognition in the next town hall</li>
                            <li>Opportunity to lead upcoming projects</li>
                        </ul>
                    </div>
                    
                    <p>Keep up the excellent work! Your contributions are highly valued.</p>
                    
                    <p>Best regards,<br>
                    <strong>HR Department</strong></p>
                </div>
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
    elif level == "Medium":
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }}
                .header {{ background: linear-gradient(135deg, #ffc107, #e0a800); color: #333; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ padding: 20px; }}
                .score-box {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center; }}
                .score {{ font-size: 48px; font-weight: bold; color: #ffc107; }}
                .strengths {{ background: #e8f5e9; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0; }}
                .improvements {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
                .footer {{ margin-top: 30px; text-align: center; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Performance Update</h1>
                </div>
                <div class="content">
                    <h2>Dear {name},</h2>
                    
                    <p>Your recent performance evaluation has been rated as <strong>MEDIUM</strong>.</p>
                    
                    <div class="score-box">
                        <h3>Your Performance Score</h3>
                        <div class="score">{score}</div>
                        <p>out of 5.0</p>
                    </div>
                    
                    <div class="strengths">
                        <h3>Your Strengths:</h3>
                        <ul>
                            <li>Good attendance and punctuality</li>
                            <li>Works well in team settings</li>
                            <li>Accepts feedback positively</li>
                        </ul>
                    </div>
                    
                    <div class="improvements">
                        <h3>Areas for Improvement:</h3>
                        <ul>
                            <li>Focus on reducing errors and improving quality</li>
                            <li>Increase productivity and task completion rate</li>
                            <li>Take more initiative without waiting for instructions</li>
                        </ul>
                    </div>
                    
                    <p>With focused effort, you can achieve a HIGH rating in the next evaluation.</p>
                    
                    <p>Best regards,<br>
                    <strong>HR Department</strong></p>
                </div>
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
    else:  # Low performance
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }}
                .header {{ background: linear-gradient(135deg, #dc3545, #c82333); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ padding: 20px; }}
                .score-box {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center; }}
                .score {{ font-size: 48px; font-weight: bold; color: #dc3545; }}
                .concerns {{ background: #f8d7da; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0; }}
                .support {{ background: #cff4fc; padding: 15px; border-left: 4px solid #0dcaf0; margin: 20px 0; }}
                .footer {{ margin-top: 30px; text-align: center; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Performance Feedback</h1>
                </div>
                <div class="content">
                    <h2>Dear {name},</h2>
                    
                    <p>Your recent performance evaluation has been rated as <strong style="color: #dc3545;">LOW</strong>.</p>
                    
                    <div class="score-box">
                        <h3>Your Performance Score</h3>
                        <div class="score">{score}</div>
                        <p>out of 5.0</p>
                    </div>
                    
                    <div class="concerns">
                        <h3>Areas Needing Improvement:</h3>
                        <ul>
                            <li>Work quality needs significant improvement</li>
                            <li>Productivity is below expected levels</li>
                            <li>Attendance and punctuality need attention</li>
                            <li>Task completion and deadlines are frequently missed</li>
                        </ul>
                    </div>
                    
                    <div class="support">
                        <h3>Support Available:</h3>
                        <ul>
                            <li>Schedule a meeting with your team leader immediately</li>
                            <li>You will be placed on a performance improvement plan</li>
                            <li>Additional training and mentorship will be provided</li>
                        </ul>
                    </div>
                    
                    <p>We are committed to helping you improve. Please contact HR to discuss your development plan.</p>
                    
                    <p>Sincerely,<br>
                    <strong>HR Department</strong></p>
                </div>
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_CONFIG['sender']
        msg['To'] = to_email
        
        html_part = MIMEText(body, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['sender'], EMAIL_CONFIG['password'])
            server.send_message(msg)
        
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)

def log_email(emp_id, email, subject, status):
    """Log email in database"""
    try:
        print(f"[DEBUG] Attempting to log email - emp_id: {emp_id}, email: {email}")
        conn = get_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO email_log (emp_id, email, subject, status)
            VALUES (%s, %s, %s, %s)
            ''', (emp_id, email, subject, status))
            conn.commit()
            print(f"[OK] Email logged for emp_id {emp_id}")
            cursor.close()
            conn.close()
            return True
        else:
            print("[ERROR] Database connection failed")
            return False
    except Exception as e:
        print(f"[ERROR] Error logging email: {e}")
        return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        from werkzeug.security import check_password_hash
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
def index():
    accuracies = {
        'Logistic Regression': 0.85,
        'Decision Tree': 0.82, 
        'Random Forest': 0.88
    }
    return render_template('index.html', accuracies=accuracies)

@app.route('/dashboard')
@login_required
def dashboard():
    # Sample data – replace with real database queries
    total_employees = 248
    avg_performance = 4.2
    attrition_rate = 12.5
    promotion_eligible = 32
    return render_template('dashboard_overview.html',
                           total_employees=total_employees,
                           avg_performance=avg_performance,
                           attrition_rate=attrition_rate,
                           promotion_eligible=promotion_eligible)

@app.route('/employee', methods=['GET', 'POST'])
@login_required
def employee_form():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            age = int(request.form['age'])
            department = request.form['department'].lower()
            education = request.form['education'].lower()
            jobrole = request.form['jobrole'].lower()
            experience = int(request.form['experience'])
            income = int(request.form['income'])
            trainings = int(request.form['trainings'])
            worklife = int(request.form['worklife'])
            satisfaction = int(request.form['satisfaction'])
            overtime = int(request.form['overtime'])
            
            # Validate
            if department not in DEPT_MAP:
                flash('Invalid department', 'error')
                return redirect(url_for('employee_form'))
            
            if education not in EDU_MAP:
                flash('Invalid education', 'error')
                return redirect(url_for('employee_form'))
            
            if jobrole not in ROLE_MAP:
                flash('Invalid job role', 'error')
                return redirect(url_for('employee_form'))
            
            conn = get_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO employee 
                (name, email, age, department, education, jobrole, experience, 
                 income, trainings, worklife, satisfaction, overtime)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (name, email, age, DEPT_MAP[department], EDU_MAP[education],
                      ROLE_MAP[jobrole], experience, income, trainings, 
                      worklife, satisfaction, overtime))
                conn.commit()
                emp_id = cursor.lastrowid
                print(f"[OK] Employee inserted with ID: {emp_id}")
                cursor.close()
                conn.close()
                
                session['emp_id'] = emp_id
                flash('Employee registered successfully!', 'success')
                return redirect(url_for('team_leader_form', emp_id=emp_id))
            else:
                flash('Database connection error', 'error')
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            print(f"[ERROR] {e}")
    
    return render_template('employee_form.html')

@app.route('/team-leader/<int:emp_id>', methods=['GET', 'POST'])
@login_required
def team_leader_form(emp_id):
    # Get employee details
    conn = get_db()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('index'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM employee WHERE emp_id = %s', (emp_id,))
    emp = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not emp:
        flash('Employee not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            # Get form data
            work_quality = int(request.form['work_quality'])
            productivity = int(request.form['productivity'])
            attendance_input = float(request.form['attendance'])
            teamwork = int(request.form['teamwork'])
            communication = int(request.form['communication'])
            task_completion = int(request.form['task_completion'])
            problem_solving = int(request.form['problem_solving'])
            initiative = int(request.form['initiative'])
            adaptability = int(request.form['adaptability'])
            deadline = int(request.form['deadline'])
            
            # Validate
            if not (0 <= attendance_input <= 100):
                flash('Attendance must be between 0 and 100', 'error')
                return redirect(url_for('team_leader_form', emp_id=emp_id))
            
            # Convert attendance to 1-5 scale
            attendance = round((attendance_input / 100) * 5, 2)
            
            # Save evaluation
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO evaluations 
            (emp_id, work_quality, productivity, attendance, teamwork, communication,
             task_completion, problem_solving, initiative, adaptability, deadline)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (emp_id, work_quality, productivity, attendance, teamwork, 
                  communication, task_completion, problem_solving, initiative, 
                  adaptability, deadline))
            conn.commit()
            print(f"[OK] Evaluation inserted for emp_id {emp_id}")
            cursor.close()
            conn.close()
            
            # Calculate performance score
            scores = [work_quality, productivity, attendance, teamwork, communication,
                     task_completion, problem_solving, initiative, adaptability, deadline]
            performance_score = round(sum(scores) / len(scores), 2)
            
            # Determine performance level
            if performance_score <= 2.5:
                performance_level = "Low"
            elif performance_score <= 3.5:
                performance_level = "Medium"
            else:
                performance_level = "High"
            
            # Store in session
            session['emp_id'] = emp_id
            session['performance_score'] = performance_score
            session['performance_level'] = performance_level
            
            flash('Team leader evaluation saved!', 'success')
            return redirect(url_for('hr_analysis', emp_id=emp_id))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            print(f"[ERROR] {e}")
    
    emp['dept_name'] = DEPT_NAMES.get(emp['department'], 'Unknown')
    emp['role_name'] = ROLE_NAMES.get(emp['jobrole'], 'Unknown')
    
    return render_template('team_leader.html', employee=emp)

@app.route('/hr-analysis/<int:emp_id>', methods=['GET', 'POST'])
@login_required
def hr_analysis(emp_id):
    # Get employee and evaluation data
    conn = get_db()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('index'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM employee WHERE emp_id = %s', (emp_id,))
    emp = cursor.fetchone()
    
    cursor.execute('''
    SELECT * FROM evaluations WHERE emp_id = %s ORDER BY created_at DESC LIMIT 1
    ''', (emp_id,))
    eval_data = cursor.fetchone()
    
    # Get existing HR analysis
    cursor.execute('''
    SELECT * FROM hr_analysis WHERE emp_id = %s ORDER BY analyzed_at DESC LIMIT 1
    ''', (emp_id,))
    hr_data = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not emp:
        flash('Employee not found', 'error')
        return redirect(url_for('index'))
    
    emp['dept_name'] = DEPT_NAMES.get(emp['department'], 'Unknown')
    emp['edu_name'] = EDU_NAMES.get(emp['education'], 'Unknown')
    emp['role_name'] = ROLE_NAMES.get(emp['jobrole'], 'Unknown')
    emp['emp_id'] = emp['emp_id']
    
    # Get performance data
    performance_score = session.get('performance_score')
    performance_level = session.get('performance_level')
    
    # If not in session but in database, calculate from eval_data
    if not performance_score and eval_data:
        scores = [
            eval_data['work_quality'], eval_data['productivity'], eval_data['attendance'],
            eval_data['teamwork'], eval_data['communication'], eval_data['task_completion'],
            eval_data['problem_solving'], eval_data['initiative'], eval_data['adaptability'],
            eval_data['deadline']
        ]
        performance_score = round(sum(scores) / len(scores), 2)
        if performance_score <= 2.5:
            performance_level = "Low"
        elif performance_score <= 3.5:
            performance_level = "Medium"
        else:
            performance_level = "High"
    
    # Add evaluation data to employee dict for charts
    if eval_data:
        emp['work_quality'] = eval_data['work_quality']
        emp['productivity'] = eval_data['productivity']
        emp['attendance'] = eval_data['attendance']
        emp['teamwork'] = eval_data['teamwork']
        emp['communication'] = eval_data['communication']
        emp['task_completion'] = eval_data['task_completion']
        emp['problem_solving'] = eval_data['problem_solving']
        emp['initiative'] = eval_data['initiative']
        emp['adaptability'] = eval_data['adaptability']
        emp['deadline'] = eval_data['deadline']
    
    # Handle email sending
    email_sent = False
    if request.method == 'POST' and 'send_email' in request.form:
        print(f"\n[DEBUG] ===== EMAIL SENDING STARTED =====")
        print(f"[DEBUG] emp_id: {emp_id}")
        print(f"[DEBUG] employee email: {emp.get('email')}")
        print(f"[DEBUG] performance_score: {performance_score}")
        print(f"[DEBUG] performance_level: {performance_level}")
        
        if emp.get('email') and performance_score and performance_level:
            print(f"[DEBUG] Attempting to send email to {emp['email']}")
            success, message = send_email(
                emp['email'], emp['name'], 
                performance_level, performance_score
            )
            print(f"[DEBUG] Email send result - success: {success}, message: {message}")
            
            # Log the email attempt
            status = "Success" if success else f"Failed: {message}"
            log_result = log_email(emp_id, emp['email'], "Performance Evaluation", status)
            print(f"[DEBUG] Log email result: {log_result}")
            
            # Save HR analysis
            save_hr_analysis(emp_id, performance_score, performance_level, email_sent=success)
            
            if success:
                flash('Email sent successfully!', 'success')
                email_sent = True
            else:
                flash(f'Email failed: {message}', 'error')
        else:
            print("[DEBUG] Missing required data for email")
            flash('Cannot send email: Missing employee email or performance data', 'error')
        print(f"[DEBUG] ===== EMAIL SENDING COMPLETED =====\n")
    
    return render_template('hr_dashboard.html',
                         employee=emp,
                         performance_score=performance_score,
                         performance_level=performance_level,
                         hr_data=hr_data,
                         email_sent=email_sent,
                         accuracies={'Logistic Regression': 0.85, 'Decision Tree': 0.82, 'Random Forest': 0.88})

@app.route('/hr-reports')
@login_required
def hr_reports():
    """View all HR analysis reports"""
    conn = get_db()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('index'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
    SELECT h.*, e.name, e.email, e.department, e.jobrole
    FROM hr_analysis h
    JOIN employee e ON h.emp_id = e.emp_id
    ORDER BY h.analyzed_at DESC
    ''')
    reports = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Add department names
    for report in reports:
        report['dept_name'] = DEPT_NAMES.get(report['department'], 'Unknown')
        report['role_name'] = ROLE_NAMES.get(report['jobrole'], 'Unknown')
    
    return render_template('hr_reports.html', reports=reports)

@app.route('/employees-list')
@login_required
def employees_list():
    conn = get_db()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('index'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
    SELECT e.*, ev.work_quality, ev.productivity, ev.attendance, 
           ev.teamwork, ev.communication, ev.task_completion,
           ev.problem_solving, ev.initiative, ev.adaptability, ev.deadline,
           h.performance_score, h.performance_level, h.analyzed_at
    FROM employee e
    LEFT JOIN evaluations ev ON e.emp_id = ev.emp_id
    LEFT JOIN hr_analysis h ON e.emp_id = h.emp_id
    ORDER BY e.emp_id DESC
    ''')
    employees = cursor.fetchall()
    cursor.close()
    conn.close()
    
    emp_list = []
    for emp in employees:
        emp['dept_name'] = DEPT_NAMES.get(emp['department'], 'Unknown')
        emp['role_name'] = ROLE_NAMES.get(emp['jobrole'], 'Unknown')
        emp['emp_id'] = emp['emp_id']
        
        # If no HR analysis but evaluation exists, calculate performance
        if not emp.get('performance_score') and emp.get('work_quality') is not None:
            scores = [
                emp.get('work_quality', 0),
                emp.get('productivity', 0),
                emp.get('attendance', 0),
                emp.get('teamwork', 0),
                emp.get('communication', 0),
                emp.get('task_completion', 0),
                emp.get('problem_solving', 0),
                emp.get('initiative', 0),
                emp.get('adaptability', 0),
                emp.get('deadline', 0)
            ]
            if any(scores):
                emp['performance_score'] = round(sum(scores) / len(scores), 2)
                if emp['performance_score'] <= 2.5:
                    emp['performance_level'] = "Low"
                elif emp['performance_score'] <= 3.5:
                    emp['performance_level'] = "Medium"
                else:
                    emp['performance_level'] = "High"
        
        emp_list.append(emp)
    
    return render_template('employees_list.html', employees=emp_list)

@app.route('/email-log')
@login_required
def email_log():
    """View email sending log"""
    print("[DEBUG] Accessing email log page")
    conn = get_db()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('index'))
    
    cursor = conn.cursor(dictionary=True)
    
    # First check if there are any logs
    cursor.execute('SELECT COUNT(*) as count FROM email_log')
    count_result = cursor.fetchone()
    print(f"[DEBUG] Total email logs in database: {count_result['count']}")
    
    # Get all email logs with employee details
    cursor.execute('''
    SELECT 
        el.id,
        el.emp_id,
        el.email,
        el.subject,
        el.status,
        el.sent_at,
        e.name as employee_name
    FROM email_log el
    LEFT JOIN employee e ON el.emp_id = e.emp_id
    ORDER BY el.sent_at DESC
    ''')
    
    logs = cursor.fetchall()
    print(f"[DEBUG] Retrieved {len(logs)} logs from database")
    
    # Convert to list of dicts and ensure all fields exist
    log_list = []
    for log in logs:
        log_dict = dict(log)
        # Use employee_name from join, fallback to 'Unknown' if not found
        log_dict['name'] = log_dict.get('employee_name', 'Unknown')
        log_list.append(log_dict)
        print(f"[DEBUG] Log entry: {log_dict}")
    
    cursor.close()
    conn.close()
    
    return render_template('email_log.html', logs=log_list)

@app.route('/clear-session')
def clear_session():
    session.clear()
    flash('Session cleared', 'success')
    return redirect(url_for('index'))

@app.route('/check-data')
def check_data():
    """Debug route to check database contents"""
    conn = get_db()
    if not conn:
        return "Database connection error"
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM employee')
    employees = cursor.fetchall()
    
    cursor.execute('SELECT * FROM evaluations')
    evaluations = cursor.fetchall()
    
    cursor.execute('SELECT * FROM hr_analysis')
    hr_analysis = cursor.fetchall()
    
    cursor.execute('SELECT * FROM email_log')
    emails = cursor.fetchall()
    
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Format the output nicely
    result = f"""
    <html>
    <head>
        <title>Database Check</title>
        <style>
            body {{ font-family: Arial; padding: 20px; }}
            h2 {{ color: #333; margin-top: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .back {{ display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <h1>MySQL Database Contents - employee_system</h1>
        
        <h2>Employee Table ({len(employees)} records)</h2>
        <table>
            <tr>
                <th>emp_id</th><th>name</th><th>email</th><th>age</th><th>dept</th><th>edu</th><th>role</th><th>exp</th><th>income</th><th>trainings</th><th>worklife</th><th>satisfaction</th><th>overtime</th><th>created_at</th>
            </tr>
            {"".join(f"<tr><td>{e['emp_id']}</td><td>{e['name']}</td><td>{e['email']}</td><td>{e['age']}</td><td>{e['department']}</td><td>{e['education']}</td><td>{e['jobrole']}</td><td>{e['experience']}</td><td>{e['income']}</td><td>{e['trainings']}</td><td>{e['worklife']}</td><td>{e['satisfaction']}</td><td>{e['overtime']}</td><td>{e.get('created_at', 'N/A')}</td></tr>" for e in employees)}
        </table>
        
        <h2>Evaluations Table ({len(evaluations)} records)</h2>
        <table>
            <tr>
                <th>id</th><th>emp_id</th><th>work</th><th>prod</th><th>attend</th><th>team</th><th>comm</th><th>task</th><th>problem</th><th>init</th><th>adapt</th><th>deadline</th><th>created_at</th>
            </tr>
            {"".join(f"<tr><td>{ev['id']}</td><td>{ev['emp_id']}</td><td>{ev['work_quality']}</td><td>{ev['productivity']}</td><td>{ev['attendance']}</td><td>{ev['teamwork']}</td><td>{ev['communication']}</td><td>{ev['task_completion']}</td><td>{ev['problem_solving']}</td><td>{ev['initiative']}</td><td>{ev['adaptability']}</td><td>{ev['deadline']}</td><td>{ev.get('created_at', 'N/A')}</td></tr>" for ev in evaluations)}
        </table>
        
        <h2>HR Analysis Table ({len(hr_analysis)} records)</h2>
        <table>
            <tr>
                <th>hr_id</th><th>emp_id</th><th>score</th><th>level</th><th>ml_pred</th><th>email_sent</th><th>analyzed_at</th>
            </tr>
            {"".join(f"<tr><td>{h['hr_id']}</td><td>{h['emp_id']}</td><td>{h['performance_score']}</td><td>{h['performance_level']}</td><td>{h['ml_prediction']}</td><td>{h['email_sent']}</td><td>{h['analyzed_at']}</td></tr>" for h in hr_analysis)}
        </table>
        
        <h2>Email Log Table ({len(emails)} records)</h2>
        <table>
            <tr>
                <th>id</th><th>emp_id</th><th>email</th><th>subject</th><th>status</th><th>sent_at</th>
            </tr>
            {"".join(f"<tr><td>{em['id']}</td><td>{em['emp_id']}</td><td>{em['email']}</td><td>{em['subject']}</td><td>{em['status']}</td><td>{em['sent_at']}</td></tr>" for em in emails)}
        </table>
        
        <h2>Users Table ({len(users)} records)</h2>
        <table>
            <tr>
                <th>id</th><th>username</th><th>created_at</th>
            </tr>
            {"".join(f"<tr><td>{u['id']}</td><td>{u['username']}</td><td>{u['created_at']}</td></tr>" for u in users)}
        </table>
        
        <a href="/" class="back">Back to Home</a>
    </body>
    </html>
    """
    return result

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("EMPLOYEE PERFORMANCE SYSTEM STARTING")
    print("=" * 60)
    print("URL: http://localhost:5000")
    print("\nMySQL Database: employee_system")
    print("Debug route: http://localhost:5000/check-data")
    print("Email Log: http://localhost:5000/email-log")
    print("HR Reports: http://localhost:5000/hr-reports")
    print("Dashboard: http://localhost:5000/dashboard")
    print("=" * 60 + "\n")
    app.run(debug=True, port=5000)
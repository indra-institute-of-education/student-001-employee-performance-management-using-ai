import mysql.connector
from mysql.connector import Error
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DB
            )
            logger.info("Database connected successfully")
        except Error as e:
            logger.error(f"Error connecting to database: {e}")
            self.create_database()
    
    def create_database(self):
        """Create database and tables if they don't exist"""
        try:
            # Connect without database
            conn = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD
            )
            cursor = conn.cursor()
            
            # Create database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
            cursor.execute(f"USE {Config.MYSQL_DB}")
            
            # Create employee table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS employee (
                emp_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
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
            """)
            
            # Create team_leader table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_leader (
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
            """)
            
            # Create hr table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS hr (
                hr_id INT AUTO_INCREMENT PRIMARY KEY,
                emp_id INT NOT NULL,
                prediction INT NOT NULL,
                score FLOAT NOT NULL,
                level VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (emp_id) REFERENCES employee(emp_id) ON DELETE CASCADE
            )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Reconnect with database
            self.connect()
            logger.info("Database and tables created successfully")
            
        except Error as e:
            logger.error(f"Error creating database: {e}")
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """Execute a query and return results"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                self.connection.commit()
                result = cursor.lastrowid
            
            cursor.close()
            return result
            
        except Error as e:
            logger.error(f"Database error: {e}")
            self.connection.rollback()
            return None
    
    def insert_employee(self, data):
        """Insert employee data"""
        query = """
        INSERT INTO employee 
        (name, email, age, department, education, jobrole, experience, 
         income, trainings, worklife, satisfaction, overtime)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, data)
    
    def insert_team_leader(self, emp_id, data):
        """Insert team leader evaluation"""
        query = """
        INSERT INTO team_leader
        (emp_id, work_quality, productivity, attendance, teamwork, communication,
         task_completion, problem_solving, initiative, adaptability, deadline)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (emp_id,) + data
        return self.execute_query(query, params)
    
    def insert_hr_result(self, emp_id, prediction, score, level):
        """Insert HR analysis result"""
        query = """
        INSERT INTO hr (emp_id, prediction, score, level)
        VALUES (%s, %s, %s, %s)
        """
        return self.execute_query(query, (emp_id, prediction, score, level))
    
    def get_employee(self, emp_id):
        """Get employee by ID"""
        query = "SELECT * FROM employee WHERE emp_id = %s"
        return self.execute_query(query, (emp_id,), fetch_one=True)
    
    def get_all_employees(self):
        """Get all employees with their latest HR results"""
        query = """
        SELECT e.*, h.score, h.level, h.prediction,
               DATE_FORMAT(e.created_at, '%%Y-%%m-%%d') as join_date
        FROM employee e
        LEFT JOIN hr h ON e.emp_id = h.emp_id
        ORDER BY e.created_at DESC
        """
        return self.execute_query(query, fetch_all=True)
    
    def get_employee_with_details(self, emp_id):
        """Get employee with team leader and HR details"""
        query = """
        SELECT e.*, t.*, h.score, h.level, h.prediction as ml_prediction,
               DATE_FORMAT(e.created_at, '%%Y-%%m-%%d') as join_date
        FROM employee e
        LEFT JOIN team_leader t ON e.emp_id = t.emp_id
        LEFT JOIN hr h ON e.emp_id = h.emp_id
        WHERE e.emp_id = %s
        ORDER BY t.created_at DESC, h.created_at DESC
        LIMIT 1
        """
        return self.execute_query(query, (emp_id,), fetch_one=True)
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Database connection closed")
import mysql.connector

# --- CONFIG ---
db_config = {
    'user': 'root', 
    'password': '', 
    'host': 'localhost', 
    'database': 'student_db'
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    print("--- 1. Setting up Admin Table ---")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            username VARCHAR(50) PRIMARY KEY,
            password VARCHAR(255)
        )
    """)
    # Create default admin if missing
    cursor.execute("SELECT * FROM admins WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO admins (username, password) VALUES ('admin', 'admin')")
        print("✅ Admin User Created (User: admin, Pass: admin)")
    else:
        print("ℹ️ Admin already exists.")

    print("\n--- 2. Adding Password to Students ---")
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN password VARCHAR(255)")
        print("✅ Password column added to Students table.")
    except:
        print("ℹ️ Password column already exists.")

    # Set default password for existing students to be their Reg Number
    print("--- 3. Setting Default Passwords ---")
    cursor.execute("UPDATE students SET password = reg_number WHERE password IS NULL OR password = ''")
    
    conn.commit()
    conn.close()
    print("\nSUCCESS: Security System Ready! You can close this.")

except Exception as e:
    print(f"Error: {e}")
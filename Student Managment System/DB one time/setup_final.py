import mysql.connector

db_config = {
    'user': 'root', 
    'password': '', 
    'host': 'localhost', 
    'database': 'student_db'
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    print("--- 1. Checking Grades Table (Mids/Finals) ---")
    try:
        cursor.execute("ALTER TABLE grades ADD COLUMN mid_term_score INT DEFAULT 0")
        print("✅ Added 'mid_term_score' column.")
    except: print("ℹ️ 'mid_term_score' already exists.")

    try:
        cursor.execute("ALTER TABLE grades ADD COLUMN final_term_score INT DEFAULT 0")
        print("✅ Added 'final_term_score' column.")
    except: print("ℹ️ 'final_term_score' already exists.")

    print("\n--- 2. Checking Attendance Table ---")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_reg VARCHAR(50),
            date VARCHAR(20),
            status VARCHAR(20),
            method VARCHAR(20)
        )
    """)
    print("✅ Attendance table secured.")

    conn.commit()
    conn.close()
    print("\nSUCCESS: Database is fully updated!")

except Exception as e:
    print(f"Error: {e}")
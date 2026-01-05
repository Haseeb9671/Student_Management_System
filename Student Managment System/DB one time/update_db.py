import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost", user="root", password="", database="student_db"
    )
    cursor = conn.cursor()

    # Add columns to store the filename of the uploaded assignment
    cursor.execute("ALTER TABLE grades ADD COLUMN assignment_file VARCHAR(255) DEFAULT NULL")
    
    # Add column to store quiz answers (text)
    cursor.execute("ALTER TABLE grades ADD COLUMN quiz_submission TEXT DEFAULT NULL")

    conn.commit()
    print("SUCCESS: Database updated to support uploads!")
    conn.close()
except Exception as e:
    print(f"Error (or already updated): {e}")
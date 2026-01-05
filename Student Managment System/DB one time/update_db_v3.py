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

    # Add Mids and Finals columns to the grades table
    print("Adding Mids and Finals columns...")
    cursor.execute("ALTER TABLE grades ADD COLUMN mid_term_score INT DEFAULT 0")
    cursor.execute("ALTER TABLE grades ADD COLUMN final_term_score INT DEFAULT 0")
    
    conn.commit()
    print("SUCCESS: Database updated! Mids and Finals added.")
    conn.close()

except Exception as e:
    print(f"Info/Error: {e}")
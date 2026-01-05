import mysql.connector

# Your database configuration
db_config = {
    'user': 'root',
    'password': '',  # Put your password here if you have one
    'host': 'localhost',
    'database': 'student_db'
}

try:
    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Add the new columns to the 'students' table
    print("Adding 'email' and 'department' columns...")
    cursor.execute("ALTER TABLE students ADD COLUMN email VARCHAR(100) AFTER name")
    cursor.execute("ALTER TABLE students ADD COLUMN department VARCHAR(100) AFTER email")
    
    conn.commit()
    print("SUCCESS: Database updated! Your students table now has email and department fields.")
    
    conn.close()

except mysql.connector.Error as err:
    if err.errno == 1060: # Error code for "Duplicate column name"
        print("INFO: Columns already exist. No changes needed.")
    else:
        print(f"Error: {err}")
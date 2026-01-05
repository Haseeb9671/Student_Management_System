import mysql.connector

db_config = {
    'user': 'root',
    'password': '',  # Your MySQL password
    'host': 'localhost',
    'database': 'student_db'
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    print("=" * 60)
    print("  DATABASE UPDATE: CSV TRACKING SYSTEM")
    print("=" * 60)
    
    print("\n📝 Adding 'csv_source' column to students table...")
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN csv_source VARCHAR(255) DEFAULT 'manual'")
        print("✅ Column 'csv_source' added successfully!")
    except mysql.connector.Error as err:
        if err.errno == 1060:  # Duplicate column
            print("ℹ️  Column 'csv_source' already exists.")
        else:
            raise err
    
    print("\n🔄 Setting default values for existing students...")
    cursor.execute("UPDATE students SET csv_source='manual' WHERE csv_source IS NULL")
    affected = cursor.rowcount
    print(f"✅ Updated {affected} existing student records.")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("  ✅ SUCCESS! Database is ready for CSV tracking!")
    print("=" * 60)
    print("\nWhat this does:")
    print("  • Tracks which CSV file each student came from")
    print("  • When you delete a CSV, it removes those students")
    print("  • Shows student count for each CSV in dashboard")
    print("\n" + "=" * 60)

except mysql.connector.Error as err:
    print(f"\n❌ Database Error: {err}")
except Exception as e:
    print(f"\n❌ Error: {e}")

input("\nPress Enter to exit...")
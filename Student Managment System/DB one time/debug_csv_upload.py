import mysql.connector
import csv
import os

db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'student_db'
}

CSV_BACKUP_FOLDER = 'csv_backups'

print("=" * 70)
print("  CSV UPLOAD DEBUG TOOL")
print("=" * 70)

try:
    # Check database connection
    print("\n1️⃣ Checking database connection...")
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    print("   ✅ Database connected!")
    
    # Check how many students in database
    print("\n2️⃣ Checking students in database...")
    cursor.execute("SELECT COUNT(*) as count FROM students")
    result = cursor.fetchone()
    student_count = result['count']
    print(f"   📊 Total students in database: {student_count}")
    
    if student_count > 0:
        print("\n   Sample students:")
        cursor.execute("SELECT reg_number, name, department FROM students LIMIT 5")
        for student in cursor.fetchall():
            print(f"      • {student['reg_number']} - {student['name']} ({student['department']})")
    
    # Check CSV backups folder
    print("\n3️⃣ Checking CSV backup folder...")
    if os.path.exists(CSV_BACKUP_FOLDER):
        csv_files = [f for f in os.listdir(CSV_BACKUP_FOLDER) if f.endswith('.csv')]
        print(f"   📁 Found {len(csv_files)} CSV file(s)")
        
        if csv_files:
            # Read the most recent CSV
            latest_csv = sorted(csv_files)[-1]
            csv_path = os.path.join(CSV_BACKUP_FOLDER, latest_csv)
            print(f"\n4️⃣ Reading latest CSV: {latest_csv}")
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                print(f"   📋 CSV Headers: {headers}")
                
                rows = list(reader)
                print(f"   📊 Total rows in CSV: {len(rows)}")
                
                if len(rows) > 0:
                    print("\n   Sample data (first 3 rows):")
                    for i, row in enumerate(rows[:3], 1):
                        print(f"\n   Row {i}:")
                        for key, value in row.items():
                            print(f"      {key}: {value}")
                    
                    # Check if these students are in database
                    print("\n5️⃣ Checking if CSV students are in database...")
                    first_reg = rows[0].get('REG_NO') or rows[0].get('reg_number')
                    if first_reg:
                        cursor.execute("SELECT * FROM students WHERE reg_number=%s", (first_reg,))
                        db_student = cursor.fetchone()
                        
                        if db_student:
                            print(f"   ✅ Found in database: {first_reg}")
                        else:
                            print(f"   ❌ NOT found in database: {first_reg}")
                            print("\n   🔍 This is the problem! CSV uploaded but students not inserted.")
                            print("\n   Possible reasons:")
                            print("      1. CSV column names don't match (REG_NO vs reg_number)")
                            print("      2. Students might already exist (duplicate)")
                            print("      3. Database insert failed silently")
                else:
                    print("   ⚠️ CSV file is empty!")
        else:
            print("   ⚠️ No CSV files found!")
    else:
        print("   ❌ CSV backup folder doesn't exist!")
    
    # Check table structure
    print("\n6️⃣ Checking students table structure...")
    cursor.execute("DESCRIBE students")
    columns = cursor.fetchall()
    print("   Columns in students table:")
    for col in columns:
        print(f"      • {col['Field']} ({col['Type']})")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("  DEBUG COMPLETE")
    print("=" * 70)

except mysql.connector.Error as err:
    print(f"\n❌ Database Error: {err}")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

input("\nPress Enter to exit...")
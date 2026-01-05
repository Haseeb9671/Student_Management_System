import mysql.connector
import os
import shutil

db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'student_db'
}

CSV_BACKUP_FOLDER = 'csv_backups'
CSV_FILE = 'lms_students.csv'

print("=" * 70)
print("  ⚠️  COMPLETE DATA CLEANUP TOOL")
print("=" * 70)
print("\nThis will:")
print("  ❌ Delete ALL students from database")
print("  ❌ Delete ALL grades")
print("  ❌ Delete ALL attendance records")
print("  ❌ Delete ALL CSV backup files")
print("  ❌ Clear main CSV file")
print("\n⚠️  THIS CANNOT BE UNDONE!")
print("=" * 70)

confirm = input("\nType 'DELETE ALL' to confirm: ")

if confirm != "DELETE ALL":
    print("\n❌ Cancelled. No changes made.")
    input("Press Enter to exit...")
    exit()

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    print("\n🗑️  Deleting all database records...")
    
    # Delete all data
    cursor.execute("DELETE FROM attendance")
    attendance_count = cursor.rowcount
    print(f"   ✅ Deleted {attendance_count} attendance records")
    
    cursor.execute("DELETE FROM grades")
    grades_count = cursor.rowcount
    print(f"   ✅ Deleted {grades_count} grade records")
    
    cursor.execute("DELETE FROM students")
    students_count = cursor.rowcount
    print(f"   ✅ Deleted {students_count} students")
    
    conn.commit()
    conn.close()
    
    print("\n🗑️  Deleting CSV backup files...")
    if os.path.exists(CSV_BACKUP_FOLDER):
        csv_files = [f for f in os.listdir(CSV_BACKUP_FOLDER) if f.endswith('.csv')]
        for csv_file in csv_files:
            os.remove(os.path.join(CSV_BACKUP_FOLDER, csv_file))
        print(f"   ✅ Deleted {len(csv_files)} CSV backup files")
    else:
        print("   ℹ️  No CSV backup folder found")
    
    print("\n🗑️  Clearing main CSV file...")
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            f.write('REG_NO,FULL_NAME,UNIVERSITY_EMAIL,DEPARTMENT\n')
        print("   ✅ Main CSV cleared")
    
    print("\n" + "=" * 70)
    print("  ✅ SUCCESS! ALL DATA DELETED!")
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  • {students_count} students removed")
    print(f"  • {grades_count} grade records removed")
    print(f"  • {attendance_count} attendance records removed")
    print(f"  • All CSV backups deleted")
    print("\nYour database is now completely clean! 🎉")
    print("=" * 70)

except mysql.connector.Error as err:
    print(f"\n❌ Database Error: {err}")
except Exception as e:
    print(f"\n❌ Error: {e}")

input("\nPress Enter to exit...")
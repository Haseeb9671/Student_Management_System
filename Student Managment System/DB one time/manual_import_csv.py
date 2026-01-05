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
print("  MANUAL CSV IMPORT TOOL")
print("=" * 70)

# List available CSV files
print("\nAvailable CSV files:")
if os.path.exists(CSV_BACKUP_FOLDER):
    csv_files = [f for f in os.listdir(CSV_BACKUP_FOLDER) if f.endswith('.csv')]
    
    if not csv_files:
        print("❌ No CSV files found in csv_backups folder!")
        input("Press Enter to exit...")
        exit()
    
    for i, filename in enumerate(csv_files, 1):
        print(f"  {i}. {filename}")
    
    choice = input(f"\nSelect file number (1-{len(csv_files)}): ")
    try:
        selected_file = csv_files[int(choice) - 1]
    except:
        print("❌ Invalid choice!")
        input("Press Enter to exit...")
        exit()
else:
    print("❌ csv_backups folder not found!")
    input("Press Enter to exit...")
    exit()

csv_path = os.path.join(CSV_BACKUP_FOLDER, selected_file)

print(f"\n📄 Selected: {selected_file}")
print("\nReading CSV file...")

try:
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    print(f"✅ Found {len(rows)} students in CSV")
    
    if len(rows) == 0:
        print("❌ CSV is empty!")
        input("Press Enter to exit...")
        exit()
    
    # Show sample
    print("\nSample data (first row):")
    for key, value in rows[0].items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 70)
    confirm = input(f"\nImport {len(rows)} students? Type 'YES' to confirm: ")
    
    if confirm != 'YES':
        print("❌ Cancelled.")
        input("Press Enter to exit...")
        exit()
    
    # Import to database
    print("\nConnecting to database...")
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    imported = 0
    skipped = 0
    errors = 0
    
    print("\nImporting students...")
    for row in rows:
        try:
            # Support both column name formats
            reg_num = row.get('REG_NO') or row.get('reg_number')
            name = row.get('FULL_NAME') or row.get('name')
            email = row.get('UNIVERSITY_EMAIL') or row.get('email') or ''
            dept = row.get('DEPARTMENT') or row.get('department') or ''
            
            if not reg_num or not name:
                print(f"⚠️  Skipping row: Missing reg_number or name")
                skipped += 1
                continue
            
            # Check if exists
            cursor.execute("SELECT * FROM students WHERE reg_number=%s", (reg_num,))
            if cursor.fetchone():
                print(f"⚠️  {reg_num} already exists, skipping...")
                skipped += 1
                continue
            
            # Insert student
            cursor.execute("""
                INSERT INTO students (reg_number, name, email, department, password, csv_source) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (reg_num, name, email, dept, reg_num, selected_file))
            
            # Create grades entry
            cursor.execute("INSERT INTO grades (student_reg) VALUES (%s)", (reg_num,))
            
            imported += 1
            print(f"✅ {reg_num} - {name}")
            
        except Exception as e:
            print(f"❌ Error importing {reg_num}: {e}")
            errors += 1
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 70)
    print("  IMPORT COMPLETE!")
    print("=" * 70)
    print(f"\n✅ Imported: {imported}")
    print(f"⚠️  Skipped: {skipped}")
    print(f"❌ Errors: {errors}")
    print(f"\nTotal in CSV: {len(rows)}")
    print("=" * 70)

except FileNotFoundError:
    print(f"❌ File not found: {csv_path}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

input("\nPress Enter to exit...")
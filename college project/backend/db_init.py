import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'college.db')

# Create DB and tables
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Students table
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    rollno TEXT PRIMARY KEY,
    name TEXT NOT NULL
)
''')

# Results table
cursor.execute('''
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_rollno TEXT,
    semester TEXT,
    subject_name TEXT,
    marks INTEGER,
    FOREIGN KEY (student_rollno) REFERENCES students (rollno)
)
''')

# Sample data
sample_students = [
    ('2023001', 'John Doe'),
    ('2023002', 'Jane Smith'),
    ('2023003', 'Alice Johnson')
]

for roll, name in sample_students:
    cursor.execute('INSERT OR IGNORE INTO students (rollno, name) VALUES (?, ?)', (roll, name))

sample_results = [
    ('2023001', 'Sem 1', 'Math', 85),
    ('2023001', 'Sem 1', 'Physics', 92),
    ('2023001', 'Sem 1', 'Chemistry', 78),
    ('2023002', 'Sem 1', 'Math', 88),
    ('2023002', 'Sem 1', 'Physics', 95),
    ('2023002', 'Sem 1', 'Chemistry', 82),
    ('2023003', 'Sem 2', 'Math', 76),
    ('2023003', 'Sem 2', 'Physics', 84),
    ('2023003', 'Sem 2', 'Chemistry', 91)
]

cursor.executemany('INSERT OR IGNORE INTO results (student_rollno, semester, subject_name, marks) VALUES (?, ?, ?, ?)', sample_results)

conn.commit()
conn.close()

print(f"Database created/initialized at {DB_PATH}")
print("Sample data added for rolls 2023001, 2023002, 2023003.")
print("Run: python backend/result.py to test API.")
print("Use backend/db_manage.py (next) for manual edits.")

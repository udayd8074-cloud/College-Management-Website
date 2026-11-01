import sqlite3
import os
from tabulate import tabulate  # Optional for pretty tables, pip install if needed

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'college.db')

def calculate_percentage(marks_list):
    return round(sum(marks_list) / len(marks_list), 2)

def calculate_grade(percentage):
    if percentage >= 90: return "A+"
    elif percentage >= 75: return "A"
    elif percentage >= 60: return "B"
    elif percentage >= 50: return "C"
    else: return "Fail"

def get_conn():
    return sqlite3.connect(DB_PATH)

def add_student():
    roll = input("Enter rollno: ")
    name = input("Enter name:  ")
    semester = input("Enter semester :  ")
    subjects = {}
    while True:
        sub = input("Enter subject name (or 'done' to finish): ")
        if sub.lower() == 'done': break
        mark = int(input(f"Enter marks for {sub}: "))
        subjects[sub] = mark
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO students (rollno, name) VALUES (?, ?)", (roll, name))
        for sub, mark in subjects.items():
            cursor.execute("INSERT INTO results (student_rollno, semester, subject_name, marks) VALUES (?, ?, ?, ?)",
                           (roll, semester, sub, mark))
        conn.commit()
        perc = calculate_percentage(list(subjects.values()))
        print(f"Added/Updated {name}. {semester} Percentage: {perc}%, Grade: {calculate_grade(perc)}")

def view_students():
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT rollno, name FROM students")
        students = cursor.fetchall()
        print(tabulate(students, headers=['Rollno', 'Name'], tablefmt='grid'))

def view_results(roll):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM students WHERE rollno=?", (roll,))
        name = cursor.fetchone()
        if not name:
            print("Student not found.")
            return
        print(f"\nResults for {name[0]} ({roll}):")
        cursor.execute("""
            SELECT semester, subject_name, marks FROM results WHERE student_rollno=? ORDER BY semester
        """, (roll,))
        rows = cursor.fetchall()
        if rows:
            sem_marks = {}
            for sem, sub, mark in rows:
                if sem not in sem_marks: sem_marks[sem] = []
                sem_marks[sem].append(mark)
            for sem, marks in sem_marks.items():
                perc = calculate_percentage(marks)
                print(f"{sem}: {perc}% - {calculate_grade(perc)}")
        else:
            print("No results found.")

def update_mark():
    roll = input("Enter rollno: ")
    sem = input("Enter semester: ")
    sub = input("Enter subject name: ")
    new_mark = int(input("Enter new marks: "))
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE results SET marks=? WHERE student_rollno=? AND semester=? AND subject_name=?
        """, (new_mark, roll, sem, sub))
        if cursor.rowcount:
            conn.commit()
            print("Updated.")
        else:
            print("Not found.")

def delete_student():
    roll = input("Enter rollno to delete: ")
    confirm = input("Confirm? (y/n): ")
    if confirm.lower() == 'y':
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM results WHERE student_rollno=?", (roll,))
            cursor.execute("DELETE FROM students WHERE rollno=?", (roll,))
            conn.commit()
            print("Deleted.")

if __name__ == "__main__":
    while True:
        print("\n1. Add/Update Student\n2. View Students\n3. View Student Results\n4. Update Mark\n5. Delete Student\n6. Exit")
        choice = input("Choose: ")
        if choice == '1': add_student()
        elif choice == '2': view_students()
        elif choice == '3':
            roll = input("Enter rollno: ")
            view_results(roll)
        elif choice == '4': update_mark()
        elif choice == '5': delete_student()
        elif choice == '6': break
        else: print("Invalid.")

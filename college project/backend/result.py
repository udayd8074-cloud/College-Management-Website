from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 🔥 allows frontend to connect

def calculate_percentage(subjects):
    total = sum(sub["marks"] for sub in subjects)
    return round(total / len(subjects), 2)

def calculate_grade(percentage):
    if percentage >= 90: return "A+"
    elif percentage >= 75: return "A"
    elif percentage >= 60: return "B"
    elif percentage >= 50: return "C"
    else: return "Fail"

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "college.db")

@app.route('/result')
def get_result():
    roll = request.args.get('rollno')
    sem = request.args.get('semester')

    if not roll or not sem:
        return jsonify({"error": "Rollno and semester required"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get student name
    cursor.execute("SELECT name FROM students WHERE rollno = ?", (roll,))
    student = cursor.fetchone()
    if not student:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    name = student[0]

    # Get subjects/marks for semester
    cursor.execute("""
        SELECT subject_name, marks FROM results 
        WHERE student_rollno = ? AND semester = ?
    """, (roll, sem))
    subject_rows = cursor.fetchall()
    conn.close()

    if not subject_rows:
        return jsonify({"error": "Result not found for this semester"}), 404

    subjects = [{"name": row[0], "marks": row[1]} for row in subject_rows]

    percentage = calculate_percentage(subjects)
    grade = calculate_grade(percentage)

    # Calculate CGPA (avg % over all semesters for student)
    conn2 = sqlite3.connect(DB_PATH)
    cursor2 = conn2.cursor()
    cursor2.execute("""
        SELECT semester, AVG(marks) as sem_perc 
        FROM results WHERE student_rollno = ? GROUP BY semester
    """, (roll,))
    sem_percs = cursor2.fetchall()
    conn2.close()
    cgpa = round(sum(p[1] for p in sem_percs) / len(sem_percs), 2) if sem_percs else percentage

    return jsonify({
        "name": name,
        "rollno": roll,
        "semester": sem,
        "subjects": subjects,
        "percentage": percentage,
        "grade": grade,
        "cgpa": cgpa
    })


if __name__ == "__main__":
    app.run(debug=True)

    
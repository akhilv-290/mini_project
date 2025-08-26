import sqlite3
import hashlib

conn=sqlite3.connect('student_grades.db')

cursor=conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'student')) NOT NULL
)
''')

cursor.execute('''
               CREATE TABLE IF NOT EXISTS students(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name VARCHAR(30))
''')

cursor.execute('''
               CREATE TABLE IF NOT EXISTS grades(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               student_id INTEGER,
               subject TEXT NOT NULL,
               grade REAL NOT NULL
               )
''')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register():
    print("\n--- Register ---")
    username = input("Enter username: ")
    password = input("Enter password: ")
    role = input("Enter role (admin/student): ")

    if role not in ["admin", "student"]:
        print("Invalid role. Choose 'admin' or 'student'.\n")
        return

    hashed_pw = hash_password(password)

    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, hashed_pw, role))
        id = cursor.lastrowid

        if role == "student":
            name = input("Enter full name of the student: ")
            cursor.execute("INSERT INTO students (id, name) VALUES (?, ?)", (id, name))

        conn.commit()
        print("Registration successful!\n")
    except sqlite3.IntegrityError:
        print("Username already exists.\n")


def login():
    print("\n--- Login ---")
    username = input("Username: ")
    password = input("Password: ")
    hashed_pw = hash_password(password)

    cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
    user = cursor.fetchone()

    if user:
        print(f"\nWelcome, {user[1]}! You are logged in as {user[2]}.\n")
        if user[2] == "admin":
            admin_menu()
        else:
            student_menu(user[0])
    else:
        print("Invalid credentials.\n")

def admin_menu():
    while True:
        print("\n--- Admin Menu ---")
        print("1. Add student")
        print("2. Add Grade for Student")
        print("3. View All Students and Grades")
        print("4. Update Grade by Grade ID")
        print("5. Delete student")
        print("6. Exit")

        choice = input("Enter choice: ")
        if choice == "1":
            name=input("Enter name:")
            add_student(name)
        if choice == "2":
            student_id=int(input("Enter Student ID:"))
            subject=input("Enter subject:")
            grade=float(input("Enter grade:"))
            add_grade(student_id,subject,grade)
        elif choice == "3":
            view_all()
        elif choice=="4":
            grade_id=int(input("Enter Grade ID:"))
            new_grade=float(input("Enter new grade:"))
            update_grade(grade_id,new_grade)
        elif choice=="5":
            student_id=int(input("Enter Student ID to delete:"))
            delete_student(student_id)
        elif choice=="6":
            print("Exiting. Thank you")
            break
        else:
            print("Invalid choice.")

def add_student(name):
    cursor.execute('''
                   INSERT INTO students (name) VALUES (?)
''',(name,))
    conn.commit
    print(f"Student '{name}' is added successfully")

def add_grade(student_id,subject,grade):
    cursor.execute('''
                   INSERT INTO grades (student_id,subject,grade) VALUES (?,?,?)
                   ''',(student_id,subject,grade))
    conn.commit()
    print("Grade added")


def view_all():
    cursor.execute('''
                   SELECT students.id,students.name,grades.subject,grades.grade FROM students
                   LEFT JOIN grades ON students.id=grades.student_id
                   ORDER BY students.id
''')    

    rows=cursor.fetchall()
    for row in rows:
        print(row)
    if not rows:
        print("No records found")


def update_grade(grade_id,new_grade):
    cursor.execute('''
                   UPDATE grades SET grade=? WHERE id=?                   
''',(new_grade,grade_id))
    conn.commit()
    print("Grade updated")


def delete_student(student_id):
    cursor.execute('''
                DELETE FROM students WHERE id=?
''',(student_id,))
    conn.commit
    print("Deleted.")


def student_menu(student_id):
    while True:
        print("\n--- Student Menu ---")
        print("1. View grades")
        print("2. Exit")

        choice=input("Enter your choice:")
        if choice=="1":
            student_id=int(input("Enter Student ID:"))
            view_student_grades(student_id)
        elif choice=="2":
            print("Exiting. Thank you ")
            break
        else:
            print("Invalid choice.")


def view_student_grades(student_id):
    cursor.execute('''
                   SELECT grades.id,subject,grade FROM grades WHERE student_id=?
''',(student_id,))
    rows=cursor.fetchall()
    for row in rows:
        print(f"Grade ID:{row[0]} subject:{row[1]} Grade:{row[2]}")
    if not rows:
        print("No grades found for this student")
        return
    
def main():
    while True:
        print("==== Student Grading System ====")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            register()
        elif choice == "2":
            login()
        elif choice == "3":
            print("Exiting system.")
            break
        else:
            print("Invalid choice.\n")


main()
conn.close()

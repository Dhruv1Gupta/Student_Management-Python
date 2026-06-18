import mysql.connector
from mysql.connector import Error #Error class for handling database-related exceptions
import os #os module for file handling operations

class StudentManagementSystem:
  def __init__(self):
    self.backup_file = 'students_backup.txt'  # Backup text file name for storing student records
    try: 
      # Establish connection with MySQL database
      self.conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='student_db'
      )
      # Create cursor object to execute SQL queries
      # dictionary=True returns records as dictionary
      self.cursor = self.conn.cursor(dictionary=True)
      print("Connected to MySQL successfully")
    # Handle connection errors
    except Error as e:
      print(f"Database connection failed: {e}")
      exit(1) # Exit program if database connection fails
  # Function to validate user inputs
  def validate_input(self, name, age, roll_no, marks):
    if not name.strip(): # Check if name is empty
      raise ValueError("Name cannot be empty")
    # Check if age is positive integer
    if not isinstance(age, int) or age <= 0:
      raise ValueError("Age must be positive integer")
    if not isinstance(roll_no, int) or roll_no <= 0:
      raise ValueError("Roll number must be positive integer")
    if not isinstance(marks, (int, float)) or marks < 0 or marks > 100:
      raise ValueError("Marks must be between 0 and 100")
    return True # Return True if all validations pass
  def add_student(self):
    try:
      roll_no = int(input("Enter Roll Number: "))
      name = input("Enter Name: ").strip()
      age = int(input("Enter Age: "))
      marks = float(input("Enter Marks: "))
      class_sec = input("Enter Class/Section: ").strip()
      self.validate_input(name, age, roll_no, marks)  # Validate all inputs
      query = "INSERT INTO students VALUES (%s, %s, %s, %s, %s)"
      self.cursor.execute(query, (roll_no, name, age, marks, class_sec))
      self.conn.commit()
      print("Student added successfully")
      self.export_to_file() # Export updated records to text file
    except ValueError as e: # Handle invalid input
      print(f"Invalid in1put: {e}")
    except Error as e: # Handle database errors
      if e.errno == 1062: # Error 1062 means duplicate primary key
        print("Roll number already exists")
      else:
        print(f"Database error: {e}")
    except Exception as e: # Handle any other exceptions
      print(f"Error: {e}")
  def view_students(self):
    try:
      self.cursor.execute("SELECT * FROM students ORDER BY roll_no") # Retrieve all student records sorted by roll number
      records = self.cursor.fetchall() # Fetch all records
      if not records:
        print("No student records found")
        return
      print("\n-- All Student Records --")
      print(f"{'Roll No':<10} {'Name':<20} {'Age':<5} {'Marks':<7} {'Class':<10}")
      print("-" * 55)
      for r in records:
        print(f"{r['roll_no']:<10} {r['name']:<20} {r['age']:<5} {r['marks']:<7} {r['class_section']:<10}")
    except Error as e:
      print(f"Database error: {e}")
  def update_student(self):
    try:
      roll_no = int(input("Enter Roll Number to update: "))
      # Check whether student exists
      self.cursor.execute("SELECT * FROM students WHERE roll_no = %s", (roll_no,))
      if not self.cursor.fetchone():
        print("Student not found")
        return
      print("Enter new details. Leave blank to keep old value")
      name = input("New Name: ").strip()
      age = input("New Age: ")
      marks = input("New Marks: ")
      class_sec = input("New Class/Section: ").strip()
      # Lists for dynamic query
      updates = []
      values = []
      # Update name if entered
      if name:
        updates.append("name = %s")
        values.append(name)
      # Update age if entered
      if age: 
        age = int(age)
        if age <= 0: 
          raise ValueError("Age must be positive")
        updates.append("age = %s")
        values.append(age)
      # Update marks if entered
      if marks:
        marks = float(marks)
        if marks < 0 or marks > 100: 
          raise ValueError("Invalid marks")
        updates.append("marks = %s")
        values.append(marks)
      # Update class section if entered
      if class_sec:
        updates.append("class_section = %s")
        values.append(class_sec)
      # If no changes
      if not updates:
        print("No changes made")
        return
      values.append(roll_no) # Add roll number to values list
      # Dynamic SQL update query
      query = f"UPDATE students SET {', '.join(updates)} WHERE roll_no = %s"
      self.cursor.execute(query, values) # Execute update query
      self.conn.commit()
      print("Student updated successfully")
      self.export_to_file() # Update backup file
    except ValueError as e:
      print(f"Invalid input: {e}")
    except Error as e:
      print(f"Database error: {e}")
  def delete_student(self):
    try:
      roll_no = int(input("Enter Roll Number to delete: "))
      # Execute delete query
      self.cursor.execute("DELETE FROM students WHERE roll_no = %s", (roll_no,))
      if self.cursor.rowcount == 0: # rowcount returns affected rows
        print("Student not found")
      else:
        self.conn.commit()
        print("Student deleted permanently")
        self.export_to_file()
    except ValueError:
      print("Invalid roll number")
    except Error as e:
      print(f"Database error: {e}")
  def search_student(self):
    try:
      print("Search by: 1. Roll Number  2. Name")
      choice = input("Enter choice: ")
      if choice == '1': # Search by roll number
        roll_no = int(input("Enter Roll Number: "))
        query = "SELECT * FROM students WHERE roll_no = %s"
        self.cursor.execute(query, (roll_no,))
      elif choice == '2': # Search by name
        name = input("Enter Name: ").strip()
        query = "SELECT * FROM students WHERE name LIKE %s"
        self.cursor.execute(query, (f"%{name}%",))
      else:
        print("Invalid choice")
        return
      records = self.cursor.fetchall() # Fetch records
      if not records: # If no student found
        print("No matching student found")
      else:
        for r in records:
          print(f"RollNo.: {r['roll_no']}, Name: {r['name']}, Age: {r['age']}, Marks: {r['marks']}, Class: {r['class_section']}")
    except ValueError:
      print("Invalid input")
    except Error as e:
      print(f"Database error: {e}")
  # Function to export data to text file
  def export_to_file(self):
    try:
      # Fetch all records
      self.cursor.execute("SELECT * FROM students ORDER BY roll_no")
      records = self.cursor.fetchall()
      # Open file in write mode
      with open(self.backup_file, 'w') as f:
        f.write("RollNo,Name,Age,Marks,Class\n")
        for r in records:
          f.write(f"{r['roll_no']},{r['name']},{r['age']},{r['marks']},{r['class_section']}\n")
    except IOError as e:
      print(f"File error: {e}")
    except Error as e:
      print(f"Database error during export: {e}")
  # Function to read backup file
  def read_from_file(self):
    print("\n-- Data from File Backup --")
    try:
      # Check whether file exists
      if not os.path.exists(self.backup_file):
        print("Backup file not found")
        return
      # Open file in read mode
      with open(self.backup_file, 'r') as f:
        for line in f: # Print each line
          print(line.strip())
    except IOError as e:
      print(f"File read error: {e}")
    except Exception as e:
      print(f"Data corruption case: {e}")
  # Function to close connection    
  def close(self):
    self.cursor.close() # Close cursor
    self.conn.close() # Close database connection
    print("Connection closed")

def main():
  sms = StudentManagementSystem() # Create object
  while True: # Display menu
    print("\n=== Student Management System ===")
    print("1. Add Student")
    print("2. View Students") 
    print("3. Update Student")
    print("4. Delete Student")
    print("5. Search Student")
    print("6. View File Backup")
    print("7. Exit")
    choice = input("Enter choice: ")
    # Call corresponding functions
    if choice == '1': sms.add_student()
    elif choice == '2': sms.view_students()
    elif choice == '3': sms.update_student()
    elif choice == '4': sms.delete_student()
    elif choice == '5': sms.search_student()
    elif choice == '6': sms.read_from_file()
    elif choice == '7': 
      sms.close() # Close connection and exit
      break
    else: print("Invalid choice")
    
if __name__ == "__main__": # Start program
  main()
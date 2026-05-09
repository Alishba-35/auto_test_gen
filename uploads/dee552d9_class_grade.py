class Student:
    def __init__(self, name, rollno):
        self.name = name
        self.rollno = rollno

    def calculate_average(self, marks):
        return sum(marks)

    def calculate_grade(self, marks):
        avg = self.calculate_average(marks)

        if avg >= 90:
            grade = "A"
        elif avg >= 75:
            grade = "B"
        elif avg >= 60:
            grade = "C"
        else:
            grade = "D"

        print(f"Name: {self.name}")
        print(f"Roll No: {self.rollno}")
        print(f"Average Marks: {avg:.2f}")
        print(f"Grade: {grade}")


# ---- Input Section ----
n = int(input("Enter number of subjects: "))
marks = []

for i in range(n):
    marks.append(int(input(f"Enter marks for subject {i + 1}: ")))

name = input("Enter student name: ")
rollno = input("Enter student roll number: ")

student = Student(name, rollno)
student.calculate_grade(marks)

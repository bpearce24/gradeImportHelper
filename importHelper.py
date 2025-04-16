"""Script to help make importing grades and adding assignments into schoology
via a CSV file easier. """

import csv
import os
import re

from typing import List

# The script ask for the following information:
# - if this is for ProjectStem or CodeHS grade import
# - the file path for the roster file
# - the file path for the grades file
# - what to name the output file
# - what range of assignments to import 
# (eg CodeHS: 8.1.3-8.3.9 or ProjectStem 5.4 - 5.8)

def main():
    # Get information from the user
    import_type = get_grade_import_type()
    roster_file, grades_file, output_file = get_file_paths()
    #assignment_range = get_assignment_range(import_type)
    # Check if the grades file is valid
    if not grade_file_is_valid(grades_file):
        print("Invalid grades file. Please check the file and try again.")
        exit(1)
    # Check if the roster file is valid
    if not roster_file_is_valid(roster_file):
        print("Invalid roster file. Please check the file and try again.")
        exit(1)
    # Get the indices of the assignments that are for a grade
    graded_assignments = getGradedAssignments(grades_file, import_type)
    print("Graded assignments: ", graded_assignments)
    # Build a dictionary of students from the grade file using the email as the 
    # key and the row as the value to enable quick lookups
    roster = get_students_in_roster(roster_file)
    if import_type == 'C':
        grades = get_codehs_grades_from_file(grades_file)
        build_CodeHS_csv(roster, grades, graded_assignments, output_file)
    elif import_type == 'P':
        # TODO: Implement the rest of ProjectStem later
        print("ProjectStem import is not yet implemented.")



def get_grade_import_type():
    """Prompt the user for the grade import type and return it."""
    while True:
        grade_import_type = input("Is this for ProjectStem or CodeHS? (P/C): ").strip().upper()
        if grade_import_type in ['P', 'C']:
            return grade_import_type
        else:
            print("Invalid input. Please enter 'P' for ProjectStem or 'C' for CodeHS.")


def get_file_paths():
    """Prompt the user for file paths and return them."""
    roster_file = get_file_path("Enter the path to the roster file: ")
    grades_file = get_file_path("Enter the path to the grades file: ")
    output_file = input("Enter the name of the output file: ")
    return roster_file, grades_file, output_file


def get_file_path(prompt):
    """Prompt the user for a file path and return it."""
    while True:
        file_path = input(prompt)
        if os.path.exists(file_path):
            return file_path
        else:
            print(f"File not found: {file_path}. Please try again.")


def get_assignment_range(import_type):
    """Prompt the user for the assignment range for ProjectStem and return it."""
    prompt = "Enter the assignment range (eg 5.4-5.8): "
    error_message = "Invalid format. Please enter the range in the format X.X-X.X."
    if import_type == 'C':
        prompt = "Enter the assignment range (eg 8.1.3-8.3.9): "
        error_message = "Invalid format. Please enter the range in the format X.X.X-X.X.X."
    while True:
        assignment_range = input(prompt)
        try:
            first_assignment, second_assignment = assignment_range.split('-')
            if check_assignment_range(first_assignment, second_assignment):
                return first_assignment, second_assignment
        except ValueError:
            print(error_message)


def check_assignment_range(first_assignment, second_assignment):
    """Check if the assignment range is valid."""
    # Split the assignment numbers into parts
    first = list(map(int, first_assignment.split('.')))
    second = list(map(int, second_assignment.split('.')))
    
    # Check if the first assignment is less than the second assignment
    if first > second:
        print("Invalid assignment range. The first assignment should be less than the second assignment.")
        return False
    return True


def grade_file_is_valid(gradesfile):
    """Do some basic checks of the grades file to ensure it is valid."""
    # Check if the length of each row is the same
    with open(gradesfile, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        # Get the number of columns in the header
        num_columns = len(header)
        for i, row in enumerate(reader):
            if len(row) != num_columns:
                print(f"Invalid grades file, number of columns in row {i} doesn't match header.")
                print("Please check the file and try again.")
                return False
    print("Grades file seems valid.")
    return True


def roster_file_is_valid(roster_file)->bool:
    """Open the roster file and ensure: 
    * the headers are all there
    * all the students have an email, first name, last and student id
    * the student id in the email matches the student id in the unique id"""
    is_valid = True
    with open(roster_file, 'r') as file:
        reader = csv.reader(file)
        is_valid = (validate_headers(file, reader) and 
                    validate_student_ids(file, reader) and
                    validate_student_data(file, reader))
        
    # TODO: Make sure there is at least one student.
    # TODO: Make sure there are no duplicate emails or unique ids.
    if is_valid:
        print("Roster file seems valid.")
        return True
    else:
        return False
    

def validate_headers(file, reader)->bool:
    file.seek(0)  # Reset the reader to the beginning of the file
    header_row = next(reader)
    required_headers = [
        'Student Email',
        'First Name',
        'Last Name',
        'Unique User ID'
    ]
    file_is_missing_headers = False
    
    # make to strip the headers of any whitespace
    for header in header_row:
        header = header.strip()

    for header in required_headers:
        if header not in header_row:
            print(f"Roster file must contain '{header}' in the header row.")
            file_is_missing_headers = True
    if file_is_missing_headers:
        print("Roster file is missing required headers. Please check the file and try again.")
        return False
    if header_row[0].strip() != 'Student Email':
        print("Roster file must contain 'Student Email' in the first column of the header row.")
        return False
    if header_row[3].strip() != 'Unique User ID':
        print("Roster file must contain 'Unique User ID' in the fourth column of the header row.")
        return False
    return True

def validate_student_data(file, reader)->bool:
    file.seek(0)  # Reset the reader to the beginning of the file
    header_row = next(reader)  # Skip the header row
    is_data_missing = False
    for i, row in enumerate(reader):
        if len(row) < 4:
            print(f"Missing data in row {i+1}. Roster file should contain 4 columns for each student.")
            #ensure that the student email and  unique id arn't empty strings
            is_data_missing = True
            continue
        unique_id = row[header_row.index('Unique User ID')]
        student_email = row[header_row.index('Student Email')]
        if (not student_email or not unique_id):
            print(f"Missing data in row {i+1}. Email and Unique Id should not be empty.")
            print("Please check the file and try again.")
            is_data_missing = True
    if is_data_missing:
        print("Roster file is missing required data. Please check the file and try again.")
        return False
    return True


def validate_student_ids(file, reader):
    #The email and the unique id both have a student id number. Since the email
    # is used to link the student in the roster files to the student and grades
    # in the grades file. As such, the program must make sure the id number in
    # the email is the same as the one in the unique id. If the program doesn't
    # the wrong grade will be linked to the wrong student.
    # The email is formated as such: XXYYYYY@<domain> where XX are two letters,
    # YYYYY is the student id number (note that there may be more than 5
    # numbers) and <domain> is the domain of the email.
    # The unique id is formated as such: 1_YYYYY where YYYYY is the student id number
    regex = r'^[a-zA-Z]{2}(\d+)(@.*)$'
    file.seek(0)  # Reset the reader to the beginning of the file
    header_row = next(reader)  # Skip the header row
    for i, row in enumerate(reader):
        student_email = row[header_row.index('Student Email')]
        unique_id = row[header_row.index('Unique User ID')]
        match = re.match(regex, student_email)
        if match:
            student_id = match.group(1)
            if unique_id != "1_" + student_id:
                print(f"Student id in email and unique id do not match in row {i+1}.")
                print("Please check the file and try again.")
                return False
        else:
            print(f"Invalid email format in row {i+1}.")
            print("Please check the file and try again.")
            return False
    return True


def getGradedAssignments(grades_file, import_type)->list[int]:
    """Open the grades file and get the list of graded assignments"""
    graded_indices = []
    if import_type == 'P':
        graded_indices = get_ProjectStem_graded_assignments(grades_file)
    elif import_type == 'C':
        graded_indices = get_CodeHS_graded_assignments(grades_file)
    return graded_indices

def get_CodeHS_graded_assignments(grades_file)->list[int]:
    with open(grades_file, 'r') as file:
        reader = csv.reader(file)
        # We don't need the first or second row.
        _ = next(reader)
        _ = next(reader)
        # Get the all the assignments
        assignment_types = next(reader)[:]
        # Get the indices of the assignments that are graded
        graded_indices = []
        for i, assignment_type in enumerate(assignment_types):
            if assignment_type.strip().lower() in ['check for understanding', 'exercise', 'unit quiz']:
                graded_indices.append(i)
        return graded_indices

def get_ProjectStem_graded_assignments(grades_file)->list[int]:
    """All of the assignments are graded in ProjectStem, so we just need to 
    get the length of the header and remove the first two items"""
    with open(grades_file, 'r') as file:
        reader = csv.reader(file)
    header = next(reader)
    num_columns = len(header)
    return [ i for i in range(2, num_columns)]
    

def get_students_in_roster(roster_file)->dict[str, List[str]]:
    """Open the roster file and get the list of students"""
    students = {}
    with open(roster_file, 'r') as file:
        reader = csv.reader(file)
        header_row = next(reader)
        students["header"] = header_row
        for row in reader:
            # Get the email
            student_email = row[0]
            # Add the student to the dictionary
            students[student_email] = row
    return students


def get_codehs_grades_from_file(grades_file)->dict[str, List[str]]:
    """Open the grades file and return a dictionary of students with their email
    as the key"""
    with open(grades_file, 'r') as file:
        reader = csv.reader(file)
        grades = {}
        grades["header"] = next(reader)
        # Get the grades for each student
        # Skip the next two rows
        _ = next(reader)
        _ = next(reader)
        for row in reader:
            # Get the email and unique id
            student_email = row[2]
            # Add the student to the dictionary
            grades[student_email] = row
    return grades

def build_CodeHS_csv(roster, grades, graded_assignments, output_file):
    """Build a CSV file for CodeHS
    Parameters:
        * roster (dict): A dictionary of students with their email as the key
          and the row as the value.
        * grades (dict) A dictionary of student grades with the email as the key
        and the row as the value. The first row is the header and contains the
          every assignment (including ungraded assignments, it will need to be
          filterd).
        * graded_assignments (list): A list of indices of the assignments that 
          included in the gradebook.
        * output_file (str): The name of the output file."""
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        header = build_CodeHS_csv_header(grades, graded_assignments)
        writer.writerow(header)
        #for student in roster:
            #row = build_CodeHS_row(student, grades, graded_assignments)


def build_CodeHS_csv_header(grades, graded_assignments):
    # Get the names of the graded assignments.
    assignments = []
    for i in graded_assignments:
        assignments.append(grades["header"][i])
    # Write the header
    header_row = ([ 
        'Email',
        'First Name',
        'Last Name',
        'Unique User ID']
        + assignments)
    return header_row

def build_CodeHS_row(student, roster, grades, graded_assignments):
    pass

if __name__ == "__main__":
    main()

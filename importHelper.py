"""Script to help make importing grades and adding assignments into schoology
via a CSV file easier. """

import csv
import os

from typing import List

# The script ask for the following information:
# - if this is for ProjectStem or CodeHS grade import
# - the file path for the roster file
# - the file path for the grades file
# - what to name the output file
# - what range of assignments to import 
# (eg CodeHS: 8.1.3-8.3.9 or ProjectStem 5.4 - 5.8)

def get_grade_import_type():
    """Prompt the user for the grade import type and return it."""
    while True:
        grade_import_type = input("Is this for ProjectStem or CodeHS? (P/C): ").strip().upper()
        if grade_import_type in ['P', 'C']:
            return grade_import_type
        else:
            print("Invalid input. Please enter 'P' for ProjectStem or 'C' for CodeHS.")

def get_file_path(prompt):
    """Prompt the user for a file path and return it."""
    while True:
        file_path = input(prompt)
        if os.path.exists(file_path):
            return file_path
        else:
            print(f"File not found: {file_path}. Please try again.")


def get_file_paths():
    """Prompt the user for file paths and return them."""
    roster_file = get_file_path("Enter the path to the roster file: ")
    grades_file = get_file_path("Enter the path to the grades file: ")
    output_file = input("Enter the name of the output file: ")
    return roster_file, grades_file, output_file

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
        for row in reader:
            if len(row) != num_columns:
                print("Invalid grades file. Please check the file and try again.")
                return False
    print("Grades file seems valid.")
    return True

def get_nongraded_assinments(grades_file, import_type)->list[int]:
    """ Open the grades file and look for assignments that aren't graded.
    CodeHS files have multiple header rows. The first row has the first and last
    name in the first two columns. Assignment names begin in the 9th column of
    the first row and continue until the last column.
    The third row contains the Activity type.
    Assignments that are not graded include: Video, Example, Survey and Badge.
    Return a list of indices of the assignments that are not graded."""
    
    # Open the grades file and look for assignments that aren't graded.
    with open(grades_file, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        # Get the indices of the assignments
        assignment_indices = list(range(8, len(header)))
        # Get the assignment names
        assignment_names = header[8:]
        # Get the activity types
        activity_types = next(reader)[8:]
        # Check if the activity types are valid
        if len(activity_types) != len(assignment_names):
            print("Invalid grades file. Please check the file and try again.")
            return []
        # Get the indices of the assignments that are not graded
        nongraded_indices = []
        for i, activity_type in enumerate(activity_types):
            if activity_type in ['Video', 'Example', 'Survey', 'Badge']:
                nongraded_indices.append(i)
        return nongraded_indices

def remove_indices_from_list(lst, indices:List[int])-> bool:
    """Remove indices from a list."""
    #check if the indices are valid
    indices.sort()
    if indices[0] < 0 or indices[-1] >= len(lst):
        print("Invalid indices. Please check the indices and try again.")
        return False
    for i in reversed(indices):
        lst.pop(i)
    return True

def roster_file_is_valid(roster_file)->bool:
    """Open the roster file and ensure all the students have a first name, last
    name and unique user id. """
    with open(roster_file, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        if 'First Name' not in header or 'Last Name' not in header or 'Unique User ID' not in header:
            print("Roster file must contain 'First Name', 'Last Name', and 'Unique User ID' columns.")
            return False
        if header[2] != 'Unique User ID':
            print("Roster file must contain 'Unique User ID' in the third column of the header row.")
            return False
        for row in reader:
            if len(row) < 3:
                print("Roster file must contain at least 3 columns.")
                return False
            #ensure that first last and unique id arn't empty strings
            first_name = row[header.index('First Name')]
            last_name = row[header.index('Last Name')]
            unique_id = row[header.index('Unique User ID')]
            if not first_name or not last_name or not unique_id:
                print("Roster file must contain a first name, last name, and unique user id for each student.")
                return False
        print("Roster file seems valid.")
        return True



if __name__ == "__main__":
    # Get information from the user
    import_type = get_grade_import_type()
    roster_file, grades_file, output_file = get_file_paths()
    assignment_range = get_assignment_range(import_type)
    # Check if the grades file is valid
    if not grade_file_is_valid(grades_file):
        print("Invalid grades file. Please check the file and try again.")
        exit(1)
    # Check if the roster file is valid
    if not roster_file_is_valid(roster_file):
        print("Invalid roster file. Please check the file and try again.")
        exit(1)




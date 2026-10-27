"""
File storage of the Restaurant Management System.

Reads and writes the JSON files (restaurant data and group requests)
and checks that their content makes sense. It never uses print() or
input(): if something is wrong it raises an exception, and main.py
catches it and tells the user.
"""
import json
import os

def load_groups(path):
    """Read a group requests file and return the group sizes, e.g. [4, 2, 6].

    Raises ValueError if the file is not a list or any group is invalid.
    FileNotFoundError and json.JSONDecodeError are not caught here.
    """
    with open(path, encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("The group file must be a list of groups.")

    groups = []
    number = 0
    for group in data:
        number += 1
        if not isinstance(group, dict):
            raise ValueError(f'Group {number} must be an object with a "customers" key.')
        if "customers" not in group:
            raise ValueError(f'Group {number}: the "customers" key is missing.')
        customers = group["customers"]
        if type(customers) != int or customers <= 0:
            raise ValueError(f'Group {number}: "customers" must be a whole number greater than 0.')
        groups.append(customers)
    return groups


def list_group_files(folder):
    """Return the sorted names of the .json files in folder, e.g. ["groups_2.json"].

    FileNotFoundError is not caught here if the folder does not exist.
    """
    files = []
    for name in os.listdir(folder):
        if name[-5:] == ".json":
            files.append(name)
    return sorted(files)


def _run_tests():
    """Check the storage functions with the test files in tables/. No output means all passed."""
    # A valid file returns the list of group sizes
    assert load_groups("tables/groups_2.json") == [4, 2, 6, 3, 5, 2, 8]

    # A group with wrong data rejects the whole file
    try:
        load_groups("tables/groups_bad.json")
        assert False, "groups_bad.json should raise ValueError"
    except ValueError:
        pass

    # A badly written JSON is not caught here: it goes up to main.py
    try:
        load_groups("tables/groups_broken.json")
        assert False, "groups_broken.json should raise JSONDecodeError"
    except json.JSONDecodeError:
        pass

    # A file that does not exist is not caught here either
    try:
        load_groups("tables/does_not_exist.json")
        assert False, "a missing file should raise FileNotFoundError"
    except FileNotFoundError:
        pass

    # list_group_files returns only .json names, sorted
    files = list_group_files("tables")
    assert "groups_2.json" in files
    assert files == sorted(files)
    for name in files:
        assert name[-5:] == ".json"

    # A folder that does not exist is not caught here
    try:
        list_group_files("folder_that_does_not_exist")
        assert False, "a missing folder should raise FileNotFoundError"
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    _run_tests()


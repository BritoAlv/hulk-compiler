import os
from pathlib import Path

def create_test(name: str, test: str, expected: str):
    test_file = f"./tests/{name}.test"
    expected_file = f"./tests/{name}.expected"

    with open(test_file, "w") as f:
        f.write(test)

    with open(expected_file, "w") as f:
        f.write(expected)




""" # Read test cases from tests.md
test_cases = []
with open("./tests.md", "r") as f:
    test = f.read()
    test_cases = test.split("##")
    test_cases = [case.strip() for case in test_cases if case.strip()]
    for i in range(0, len(test_cases)):
        print(test_cases[i])
        name = input()
        expected = input()
        create_test(name, test_cases[i], expected)
"""
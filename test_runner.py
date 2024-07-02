import glob
import os


def runner():
    test_files = glob.glob('./test/tests/*.test')
    result_oks = []
    result_bad = []
    for file in test_files:
        with open(file, 'r') as f:
            name = f.name
            output_name = name[:-4] + "out"

            result = os.system(f'python3 main.py -r < {name} > {output_name}')

            if result == 0:
                result_oks.append(name)
            else:
                result_bad.append(name)

    return (result_oks, result_bad)

results = runner()

print("Good: ")
for x in results[0]:
    print(x)
print("--------------")
print("Bad: ")
for x in results[1]:
    print(x)
print("--------------")
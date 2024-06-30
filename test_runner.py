import glob
import os

def runner():
    test_files = glob.glob('./test/tests/*.test')
    for file in test_files:
        with open(file, 'r') as f:
            name = f.name
            output_name = name[:-4] + "out"
            os.system(f'python3 main.py -r < {name} > {output_name}')

runner()
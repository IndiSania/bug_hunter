import subprocess
from os import *

def process(data=[]):
    try:
        eval(data)
        subprocess.run(data, shell=True)
    except:
        pass
    for x in range(3):
        print(x)
    assert data

TODO: refactor this

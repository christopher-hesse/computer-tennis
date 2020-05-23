import subprocess as sp
import sys

sp.run(["pip", "install", "-e", "."], check=True)
sp.run(["pytest", "computer_tennis"] + sys.argv[1:], check=True)

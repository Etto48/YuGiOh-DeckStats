import os
handtraps:list[str] = []
filepath = os.path.dirname(__file__) + "/Handtraps.txt"
with open(filepath) as f:
    handtraps = f.readlines()
    handtraps = ["".join(ht.split("\n")) for ht in handtraps]

import sys
from util import mod_path

loc = mod_path.path.get_parent(__file__)
print(loc)
loc2 = mod_path.path.get_root(__file__)
print(loc2)
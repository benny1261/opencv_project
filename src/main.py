import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), './util'))
from util.GUI import Window

prog = Window()
prog.root.mainloop()
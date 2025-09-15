# -----------------------------------------------------------------------------
# File: __init__.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------

# Without this file, Python won't recognize a directory as a package.
# Runs first when this package is imported
from .corridor import enterCorridor
from .studylandscape import enterStudyLandscape
from .classroom2015 import enterClassroom2015
from .projectroom3 import enterProjectRoom3
from .utils import chooseNextRoom
from .corridorquiz import generate_quadratic_inequality
from .mechanics import take_damage
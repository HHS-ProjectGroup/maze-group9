# -----------------------------------------------------------------------------
# File: __init__.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------

# Without this file, Python won't recognize a directory as a package.
# Runs first when this package is imported
from rooms.classroom2015 import enterClassroom2015
from rooms.corridor import enterCorridor
from rooms.frontdeskoffice import enterFrontDeskOffice
from rooms.lab03 import enterLab03
from rooms.lobby import enterStudyLandscape
from rooms.projectroom3 import enterProjectRoom3


## we don't need it here bc there are not used externally. Can be added if we need smth to initialize on start and not in main(resurcive imports and stuff)
# from mechanics import *
# from utils import chooseNextRoom
# from corridorquiz import generate_quadratic_inequality

# Runs first when this package is imported
from rooms.classroom2015 import enterClassroom2015
from rooms.corridor import enterCorridor
from rooms.frontdeskoffice import enterFrontDeskOffice
from rooms.lab03 import enterLab03
from rooms.studylandscape import enterStudyLandscape
from rooms.projectroom3 import enterProjectRoom3
from rooms.lab01 import enterLab01


# __all__ = [enterLab03, enterClassroom2015, enterProjectRoom3, enterFrontDeskOffice, enterCorridor, enterStudyLandscape]

## we don't need it here bc there are not used externally. Can be added if we need smth to initialize on start and not in main(resurcive imports and stuff)
# from mechanics import *
# from utils import chooseNextRoom
# from corridorquiz import generate_quadratic_inequality

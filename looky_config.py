RETINA_UNIT_DEG = 2.0
RETINA_ALTERNATE_UNIT_DEG = 0.5

OFFSET_UNIT_PIXELS = 10
OFFSET_CROSS_DURATION = 3.0
OFFSET_COLOR = [0.5,0.1,0.1]

DEFAULT_LINE_WIDTH_DEG = 1.0/30.0
DEFAULT_TARGET_RADIUS_DEG = 1.0
LINE_WIDTH_UNIT = DEFAULT_LINE_WIDTH_DEG/2.0
TARGET_RADIUS_UNIT = 0.1

BLINK_PERIOD = 1e10
BLINK_PERIOD_ADJUSTMENT_FACTOR = 0.1
BLINK_DUTY_CYCLE = 0.5
BLINK_PERIOD_MINIMUM = 0.2

TARGET_DEFAULT_SCREEN = 0
FUNDUS_DEFAULT_SCREEN = 1

USE_FUNDUS_IMAGE = False
FUNDUS_IMAGE_DIRECTORY = './fundus'

BACKGROUND_COLOR = [0.0,0.0,0.0]
FOREGROUND_COLOR = [0.99,0.99,0.99]

FONT_NAME = 'sans' # 'sans', 'times','serif'
FONT_SIZE = 14

HELP_FONT_SIZE = 12
HELP_COLOR = [255,255,255,255]

CONSOLE_FONT_NAME = 'courier'
CONSOLE_FONT_SIZE = 12

LOGGING_PERIOD = 30.0
LOGGING_SETTLING_PERIOD = 1.5

MAX_GRID_POINTS = 2e4
DEFAULT_GRID_BORDER = 400
TARGET_GRID_CENTER_COLOR = [0.5,0.5,0.5]
TARGET_GRID_MAJOR_COLOR = [0.4,0.4,0.4]
TARGET_GRID_MINOR_COLOR = [0.2,0.2,0.2]

FUNDUS_GRID_CENTER_COLOR = [0.0,0.0,0.0]
FUNDUS_GRID_MAJOR_COLOR = [0.1,0.1,0.1]
FUNDUS_GRID_MINOR_COLOR = [0.5,0.5,0.5]

EYE_LABELS = ['LE','RE']
HORIZONTAL_LABELS = ['TR','','NR']
VERTICAL_LABELS = ['IR','','SR']
LEFT = 0
RIGHT = 1

CALIBRATION_FILENAME = 'dpi_calibration.txt'

DISTANCE_TO_SCREEN_M = 0.93
MAGNIFICATION = 1.0

# FRAME_RATE = 10.0
# DEFAULT_TARGET_PERIOD = 1.0
################################################################################
# PLATE SCALE and INVERSIONS
# An important parameter is the plate scale of the fixation target
# optical system. You may define it explicitly or use the function
# COMPUTE_PLATE_SCALE:
def COMPUTE_PLATE_SCALE(dZ,magnification):
    import math
    '''Calculate plate scale (in rad/m) for a given
    distance (dZ) between the eye and screen. If refractive
    elements are employed between the screen and the eye,
    magnification or minificaiton of the screen may occur.
    Use the magnification parameter accordingly.'''
    return 2.0 * math.atan(magnification*1.0/(2.0*dZ))

PLATE_SCALE_RAD_PER_M = COMPUTE_PLATE_SCALE(DISTANCE_TO_SCREEN_M,MAGNIFICATION)

# Additionally, the image of the screen may be inverted horizontally and/or
# vertically. Please specify these by setting H_ORIENTATION and V_ORIENTATION
# to 1.0 or -1.0 accordingly. If, for instance, a single planar mirror is
# used in the target system, H_ORIENTATION will be -1.0 and V_ORIENTATION will
# be 1.0. If a real, inverted image of the screen is reimaged onto the retina,
# both should be -1.0.

H_ORIENTATION = -1.0
V_ORIENTATION = 1.0
################################################################################


TESTING = False

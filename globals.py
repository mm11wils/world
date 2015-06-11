import libtcodpy as ltc

#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
 
#size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 43
 
#sizes and coordinates relevant for the GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50
CHARACTER_SCREEN_WIDTH = 30
LEVEL_SCREEN_WIDTH = 40
 
#parameters for dungeon generator
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
 
#spell values
HEAL_AMOUNT = 40
LIGHTNING_DAMAGE = 40
LIGHTNING_RANGE = 5
CONFUSE_RANGE = 8
CONFUSE_NUM_TURNS = 10
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 25
 
#experience and level-ups
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150
 
 
FOV_ALGO = 0  #default FOV algorithm
FOV_LIGHT_WALLS = True  #light walls or not
TORCH_RADIUS = 10
 
LIMIT_FPS = 20  #20 frames-per-second maximum
 
 
#color_dark_wall = ltc.Color(0, 0, 100)
#color_light_wall = ltc.Color(130, 110, 50)
#color_dark_ground = ltc.Color(50, 50, 150)
#color_light_ground = ltc.Color(200, 180, 50)
 
color_dark_wall = ltc.Color(50, 50, 50)
color_light_wall = ltc.Color(190, 190, 190)
color_dark_ground = ltc.Color(35, 35, 35)
color_light_ground = ltc.Color(140, 80, 25)

fov_recompute = False

objects = []

ltc.console_set_custom_font('arial10x1023.png', ltc.FONT_TYPE_GREYSCALE | ltc.FONT_LAYOUT_TCOD)
ltc.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/ltc tutorial', False)
ltc.sys_set_fps(LIMIT_FPS)
con = ltc.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = ltc.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

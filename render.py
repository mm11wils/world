from globals import *


import libtcodpy as ltc
import math
import textwrap
import shelve


    
def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute
 
    if fov_recompute:
        #recompute FOV if needed (the player moved or something)
        fov_recompute = False
        ltc.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
 
        #go through all tiles, and set their background color according to the FOV
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = ltc.map_is_in_fov(fov_map, x, y)
                wall = map[x][y].block_sight
                if not visible:
                    #if it's not visible right now, the player can only see it if it's explored
                    if map[x][y].explored:
                        if wall:
                            ltc.console_set_char_background(con, x, y, color_dark_wall, ltc.BKGND_SET)
                        else:
                            ltc.console_set_char_background(con, x, y, color_dark_ground, ltc.BKGND_SET)
                else:
                    #it's visible
                    if wall:
                        ltc.console_set_char_background(con, x, y, color_light_wall, ltc.BKGND_SET )
                    else:
                        ltc.console_set_char_background(con, x, y, color_light_ground, ltc.BKGND_SET )
                        #since it's visible, explore it
                    map[x][y].explored = True
 
    #draw all objects in the list, except the player. we want it to
    #always appear over all other objects! so it's drawn later.
    for object in objects:
        if object != player:
            object.draw()
    player.draw()
 
    #blit the contents of "con" to the root console
    ltc.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)
 
 
    #prepare to render the GUI panel
    ltc.console_set_default_background(panel, ltc.black)
    ltc.console_clear(panel)
 
    #print the game messages, one line at a time
    y = 1
    for (line, color) in game_msgs:
        ltc.console_set_default_foreground(panel, color)
        ltc.console_print_ex(panel, MSG_X, y, ltc.BKGND_NONE, ltc.LEFT,line)
        y += 1
 
    #show the player's stats
    render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
               ltc.light_red, ltc.darker_red)
    ltc.console_print_ex(panel, 1, 3, ltc.BKGND_NONE, ltc.LEFT, 'Dungeon level ' + str(dungeon_level))
 
    #display names of objects under the mouse
    ltc.console_set_default_foreground(panel, ltc.light_gray)
    ltc.console_print_ex(panel, 1, 0, ltc.BKGND_NONE, ltc.LEFT, get_names_under_mouse())
 
    #blit the contents of "panel" to the root console
    ltc.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)



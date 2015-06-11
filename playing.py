from globals import *

import libtcodpy as ltc
import math
import textwrap
import shelve

import render as r

def play_game():
    global key, mouse
 
    player_action = None
 
    mouse = ltc.Mouse()
    key = ltc.Key()
    #main loop
    while not ltc.console_is_window_closed():
        ltc.sys_check_for_event(ltc.EVENT_KEY_PRESS | ltc.EVENT_MOUSE, key, mouse)
        #render the screen
        r.render_all()
 
        ltc.console_flush()
 
        #level up if needed
        check_level_up()
 
        #erase all objects at their old locations, before they move
        for object in objects:
            object.clear()
 
        #handle keys and exit game if needed
        player_action = handle_keys()
        if player_action == 'exit':
            save_game()
            break
 
        #let monsters take their turn
        if game_state == 'playing' and player_action != 'didnt-take-turn':
            for object in objects:
                if object.ai:
                    object.ai.take_turn()
 

from globals import *

import libtcodpy as ltc
import math
import textwrap
import shelve

import map as m
import playing as p
import render as r
import object as o 
import items as i


import ai 

from fighter import Fighter
 

#CLASS OBJECT
 
 
#FIGHTER
 

 
class Equipment:
    #an object that can be equipped, yielding bonuses. automatically adds the i.Item component.
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
 
        self.slot = slot
        self.is_equipped = False
 
    def toggle_equip(self):  #toggle equip/dequip status
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()
 
    def equip(self):
        #if the slot is already being used, dequip whatever is there first
        old_equipment = get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()
 
        #equip object and show a message about it
        self.is_equipped = True
        message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', ltc.light_green)
 
    def dequip(self):
        #dequip object and show a message about it
        if not self.is_equipped: return
        self.is_equipped = False
        message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', ltc.light_yellow)
 
 
def get_equipped_in_slot(slot):  #returns the equipment in a slot, or None if it's empty
    for obj in inventory:
        if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
            return obj.equipment
    return None
 
def get_all_equipped(obj):  #returns a list of equipped items
    if obj == player:
        equipped_list = []
        for item in inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
    else:
        return []  #other objects have no equipment
 
 
def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)
 
    #render the background first
    ltc.console_set_default_background(panel, back_color)
    ltc.console_rect(panel, x, y, total_width, 1, False, ltc.BKGND_SCREEN)
 
    #now render the bar on top
    ltc.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        ltc.console_rect(panel, x, y, bar_width, 1, False, ltc.BKGND_SCREEN)
 
    #finally, some centered text with the values
    ltc.console_set_default_foreground(panel, ltc.white)
    ltc.console_print_ex(panel, x + total_width / 2, y, ltc.BKGND_NONE, ltc.CENTER,
                                 name + ': ' + str(value) + '/' + str(maximum))
 
def get_names_under_mouse():
    global mouse
    #return a string with the names of all objects under the mouse
 
    (x, y) = (mouse.cx, mouse.cy)
 
    #create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [obj.name for obj in objects
             if obj.x == x and obj.y == y and ltc.map_is_in_fov(fov_map, obj.x, obj.y)]
 
    names = ', '.join(names)  #join the names, separated by commas
    return names.capitalize()
 

 
 
def message(new_msg, color = ltc.white):
    #split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
 
    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]
 
        #add the new line as a tuple, with the text and the color
        game_msgs.append( (line, color) )
 

def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
 
    #calculate total height for the header (after auto-wrap) and one line per option
    header_height = ltc.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height
 
    #create an off-screen console that represents the menu's window
    window = ltc.console_new(width, height)
 
    #print the header, with auto-wrap
    ltc.console_set_default_foreground(window, ltc.white)
    ltc.console_print_rect_ex(window, 0, 0, width, height, ltc.BKGND_NONE, ltc.LEFT, header)
 
    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        ltc.console_print_ex(window, 0, y, ltc.BKGND_NONE, ltc.LEFT, text)
        y += 1
        letter_index += 1
 
    #blit the contents of "window" to the root console
    x = SCREEN_WIDTH/2 - width/2
    y = SCREEN_HEIGHT/2 - height/2
    ltc.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)
 
    #present the root console to the player and wait for a key-press
    ltc.console_flush()
    key = ltc.console_wait_for_keypress(True)
 
    if key.vk == ltc.KEY_ENTER and key.lalt:  #(special case) Alt+Enter: toggle fullscreen
        ltc.console_set_fullscreen(not ltc.console_is_fullscreen)
 
    #convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None
 
def inventory_menu(header):
    #show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in inventory:
            text = item.name
            #show additional information, in case it's equipped
            if item.equipment and item.equipment.is_equipped:
                text = text + ' (on ' + item.equipment.slot + ')'
            options.append(text)
 
    index = menu(header, options, INVENTORY_WIDTH)
 
    #if an item was chosen, return it
    if index is None or len(inventory) == 0: return None
    return inventory[index].item
 
def msgbox(text, width=50):
    menu(text, [], width)  #use menu() as a sort of "message box"
 
def handle_keys():
    global key
 
    if key.vk == ltc.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        ltc.console_set_fullscreen(not ltc.console_is_fullscreen())
 
    elif key.vk == ltc.KEY_ESCAPE:
        return 'exit'  #exit game
 
    if game_state == 'playing':
        #movement keys
        if key.vk == ltc.KEY_UP or key.vk == ltc.KEY_KP8:
            player_move_or_attack(0, -1)
        elif key.vk == ltc.KEY_DOWN or key.vk == ltc.KEY_KP2:
            player_move_or_attack(0, 1)
        elif key.vk == ltc.KEY_LEFT or key.vk == ltc.KEY_KP4:
            player_move_or_attack(-1, 0)
        elif key.vk == ltc.KEY_RIGHT or key.vk == ltc.KEY_KP6:
            player_move_or_attack(1, 0)
        elif key.vk == ltc.KEY_HOME or key.vk == ltc.KEY_KP7:
            player_move_or_attack(-1, -1)
        elif key.vk == ltc.KEY_PAGEUP or key.vk == ltc.KEY_KP9:
            player_move_or_attack(1, -1)
        elif key.vk == ltc.KEY_END or key.vk == ltc.KEY_KP1:
            player_move_or_attack(-1, 1)
        elif key.vk == ltc.KEY_PAGEDOWN or key.vk == ltc.KEY_KP3:
            player_move_or_attack(1, 1)
        elif key.vk == ltc.KEY_KP5:
            pass  #do nothing ie wait for the monster to come to you
        else:
            #test for other keys
            key_char = chr(key.c)
 
            if key_char == 'g':
                #pick up an item
                for object in objects:  #look for an item in the player's tile
                    if object.x == player.x and object.y == player.y and object.item:
                        object.item.pick_up()
                        break
 
            if key_char == 'i':
                #show the inventory; if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()
 
            if key_char == 'd':
                #show the inventory; if an item is selected, drop it
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()
 
            if key_char == 'c':
                #show character information
                level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
                msgbox('Character Information\n\nLevel: ' + str(player.level) + '\nExperience: ' + str(player.fighter.xp) +
                       '\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' + str(player.fighter.max_hp) +
                       '\nAttack: ' + str(player.fighter.power) + '\nDefense: ' + str(player.fighter.defense), CHARACTER_SCREEN_WIDTH)
 
            if key_char == '<':
                #go down stairs, if the player is on them
                if stairs.x == player.x and stairs.y == player.y:
                    next_level()
 
            return 'didnt-take-turn'
 
def check_level_up():
    #see if the player's experience is enough to level-up
    level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    if player.fighter.xp >= level_up_xp:
        #it is! level up and ask to raise some stats
        player.level += 1
        player.fighter.xp -= level_up_xp
        message('Your battle skills grow stronger! You reached level ' + str(player.level) + '!', ltc.yellow)
 
        choice = None
        while choice == None:  #keep asking until a choice is made
            choice = menu('Level up! Choose a stat to raise:\n',
                          ['Constitution (+20 HP, from ' + str(player.fighter.max_hp) + ')',
                           'Strength (+1 attack, from ' + str(player.fighter.power) + ')',
                           'Agility (+1 defense, from ' + str(player.fighter.defense) + ')'], LEVEL_SCREEN_WIDTH)
 
        if choice == 0:
            player.fighter.base_max_hp += 20
            player.fighter.hp += 20
        elif choice == 1:
            player.fighter.base_power += 1
        elif choice == 2:
            player.fighter.base_defense += 1
 
def player_death(player):
	#the game ended!
	global game_state
	message('You died!', ltc.red)
	game_state = 'dead'
 
	#for added effect, transform the player into a corpse!
	player.char = '%'
	player.color = ltc.dark_red
 
def monster_death(monster):
    #transform it into a nasty corpse! it doesn't block, can't be
    #attacked and doesn't move
    message('The ' + monster.name + ' is dead! You gain ' + str(monster.fighter.xp) + ' experience points.', ltc.orange)
    monster.char = '%'
    monster.color = ltc.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()
 
def target_tile(max_range=None):
    global key, mouse
    #return the position of a tile left-clicked in player's FOV (optionally in a range), or (None,None) if right-clicked.
    while True:
        #render the screen. this erases the inventory and shows the names of objects under the mouse.
        ltc.console_flush()
        ltc.sys_check_for_event(ltc.EVENT_KEY_PRESS | ltc.EVENT_MOUSE, key, mouse)
        render_all()
 
        (x, y) = (mouse.cx, mouse.cy)
 
        if mouse.rbutton_pressed or key.vk == ltc.KEY_ESCAPE:
            return (None, None)  #cancel if the player right-clicked or pressed Escape
 
        #accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
        if (mouse.lbutton_pressed and ltc.map_is_in_fov(fov_map, x, y) and
                (max_range is None or player.distance(x, y) <= max_range)):
            return (x, y)
 
def target_monster(max_range=None):
    #returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(max_range)
        if x is None:  #player cancelled
            return None
 
        #return the first clicked monster, otherwise continue looping
        for obj in objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != player:
                return obj
 
def closest_monster(max_range):
    #find closest enemy, up to a maximum range, and in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1  #start with (slightly more than) maximum range
 
    for object in objects:
        if object.fighter and not object == player and ltc.map_is_in_fov(fov_map, object.x, object.y):
            #calculate distance between this object and the player
            dist = player.distance_to(object)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = object
                closest_dist = dist
    return closest_enemy
 

 
 
def save_game():
    #open a new empty shelve (possibly overwriting an old one) to write the game data
    file = shelve.open('savegame', 'n')
    file['map'] = map
    file['objects'] = objects
    file['player_index'] = objects.index(player)  #index of player in objects list
    file['stairs_index'] = objects.index(stairs)  #same for the stairs
    file['inventory'] = inventory
    file['game_msgs'] = game_msgs
    file['game_state'] = game_state
    file['dungeon_level'] = dungeon_level
    file.close()
 
def load_game():
    #open the previously saved shelve and load the game data
    global map, objects, player, stairs, inventory, game_msgs, game_state, dungeon_level
 
    file = shelve.open('savegame', 'r')
    map = file['map']
    objects = file['objects']
    player = objects[file['player_index']]  #get index of player in objects list and access it
    stairs = objects[file['stairs_index']]  #same for the stairs
    inventory = file['inventory']
    game_msgs = file['game_msgs']
    game_state = file['game_state']
    dungeon_level = file['dungeon_level']
    file.close()
 
    r.initialize_fov()
 
def new_game():
    global player, inventory, game_msgs, game_state, dungeon_level, objects
	
    o.objects = []
    #create object representing the player
    fighter_component = Fighter(hp=100, defense=1, power=2, xp=0, death_function=player_death)
    player = o.Object(0, 0, '@', 'player', ltc.white, blocks=True, fighter=fighter_component)
	

    player.level = 1

    #generate map (at this point it's not drawn to the screen)
    #dungeon_level = 1
    m.make_map()
    m.initialize_fov()
 
    game_state = 'playing'
    inventory = []

 
    #create the list of game messages and their colors, starts empty
    game_msgs = []
 
    #a warm welcoming message!
    message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', ltc.red)
 
    #initial equipment: a dagger
    equipment_component = Equipment(slot='right hand', power_bonus=2)
    obj = o.Object(0, 0, '-', 'dagger', ltc.sky, equipment=equipment_component)
    inventory.append(obj)
    equipment_component.equip()
    obj.always_visible = True
    print "new_game pass"
 
def next_level():
    #advance to the next level
    global dungeon_level
    message('You take a moment to rest, and recover your strength.', ltc.light_violet)
    player.fighter.heal(player.fighter.max_hp / 2)  #heal the player by 50%
 
    dungeon_level += 1
    message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', ltc.red)
    m.make_map()  #create a fresh new level!
    r.initialize_fov()
 

def main_menu():
    img = ltc.image_load('menu_background.png')
 
    while not ltc.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        ltc.image_blit_2x(img, 0, 0, 0)
 
        #show the game's title, and some credits!
        ltc.console_set_default_foreground(0, ltc.light_yellow)
        ltc.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2-4, ltc.BKGND_NONE, ltc.CENTER,
                                 'TOMBS OF THE ANCIENT KINGS')
        ltc.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT-2, ltc.BKGND_NONE, ltc.CENTER, 'By Jotaf')
 
        #show options and wait for the player's choice
        choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)
 
        if choice == 0:  #new game
            new_game()
            p.play_game()
        if choice == 1:  #load last game
            try:
                load_game()
            except:
                msgbox('\n No saved game to load.\n', 24)
                continue
            p.play_game()
        elif choice == 2:  #quit
            break
 

 
main_menu()

import libtcodpy as ltc
import math
import textwrap
import shelve
import object as o 
import items as i
from fighter import Fighter
 
class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
 
        #all tiles start unexplored
        self.explored = False
 
        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
 
class Rect:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
 
    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)
 
    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)
 
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
 
 
def is_blocked(x, y):
    #first test the map tile
    if map[x][y].blocked:
        return True
 
    #now check for any blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True
 
    return False
 
def create_room(room):
    global map
    #go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False
 
def create_h_tunnel(x1, x2, y):
    global map
    #horizontal tunnel. min() and max() are used in case x1>x2
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False
 
def create_v_tunnel(y1, y2, x):
    global map
    #vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False
 
def make_map():
    global map, objects, stairs
 
    #the list of objects with just the player
    objects = [player]
 
    #fill map with "blocked" tiles
    map = [[ Tile(True)
             for y in range(MAP_HEIGHT) ]
           for x in range(MAP_WIDTH) ]
 
    rooms = []
    num_rooms = 0
 
    for r in range(MAX_ROOMS):
        #random width and height
        w = ltc.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = ltc.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = ltc.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = ltc.random_get_int(0, 0, MAP_HEIGHT - h - 1)
 
        #"Rect" class makes rectangles easier to work with
        new_room = Rect(x, y, w, h)
 
        #run through the other rooms and see if they intersect with this one
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break
 
        if not failed:
            #this means there are no intersections, so this room is valid
 
            #"paint" it to the map's tiles
            create_room(new_room)
 
            #add some contents to this room, such as monsters
            place_objects(new_room)
 
            #center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()
 
            if num_rooms == 0:
                #this is the first room, where the player starts at
                player.x = new_x
                player.y = new_y
            else:
                #all rooms after the first:
                #connect it to the previous room with a tunnel
 
                #center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms-1].center()
 
                #draw a coin (random number that is either 0 or 1)
                if ltc.random_get_int(0, 0, 1) == 1:
                    #first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)
 
            #finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1
 
    #create stairs at the center of the last room
    stairs = o.Object(new_x, new_y, '<', 'stairs', ltc.white, always_visible=True)
    objects.append(stairs)
    stairs.send_to_back()  #so it's drawn below the monsters
 
def random_choice_index(chances):  #choose one option from list of chances, returning its index
    #the dice will land on some number between 1 and the sum of the chances
    dice = ltc.random_get_int(0, 1, sum(chances))
 
    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w
 
        #see if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1
 
def random_choice(chances_dict):
    #choose one option from dictionary of chances, returning its key
    chances = chances_dict.values()
    strings = chances_dict.keys()
 
    return strings[random_choice_index(chances)]
 
def from_dungeon_level(table):
    #returns a value that depends on level. the table specifies what value occurs after each level, default is 0.
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0
 
def place_objects(room):
    #this is where we decide the chance of each monster or item appearing.
 
    #maximum number of monsters per room
    max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]])
 
    #chance of each monster
    monster_chances = {}
    monster_chances['orc'] = 80  #orc always shows up, even if all other monsters have 0 chance
    monster_chances['troll'] = from_dungeon_level([[15, 3], [30, 5], [60, 7]])
 
    #maximum number of items per room
    max_items = from_dungeon_level([[1, 1], [2, 4]])
 
    #chance of each item (by default they have a chance of 0 at level 1, which then goes up)
    item_chances = {}
    item_chances['heal'] = 35  #healing potion always shows up, even if all other items have 0 chance
    item_chances['lightning'] = from_dungeon_level([[25, 4]])
    item_chances['fireball'] =  from_dungeon_level([[25, 6]])
    item_chances['confuse'] =   from_dungeon_level([[10, 2]])
    item_chances['sword'] =     from_dungeon_level([[5, 4]])
    item_chances['shield'] =    from_dungeon_level([[15, 8]])
 
 
    #choose random number of monsters
    num_monsters = ltc.random_get_int(0, 0, max_monsters)
 
    for i in range(num_monsters):
        #choose random spot for this monster
        x = ltc.random_get_int(0, room.x1+1, room.x2-1)
        y = ltc.random_get_int(0, room.y1+1, room.y2-1)
 
        #only place it if the tile is not blocked
        if not is_blocked(x, y):
            choice = random_choice(monster_chances)
            if choice == 'orc':
                #create an orc
                fighter_component = Fighter(hp=20, defense=0, power=4, xp=35, death_function=monster_death)
                ai_component = BasicMonster()
 
                monster = o.Object(x, y, 'o', 'orc', ltc.desaturated_green,
                                 blocks=True, fighter=fighter_component, ai=ai_component)
 
            elif choice == 'troll':
                #create a troll
                fighter_component = Fighter(hp=30, defense=2, power=8, xp=100, death_function=monster_death)
                ai_component = BasicMonster()
 
                monster = o.Object(x, y, 'T', 'troll', ltc.darker_green,
                                 blocks=True, fighter=fighter_component, ai=ai_component)
 
            objects.append(monster)
 
    #choose random number of items
    num_items = ltc.random_get_int(0, 0, max_items)
 
    for i in range(num_items):
        #choose random spot for this item
        x = ltc.random_get_int(0, room.x1+1, room.x2-1)
        y = ltc.random_get_int(0, room.y1+1, room.y2-1)
 
        #only place it if the tile is not blocked
        if not is_blocked(x, y):
            choice = random_choice(item_chances)
            if choice == 'heal':
                #create a healing potion
                item_component = i.Item(use_function=cast_heal)
                item = o.Object(x, y, '!', 'healing potion', ltc.violet, item=item_component)
 
            elif choice == 'lightning':
                #create a lightning bolt scroll
                item_component = i.Item(use_function=cast_lightning)
                item = o.Object(x, y, '#', 'scroll of lightning bolt', ltc.light_yellow, item=item_component)
 
            elif choice == 'fireball':
                #create a fireball scroll
                item_component = i.Item(use_function=cast_fireball)
                item = o.Object(x, y, '#', 'scroll of fireball', ltc.light_yellow, item=item_component)
 
            elif choice == 'confuse':
                #create a confuse scroll
                item_component = i.Item(use_function=cast_confuse)
                item = o.Object(x, y, '#', 'scroll of confusion', ltc.light_yellow, item=item_component)
 
            elif choice == 'sword':
                #create a sword
                equipment_component = Equipment(slot='right hand', power_bonus=3)
                item = o.Object(x, y, '/', 'sword', ltc.sky, equipment=equipment_component)
 
            elif choice == 'shield':
                #create a shield
                equipment_component = Equipment(slot='left hand', defense_bonus=1)
                item = o.Object(x, y, '[', 'shield', ltc.darker_orange, equipment=equipment_component)
 
            objects.append(item)
            item.send_to_back()  #items appear below other objects
            item.always_visible = True  #items are visible even out-of-FOV, if in an explored area
 
 
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
 
 
def message(new_msg, color = ltc.white):
    #split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
 
    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]
 
        #add the new line as a tuple, with the text and the color
        game_msgs.append( (line, color) )
 
 
def player_move_or_attack(dx, dy):
    global fov_recompute
 
    #the coordinates the player is moving to/attacking
    x = player.x + dx
    y = player.y + dy
 
    #try to find an attackable object there
    target = None
    for object in objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break
 
    #attack if target found, move otherwise
    if target is not None:
        player.fighter.attack(target)
    else:
        player.move(dx, dy)
        fov_recompute = True
 
 
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
 
def cast_heal():
    #heal the player
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health.', ltc.red)
        return 'cancelled'
 
    message('Your wounds start to feel better!', ltc.light_violet)
    player.fighter.heal(HEAL_AMOUNT)
 
def cast_lightning():
    #find closest enemy (inside a maximum range) and damage it
    monster = closest_monster(LIGHTNING_RANGE)
    if monster is None:  #no enemy found within maximum range
        message('No enemy is close enough to strike.', ltc.red)
        return 'cancelled'
 
    #zap it!
    message('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
            + str(LIGHTNING_DAMAGE) + ' hit points.', ltc.light_blue)
    monster.fighter.take_damage(LIGHTNING_DAMAGE)
 
def cast_fireball():
    #ask the player for a target tile to throw a fireball at
    message('Left-click a target tile for the fireball, or right-click to cancel.', ltc.light_cyan)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    message('The fireball explodes, burning everything within ' + str(FIREBALL_RADIUS) + ' tiles!', ltc.orange)
 
    for obj in objects:  #damage every fighter in range, including the player
        if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter:
            message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', ltc.orange)
            obj.fighter.take_damage(FIREBALL_DAMAGE)
 
def cast_confuse():
    #ask the player for a target to confuse
    message('Left-click an enemy to confuse it, or right-click to cancel.', ltc.light_cyan)
    monster = target_monster(CONFUSE_RANGE)
    if monster is None: return 'cancelled'
 
    #replace the monster's AI with a "confused" one; after some turns it will restore the old AI
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster  #tell the new component who owns it
    message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', ltc.light_green)
 
 
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
 
    initialize_fov()
 
def new_game():
    global player, inventory, game_msgs, game_state, dungeon_level, objects
	
    o.objects = []
    #create object representing the player
    fighter_component = Fighter(hp=100, defense=1, power=2, xp=0, death_function=player_death)
    player = o.Object(0, 0, '@', 'player', ltc.white, blocks=True, fighter=fighter_component)
	

    player.level = 1

    #generate map (at this point it's not drawn to the screen)
    dungeon_level = 1
    make_map()
    initialize_fov()
 
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
 
def next_level():
    #advance to the next level
    global dungeon_level
    message('You take a moment to rest, and recover your strength.', ltc.light_violet)
    player.fighter.heal(player.fighter.max_hp / 2)  #heal the player by 50%
 
    dungeon_level += 1
    message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', ltc.red)
    make_map()  #create a fresh new level!
    initialize_fov()
 
def initialize_fov():
    global fov_recompute, fov_map
    fov_recompute = True
 
    #create the FOV map, according to the generated map
    fov_map = ltc.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            ltc.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)
 
    ltc.console_clear(con)  #unexplored areas start black (which is the default background color)
 
def play_game():
    global key, mouse
 
    player_action = None
 
    mouse = ltc.Mouse()
    key = ltc.Key()
    #main loop
    while not ltc.console_is_window_closed():
        ltc.sys_check_for_event(ltc.EVENT_KEY_PRESS | ltc.EVENT_MOUSE, key, mouse)
        #render the screen
        render_all()
 
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
            play_game()
        if choice == 1:  #load last game
            try:
                load_game()
            except:
                msgbox('\n No saved game to load.\n', 24)
                continue
            play_game()
        elif choice == 2:  #quit
            break
 
ltc.console_set_custom_font('arial10x1023.png', ltc.FONT_TYPE_GREYSCALE | ltc.FONT_LAYOUT_TCOD)
ltc.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/ltc tutorial', False)
ltc.sys_set_fps(LIMIT_FPS)
con = ltc.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = ltc.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
 
main_menu()

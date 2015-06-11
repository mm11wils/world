from globals import *

import libtcodpy as ltc
import math
import textwrap
import shelve

import playing as p
import render as r
import object as o 
import items as i
import cast as c

import ai 

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
        
def player_death(player):
	#the game ended!
	global game_state
	message('You died!', ltc.red)
	game_state = 'dead'
 
	#for added effect, transform the player into a corpse!
	player.char = '%'
	player.color = ltc.dark_red

def make_map():
    global map, objects, stairs

    #the list of objects with just the player
    objects = [] #no player add yet
 
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
    
dungeon_level = 1

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

def place_objects(room):
    #this is where we decide the chance of each monster or item appearing.
 
    #maximum number of monsters per room
    max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]])
 
    #chance of each monster
    monster_chances = {}
    monster_chances['warg pup'] = 80  #orc always shows up, even if all other monsters have 0 chance
    monster_chances['warg'] = from_dungeon_level([[15, 3], [30, 5], [60, 7]])
 
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
 
    for n in range(num_monsters):
        #choose random spot for this monster
        x = ltc.random_get_int(0, room.x1+1, room.x2-1)
        y = ltc.random_get_int(0, room.y1+1, room.y2-1)
 
        #only place it if the tile is not blocked
        if not is_blocked(x, y):
            choice = random_choice(monster_chances)


            if choice == 'warg pup': 
             
                #create a warg pup
                fighter_component = Fighter(hp=20, defense=0, power=0, xp = 10, death_function=monster_death)
                ai_component = ai.BasicMonster()
                monster = o.Object(x, y, 'w', "warg pup", ltc.amber, blocks=True, fighter=fighter_component, ai=ai_component)
  
            elif choice == 'warg':
             
                #create a warg
                fighter_component = Fighter(hp=16, defense=1, power=4, xp = 100, death_function=monster_death)
                ai_component = ai.BasicMonster()
                monster = o.Object(x, y, 'W', "warg", ltc.dark_orange, blocks=True, fighter=fighter_component, ai=ai_component)
  
            objects.append(monster) 			
 
    #choose random number of items
    num_items = ltc.random_get_int(0, 0, max_items)
 
    for n in range(num_items):
        #choose random spot for this item
        x = ltc.random_get_int(0, room.x1+1, room.x2-1)
        y = ltc.random_get_int(0, room.y1+1, room.y2-1)
 
        #only place it if the tile is not blocked
        if not is_blocked(x, y):
            choice = random_choice(item_chances)
            if choice == 'heal':
                #create a healing potion
                item_component = i.Item(use_function=c.cast_heal)
                item = o.Object(x, y, '!', 'healing potion', ltc.violet, item=item_component)
 
            elif choice == 'lightning':
                #create a lightning bolt scroll
                item_component = i.Item(use_function=c.cast_lightning)
                item = o.Object(x, y, '#', 'scroll of lightning bolt', ltc.light_yellow, item=item_component)
 
            elif choice == 'fireball':
                #create a fireball scroll
                item_component = i.Item(use_function=c.cast_fireball)
                item = o.Object(x, y, '#', 'scroll of fireball', ltc.light_yellow, item=item_component)
 
            elif choice == 'confuse':
                #create a confuse scroll
                item_component = i.Item(use_function=c.cast_confuse)
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
        
def initialize_fov():
    global fov_recompute, fov_map
    fov_recompute = True
 
    #create the FOV map, according to the generated map
    fov_map = ltc.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            ltc.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)
 
    ltc.console_clear(con)  #unexplored areas start black (which is the default background color)           

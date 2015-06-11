from globals import *

import libtcodpy as ltc
import math
import textwrap
import shelve

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

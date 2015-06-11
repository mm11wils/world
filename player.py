import libtcodpy as ltc
import object as object
import fighter as Fighter
import map as m

player_death = Fighter.player_death
fighter_component = Fighter(hp=100, defense=1, power=2, xp=0, death_function=player_death)
player = o.Object(0, 0, '@', 'player', ltc.white, blocks=True, fighter=fighter_component)    

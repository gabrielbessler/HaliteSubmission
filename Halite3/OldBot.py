#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction

import random
import collections  

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   is reserved for the engine-bot communication.
import logging

# This game object contains the initial game state.
game = hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.

class Utils(object): 
    def __init__(self): 
        self.tiles_visited = [] 

utils = Utils()
DROPOFF_THRESHOLD = constants.MAX_HALITE * 0.8
MAX_STEPS_AHEAD = 25
MIN_STEPS_AHEAD = 15
game.ready("Steve v.7")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))
            
""" <<<Game Loop>>> """

def get_valid_position(vertex): 
    directions = Direction.get_all_cardinals()
    random.shuffle(directions) 
    possible_positions = [vertex.directional_offset(direction) for direction in directions]
    for index, position in enumerate(possible_positions):
        if position not in utils.tiles_visited:
            return directions[index]

while True: 
    game.update_frame() 
    me = game.me 
    game_map = game.game_map 
         
    command_queue = [] 
    utils.tiles_visited = [] 
    dropOffs = me.get_dropoffs() 

    def add_move_to_queue(ship, direction): 
        command_queue.append(ship.move(direction))
        utils.tiles_visited += [ship.position.directional_offset(direction)]

    def add_stationary_to_queue(ship): 
        command_queue.append(ship.stay_still())
        utils.tiles_visited += [ship.position]

    def get_closest_dropoff(ship): 
        dropOffDistance = game_map.calculate_distance(me.shipyard.position, ship.position)
        dropOffIndex = -1
        for i in range(len(dropOffs)):
            dropOff = dropOffs[i]
            dist = game_map.calculate_distance(dropOff.position, ship.position)
            if dist < dropOffDistance: 
                dropOffDistance = dist 
                dropOffIndex = i

        if dropOffIndex > -1: 
            destination = me.get_dropoffs()[dropOffIndex]
        else:
            destination = me.shipyard.position
        
        return destination, dropOffDistance

    ships_fixed = [] 
    # Check for ships that cannot move 
    for ship in me.get_ships(): 
        if ship.halite_amount < game_map[ship.position].halite_amount / 10: 
            add_stationary_to_queue(ship)
            ships_fixed.append(ship)

    for ship in me.get_ships(): 
        if ship in ships_fixed:
            continue 
    
        # If the ship is full, return to the drop-off zone 
        # If the game is almost over, drop off the rest of our resources 
        #   - When to drop off resources depends on how far ship is 
        drop_off_destination, drop_off_distance = get_closest_dropoff(ship)
        if ship.halite_amount > DROPOFF_THRESHOLD or (constants.MAX_TURNS - game.turn_number < drop_off_distance + 10 and ship.halite_amount > 0): 
            direction = game_map.naive_navigate(ship, drop_off_destination)
            next_position = ship.position.directional_offset(direction) 
            # Make sure we don't crash into another ship while going back 
            if next_position not in utils.tiles_visited:
                add_move_to_queue(ship, direction)
            elif ship.position not in utils.tiles_visited: 
                add_stationary_to_queue(ship)
            else: 
                add_move_to_queue(ship, get_valid_position(ship.position))

        # If there is not a lot of Halite at the current position go in random (valid) direction
        # Or if another ship is moving to this position 
        elif game_map[ship.position].halite_amount < constants.MAX_HALITE / 10 or game_map[ship.position].position in utils.tiles_visited:
            # Check if we can move 
            if ship.halite_amount < (game_map[ship.position].halite_amount / 10):
                add_stationary_to_queue(ship)
            else: 
                foundDirection = False 
                steps_ahead = 0

                visited = [] # Stores all of the vertices we have already looked at 
                queue = [[ship.position, [], 0]] # Each element is [position, path, cost]
                max_score = 0
                while (not foundDirection and steps_ahead < MAX_STEPS_AHEAD) or (steps_ahead < MIN_STEPS_AHEAD):
                    # Look at one of the vertices 
                    vertex, path, cost = queue.pop(0)

                    # Check if this vertex is a good destination:
                    # 1. See if there are a large number of resources
                    # 2. Compute the cost of arriving there 
                    # 3. Check if cost < reward 
                    resources = game_map[vertex].halite_amount
                    if cost < resources and len(path) != 0 and ship.position.directional_offset(path[0]) not in utils.tiles_visited:
                            score = (resources - cost) / steps_ahead
                            if score > max_score: 
                                max_score = score
                                directionToMove = path[0]
                                foundDirection = True 
                    
                    # Get all tiles you can access from it 
                    directions = Direction.get_all_cardinals()
                    random.shuffle(directions)
                    possible_positions = [vertex.directional_offset(direction) for direction in directions]

                    # For each tile, check if we have already visited it. If not, add to the queue 
                    for index, position in enumerate(possible_positions): 
                        if position not in visited: 
                            visited.append(position)
                            L = [position, path + [directions[index]], cost + (.1*resources)] 
                            queue.append(L)

                    steps_ahead += 1
                    
                if foundDirection is False: 
                    if ship.position == me.shipyard.position or ship.position in utils.tiles_visited:
                        add_move_to_queue(ship, get_valid_position(ship))
                    else:
                        add_stationary_to_queue(ship)
                else:
                    add_move_to_queue(ship, directionToMove)
        else:
            add_stationary_to_queue(ship)

    # If the game is in the first 100 turns and you have enough halite, spawn a ship
    # Prevent ships from colliding on spawn
    if game.turn_number <= 100 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        if game_map[me.shipyard].position not in utils.tiles_visited:
            command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

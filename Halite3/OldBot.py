#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction

import random
import collections  

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("Steve v.4")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))
            
""" <<<Game Loop>>> """

while True: 
    game.update_frame() 
    me = game.me 
    game_map = game.game_map 
         
    command_queue = [] 
     
    tiles_visited = [] 
    for ship in me.get_ships(): 
        
        # Get the closest dropoff point
        dropOffs = me.get_dropoffs() 
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
        
        # If the ship is full we want to return to the drop-off zone 
        # If the game is almost ending, we want to make sure to drop off the rest of our resources 
        #   -> When we drop off the resources depends on how far we are 
        if ship.halite_amount > .8 * constants.MAX_HALITE or (constants.MAX_TURNS - game.turn_number < dropOffDistance + 10 and ship.halite_amount > 0): 
            direction = game_map.naive_navigate(ship, destination)
            next_position = ship.position.directional_offset(direction) 
            # Make sure we don't crash into another ship while going back 
            if next_position not in tiles_visited:
                command_queue.append(ship.move(direction))
                tiles_visited += [ship.position.directional_offset(direction)]
            else: 
                command_queue.append(ship.stay_still())
                tiles_visited += [ship.position]
        # If there is not a lot of Halite at the current position go in random (valid) direction
        # OR if another ship is moving to this position 
        elif game_map[ship.position].halite_amount < constants.MAX_HALITE / 10 or game_map[ship.position].position in tiles_visited:
        
            # Check if we can move 
            if ship.halite_amount < game_map[ship.position].halite_amount / 10:
                command_queue.append(ship.stay_still())
                tiles_visited += [ship.position]
            else: 
                foundDirection = False 
                steps_ahead = 0

                visited = [] # Stores all of the vertices we have already looked at 
                queue = []
                queue.append([ship.position, [], 0]) # Each element is [position, path, cost]
                while steps_ahead < 20:
                    # Look at one of the vertices 
                    vertex, path, cost = queue.pop(0)

                    # Check if this vertex is a good destination:
                    # 1. See if there are a large number of resources
                    # 2. Compute the cost of arriving there 
                    # 3. Check if cost < reward 
                    resources = game_map[vertex].halite_amount
                    if cost < resources:
                        if len(path) != 0 and ship.position.directional_offset(path[0]) not in tiles_visited: 
                            directionToMove = path[0]
                            foundDirection = True 
                            break
                    
                    # Get all tiles you can access from it 
                    directions = [Direction.North, Direction.South, Direction.East, Direction.West] 
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
                    if ship.position == me.shipyard.position:
                        direct = random.choice([Direction.North, Direction.South, Direction.East, Direction.West])
                        command_queue.append(ship.move(direct))
                        tiles_visited += (ship.position.directional_offset(direct))
                    else: 
                        command_queue.append(ship.stay_still())
                        tiles_visited += [ship.position]
                else:
                    tiles_visited += [ship.position.directional_offset(directionToMove)]
                    command_queue.append(ship.move(directionToMove))
            
        # No case 
        else:
            command_queue.append(ship.stay_still())
            tiles_visited += [ship.position]

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number <= 100 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        # Don't spawn ship if another ship is about to enter that spot 
        if game_map[me.shipyard].position not in tiles_visited:
            command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
